import os
import pytest
from dotenv import load_dotenv
from src.client.base import BaseClient
from src.client.auth import AuthClient
from faker import Faker


load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8080")

@pytest.fixture(scope="session")
def auth_client():
    return AuthClient(base_url=API_BASE_URL)

@pytest.fixture(scope="session")
def ai_client():
    from src.client.ai import AIClient
    return AIClient(base_url=API_BASE_URL)

@pytest.fixture(scope="session")
def transaction_client():
    from src.client.transaction import TransactionClient
    return TransactionClient(base_url=API_BASE_URL)

@pytest.fixture(scope="session")
def faker():
    return Faker()

@pytest.fixture(scope="function")
def new_user_payload(faker):
    password = faker.password(length=12)
    return {
        "email": faker.unique.email(),
        "password": password,
        "username": faker.user_name()
    }
@pytest.fixture(scope="function")
def auth_session(auth_client, new_user_payload):
    auth_client.register(new_user_payload)
    login_response = auth_client.login(new_user_payload)
    cookies = login_response.cookies.get_dict()
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"} if token else None
    return {"cookies": cookies, "headers": headers}
