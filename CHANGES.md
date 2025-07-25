This document outlines the refactoring of a legacy user management API, focusing on improving its quality, security, and maintainability while preserving all original functionality.

Major Issues Identified
1. SQL Injection Vulnerabilities: Direct string formatting in queries was a critical security flaw.
2. Plain Text Passwords: Passwords were stored and verified insecurely.
Poor Input Validation: Incoming data lacked robust validation.
3. Monolithic Code: All application logic was tightly coupled in a single file.
4. Inconsistent Error Handling: Error responses lacked standardization and proper HTTP status codes.
5. Hardcoded Configuration: Settings were inflexible and insecure.
6.   Absence of Logging: No structured logging for monitoring or debugging.

Solutions Implemented
1. Code Organization
Modular Design: Code is split into distinct files (app.py, init_db.py, app/__init__.py, app/db.py, app/errors.py, app/routes.py, app/schemas.py, app/utils.py, tests/).
Clear Responsibilities: Each file has a specific role
2. Security Improvements
Parameterized Queries: SQL injection is prevented by using parameterized queries in all database operations.
Secure Password Hashing: Passwords are securely hashed and salted using werkzeug.security.
Robust Input Validation: Marshmallow schemas validate all incoming data, providing detailed error messages for invalid input.
Externalized Configuration: Sensitive settings are loaded from a .env file for better security.
3. Best Practices
Consistent Error Handling: Custom APIError and a centralized handler provide standardized JSON responses with correct HTTP status codes.
Comprehensive Logging: Basic logging is configured to provide insights into application behavior.
Automated Testing: Integration tests using pytest (tests/test_app.py) verify critical API functionality, demonstrating code quality.

Tradoff:
1. No Full ORM: Direct sqlite3 parameterized queries were chosen to maintain simplicity for this challenge, while still ensuring security.
2. The login endpoint provides basic authentication, but a full token-based authentication system (e.g., JWT) for securing all API endpoints was considered outside the scope of refactoring existing features.
3. Kept the project structure simple inorder to fit in with the given time

If given more time I would:
1. Implement Token-Based Authentication (e.g., JWT): To secure all API endpoints beyond just the login, ensuring only authenticated and authorized users can access resources.
2. Expand Automated Tests: Develop more exhaustive unit tests for individual functions and more integration tests covering all API endpoints and complex scenarios.
3. Structure it better by adding config file and util files to imporve reusability.
4. Rate Limiting: Add rate limiting to sensitive endpoints (e.g., login, user creation) to prevent abuse and brute-force attacks.



AI Usage:
 Used co-pilot to generate test cases and configure them.
 Some of the boiler plate code such as schemas was coded using copilot as well


Documentation utilised :
  marshmallow docs https://marshmallow.readthedocs.io/en/latest/
  logging docs https://docs.python.org/3/howto/logging.html#
  sql injection prevention https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
 