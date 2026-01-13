# Quickstart Guide: Phase II Full-Stack Web Application

**Feature**: 001-fullstack-web-app
**Date**: 2026-01-07
**Purpose**: Setup instructions and testing procedures for local development

## Prerequisites

Before starting, ensure you have the following installed:

- **Node.js**: v18.x or higher (for Next.js frontend)
- **Python**: 3.13+ (for FastAPI backend)
- **PostgreSQL**: Access to Neon Serverless PostgreSQL (or local PostgreSQL 14+)
- **Git**: For version control
- **curl** or **Postman**: For API testing

---

## Project Setup

### 1. Clone Repository and Install Dependencies

```bash
# Navigate to project root
cd Todo-Console-Application-main

# Install root dependencies (concurrently for parallel dev servers)
npm install

# Install frontend dependencies
cd frontend
npm install
cd ..

# Install backend dependencies
cd backend
pip install -r requirements.txt
# OR if using Poetry:
# poetry install
cd ..
```

---

## Backend Setup

### 2. Configure Backend Environment

Create `.env` file in `backend/` directory:

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` with your configuration:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host/database
# Example for Neon: postgresql+asyncpg://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb

# JWT Secret (MUST match frontend AUTH_SECRET)
JWT_SECRET=your-random-256-bit-secret-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
CORS_ORIGINS=http://localhost:3000

# Environment
ENVIRONMENT=development
```

**Generate JWT Secret**:
```bash
openssl rand -base64 32
```

### 3. Initialize Database

```bash
cd backend

# Initialize Alembic (if not already done)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial schema: users and tasks"

# Apply migration
alembic upgrade head

# Verify tables created
# Connect to your database and run:
# \dt (PostgreSQL) to list tables
# You should see: users, tasks, alembic_version
```

### 4. Run Backend Server

```bash
cd backend

# Development mode (with hot reload)
uvicorn src.main:app --reload --port 8000

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete
```

**Verify Backend**:
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

---

## Frontend Setup

### 5. Configure Frontend Environment

Create `.env.local` file in `frontend/` directory:

```bash
cd frontend
cp .env.local.example .env.local
```

Edit `frontend/.env.local`:

```env
# Better Auth Secret (MUST match backend JWT_SECRET)
AUTH_SECRET=your-random-256-bit-secret-here

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration
BETTER_AUTH_URL=http://localhost:3000
```

**CRITICAL**: `AUTH_SECRET` must be identical to backend `JWT_SECRET`

### 6. Run Frontend Server

```bash
cd frontend

# Development mode (with hot reload)
npm run dev

# You should see:
# ▲ Next.js 16.x
# - Local:        http://localhost:3000
# - Ready in Xms
```

**Verify Frontend**:
Open browser to `http://localhost:3000` - you should see the landing/login page

---

## Running Both Servers Concurrently

From project root:

```bash
# Start both frontend and backend with one command
npm run dev

# You should see output from both servers:
# [frontend] ▲ Next.js 16.x ready on http://localhost:3000
# [backend] INFO: Uvicorn running on http://127.0.0.1:8000
```

**Stop servers**: Press `Ctrl+C` in terminal

---

## Testing Procedures

### Test 1: API Health Check

**Purpose**: Verify backend is running and accessible

```bash
curl http://localhost:8000/health
```

**Expected Response**:
```json
{"status": "healthy"}
```

---

### Test 2: User Registration

**Purpose**: Verify user registration endpoint

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePass123"
  }'
```

**Expected Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "testuser@example.com",
  "created_at": "2026-01-07T12:00:00Z"
}
```

**Test Edge Cases**:
```bash
# Duplicate email (should return 409 Conflict)
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "testuser@example.com", "password": "SecurePass123"}'

# Weak password (should return 400 Bad Request)
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "newuser@example.com", "password": "weak"}'
```

---

### Test 3: User Login

**Purpose**: Verify authentication and JWT token issuance

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePass123"
  }'
```

**Expected Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Save the token** for subsequent tests:
```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### Test 4: Authentication Testing (401 Unauthorized)

**Purpose**: Verify endpoints reject requests without valid JWT

```bash
# Attempt to access protected endpoint without token
curl http://localhost:8000/api/tasks

# Expected Response (401 Unauthorized):
# {"detail": "Not authenticated"}

# Attempt with invalid token
curl -H "Authorization: Bearer invalid-token" \
  http://localhost:8000/api/tasks

# Expected Response (401 Unauthorized):
# {"detail": "Invalid token"}
```

---

### Test 5: Task Creation

**Purpose**: Verify authenticated users can create tasks

```bash
# Create task with description
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }'

# Expected Response (201 Created):
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "is_completed": false,
  "created_at": "2026-01-07T14:30:00Z",
  "updated_at": "2026-01-07T14:30:00Z"
}

# Create task without description
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Call dentist"}'
```

---

### Test 6: Task Retrieval

**Purpose**: Verify users can view their tasks

```bash
# Get all tasks for authenticated user
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/tasks

# Expected Response (200 OK):
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "is_completed": false,
    "created_at": "2026-01-07T14:30:00Z",
    "updated_at": "2026-01-07T14:30:00Z"
  },
  {
    "id": "123e4567-e89b-12d3-a456-426614174001",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Call dentist",
    "description": null,
    "is_completed": false,
    "created_at": "2026-01-07T14:35:00Z",
    "updated_at": "2026-01-07T14:35:00Z"
  }
]
```

---

### Test 7: Task Update

**Purpose**: Verify users can update their tasks

```bash
# Mark task as complete
curl -X PUT http://localhost:8000/api/tasks/123e4567-e89b-12d3-a456-426614174000 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_completed": true}'

# Update task title and description
curl -X PUT http://localhost:8000/api/tasks/123e4567-e89b-12d3-a456-426614174000 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries and cook dinner",
    "description": "Updated shopping list"
  }'
```

---

### Test 8: Task Deletion

**Purpose**: Verify users can delete their tasks

```bash
curl -X DELETE http://localhost:8000/api/tasks/123e4567-e89b-12d3-a456-426614174000 \
  -H "Authorization: Bearer $TOKEN"

# Expected Response (204 No Content)
# No response body

# Verify deletion
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/tasks/123e4567-e89b-12d3-a456-426614174000

# Expected Response (404 Not Found):
# {"detail": "Task not found"}
```

---

### Test 9: Data Isolation Testing (CRITICAL)

**Purpose**: Verify users CANNOT access other users' tasks

**Setup**:
```bash
# 1. Register User A
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "usera@example.com", "password": "SecurePass123"}'

# 2. Login as User A and save token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "usera@example.com", "password": "SecurePass123"}'
# Save token: export TOKEN_A="..."

# 3. Create tasks for User A
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"title": "User A Task 1"}'

curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"title": "User A Task 2"}'

# 4. Register User B
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "userb@example.com", "password": "SecurePass123"}'

# 5. Login as User B and save token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "userb@example.com", "password": "SecurePass123"}'
# Save token: export TOKEN_B="..."
```

**Test Isolation**:
```bash
# User B retrieves their tasks (should be empty)
curl -H "Authorization: Bearer $TOKEN_B" \
  http://localhost:8000/api/tasks

# Expected Response: []
# ✅ PASS: User B sees empty list (not User A's tasks)

# User B attempts to access User A's task by ID
# (Get task ID from User A's task list first)
curl -H "Authorization: Bearer $TOKEN_B" \
  http://localhost:8000/api/tasks/<USER_A_TASK_ID>

# Expected Response (403 Forbidden):
# {"detail": "Not authorized to access this task"}
# ✅ PASS: User B cannot access User A's task

# User B attempts to update User A's task
curl -X PUT http://localhost:8000/api/tasks/<USER_A_TASK_ID> \
  -H "Authorization: Bearer $TOKEN_B" \
  -H "Content-Type: application/json" \
  -d '{"title": "Hacked!"}'

# Expected Response (403 Forbidden):
# {"detail": "Not authorized to access this task"}
# ✅ PASS: User B cannot modify User A's task

# User B attempts to delete User A's task
curl -X DELETE http://localhost:8000/api/tasks/<USER_A_TASK_ID> \
  -H "Authorization: Bearer $TOKEN_B"

# Expected Response (403 Forbidden):
# {"detail": "Not authorized to access this task"}
# ✅ PASS: User B cannot delete User A's task
```

**Validation Criteria**:
- ✅ User B's task list is empty (does not include User A's tasks)
- ✅ User B receives 403 Forbidden when accessing User A's task by ID
- ✅ User B cannot update User A's tasks
- ✅ User B cannot delete User A's tasks
- ✅ User A's tasks remain intact after User B's attempts

---

## Frontend Testing (Browser)

### Test 10: End-to-End User Flow

1. **Open Browser**: Navigate to `http://localhost:3000`

2. **Register New User**:
   - Click "Register" or navigate to `/register`
   - Enter email: `frontend-test@example.com`
   - Enter password: `SecurePass123`
   - Submit form
   - **Expected**: Redirected to dashboard

3. **Create Tasks**:
   - Click "Add Task" button
   - Enter title: "Test Task 1"
   - Enter description (optional): "This is a test"
   - Submit form
   - **Expected**: Task appears in list immediately

4. **Mark Task Complete**:
   - Click checkbox next to task
   - **Expected**: Task shows strikethrough or different styling

5. **Edit Task**:
   - Click "Edit" button on task
   - Modify title or description
   - Save changes
   - **Expected**: Changes reflected immediately

6. **Delete Task**:
   - Click "Delete" button on task
   - Confirm deletion (if prompted)
   - **Expected**: Task removed from list

7. **Logout and Login**:
   - Click "Logout"
   - **Expected**: Redirected to login page
   - Login with same credentials
   - **Expected**: All tasks still present (data persistence verified)

8. **Responsive Design**:
   - Resize browser window to mobile width (320px)
   - **Expected**: Layout adapts, all features remain functional
   - Resize to desktop width (1920px)
   - **Expected**: Layout expands, no broken elements

---

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`
**Solution**: Install backend dependencies: `cd backend && pip install -r requirements.txt`

**Problem**: `sqlalchemy.exc.OperationalError: could not connect to server`
**Solution**: Verify `DATABASE_URL` in `backend/.env` is correct and database is accessible

**Problem**: `jose.exceptions.JWTError: Invalid token`
**Solution**: Ensure `JWT_SECRET` in `backend/.env` matches `AUTH_SECRET` in `frontend/.env.local`

### Frontend Issues

**Problem**: `Error: Cannot find module 'next'`
**Solution**: Install frontend dependencies: `cd frontend && npm install`

**Problem**: CORS error in browser console
**Solution**: Verify `CORS_ORIGINS` in `backend/.env` includes `http://localhost:3000`

**Problem**: 401 Unauthorized on all API calls
**Solution**: Check that Better Auth is configured correctly and JWT secret matches backend

### Database Issues

**Problem**: `alembic.util.exc.CommandError: Can't locate revision identified by 'head'`
**Solution**: Initialize Alembic: `cd backend && alembic init alembic`

**Problem**: Tables not created
**Solution**: Run migrations: `cd backend && alembic upgrade head`

---

## Success Criteria Validation

After completing all tests, verify:

- ✅ **SC-001**: Registration completes in <60 seconds
- ✅ **SC-002**: Task creation appears in <3 seconds
- ✅ **SC-003**: All 5 CRUD operations work without errors
- ✅ **SC-004**: Data isolation test passes (User B cannot access User A's tasks)
- ✅ **SC-005**: Tasks persist after server restart
- ✅ **SC-006**: UI functional on mobile (320px width)
- ✅ **SC-007**: UI functional on desktop (1920px width)
- ✅ **SC-008**: 95%+ operations succeed on first attempt
- ✅ **SC-009**: Authentication flow works correctly
- ✅ **SC-010**: Invalid auth attempts handled gracefully

---

## Next Steps

Once all tests pass:

1. **Generate Tasks**: Run `/sp.tasks` to create implementation task list
2. **Begin Implementation**: Start with foundational tasks (database models, authentication)
3. **Iterative Testing**: Re-run tests after each major implementation milestone
4. **Documentation**: Update README.md with production deployment instructions

---

## Quick Reference

**Start Development**:
```bash
npm run dev  # From project root
```

**Backend Only**:
```bash
cd backend && uvicorn src.main:app --reload --port 8000
```

**Frontend Only**:
```bash
cd frontend && npm run dev
```

**Run Migrations**:
```bash
cd backend && alembic upgrade head
```

**Generate Migration**:
```bash
cd backend && alembic revision --autogenerate -m "description"
```

**Test API**:
```bash
curl http://localhost:8000/health
```
