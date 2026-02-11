import pytest
from src.client.auth import AuthClient
from src.models.response.auth import AuthResponse, ErrorResponse

@pytest.fixture(scope="module")
def auth_client():
    from src.client.base import BaseClient
    base_url = BaseClient().base_url
    return AuthClient(base_url=base_url)

@pytest.mark.integration
class TestAuthFlow:
    def test_register_new_user_success(self, auth_client, new_user_payload):
        """
        R1: Successful registration with valid data.
        """
        response = auth_client.register(new_user_payload)
        
        # Assert Status Code
        assert response.status_code == 200 or response.status_code == 201, \
            f"Expected 200/201, got {response.status_code}: {response.text}"
        
        # Verify Response Structure (should return Token + User)
        # Note: Spec says it logs in immediately
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        
        # Schema Validation
        AuthResponse(**data)
        
    def test_register_duplicate_email(self, auth_client, new_user_payload):
        """
        R1: Duplicate email should return 409 Conflict.
        """
        # 1. Register first time
        auth_client.register(new_user_payload)
        
        # 2. Register again with same email
        response = auth_client.register(new_user_payload)
        
        assert response.status_code == 409
        error = response.json()
        assert error["status"] == 409
        # RFC 7807 Validation
        ErrorResponse(**error)

    def test_login_success(self, auth_client, new_user_payload):
        """
        R2: Login with valid credentials returns Token + Cookie.
        """
        # Uses the global mock defined in conftest.py which returns 200 OK
        # 1. Ensure user exists (Mocked)
        auth_client.register(new_user_payload)
        
        # 2. Login
        login_payload = {
            "email": new_user_payload["email"],
            "password": new_user_payload["password"]
        }
        response = auth_client.login(login_payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify Body
        assert "access_token" in data or "token" in data
        
        # Verify Cookie
        # Note: requests-mock might not populate response.cookies from 'Set-Cookie' header automatically 
        # in the same way a real generic adapter does, ensuring we check headers if cookies empty.
        val = response.cookies.get("refresh_token")
        if val:
             assert len(val) > 0 # Just check it exists and is not empty
        else:
             header = response.headers.get("Set-Cookie")
             assert header and "refresh_token" in header
        
    def test_login_invalid_credentials(self, auth_client, faker):
        """
        R2: Login with invalid credentials returns 401.
        """
        login_payload = {
            "email": faker.email(),
            "password": "wrongpassword"
        }
        response = auth_client.login(login_payload)
        
        assert response.status_code == 401
        
