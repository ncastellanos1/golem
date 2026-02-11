# Golem — API Test Automation Framework

Automated testing suite for the Authentication API built with **Python**, **Pytest**, and **Pydantic**.

## What does it test?

| Flow | Endpoint | Scenarios |
|---|---|---|
| Register | `POST /auth/register` | Success, Duplicate email (409) |
| Login | `POST /auth/login` | Success + cookie, Invalid credentials (401) |
| Refresh Token | `POST /auth/refresh` | Success with cookie, Missing cookie (401) |
| Logout | `POST /auth/logout` | Cookie clearing verification |

Additionally includes **contract tests** that validate request/response schemas with Pydantic models.

## Tech Stack

- Python 3.9+
- Pytest
- Requests (HTTP client with session/cookie support)
- Pydantic (schema validation)
- Faker (test data generation)

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/ncastellanos1/golem.git
cd golem

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API base URL
```

## Running Tests

```bash
# Make sure your API is running (default: http://127.0.0.1:8080)
export API_BASE_URL=http://127.0.0.1:8080

# Run all tests
pytest tests/

# Run only contract tests
pytest tests/contract/

# Run only integration tests
pytest tests/integration/

# Generate HTML report
pytest tests/ --html=report.html
```

## Project Structure

```
golem/
├── src/
│   ├── client/          # HTTP clients (BaseClient, AuthClient)
│   ├── models/
│   │   ├── request/     # Pydantic request models
│   │   └── response/    # Pydantic response models
│   └── utils/
├── tests/
│   ├── contract/        # Schema validation tests
│   ├── integration/     # API integration tests
│   └── conftest.py      # Shared fixtures
├── specs/               # Project specifications
├── .env.example
├── pytest.ini
└── requirements.txt
```
