# Todo Backend API

FastAPI backend for the Phase II Full-Stack Todo Application.

## Tech Stack

- **FastAPI** - Modern Python web framework
- **SQLModel** - SQL database ORM with Pydantic integration
- **PostgreSQL** - Database (via asyncpg)
- **Alembic** - Database migrations
- **python-jose** - JWT token handling
- **passlib** - Password hashing with bcrypt
- **Pydantic** - Data validation

## Prerequisites

- Python 3.11+
- PostgreSQL database (Neon recommended)

## Installation

```bash
# Install dependencies
pip install -e .

# For development with testing tools
pip install -e ".[dev]"
```

## Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
# Example for Neon: postgresql+asyncpg://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb

# JWT Configuration (MUST match frontend AUTH_SECRET)
JWT_SECRET=your-random-256-bit-secret-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS Configuration
CORS_ORIGINS=http://localhost:3000

# Environment
ENVIRONMENT=development
```

**⚠️ IMPORTANT**: `JWT_SECRET` must match the frontend's `AUTH_SECRET`

## Database Setup

### Run Migrations

```bash
# Apply all migrations to create tables
python -m alembic upgrade head
```

### Create New Migration

```bash
# Auto-generate migration from model changes
python -m alembic revision --autogenerate -m "description"

# Create empty migration
python -m alembic revision -m "description"
```

### Rollback Migration

```bash
# Rollback one migration
python -m alembic downgrade -1

# Rollback to specific revision
python -m alembic downgrade <revision_id>
```

## Running the Server

### Development Mode

```bash
uvicorn src.main:app --reload --port 8000
```

The API will be available at http://localhost:8000

### Production Mode

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info (requires auth)

### Tasks

All task endpoints require authentication (Bearer token).

- `GET /api/tasks` - Get all tasks for current user
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{task_id}` - Get specific task
- `PUT /api/tasks/{task_id}` - Update task
- `DELETE /api/tasks/{task_id}` - Delete task

### Health Check

- `GET /health` - Health check endpoint

## Project Structure

```
backend/
├── src/
│   ├── api/              # API endpoints
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── tasks.py      # Task CRUD endpoints
│   │   └── deps.py       # Dependency injection
│   ├── core/             # Core utilities
│   │   ├── config.py     # Environment configuration
│   │   ├── database.py   # Database connection
│   │   └── security.py   # JWT and password utilities
│   ├── models/           # SQLModel database models
│   │   ├── user.py       # User model
│   │   └── task.py       # Task model
│   ├── schemas/          # Pydantic request/response schemas
│   │   ├── user.py       # User schemas
│   │   └── task.py       # Task schemas
│   └── main.py           # FastAPI application
├── alembic/              # Database migrations
│   ├── versions/         # Migration files
│   └── env.py            # Alembic configuration
├── tests/                # Backend tests
├── pyproject.toml        # Python dependencies
└── alembic.ini           # Alembic configuration
```

## Security Features

- ✅ JWT-based stateless authentication
- ✅ Bcrypt password hashing (cost factor 12)
- ✅ User data isolation (all queries filtered by user_id)
- ✅ Ownership validation on all task operations
- ✅ CORS configuration
- ✅ Password strength validation
- ✅ Case-insensitive email uniqueness

## Database Schema

### Users Table
- `id` (UUID, PK)
- `email` (VARCHAR, UNIQUE)
- `hashed_password` (VARCHAR)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

### Tasks Table
- `id` (UUID, PK)
- `user_id` (UUID, FK → users.id)
- `title` (VARCHAR(200))
- `description` (TEXT, nullable)
- `is_completed` (BOOLEAN)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_auth.py
```

## Troubleshooting

### Database Connection Issues

- Verify DATABASE_URL format: `postgresql+asyncpg://user:pass@host:port/db`
- For Neon: ensure connection string uses asyncpg driver
- Check database credentials and network access

### Migration Issues

```bash
# Check current migration status
python -m alembic current

# View migration history
python -m alembic history

# Reset database (⚠️ destroys all data)
python -m alembic downgrade base
python -m alembic upgrade head
```

### Import Errors

```bash
# Reinstall package in editable mode
pip install -e .
```

## License

This project is part of the Phase II Full-Stack Web Application specification.
