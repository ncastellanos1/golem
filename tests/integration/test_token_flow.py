import pytest
import requests
from src.client.auth import AuthClient
from src.models.response.auth import AuthResponse
from src.models.response.refresh import RefreshResponse
from tests.integration.schemas import RegisterUserRequest, LoginUserRequest

@pytest.mark.integration
class TestTokenFlow:
    
    def test_refresh_token_success(self, auth_client: AuthClient, new_user_payload):
        """
        Scenario: Refresh token should return a new access token when a valid cookie is present.
        """
        register_payload = RegisterUserRequest(**new_user_payload).model_dump()
        login_payload = LoginUserRequest(
            email=new_user_payload["email"],
            password=new_user_payload["password"]
        ).model_dump()
        
        auth_client.register(register_payload)
        login_response = auth_client.login(login_payload)
        assert login_response.status_code == 200
        
        cookies = {}
        cookie_header = login_response.headers.get("Set-Cookie", "")
        if "refresh_token" in cookie_header:
             import re
             match = re.search(r'refresh_token=([^;]+)', cookie_header)
             if match:
                 cookies["refresh_token"] = match.group(1)
        
        refresh_response = auth_client.refresh_token(cookies=cookies)
        
        assert refresh_response.status_code == 200, f"Refresh failed: {refresh_response.text}"
        
        data = refresh_response.json()
        assert "access_token" in data
        assert "expires_in" in data
        
        RefreshResponse(**data)
        
    def test_logout_success(self, auth_client: AuthClient, new_user_payload):
        """
        Scenario: Logout should invalidate and clear the refresh cookie.
        """
        register_payload = RegisterUserRequest(**new_user_payload).model_dump()
        login_payload = LoginUserRequest(
            email=new_user_payload["email"],
            password=new_user_payload["password"]
        ).model_dump()

        auth_client.register(register_payload)
        login_response = auth_client.login(login_payload)
        
        cookies = {}
        cookie_header = login_response.headers.get("Set-Cookie", "")
        if "refresh_token" in cookie_header:
             import re
             match = re.search(r'refresh_token=([^;]+)', cookie_header)
             if match:
                 cookies["refresh_token"] = match.group(1)

        logout_response = auth_client.logout(cookies=cookies) 
        
        assert logout_response.status_code == 200
        
        cookie_header = logout_response.headers.get("Set-Cookie", "")
        assert "refresh_token=;" in cookie_header or "Max-Age=0" in cookie_header
        
    def test_refresh_without_cookie(self, auth_client: AuthClient):
        """
        Scenario: Refresh without a cookie returns 401 Unauthorized.
        """
        auth_client.session.cookies.clear()
        
        response = auth_client.refresh_token()
        assert response.status_code == 401
