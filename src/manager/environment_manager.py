from dotenv import load_dotenv # type: ignore
import os
import logging

class EnvironmentManager:
    """
    Manages environment variables for the application.
    """
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.env_path = os.path.join(project_root, ".env")
        self.logger = logging.getLogger(__name__)

        # Env variables
        self.email = None
        self.password = None
        self.club_name = None

        # Dirs
        self.session_directory = os.path.join(project_root, "session")
        self.pathways_directory = os.path.join(project_root, "pathways")

        # Sub-dirs
        self.auth_directory = os.path.join(self.session_directory, "auth")
        self.endpoint_data_directory = os.path.join(self.session_directory, "endpoint_data")
        self.summary_directory = os.path.join(self.session_directory, "summary")
        self.reports_directory = os.path.join(self.session_directory, "reports")

        # Initialize env variables and directories
        self._initialize_env_vars()
        self._create_directories()

    def _initialize_env_vars(self):
        """
        Initialize env variables

        Returns:
            None
        """
        self.logger.info("Initializing environment variables")

        if not os.path.exists(self.env_path):
            self._create_env_file()

        self._load_env_vars()

    def _create_directories(self):
        """
        Create necessary directories for the application
        """
        dirs = [
            self.session_directory,
            self.auth_directory,
            self.endpoint_data_directory,
            self.summary_directory,
            self.reports_directory
        ]

        for dir in dirs:
            os.makedirs(dir, exist_ok=True)
            self.logger.info(f"Created directory: {dir}")

        # Check for optional pathways dir
        if not os.path.exists(self.pathways_directory):
            self.logger.warning(f"Pathways directory does not exist: {self.pathways_directory}. Pathway enrichment may be unavailable.")

    def _load_env_vars(self):
        """
        Load and validate environment variables
        
        Returns:
            None
        """
        # Load existing env variables
        load_dotenv(self.env_path)
        self.email = os.getenv("EMAIL")
        self.password = os.getenv("PASSWORD")
        self.club_name = os.getenv("CLUB_NAME")

        # Determine missing vars
        missing_vars = []
        if not self.email:
            missing_vars.append('email')
        if not self.password:
            missing_vars.append('password')
        if not self.club_name:
            missing_vars.append('club_name')

        # Get user input for missing variables
        if missing_vars:
            self._get_user_input_for_missing_vars()
            
            # Update env vars if applicable
            self._update_env_file()

        # Validate
        self._validate_credentials()

    def _create_env_file(self):
        """
        Create a .env file with user-provided credentials

        Returns:
            None
        """
        self.logger.info("Creating new .env file")
        
        # Get user input for all variables
        self._get_user_input_for_missing_vars(prompt_all=True)
        
        # Validate and write
        self._validate_credentials()
        self._write_env_file()

    def _get_user_input_for_missing_vars(self, prompt_all=False):
        """
        Get user input for missing environment variables
        
        Returns:
            None
        """
        if not self.email or prompt_all:
            self.email = input("Enter your email used for Toastmasters: ")
        if not self.password or prompt_all:
            self.password = input("Enter your password used for Toastmasters: ")
        if not self.club_name or prompt_all:
            self.club_name = input("Enter your club name: ")

    def _validate_credentials(self):
        """
        Validate that all required credentials are provided
        
        Returns:
            None
        """
        if not all([self.email, self.password, self.club_name]):
            raise ValueError("Email, password, and club name cannot be empty")

    def _write_env_file(self):
        """
        Write credentials to .env file

        Returns:
            None
        """
        with open(self.env_path, "w") as env_file:
            env_file.write(f"EMAIL={self.email}\n")
            env_file.write(f"PASSWORD={self.password}\n")
            env_file.write(f"CLUB_NAME={self.club_name}\n")
        
        self.logger.info(f".env file created at {self.env_path}")

    def _update_env_file(self):
        """
        Update the .env file with current values
        
        Returns:
            None
        """
        self._validate_credentials()
        self._write_env_file()
        self.logger.info("Environment file updated successfully")

    def update_credential(self, **kwargs):
        """
        Update specific credentials and save to file
        
        Args:
            **kwargs: email, password, or club_name values to update
        """
        if 'email' in kwargs:
            self.email = kwargs['email']
        if 'password' in kwargs:
            self.password = kwargs['password']
        if 'club_name' in kwargs:
            self.club_name = kwargs['club_name']
        
        self._update_env_file()