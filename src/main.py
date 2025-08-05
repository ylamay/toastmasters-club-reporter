import asyncio
import os
import logging
from log.logger import setup_logger
from datetime import datetime
import config.app_settings as APP_SETTINGS
from manager.environment_manager import EnvironmentManager
from manager.file_manager import FileManager
from manager.toastmasters_manager import ToastmastersManager

async def main(logger):
    """
    Main function for data collection

    Args:
        logger (logging.Logger): Logger instance for logging messages
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        logger.info("Starting Toastmasters Data Collection")
        
        # Get project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root  = os.path.dirname(current_dir)

        # Setup env var manager (init directories and env vars)
        env_manager = EnvironmentManager(project_root)

        # Create an instance of the file manager
        file_manager = FileManager(env_manager)

        # Create toastmasters manager instance
        toastmasters_manager = ToastmastersManager(
            app_settings=APP_SETTINGS,
            env_manager=env_manager,
            file_manager=file_manager
        )

        # Authenticate the user
        await toastmasters_manager.authenticate()

        # Fetch data from API endpoints
        result = await toastmasters_manager.fetch_data_from_endpoints()
        if not result:
            logger.error("Data fetching failed")
            raise RuntimeError("Data fetching failed")

        # Build out the indexes
        toastmasters_manager.build_indexes()

        # Save the index files
        toastmasters_manager.save_data()

        logger.info("Data collection completed successfully")

        # Generate the report(s)
        toastmasters_manager.generate_reports()

    except Exception as e:
        logger.error(f"Application error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    # Setup the logger
    setup_logger(log_file="app.log")
    logger = logging.getLogger(__name__)

    start_time = datetime.now()
    
    try:
        exit_code = asyncio.run(main(logger))
    except KeyboardInterrupt:
        logger.warning("Collection interrupted by user")
        exit_code = 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        exit_code = 1
    
    logger.info("Application completed successfully")
    logger.info(f"Total execution time: {(datetime.now() - start_time).total_seconds():.1f} seconds")
    exit(exit_code)