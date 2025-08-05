import logging

def setup_logger(log_file: str = None, level=logging.INFO):
    """
    Setup the logger for the application.

    Args:
        log_file (str): Optional path to a file where logs should be written.
        level (int): Logging level, default is logging.INFO.

    Returns:
        None
    """
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers
    )

def get_logger(name):
    """
    Get a logger instance for the specified name.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: A logger instance with the specified name.
    """
    return logging.getLogger(name)