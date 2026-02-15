import pytest
from src.models.response.auth import AuthResponse, ErrorResponse
from src.models.request.auth import RegisterRequest

@pytest.mark.contract
class TestAuthContract:
    def test_register_request_schema(self, new_user_payload):
        """
        Verify that the RegisterRequest model correctly validates input.
        """
        # Valid payload
        model = RegisterRequest(**new_user_payload)
        assert model.email == new_user_payload["email"]
        
        # Invalid email
        with pytest.raises(ValueError):
            invalid_payload = new_user_payload.copy()
            invalid_payload["email"] = "not-an-email"
            RegisterRequest(**invalid_payload)

    def test_auth_response_schema(self):
        """
        Verify that AuthResponse model matches expected structure.
        """
        data = {
            "access_token": "paseto.v4.local.token...",
            "expires_in": 900,
            "user": {
                "id": "uuid-1234",
                "username": "testuser",
                "email": "test@example.com",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
        model = AuthResponse(**data)
        assert model.access_token == data["access_token"]
        assert model.user.email == "test@example.com"

    def test_error_response_schema(self):
        """
        Verify RFC 7807 Error Response schema.
        """
        data = {
            "type": "about:blank",
            "title": "Bad Request",
            "status": 400,
            "detail": "Invalid input",
        }
        model = ErrorResponse(**data)
        assert model.status == 400
