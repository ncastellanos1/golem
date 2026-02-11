from src.client.base import BaseClient
from src.models.request.auth import RegisterRequest, LoginRequest
import requests

class AuthClient(BaseClient):
    def register(self, payload: dict) -> requests.Response:
        """
        Register a new user.
        Payload can be a dict or RegisterRequest model (dumped).
        """
        return self.post("/auth/register", json=payload)

    def login(self, payload: dict) -> requests.Response:
        """
        Login an existing user.
        Payload can be a dict or LoginRequest model (dumped).
        """
        return self.post("/auth/login", json=payload)

    def verify_token(self, token: str) -> requests.Response:
        """
        Verify if a token is valid by calling a protected endpoint.
        """
        headers = {"Authorization": f"Bearer {token}"}
        # Assuming /auth/me or similar endpoint exists to verify token
        return self.get("/auth/me", headers=headers)

    def refresh_token(self, cookies: dict = None) -> requests.Response:
        """
        Refresh access token using the HttpOnly cookie.
        """
        # The session automatically includes cookies from previous requests
        return self.post("/auth/refresh", json={}, cookies=cookies) # Empty JSON might be required by some strict parsers

    def logout(self, cookies: dict = None) -> requests.Response:
        """
        Logout the user and invalidate cookies.
        """
        return self.post("/auth/logout", cookies=cookies)
