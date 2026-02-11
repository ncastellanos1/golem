import os
import pytest
from dotenv import load_dotenv
from src.client.base import BaseClient
from src.client.auth import AuthClient
from faker import Faker

# Load env vars
load_dotenv()

@pytest.fixture(scope="session")
def api_client():
    base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8080")
    return AuthClient(base_url=base_url)

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


