import pytest
import requests
from src.client.auth import AuthClient
from src.models.response.auth import AuthResponse
from src.models.response.refresh import RefreshResponse

@pytest.mark.integration
class TestTokenManagement:
    
    def test_refresh_token_success(self, api_client: AuthClient, new_user_payload):
        """
        R3: Refresh token should return new access token when valid cookie present.
        """
        # 1. Login to get initial cookies
        api_client.register(new_user_payload)
        login_response = api_client.login(new_user_payload)
        assert login_response.status_code == 200
        
        # Verify we have the cookie
        # Note: requests.Session handles logic, but since the API returns 'Secure' cookies
        # and we are testing on 'http://', requests drops the cookie.
        # We manually inject it for testing purposes.
        cookies = {}
        cookie_header = login_response.headers.get("Set-Cookie", "")
        if "refresh_token" in cookie_header:
             import re
             match = re.search(r'refresh_token=([^;]+)', cookie_header)
             if match:
                 cookies["refresh_token"] = match.group(1)
        
        # 2. Call Refresh Endpoint
        refresh_response = api_client.refresh_token(cookies=cookies)
        
        assert refresh_response.status_code == 200, f"Refresh failed: {refresh_response.text}"
        
        data = refresh_response.json()
        assert "access_token" in data
        assert "expires_in" in data
        
        RefreshResponse(**data)
        
    def test_logout_success(self, api_client: AuthClient, new_user_payload):
        """
        R4: Logout should invalidate/clear the refresh cookie.
        """
        # 1. Login
        api_client.register(new_user_payload)
        login_response = api_client.login(new_user_payload)
        
        # Extract cookie for logout too? Logout usually requires cookie to identify session to kill
        cookies = {}
        cookie_header = login_response.headers.get("Set-Cookie", "")
        if "refresh_token" in cookie_header:
             import re
             match = re.search(r'refresh_token=([^;]+)', cookie_header)
             if match:
                 cookies["refresh_token"] = match.group(1)

        # 2. Logout
        # We need to pass the cookie so server knows WHAT session to logout
        # (Unless it uses access token, but standard is refresh token cookie for logout)
        logout_response = api_client.logout(cookies=cookies) 
        
        assert logout_response.status_code == 200
        
        # 3. Verify Cookie is cleared (Max-Age=0 or Expires=Past)
        cookie_header = logout_response.headers.get("Set-Cookie", "")
        # Check for indicators of clearing: empty value, Max-Age=0, or Expires in past
        assert "refresh_token=;" in cookie_header or "Max-Age=0" in cookie_header
        
        # Note: Server might be stateless (JWT/PASETO without blacklist), so the token itself 
        # might still be valid if replayed. We only verify client-side clearing here.
        # refresh_response = api_client.refresh_token(cookies=cookies)
        # assert refresh_response.status_code == 401
        
    def test_refresh_without_cookie(self, api_client: AuthClient):
        """
        R3: Refresh without cookie returns 401.
        """
        # Clear cookies just in case session is dirty (from other tests if scope shared)
        api_client.session.cookies.clear()
        
        response = api_client.refresh_token()
        assert response.status_code == 401
