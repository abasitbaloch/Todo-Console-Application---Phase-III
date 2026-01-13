# Research: Phase II Full-Stack Web Application

**Feature**: 001-fullstack-web-app
**Date**: 2026-01-07
**Purpose**: Document architectural decisions and technical research for Phase II implementation

## Overview

This document captures research findings and architectural decisions for transforming the Phase I CLI application into a full-stack web application. Key areas of investigation: authentication flow, state management, database connection handling, and monorepo development tooling.

---

## Decision 1: Authentication Flow Architecture

### Context
Better Auth (frontend) must issue JWT tokens that FastAPI (backend) can independently verify. The shared secret must be synchronized between both systems without compromising security.

### Decision
**Chosen Approach**: Symmetric JWT signing with shared secret via environment variables

### Implementation Details

**Frontend (Better Auth)**:
```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  secret: process.env.AUTH_SECRET, // Shared secret from .env.local
  jwt: {
    expiresIn: "24h",
    algorithm: "HS256" // HMAC SHA-256 (symmetric)
  },
  database: {
    // Better Auth uses its own database for user management
    // Backend will verify JWT but not query Better Auth DB
  }
})
```

**Backend (FastAPI)**:
```python
# core/security.py
from jose import jwt, JWTError
from fastapi import HTTPException, status

JWT_SECRET = os.getenv("JWT_SECRET")  # Same value as AUTH_SECRET
JWT_ALGORITHM = "HS256"

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Environment Configuration**:
- Frontend `.env.local`: `AUTH_SECRET=<random-256-bit-secret>`
- Backend `.env`: `JWT_SECRET=<same-random-256-bit-secret>`
- Secret generation: `openssl rand -base64 32`

### Rationale
1. **Simplicity**: Symmetric signing (HS256) is simpler than asymmetric (RS256) for single-backend scenarios
2. **Performance**: HMAC verification is faster than RSA signature verification
3. **Security**: 256-bit secret provides sufficient entropy; secret stored in environment variables (never committed)
4. **Independence**: Backend doesn't need to query Better Auth database or make HTTP calls to verify tokens
5. **Stateless**: JWT contains all necessary claims (user_id in "sub" field); no session storage required

### Alternatives Considered
- **Asymmetric JWT (RS256)**: More complex; requires public/private key pair management; overkill for single backend
- **Session-based auth**: Violates Stateless Architecture principle; requires shared session store (Redis)
- **OAuth2 with external provider**: Adds external dependency; increases complexity for MVP

### Trade-offs
- **Pro**: Fast, simple, stateless verification
- **Pro**: No network calls or database queries for authentication
- **Con**: Secret must be kept secure; if leaked, all tokens can be forged
- **Con**: Token revocation requires additional infrastructure (token blacklist)

### Validation
Test with curl:
```bash
# 1. Register/login via frontend to get JWT
# 2. Extract token from browser DevTools (localStorage or cookie)
# 3. Test backend endpoint
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/tasks
```

---

## Decision 2: State Management Strategy

### Context
Next.js 16+ App Router supports both Server Components (default) and Client Components. Need to determine optimal pattern for fetching and displaying tasks.

### Decision
**Chosen Approach**: Hybrid - Server Components for initial data fetch, Client Components for mutations

### Implementation Details

**Server Component (Dashboard Page)**:
```typescript
// app/dashboard/page.tsx
import { TaskList } from '@/components/TaskList'

async function getTasks(token: string) {
  const res = await fetch('http://localhost:8000/api/tasks', {
    headers: { 'Authorization': `Bearer ${token}` },
    cache: 'no-store' // Always fetch fresh data
  })
  return res.json()
}

export default async function DashboardPage() {
  const session = await auth.getSession()
  const tasks = await getTasks(session.token)

  return <TaskList initialTasks={tasks} />
}
```

**Client Component (Task List with Mutations)**:
```typescript
// components/TaskList.tsx
'use client'
import { useState } from 'react'

export function TaskList({ initialTasks }) {
  const [tasks, setTasks] = useState(initialTasks)

  async function createTask(title: string) {
    const res = await fetch('/api/tasks', {
      method: 'POST',
      body: JSON.stringify({ title })
    })
    const newTask = await res.json()
    setTasks([newTask, ...tasks])
  }

  // Similar handlers for update, delete, mark complete
  return (/* UI with mutation handlers */)
}
```

### Rationale
1. **Performance**: Server Components fetch data on server (no client-side API call on initial load)
2. **SEO**: Task data rendered on server (though dashboard is protected, pattern is extensible)
3. **Simplicity**: No need for complex state management library (Redux, Zustand) for MVP
4. **Reactivity**: Client Components handle user interactions and optimistic updates
5. **Progressive Enhancement**: Works without JavaScript for initial render

### Alternatives Considered
- **Pure Client Components with SWR/React Query**: More client-side code; slower initial load; better for real-time updates
- **Pure Server Components with Server Actions**: Requires form submissions; less interactive UX
- **Global state management (Redux)**: Overkill for simple CRUD operations; adds complexity

### Trade-offs
- **Pro**: Fast initial page load (server-rendered)
- **Pro**: Simple mental model (server fetch → client mutations)
- **Con**: Requires careful token passing from server to client
- **Con**: No automatic revalidation (must manually refresh or use optimistic updates)

### Validation
1. Measure Time to First Byte (TTFB) - should be <500ms
2. Verify tasks appear without JavaScript enabled (progressive enhancement)
3. Test optimistic updates feel instant (<100ms perceived latency)

---

## Decision 3: Database Connection Pooling

### Context
Neon Serverless PostgreSQL has connection limits and can timeout on idle connections. Need robust connection pooling strategy for FastAPI async operations.

### Decision
**Chosen Approach**: SQLModel with asyncpg engine and connection pooling via SQLAlchemy

### Implementation Details

**Database Configuration**:
```python
# core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

DATABASE_URL = os.getenv("DATABASE_URL")  # postgresql+asyncpg://...

engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set True for SQL logging in development
    pool_size=5,  # Max 5 connections in pool
    max_overflow=10,  # Allow 10 additional connections under load
    pool_pre_ping=True,  # Verify connection health before use
    pool_recycle=3600,  # Recycle connections after 1 hour
)

async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
```

**Dependency Injection**:
```python
# api/deps.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

# Usage in endpoints
@router.get("/tasks")
async def get_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    result = await db.execute(
        select(Task).where(Task.user_id == current_user["user_id"])
    )
    return result.scalars().all()
```

### Rationale
1. **Connection Reuse**: Pool maintains 5 persistent connections; avoids connection overhead
2. **Health Checks**: `pool_pre_ping` detects stale connections before use
3. **Timeout Prevention**: `pool_recycle` prevents long-lived connections from timing out
4. **Scalability**: `max_overflow` handles traffic spikes without rejecting requests
5. **Async Support**: asyncpg is fastest PostgreSQL driver for Python async

### Alternatives Considered
- **Synchronous SQLAlchemy**: Blocks event loop; poor performance for I/O-bound operations
- **Raw asyncpg**: No ORM; more boilerplate; harder to maintain
- **Prisma (TypeScript ORM)**: Would require Node.js backend; violates Python constraint

### Trade-offs
- **Pro**: Excellent performance for async operations
- **Pro**: Automatic connection management (no manual open/close)
- **Con**: Slightly more complex than synchronous code
- **Con**: Requires understanding of async/await patterns

### Validation
1. Monitor connection pool metrics (active, idle, overflow)
2. Load test with 100 concurrent requests - should not exhaust pool
3. Test connection recovery after database restart

---

## Decision 4: Monorepo Development Tooling

### Context
Need to run Next.js dev server (port 3000) and FastAPI server (port 8000) concurrently during development with hot reload for both.

### Decision
**Chosen Approach**: npm scripts with concurrently package for parallel execution

### Implementation Details

**Root package.json**:
```json
{
  "name": "todo-fullstack-monorepo",
  "private": true,
  "scripts": {
    "dev": "concurrently \"npm run dev:frontend\" \"npm run dev:backend\"",
    "dev:frontend": "cd frontend && npm run dev",
    "dev:backend": "cd backend && uvicorn src.main:app --reload --port 8000",
    "install:all": "npm install && cd frontend && npm install && cd ../backend && pip install -r requirements.txt"
  },
  "devDependencies": {
    "concurrently": "^8.2.2"
  }
}
```

**Frontend package.json**:
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  }
}
```

**Backend requirements.txt** (or pyproject.toml):
```
fastapi==0.109.0
sqlmodel==0.0.14
python-jose[cryptography]==3.3.0
asyncpg==0.29.0
alembic==1.13.1
uvicorn[standard]==0.27.0
```

### Rationale
1. **Single Command**: `npm run dev` starts both servers with one command
2. **Hot Reload**: Both servers watch for file changes and reload automatically
3. **Colored Output**: concurrently prefixes logs with [frontend] and [backend] labels
4. **Cross-Platform**: Works on Windows, macOS, Linux
5. **Standard Tools**: Uses npm (already required for frontend) and uvicorn (FastAPI standard)

### Alternatives Considered
- **Docker Compose**: Overkill for development; slower hot reload; deferred to Phase IV
- **Turborepo/Nx**: Complex monorepo tools; unnecessary for 2-project setup
- **Separate terminals**: Manual; error-prone; no unified logging

### Trade-offs
- **Pro**: Simple, fast, standard tooling
- **Pro**: Unified development experience
- **Con**: Requires Node.js even for backend-only work
- **Con**: No process isolation (one crash can affect the other)

### Validation
1. Run `npm run dev` - both servers should start
2. Edit frontend file - Next.js should hot reload
3. Edit backend file - uvicorn should restart
4. Verify CORS configured (frontend:3000 → backend:8000)

---

## Additional Research Findings

### CORS Configuration
Backend must allow requests from frontend origin:
```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Environment Variables Management
- **Frontend**: `.env.local` (Next.js convention, gitignored)
- **Backend**: `.env` (Python convention, gitignored)
- **Templates**: `.env.example` and `.env.local.example` (committed to repo)

### Database Migrations Strategy
- **Tool**: Alembic (SQLAlchemy migration tool)
- **Workflow**:
  1. Modify SQLModel models
  2. Generate migration: `alembic revision --autogenerate -m "description"`
  3. Review generated migration file
  4. Apply migration: `alembic upgrade head`

---

## Summary of Decisions

| Decision Area | Chosen Approach | Key Benefit |
|---------------|----------------|-------------|
| Authentication | Symmetric JWT (HS256) with shared secret | Simple, fast, stateless |
| State Management | Hybrid Server/Client Components | Fast initial load, reactive mutations |
| Database Pooling | asyncpg with SQLAlchemy pool | Connection reuse, timeout prevention |
| Dev Tooling | npm + concurrently | Single command, hot reload |

All decisions align with constitutional principles (Simplicity, Stateless Architecture, Monorepo Separation, Security First) and support the Phase II MVP scope.

---

## Next Steps

1. **Phase 1**: Generate data-model.md with User and Task entity schemas
2. **Phase 1**: Generate API contracts (auth.yaml, tasks.yaml) with OpenAPI specs
3. **Phase 1**: Generate quickstart.md with setup and testing instructions
4. **Phase 2**: Generate tasks.md with implementation tasks ordered by dependencies
