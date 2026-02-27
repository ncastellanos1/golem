import logging
import os
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class BaseClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://127.0.0.1:8080")
        self.session = requests.Session()
        
        # Configure Retries
        retries = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE", "PATCH"],
            raise_on_status=False
        )
        # Enable retries for all requests by mounting the adapter
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.logger = logging.getLogger(__name__)

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        
        # Log Request
        self.logger.info(f"Request: {method} {url}")
        if "json" in kwargs:
            self.logger.debug(f"Payload: {kwargs['json']}")
            
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Log Response
            self.logger.info(f"Response: {response.status_code} {response.reason}")
            try:
                self.logger.debug(f"Body: {response.json()}")
            except ValueError:
                self.logger.debug(f"Body: {response.text}")
                
            return response
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("DELETE", endpoint, **kwargs)
