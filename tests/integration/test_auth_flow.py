import pytest
from src.client.auth import AuthClient
from src.models.response.auth import AuthResponse, ErrorResponse


@pytest.mark.integration
class TestAuthFlow:
    def test_register_new_user_success(self, auth_client, new_user_payload):
        response = auth_client.register(new_user_payload)
        assert response.status_code in [200, 201]
        AuthResponse(**response.json())
        
    def test_register_duplicate_email(self, auth_client, new_user_payload):
        auth_client.register(new_user_payload)
        response = auth_client.register(new_user_payload)
        assert response.status_code == 409
        ErrorResponse(**response.json())

    def test_login_success(self, auth_client, new_user_payload):
        auth_client.register(new_user_payload)
        
        login_payload = {
            "email": new_user_payload["email"],
            "password": new_user_payload["password"]
        }
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
        login_payload = {
            "email": faker.email(),
            "password": "wrongpassword"
        }
        response = auth_client.login(login_payload)
        
        assert response.status_code == 401
        
