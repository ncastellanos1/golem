import pytest
import requests
from src.client.auth import AuthClient
from src.models.response.auth import AuthResponse
from src.models.response.refresh import RefreshResponse

@pytest.mark.integration
class TestTokenManagement:
    
    def test_refresh_token_success(self, auth_client: AuthClient, new_user_payload):
        auth_client.register(new_user_payload)
        login_response = auth_client.login(new_user_payload)
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
        auth_client.register(new_user_payload)
        login_response = auth_client.login(new_user_payload)
        
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
        auth_client.session.cookies.clear()
        
        response = auth_client.refresh_token()
        assert response.status_code == 401
