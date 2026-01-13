# Todo Full-Stack Web Application

Phase II - Full-Stack Todo Application with Next.js and FastAPI

## Features

- ✅ User authentication (registration, login, logout)
- ✅ JWT-based stateless authentication
- ✅ Create, read, update, and delete tasks
- ✅ Mark tasks as complete/incomplete
- ✅ Data isolation (users can only access their own tasks)
- ✅ Responsive UI with Tailwind CSS
- ✅ Secure password hashing with bcrypt
- ✅ PostgreSQL database with connection pooling

## Tech Stack

### Frontend
- **Next.js 15.1.3** - React framework with App Router
- **React 19** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS framework
- **lucide-react** - Icon library

### Backend
- **FastAPI** - Modern Python web framework
- **SQLModel** - SQL database ORM with Pydantic integration
- **PostgreSQL** - Database (via Neon serverless)
- **Alembic** - Database migrations
- **python-jose** - JWT token handling
- **passlib** - Password hashing
- **asyncpg** - Async PostgreSQL driver

## Prerequisites

- **Python 3.11+** (backend)
- **Node.js 18+** (frontend)
- **PostgreSQL database** (Neon recommended)

## Installation

### 1. Clone the repository

```bash
cd Todo-Console-Application-main
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies
pip install -e .

# Create .env file from example
cp .env.example .env

# Edit .env and add your database credentials:
# DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
# JWT_SECRET=your-random-256-bit-secret-here
# CORS_ORIGINS=http://localhost:3000
```

### 3. Database Migration

```bash
# Run migrations to create tables
python -m alembic upgrade head
```

### 4. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Create .env.local file from example
cp .env.local.example .env.local

# Edit .env.local and add your configuration:
# AUTH_SECRET=your-random-256-bit-secret-here (MUST match backend JWT_SECRET)
# NEXT_PUBLIC_API_URL=http://localhost:8000
# BETTER_AUTH_URL=http://localhost:3000
```

## Running the Application

### Option 1: Run Both Servers Simultaneously (Recommended)

From the root directory:

```bash
npm run dev
```

This will start:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

### Option 2: Run Servers Separately

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Usage

1. **Register**: Navigate to http://localhost:3000/register
   - Enter email and password (min 8 chars, must contain letter and number)
   - Click "Sign Up"

2. **Login**: Navigate to http://localhost:3000
   - Enter your email and password
   - Click "Sign In"

3. **Create Tasks**: On the dashboard
   - Enter task title (required)
   - Optionally add description
   - Click "Create Task"

4. **Manage Tasks**:
   - ✅ Check/uncheck to mark complete/incomplete
   - 🗑️ Click "Delete" to remove task (with confirmation)

5. **Logout**: Click "Logout" button in navigation

## Implementation Status

**Completed: 48 of 68 tasks (71%)**

### ✅ MVP Complete (Phases 1-3)
- Project setup and infrastructure
- User authentication and authorization
- Basic task management

### ✅ Extended Features (Phases 4-5)
- Full CRUD operations for tasks
- Task completion toggle
- Task deletion with confirmation

### ⏳ Remaining Work
- **T044-T045**: Inline editing for task title/description
- **Phase 6**: Enhanced responsive UI and accessibility
- **Phase 7**: Polish and documentation

## Environment Variables

### Backend (.env)

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
JWT_SECRET=your-random-256-bit-secret-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development
```

### Frontend (.env.local)

```env
AUTH_SECRET=your-random-256-bit-secret-here
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_URL=http://localhost:3000
```

**⚠️ IMPORTANT**: `AUTH_SECRET` (frontend) MUST match `JWT_SECRET` (backend)

## Security Features

- ✅ JWT-based stateless authentication
- ✅ Bcrypt password hashing (cost factor 12)
- ✅ User data isolation (all queries filtered by user_id)
- ✅ Ownership validation on all task operations
- ✅ CORS configuration
- ✅ Password strength validation (min 8 chars, letter + number)
- ✅ Case-insensitive email uniqueness

## Troubleshooting

### Backend won't start
- Verify Python 3.11+ is installed: `python --version`
- Check DATABASE_URL is correct in backend/.env
- Ensure PostgreSQL database is accessible
- Run migrations: `python -m alembic upgrade head`

### Frontend won't start
- Verify Node.js 18+ is installed: `node --version`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`
- Check .env.local exists and has correct values

### Authentication fails
- Verify AUTH_SECRET (frontend) matches JWT_SECRET (backend)
- Check backend is running on port 8000
- Check CORS_ORIGINS includes http://localhost:3000

### Database connection fails
- Verify DATABASE_URL format: `postgresql+asyncpg://user:pass@host:port/db`
- For Neon: ensure connection string uses asyncpg driver
- Check database credentials and network access

## License

This project is part of the Phase II Full-Stack Web Application specification.
