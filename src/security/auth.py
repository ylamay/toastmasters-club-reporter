"""
Handling of authentication (playwright) and session handling/persistence
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from playwright.async_api import async_playwright # type: ignore
from api.client_api import ToastmastersAPIClient
from manager.file_manager import FileManager
import logging

class SessionManager:
    """
    Manages user sessions for the Toastmasters application

    Attributes:
        file_manager (FileManager): File manager instance for handling file operations
        session_file (str): Session file name
        logger (logging.Logger): Logger instance for logging messages
    """
    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager
        self.session_file = "toastmasters_session.json"
        self.logger = logging.getLogger(__name__)

    def save_session_data(
        self, cookies: List[Dict], user_agent: str,
        user_id: Optional[str] = None, club_id: Optional[str] = None
    ) -> bool:
        """
        Save session data for reuse

        Args:
            cookies (List[Dict]): Array of cookie objects found
            user_agent (str): The browser agent used
            user_id (Optional[str]): Toastmasters unique username
            club_id (Optional[str]): Toastmasters unique club id

        Returns:
            bool: True if save was successful, False otherwise
        """
        session_data = {
            'cookies': cookies,
            'user_agent': user_agent,
            'user_id': user_id,
            'club_id': club_id,
            'timestamp': datetime.now().isoformat(),
            'expires': (datetime.now() + timedelta(hours=8)).isoformat()
        }
        
        success = self.file_manager.save_json(
            session_data,
            self.session_file,
            "auth_directory"
        )

        if success:
            self.logger.info("Session data saved")
            if user_id:
                self.logger.info(f"- User ID: {user_id}")
            if club_id:
                self.logger.info(f"- Club ID: {club_id}")
        else:
            self.logger.error("Failed to save session data")
        
        return success

    def load_session_data(self) -> Optional[Dict]:
        """
        Load existing session data if applicable

        Returns:
            Optional[Dict]: Session data if available and valid, otherwise None
        """
        session_data = self.file_manager.load_json(
            self.session_file,
            "auth_directory"
        )

        if not session_data:
            self.logger.info("No existing session found")
            return None
        
        try:            
            # Check if session has expired
            expires = datetime.fromisoformat(session_data['expires'])
            if datetime.now() > expires:
                self.logger.info("Session expired, will re-authenticate")
                return None
            
            self.logger.info("Found valid session data")
            return session_data
            
        except Exception as e:
            self.logger.error(f"Error loading session: {e}")
            return None
        
class ToastmastersAuthenticator:
    """
    Handles authentication for the Toastmasters application

    Attributes:
        session_manager (SessionManager): Manages user sessions
        app_settings: Application settings containing app configurations
        logger (logging.Logger): Logger instance for logging messages
    """
    def __init__(self, session_manager: SessionManager, app_settings):
        self.session_manager = session_manager
        self.app_settings = app_settings
        self.logger = logging.getLogger(__name__)

    async def authenticate(self, email: str, password: str, club_name: str) -> Optional[Tuple[str, str, Dict]]:
        """
        Authenticate and retrieve session data

        Args:
            email (str): Email to login with
            password (str): Password to login with
            club_name (str): Name of the club to fetch data for

        Returns:
            Optional[Tuple[str, str, Dict]]: Tuple containing user_id, club_id, and session data if successful,
                                             otherwise None
        """
        try:
            async with async_playwright() as p:
                browser = await p.firefox.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                # Login
                self.logger.info("Navigating to login page...")
                await page.goto(self.app_settings.LOGIN_URL)
                
                try:
                    self.logger.info("Checking if login is required...")
                    await page.wait_for_selector('button:has-text("Log in")', timeout=5000)
                    self.logger.info("Login required. Proceeding to log in...")

                    await page.fill('input[id="signInName"]', email)
                    await page.fill('input[id="password"]', password)
                    await page.click('button:has-text("Log in")')
                    await page.wait_for_load_state("networkidle")
                    self.logger.info("Login successful")

                except Exception:
                    self.logger.info("Already logged in or login not required")
                
                # Establish Base Camp session
                self.logger.info("Establishing Base Camp session...")
                await page.goto(self.app_settings.BASECAMP_URL)
                await page.wait_for_load_state("networkidle", timeout=15000)
                
                # Capture session data
                cookies = await context.cookies()
                user_agent = await page.evaluate('navigator.userAgent')
                
                # Extract user ID
                user_id = self._extract_user_id(cookies)
                if not user_id:
                    self.logger.info("Could not find user ID")
                    await browser.close()
                    return None
                
                # Get club ID
                club_id = self._get_club_id(cookies, user_agent, user_id, club_name)
                if not club_id:
                    self.logger.info("Could not retrieve club ID")
                    await browser.close()
                    return None
                
                await browser.close()
                
                # Save session
                session_data = {
                    'cookies': cookies,
                    'user_agent': user_agent,
                    'user_id': user_id,
                    'club_id': club_id,
                    'timestamp': datetime.now().isoformat(),
                    'expires': (datetime.now() + timedelta(hours=24)).isoformat()
                }
                
                self.session_manager.save_session_data(cookies, user_agent, user_id, club_id)
                self.logger.info("Session captured successfully")
                return user_id, club_id, session_data
                
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return None
        
    def _extract_user_id(self, cookies: List[Dict]) -> Optional[str]:
        """
        Extract user_id from CEContactId cookie
        
        Args:
            cookies (List[Dict]): List of cookie dictionaries
        
        Returns:
            Optional[str]: User ID if found, otherwise None
        """
        for cookie in cookies:
            if cookie['name'] == 'CEContactId' and 'toastmasters.org' in cookie['domain']:
                self.logger.info(f"Found user ID: {cookie['value']}")
                return cookie['value']
        return None
    
    def _get_club_id(self, cookies: List[Dict], user_agent: str, user_id: str, club_name: str) -> Optional[str]:
        """
        Get club_id by calling the user profile API
        
        Args:
            cookies (List[Dict]): List of cookie dictionaries
            user_agent (str): User agent string
            user_id (str): User ID to fetch profile for

        Returns:
            Optional[str]: Club ID if found, otherwise None
        """
        try:
            # Convert cookies
            cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
            
            # Create client and make request
            client = ToastmastersAPIClient(cookie_dict, user_agent)
            profile_url = self.app_settings.API_ENDPOINTS['profile'].format(user_id=user_id)
            
            self.logger.info("Fetching profile data...")
            success, profile_data, status_code = client.make_request(profile_url)
            
            if success and profile_data:
                clubs = profile_data.get('clubs', [])
                self.logger.info(f"Found {len(clubs)} club(s) in profile")
                
                for club in clubs:
                    club_name = club.get('name', '')
                    if club_name == 'Shaw Floor Speakers':
                        club_uuid = club.get('uuid')
                        if club_uuid:
                            print(f"Found {club_name} club: {club_uuid}")
                            return club_uuid

                self.logger.info(f"{club_name} club not found in profile")
                return None
            else:
                self.logger.warning(f"Profile API failed: {status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting club ID: {e}")
            return None