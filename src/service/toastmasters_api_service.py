import asyncio
import logging
from api.client_api import ToastmastersAPIClient

class ToastmastersAPIService:
    def __init__(self, client: ToastmastersAPIClient, app_settings):
        """
        Initializes the Toastmasters API Service

        Attributes:
            client (ToastmastersAPIClient): The API client to make requests
            app_settings: Application settings containing app configurations
            logger (logging.Logger): Logger instance for logging messages
        """
        self.client = client
        self.app_settings = app_settings
        self.logger = logging.getLogger(__name__)

    async def _execute_parallel_requests(self, tasks: list, task_description: str):
        """
        Common parallel request executor

        Args:
            tasks (list): List of async tasks to execute
            task_description (str): Description of the tasks for logging

        Returns:
            list: List of results from the executed tasks
        """
        self.logger.info(f"Processing {len(tasks)} {task_description} in parallel")

        # Handle tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter successful results
        successful_results = []
        error_count = 0
        for result in results:
            if isinstance(result, Exception):
                error_count += 1
                self.logger.error(f"Task failed: {result}")
            elif result is not None:
                successful_results.append(result)

        self.logger.info(f"{task_description} completed: {len(successful_results)}/{len(tasks)}")
        if error_count > 0: 
            self.logger.warning(f"{error_count} tasks failed")

        return successful_results, error_count

    async def get_primary_endpoints(self, club_id: str, endpoints: list):
        """
        Fetch primary data from multiple endpoints for a specific club.

        Args:
            club_id (str): The ID of the club to fetch data for
            endpoints (list): List of endpoint names to fetch data from

        Returns:
            dict: Dictionary containing data from each endpoint
        """
        # Create tasks for each endpoint
        tasks = [
            self._fetch_primary_endpoint(club_id, endpoint_name)
            for endpoint_name in endpoints
        ]

        results, error_count = await self._execute_parallel_requests(tasks, "primary endpoints")

        # Primary endpoints must not have errors
        if error_count > 0:
            self.logger.error("Failed to fetch some primary endpoints")
            raise

        # Convert list of tuples to dict
        data_output = {}
        for endpoint_name, endpoint_data in results:
            data_output[endpoint_name] = endpoint_data
            self.logger.info(f"Successfully retrieved {endpoint_name}")

        return data_output
    
    async def get_detailed_progress(self, user_course_combinations: list):
        """
        Fetch detailed progress for multiple user/course combinations.

        Args:
            user_course_combinations (list): List of tuples containing (username, course_id)

        Returns:
            list: List of dictionaries containing detailed progress for each user/course
        """
        self.logger.info(f"Processing {len(user_course_combinations)} user/course combinations")

        tasks = [
            self._fetch_detailed_progress(username, course_id)
            for username, course_id in user_course_combinations
        ]
        
        results, error_count = await self._execute_parallel_requests(tasks, "detailed user progress endpoints")

        # Okay to have errors since their are no dependent API calls
        if error_count > 0:
            self.logger.warning("Failed to fetch some detailed progress data")

        return results
    
    async def _fetch_primary_endpoint(self, club_id: str, endpoint_name: str):
        """
        Fetch data from a primary endpoint for a specific club.

        Args:
            club_id (str): The ID of the club to fetch data for
            endpoint_name (str): The name of the endpoint to fetch data from

        Returns:
            tuple: A tuple containing the endpoint name and the fetched data
        """
        try:
            api_template = self.app_settings.API_ENDPOINTS[endpoint_name]
            api_url = api_template.format(club_id=club_id, page=1)

            success, data, status_code = await self.client.make_async_request(api_url)
            self.logger.info(f"{endpoint_name} API response: {status_code}")

            if success and data:
                endpoint_data = [data]

                # Handle pagination
                self.client.handle_pagination(
                    data,
                    api_url,
                    lambda page_data: endpoint_data.append(page_data)
                )

                return (endpoint_name, endpoint_data)
            else:
                self.logger.error(f"Failed to fetch {endpoint_name}: {status_code}")
                raise

        except Exception as e:
            self.logger.error(f"Error fetching {endpoint_name}: {e}")
            raise
    
    async def _fetch_detailed_progress(self, username: str, course_id: str):
        """
        Fetch detailed progress for a specific user and course.

        Args:
            username (str): The username of the user
            course_id (str): The ID of the course

        Returns:
            dict: Dictionary containing detailed progress data for the user/course
        """
        try:
            api_url = self.app_settings.API_ENDPOINTS["progress_detail"].format(
                course_id=course_id,
                username=username
            )
            
            success, data, status_code = await self.client.make_async_request(api_url)
            
            if success and data:
                return {
                    'username': username,
                    'course_id': course_id,
                    'data': data
                }
            elif status_code == 401:
                self.logger.error("Authentication expired for detailed progress. Please re-authenticate by deleting the toastmasters_session.json.")
                raise           
            else:
                self.logger.error(f"Failed to fetch progress for {username}: {status_code}")
                raise
                
        except Exception as e:
            self.logger.error(f"Error fetching progress for {username}: {e}")
            raise