import pytest
import re
from http import HTTPStatus
from src.client.auth import AuthClient
from src.models.response.auth import AuthResponse
from src.models.response.refresh import RefreshResponse
from tests.integration.schemas import RegisterUserRequest, LoginUserRequest

COOKIE_REFRESH_TOKEN = "refresh_token"
HEADER_SET_COOKIE = "Set-Cookie"

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
        assert login_response.status_code == HTTPStatus.OK
        
        cookies = {}
        cookie_header = login_response.headers[HEADER_SET_COOKIE] if HEADER_SET_COOKIE in login_response.headers else ""
        if COOKIE_REFRESH_TOKEN in cookie_header:
             match = re.search(rf'{COOKIE_REFRESH_TOKEN}=([^;]+)', cookie_header)
             if match:
                 cookies[COOKIE_REFRESH_TOKEN] = match.group(1)
        
        refresh_response = auth_client.refresh_token(cookies=cookies)
        
        assert refresh_response.status_code == HTTPStatus.OK, f"Refresh failed: {refresh_response.text}"
        
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
        cookie_header = login_response.headers[HEADER_SET_COOKIE] if HEADER_SET_COOKIE in login_response.headers else ""
        if COOKIE_REFRESH_TOKEN in cookie_header:
             match = re.search(rf'{COOKIE_REFRESH_TOKEN}=([^;]+)', cookie_header)
             if match:
                 cookies[COOKIE_REFRESH_TOKEN] = match.group(1)

        logout_response = auth_client.logout(cookies=cookies) 
        
        assert logout_response.status_code == HTTPStatus.OK
        
        cookie_header = logout_response.headers[HEADER_SET_COOKIE] if HEADER_SET_COOKIE in logout_response.headers else ""
        assert f"{COOKIE_REFRESH_TOKEN}=;" in cookie_header or "Max-Age=0" in cookie_header
        
    def test_refresh_without_cookie(self, auth_client: AuthClient):
        """
        Scenario: Refresh without a cookie returns 401 Unauthorized.
        """
        auth_client.session.cookies.clear()
        
        response = auth_client.refresh_token()
        assert response.status_code == HTTPStatus.UNAUTHORIZED
