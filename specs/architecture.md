# Architecture: API Testing Framework

**Date**: 2026-02-09
**Status**: APPROVED
**Scope**: Test Automation Only (No API Implementation)

## 1. Directory Structure

We will use a standard **Pytest** structure with a simplified Page Object Model (POM) adaptation for APIs, separating the *API Client* (how we talk to the API) from the *Test Logic* (what we assert).

```text
.
├── specs/                  # Requirements & Plans
├── src/
│   ├── client/             # API Interaction Layer
│   │   ├── base.py         # BaseClient (Session, Retries, Logging)
│   │   └── auth.py         # AuthClient (Specific endpoints: /login, /register)
│   ├── models/             # Data Validation Layer (Pydantic)
│   │   ├── request/        # Request Bodies (RegisterUser, LoginCredentials)
│      └── response/       # Response Schemas (AuthResponse, ErrorResponse)
│   └── utils/              # Helpers
│       ├── tokens.py       # PASETO/JWT decoding & validation
│       └── data_gen.py     # Random data generation (Faker)
├── tests/
│   ├── conftest.py         # Global Fixtures (env setup, client instantiation)
│   ├── integration/        # End-to-End User Flows
│   │   └── test_auth_flow.py
│   └── contract/           # Schema/Field validation tests
│       └── test_auth_contract.py
├── .env.example            # Environment Config (Base URL, Secrets)
├── pytest.ini              # Pytest configuration
└── requirements.txt        # Dependencies
```

## 2. Test Framework Design (Mermaid)

```mermaid
graph TD
    subgraph "Test Execution (Pytest)"
        TestRunner[Pytest Runner]
        Fixtures[conftest.py\n(Client, Env, Data)]
        Tests[Test Cases\n(Integration/Contract)]
    end

    subgraph "Abstraction Layer (src)"
        AuthClient[AuthClient\n(Methods: register, login)]
        Models[Pydantic Models\n(Validation & Type Safety)]
        Utils[Utils\n(Token Parser, Data Gen)]
    end

    subgraph "System Under Test (SUT)"
        API[Target API\n(Localhost / Staging)]
        DB[(Target DB)\n(Optional: For teardown)]
    end

    TestRunner --> Tests
    Tests --> Fixtures
    Fixtures --> AuthClient
    Tests --> Models
    
    AuthClient -->|HTTP Requests| API
    AuthClient --> Models
    
    %% Flow
    Tests -->|1. Call API| AuthClient
    API -->|2. JSON Response| AuthClient
    AuthClient -->|3. Validate Schema| Models
    Models -->|4. Return Object| Tests
    Tests -->|5. Assert Logic| Utils
```

## 3. Key Architectural Decisions

1.  **Pydantic for Validation**: We will use Pydantic models not just for sending data, but for *validating* responses. If the API changes a field type, the test should fail immediately at the schema validation layer.
2.  **Requests Session**: `BaseClient` will maintain a `requests.Session` to handle cookies (necessary for the Refresh Token flow) automatically.
3.  **Data Generation**: Use `Faker` to generate unique emails/users for every test run to ensure idempotency and avoid "User already exists" errors.
4.  **Environments**: Configuration via `.env` to easily switch between Local, Staging, and Production targets.
5.  **Strict Separation**: Tests should not contain raw HTTP calls (`requests.post`). All interaction must go through `AuthClient` methods (`client.register()`).

## 4. Dependencies

- **pytest**: Test runner.
- **requests**: HTTP client.
- **pydantic**: Data validation.
- **faker**: Data generation.
- **pyjwt**: Token decoding (for verification).
- **pytest-html** (optional): Reporting.
