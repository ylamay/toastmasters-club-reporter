from security.auth import SessionManager, ToastmastersAuthenticator
from api.client_api import ToastmastersAPIClient
from service.toastmasters_api_service import ToastmastersAPIService
from service.toastmasters_data_service import ToastmastersDataService
from service.toastmasters_report_service import ToastmastersReportService
from manager.environment_manager import EnvironmentManager
from manager.file_manager import FileManager
import logging

class ToastmastersManager:
    """
    Manages interactions with the Toastmasters API and user sessions.

    Attributes:
        app_settings: Application settings containing app configurations
        env_manager: Environment Manager for authentication
        file_manager: FileManager instance for file operations
        session_manager: SessionManager instance for handling user sessions
        authenticator: ToastmastersAuthenticator instance for user authentication
        data_service: ToastmastersDataService instance for handling data operations
        report_service: ToastmastersReportService instance for generating reports
        user_id: ID of the authenticated user
        club_id: ID of the club associated with the user
        session_data: Data associated with the current user session
        data_output: Dictionary to store fetched data from API endpoints
        members: Dictionary to store member data indexed by user ID
        club: Club data indexed by club ID
        logger: Logger instance for logging messages
    """
    def __init__(self, app_settings, env_manager: EnvironmentManager, file_manager: FileManager):
        self.app_settings = app_settings
        self.env_manager = env_manager
        self.file_manager = file_manager
        self.session_manager = SessionManager(self.file_manager)
        self.authenticator = ToastmastersAuthenticator(self.session_manager, app_settings)
        self.data_service = ToastmastersDataService(self.env_manager)
        self.report_service = ToastmastersReportService(self.file_manager, app_settings)
        self.user_id = None
        self.club_id = None
        self.session_data = None
        self.data_output = {}
        self.members = {}
        self.club = {}
        self.logger = logging.getLogger(__name__)

    async def authenticate(self, force_auth=False):
        """
        Authenticate the user with the Toastmasters API.

        Args:
            force_auth (bool): If True, forces re-authentication even if session data exists

        Returns:
            None: If authentication is successful, sets user_id, club_id, and session_data attributes
        """
        # Check for existing session
        existing_session = self.session_manager.load_session_data()

        # Handle setting session details
        if existing_session and not force_auth:
            self.logger.info("Found existing session object")
            self.user_id = existing_session.get('user_id')
            self.club_id = existing_session.get('club_id')
            self.session_data = existing_session
        
        # Force re-authentication if missing any details
        if not any(val is None for val in [self.user_id, self.club_id, self.session_data]):
            return
        
        # Authenticate if applicable
        email = self.env_manager.email
        password = self.env_manager.password
        club_name = self.env_manager.club_name
        auth_result = await self.authenticator.authenticate(email, password, club_name)

        if auth_result:
            self.user_id, self.club_id, self.session_data = auth_result
        else:
            self.logger.error("Authentication failed")
            raise ValueError("Authentication failed: auth_result returned empty")
        
    async def fetch_data_from_endpoints(self) -> bool:
        """
        Fetch data from the Toastmasters API endpoints.

        Returns:
            bool: True if data fetching is successful, False otherwise
        """
        try:
            # Create API client
            cookies = {cookie['name']: cookie['value'] for cookie in self.session_data.get('cookies', [])}
            client = ToastmastersAPIClient(cookies, self.session_data.get('user_agent', ''))
            api_service = ToastmastersAPIService(client, self.app_settings)

            # Primary endpoints
            primary_data = await api_service.get_primary_endpoints(
                self.club_id,
                ["overview", "progress"]
            )
            self.data_output.update(primary_data)

            # Collect detailed progress data on each user
            user_course_combinations = self.data_service.get_user_course_combinations(self.data_output)
            detailed_user_progress = await api_service.get_detailed_progress(user_course_combinations)
            self.data_output['progress_detail'] = detailed_user_progress

            return True

        except Exception as e:
            self.logger.error(f"Direct API calls failed: {e}")
            return False
        
    def build_indexes(self):
        """
        Build indexes for members and clubs from the fetched data.

        Returns:
            None
        """
        self.logger.info("Building out indexes for members and clubs")
        # Build the member index
        self.members = self.data_service.build_member_index(self.data_output)

        # Build the club index
        self.club = self.data_service.build_club_index(self.club_id, self.env_manager.club_name, self.members)

    def generate_reports(self):
        """
        Generate reports based on the fetched data.
        """
        try:
            if not self.members or not self.club:
                self.logger.warning("No members or club data available for report generation")
                return
            
            self.report_service.generate_reports(self.club)
            self.logger.info("Reports generated successfully")

        except Exception as e:
            self.logger.error(f"Failed to generate reports: {e}")
            raise

    def save_data(self):
        """
        Save the fetched and processed data to JSON files.

        Returns:
            None
        """
        self.logger.info("Starting save data operations")

        try:
            # Save raw endpoint data if configured
            if self.app_settings.SAVE_ENDPOINT_DATA:
                for endpoint_name, endpoint_data in self.data_output.items():
                    endpoint_file = f"{endpoint_name}_data.json"
                    success = self.file_manager.save_json(
                        endpoint_data,
                        endpoint_file,
                        "endpoint_data_directory"
                    )

                    # Optional warning for failed writes
                    if not success:
                        self.logger.warning(f"Failed to write {endpoint_name} data")

            else:
                self.logger.info("Skipping saving raw endpoint data")

            # Save member summary data
            self.logger.info("Saving member summary data")
            member_object = {k: v.to_dict() for k, v in self.members.items()}
            success = self.file_manager.save_json(
                member_object,
                "member_summary_data.json",
                "summary_directory"
                )
            
            if not success:
                self.logger.error("Failed to write member summary data")
                raise RuntimeError("Failed to write member summary data")
            
            # Save club summary data
            self.logger.info("Saving club summary data")
            club_object = {k: v.to_dict() for k, v in self.club.items()}
            success = self.file_manager.save_json(
                club_object,
                "club_summary_data.json",
                "summary_directory"
            )

            if not success:
                self.logger.error("Failed to write club summary data")
                raise RuntimeError("Failed to write club summary data")            

        except Exception as e:
            self.logger.error(f"Failed to write data: {e}")
            raise