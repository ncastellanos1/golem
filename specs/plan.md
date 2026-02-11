# Implementation Plan: API Testing Framework

**Date**: 2026-02-09
**Spec**: [spec.md](./spec.md)
**Focus**: Automated Testing Framework (Python/Pytest)

## 1. Strategy

We will build a robust automation framework that verifies the Authentication System against the requirements defined in `spec.md`. The framework will focus on:
1.  **Contract Testing**: Ensuring API inputs/outputs match the expected Pydantic schemas.
2.  **Integration Testing**: Verifying complete user flows (Register -> Login -> Business Action).
3.  **Negative Testing**: Validating error handling (400, 401, 409 responses).

---

## 2. Implementation Phases

### Phase 1: Framework Foundation

**Goal**: Setup the test harness and base HTTP client.

- [ ] **T001**: Initialize Python Project
    - Create `requirements.txt` (pytest, requests, pydantic, faker, python-dotenv).
    - Create `pytest.ini` with standard configurations.
- [ ] **T002**: Implement `BaseClient`
    - Wrapper around `requests.Session`.
    - Handle base URL from env vars.
    - Automatic timeout and error logging.
- [ ] **T003**: Create Pydantic Models (Schemas)
    - `UserRegisterRequest`, `LoginRequest`.
    - `TokenResponse`, `ErrorResponse` (RFC 7807).

### Phase 2: Auth Client & Core Tests

**Goal**: Test traditional Email/Password authentication.

- [ ] **T004**: Implement `AuthClient`
    - Methods: `register(payload)`, `login(payload)`, `verify_token()`.
- [ ] **T005**: Setup `conftest.py` Fixtures
    - `api_client`: Returns an instance of AuthClient.
    - `new_user`: Generates random user data (email/pass) using Faker.
    - `registered_user`: Fixture that actually registers a user and returns creds.
- [ ] **T006**: Test Suite: Registration (R1)
    - TC01: Successful registration (200 OK).
    - TC02: Duplicate email (409 Conflict).
    - TC03: Weak password (400 Bad Request).
- [ ] **T007**: Test Suite: Login (R2)
    - TC04: Successful login (200 OK + Token Body + Cookie).
    - TC05: Invalid credentials (401 Unauthorized).

### Phase 3: Token Management & Security

**Goal**: Verify token rotation and security headers.

- [ ] **T008**: Implement Cookie Verification
    - Helper method to inspect `response.cookies` for `HttpOnly` and `Secure` flags.
- [ ] **T009**: Test Suite: Token Refresh (R4, R5)
    - TC06: Refresh token rotation (exchange old cookie for new token).
    - TC07: Logout (cookie deletion).
    - TC08: Access protected resource with expired token (401).

### Phase 4: Google OAuth (Mocking/Stubbing)

**Goal**: Verify Google Auth flow handling.

*Note: Since we cannot easily automate real Google Login in a headless API test without a UI, we will focus on how the API handles the token exchange.*

- [ ] **T010**: Implement `login_with_google` method in Client.
- [ ] **T011**: Test Suite: Social Auth (R3)
    - TC09: Login with valid (mock) Google Token.
    - TC10: Login with invalid Google Token (401).

---

## 3. Execution & Reporting

- **Local Run**: `pytest tests/ -v`
- **Report Generation**: `pytest --html=report.html`
