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
│   │   ├── deps.py                # Authentication dependencies
│   │   └── v1/
│   │       ├── api_v1.py          # Main API router for v1
│   │       └── routers/
│   │           ├── user_router.py # User CRUD endpoints, login, profile
│   │           └── file_router.py # File upload endpoint using MinIO
│   ├── core/
│   │   ├── config.py              # App settings (env vars)
│   │   ├── db.py                  # DB connection pool, query helper
│   │   ├── db_init.py             # Optional DB schema/migration setup
│   │   ├── security.py            # Password hashing/verification (bcrypt)
│   │   ├── jwt.py                 # JWT creation and verification
│   │   ├── logger.py              # Centralized logger
│   │   ├── checker.py             # Common validation (e.g. user existence)
│   │   └── minio_client.py        # MinIO client and upload logic
│   ├── domains/
│   │   ├── user/
│   │   │   ├── models.py          # Pydantic models for user
│   │   │   ├── repository.py      # DB queries
│   │   │   └── service.py         # Business logic
│   │   └── file/
│   │       └── service.py         # File upload logic
│   └── main.py                    # FastAPI app entrypoint
│
├── app/migrations/
│   ├── 001_create_user.sql        # SQL schema
│   └── run.py                     # Optional migration runner
│
├── docker-compose.yml             # Compose configuration for app + DB + MinIO
├── Dockerfile                     # App Dockerfile
├── requirements.txt               # Python dependencies
├── wait-for-it.sh                 # Wait for DB before app starts
└── .env                           # Environment variables

```

---

## Environment Variables (`.env`)

```
DATABASE_URL=postgresql://postgres:password@db:5432/app_db
JWT_SECRET=your_super_secret_jwt_key
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=uploads
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
      "created_at": "timestamp",
      "updated_at": "timestamp"
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

### Get Profile (Protected Route)

- **GET** `/users/profile`
- **Headers:**
  ```
  Authorization: Bearer <jwt_token>
  ```
- **Response:**
  `200 OK`
  ```json
  {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "timestamp",
    "updated_at": "timestamp"
  }
  ```

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
    "user": {
      "id": "uuid",
      "name": "John Doe",
      "email": "john@example.com",
      "created_at": "timestamp",
      "updated_at": "timestamp"
    },
    "access_token": "<jwt>",
    "token_type": "bearer"
  }
  ```
  The JWT token includes only the user's ID in the `sub` claim for security.

---

### 📤 File Upload

- **POST** `/files/upload`
- **Response:**
  ```json
  {
    "filename": "cool_meme.png",
    "message": "File uploaded successfully"
  }
  ```

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

- **Password Security:**
  - Passwords are hashed with bcrypt (see `app/core/security.py`)
  - Passwords are never returned in API responses

- **Authentication:**
  - JWT-based authentication using HTTPBearer scheme
  - JWT secret loaded from `.env`
  - Stateless authentication using tokens containing only the user ID
  - Protected routes require valid JWT token in Authorization header

- **Data Protection:**
  - Email uniqueness enforced at database level
  - Duplicate email registration prevented with clear error messages
  - User data consistently returned using Pydantic models
  - Input validation using Pydantic models

---

## Development

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

---

## Future Enhancements

- ✅ Add file download support
- ⏳ Email verification
- 🔐 Password reset flow
- 📊 Admin dashboard (optional)

---


<!-- Fixes Needed!! + Current New File upload is bare minimum and may not be up to date with other features -->