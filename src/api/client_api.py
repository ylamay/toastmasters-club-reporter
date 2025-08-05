import asyncio
import requests # type: ignore
from typing import Dict, Optional, Tuple
import urllib3 # type: ignore
import logging

# Disable request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ToastmastersAPIClient:
    """
    Client for interacting with the Toastmasters API.

    Attributes:
        cookies (Dict[str, str]): Cookies for authentication.
        headers (Dict[str, str]): Headers for the requests.
        logger (logging.Logger): Logger for logging API interactions.
    """ 
    def __init__(self, cookies: Dict[str, str], user_agent: str):
        self.cookies = cookies
        self.headers = {
            'User-Agent': user_agent,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://basecamp.toastmasters.org/dashboard/'
        }
        self.logger = logging.getLogger(__name__)
    
    def make_request(self, url: str, timeout: int = 60) -> Tuple[bool, Optional[Dict], int]:
        """
        Make a GET request and return (success, data, status_code)

        Args:
            url (str): The URL to make the request to.
            timeout (int): Timeout for the request in seconds.

        Returns:
            Tuple[bool, Optional[Dict], int]: A tuple containing success status, response data, and HTTP status code.
        """
        try:
            response = requests.get(
                url,
                cookies=self.cookies,
                headers=self.headers,
                timeout=timeout,
                verify=False
            )
            
            if response.status_code == 200:
                return True, response.json(), response.status_code
            else:
                return False, None, response.status_code
                
        except Exception as e:
            self.logger.error(f"Request error for {url}: {e}")
            return False, None, 0
    
    async def make_async_request(self, url: str, timeout: int = 60) -> Tuple[bool, Optional[Dict], int]:
        """
        Make an async GET request using thread pool

        Args:
            url (str): The URL to make the request to.
            timeout (int): Timeout for the request in seconds.

        Returns:
            Tuple[bool, Optional[Dict], int]: A tuple containing success status, response data, and HTTP status code.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.make_request(url, timeout))
    
    def handle_pagination(self, initial_data: Dict, base_url: str, data_callback) -> int:
        """
        Handle pagination for API calls
        Returns number of pages processed

        Args:
            initial_data (Dict): Initial data containing 'next' URL.
            base_url (str): Base URL for the API.
            data_callback (callable): Callback function to process each page of data.

        Returns:
            int: Number of pages processed.
        """
        next_url = initial_data.get('next')
        page_count = 1
        
        while next_url and page_count < 20:  # Safety limit
            page_count += 1
            self.logger.info(f"Fetching page {page_count}...")
            
            success, data, status_code = self.make_request(next_url)
            
            if success and data:
                results = data.get('results', [])
                if not results:
                    self.logger.info(f"No more data on page {page_count}, pagination complete")
                    break
                    
                data_callback(data)
                next_url = data.get('next')
                self.logger.info(f"Page {page_count} collected: {len(results)} records")
            else:
                self.logger.warning(f"Page {page_count} failed: {status_code}")
                break
        
        return page_count
