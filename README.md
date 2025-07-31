# FastAPI + PostgreSQL User Management

## Overview

This project is a FastAPI application with PostgreSQL for user management. It supports user CRUD operations (Create, Read, Update, Delete) with secure password hashing using bcrypt. The project is containerized with Docker and supports live reload for development.

---

## Project Structure

```
python-fastapi-postgres/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api_v1.py          # Main API router for v1
│   │       └── routers/
│   │           └── user_router.py # User CRUD endpoints, login with JWT
│   ├── core/
│   │   ├── config.py              # App settings (env vars)
│   │   ├── db.py                  # Database connection pool, db_query helper
│   │   ├── db_init.py             # (Optional) DB schema/migration logic
│   │   ├── security.py            # Password hashing/verification (bcrypt)
│   │   ├── jwt.py                 # JWT creation and verification utilities
│   │   ├── logger.py              # Centralized logger utility
│   │   └── checker.py             # Common checkers (e.g., user existence)
│   ├── domains/
│   │   └── user/
│   │       ├── models.py          # Pydantic models for user
│   │       ├── repository.py      # DB queries for user (uses db_query, logger)
│   │       └── service.py         # Business logic for user (uses logger, checker)
│   └── main.py                    # FastAPI app entrypoint
│
├── app/migrations/
│   ├── 001_create_user.sql        # SQL for user table
│   └── run.py                     # (Optional) Migration runner
│
├── docker-compose.yml             # Docker Compose config
├── Dockerfile                     # Docker build config
├── requirements.txt               # Python dependencies
├── wait-for-it.sh                 # Wait for DB before starting app
└── .env                           # Environment variables (not in repo)
```

---

## Environment Variables (`.env`)

```
DATABASE_URL=postgresql://postgres:password@db:5432/app_db
JWT_SECRET=your_super_secret_jwt_key
```

---

## DRY Utilities and Improvements

- **Logger Utility (`app/core/logger.py`)**: Use `get_logger("name")` for consistent, centralized logging across the app.
- **Database Query Helper (`app/core/db.py`)**: Use `db_query(query_func)` to avoid repeating connection acquisition and query execution in repository functions.
- **Checker Utility (`app/core/checker.py`)**: Use `user_exists_checker(user_id)` for user existence checks, reducing code duplication in services and routers.
- **Repository and Service Layers**: Now use these helpers/utilities, making the code DRY and easier to maintain.

---

## API Endpoints

All endpoints are under `/users` (e.g., `/users/`, `/users/{user_id}`).

### Create User

- **POST** `/users/`
- **Body:**
  ```json
  {
    "name": "John Doe",
    "email": "john@example.com",
    "password": "yourpassword"
  }
  ```
- **Response:**
  `201 Created`
  ```json
  {
    "user": {
      "id": "uuid",
      "name": "John Doe",
      "email": "john@example.com",
      "created_at": "timestamp"
    },
    "access_token": "<jwt>",
    "token_type": "bearer"
  }
  ```
  Returns the created user (without password) and a JWT token containing the user's ID.

### Get User by ID

- **GET** `/users/{user_id}`
- **Response:**
  `200 OK`
  Returns the user object.

### Update User

- **PATCH** `/users/{user_id}`
- **Body:**
  ```json
  {
    "name": "New Name", // optional
    "email": "new@email.com" // optional
  }
  ```
- **Response:**
  `200 OK`
  `{ "message": "User updated successfully" }`
  or `404` if not found.

### Delete User

- **DELETE** `/users/{user_id}`
- **Response:**
  `200 OK`
  `{ "message": "User deleted successfully" }`
  or `404` if not found.

### List All Users

- **GET** `/users/`
- **Response:**
  `200 OK`
  List of user objects.

### Login (JWT Auth)

- **POST** `/users/login`
- **Body:**
  ```json
  {
    "email": "john@example.com",
    "password": "yourpassword"
  }
  ```
  - **Response:**
    `200 OK`
  ```json
  {
    "access_token": "<jwt>",
    "token_type": "bearer"
  }
  ```
  The JWT token includes the user's ID in the `sub` claim.

---

## Database Schema

**Table:** `users`
| Column | Type | Constraints |
|-------------|-----------|--------------------|
| id | UUID | PRIMARY KEY |
| name | TEXT | NOT NULL |
| email | TEXT | NOT NULL, UNIQUE |
| password | TEXT | NOT NULL (bcrypt) |
| created_at | TIMESTAMP | DEFAULT NOW() |
| updated_at | TIMESTAMP | DEFAULT NOW() |

---

## Security

- Passwords are hashed with bcrypt (see `app/core/security.py`).
- JWT secret is loaded from `.env` and used for generating login tokens.
- Authentication is stateless, using JWT tokens that contain only the user ID.

---

## Development

- **Live reload:** Docker Compose is set up for hot reload with `uvicorn --reload`.
- **DB wait:** Uses `wait-for-it.sh` to ensure the app starts only after the database is ready.
- **DRY code:** Logger, DB query, and checker utilities keep the codebase clean and maintainable.

---

## How to Run

```bash
docker-compose up --build
```

- Visit [http://localhost:8000/docs](http://localhost:8000/docs) for Swagger UI.

---

## Testing

- You can use Swagger UI or any HTTP client (e.g., Postman, curl) to test the endpoints.
- For automated tests, see `test_improvements.py` (if present).

---

## Extending

- Add more routers to `app/api/v1/api_v1.py` as needed.
- Add protected routes by implementing your own authentication middleware.
- Add more business logic in the `service.py` layer.
- Use the provided utilities to keep your code DRY and maintainable.
