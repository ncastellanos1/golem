import pytest
from src.client.auth import AuthClient
from src.models.response.auth import AuthResponse, ErrorResponse
from tests.integration.schemas import RegisterUserRequest, LoginUserRequest


@pytest.mark.integration
class TestAuthFlow:
    def test_register_new_user_success(self, auth_client, new_user_payload):
        """
        R1: Successful registration with valid data.
        """
        payload = RegisterUserRequest(**new_user_payload).model_dump()
        response = auth_client.register(payload)
        assert response.status_code in [200, 201]
        AuthResponse(**response.json())
        
    def test_register_duplicate_email(self, auth_client, new_user_payload):
        """
        R1: Duplicate email should return 409 Conflict.
        """
        payload = RegisterUserRequest(**new_user_payload).model_dump()
        auth_client.register(payload)
        response = auth_client.register(payload)
        assert response.status_code == 409
        ErrorResponse(**response.json())

    def test_login_success(self, auth_client, new_user_payload):
        """
        R2: Login with valid credentials returns Token + Cookie.
        """
        register_payload = RegisterUserRequest(**new_user_payload).model_dump()
        auth_client.register(register_payload)
        
        login_payload = LoginUserRequest(
            email=new_user_payload["email"],
            password=new_user_payload["password"]
        ).model_dump()
        response = auth_client.login(login_payload)
        
        assert response.status_code == 200
        AuthResponse(**response.json())
        
        val = response.cookies.get("refresh_token")
        if val:
             assert len(val) > 0
        else:
             header = response.headers.get("Set-Cookie")
             assert header and "refresh_token" in header
        
    def test_login_invalid_credentials(self, auth_client, faker):
        """
        R2: Login with invalid credentials returns 401.
        """
        login_payload = LoginUserRequest(
            email=faker.email(),
            password="wrongpassword"
        ).model_dump()
        response = auth_client.login(login_payload)
        
        assert response.status_code == 401
        
