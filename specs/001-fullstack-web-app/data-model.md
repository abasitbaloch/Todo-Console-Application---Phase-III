# Data Model: Phase II Full-Stack Web Application

**Feature**: 001-fullstack-web-app
**Date**: 2026-01-07
**Purpose**: Define database schema and entity relationships for User and Task models

## Overview

This document defines the data models for the Phase II full-stack application. The schema supports multi-user authentication with strict data isolation, ensuring each user can only access their own tasks.

---

## Entity: User

### Purpose
Represents an authenticated user account. Users can register, login, and own multiple tasks.

### Schema

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL, DEFAULT uuid_generate_v4() | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User's email address (used for login) |
| hashed_password | VARCHAR(255) | NOT NULL | Bcrypt-hashed password (never store plaintext) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last account update timestamp |

### Validation Rules

- **email**: Must match email format regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- **email**: Case-insensitive uniqueness (normalize to lowercase before storage)
- **password** (before hashing): Minimum 8 characters, at least one letter and one number
- **hashed_password**: Bcrypt hash with cost factor 12

### Indexes

```sql
CREATE UNIQUE INDEX idx_users_email ON users(LOWER(email));
CREATE INDEX idx_users_created_at ON users(created_at);
```

### SQLModel Implementation

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Relationships

- **One-to-Many**: User → Tasks (one user owns many tasks)

### Security Considerations

1. **Password Storage**: Never store plaintext passwords; always use bcrypt hashing
2. **Email Privacy**: Email addresses are PII; never expose in public APIs
3. **User ID Exposure**: UUIDs are safe to expose (non-sequential, hard to guess)
4. **Token Claims**: JWT "sub" field contains user.id for authentication

---

## Entity: Task

### Purpose
Represents a single todo item owned by a user. Tasks have a title, optional description, completion status, and timestamps.

### Schema

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL, DEFAULT uuid_generate_v4() | Unique task identifier |
| user_id | UUID | FOREIGN KEY (users.id), NOT NULL, INDEX | Owner of this task |
| title | VARCHAR(200) | NOT NULL | Task title (required) |
| description | TEXT | NULL | Optional task description (max 2000 chars) |
| is_completed | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Task creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last task update timestamp |

### Validation Rules

- **title**: Required, 1-200 characters, no leading/trailing whitespace
- **description**: Optional, max 2000 characters
- **user_id**: Must reference existing user (foreign key constraint)
- **is_completed**: Boolean only (true/false)

### Indexes

```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);
```

**Rationale for indexes**:
- `idx_tasks_user_id`: Fast filtering by user (required for data isolation)
- `idx_tasks_created_at`: Fast ordering by creation date (newest first)
- `idx_tasks_user_created`: Composite index for user-specific queries with ordering

### SQLModel Implementation

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship (optional, for ORM convenience)
    # user: Optional[User] = Relationship(back_populates="tasks")
```

### Relationships

- **Many-to-One**: Task → User (many tasks belong to one user)

### Security Considerations

1. **Data Isolation**: ALL queries MUST filter by user_id from JWT claims
2. **Ownership Validation**: Before update/delete, verify task.user_id == current_user.id
3. **No Cross-User Access**: Never expose task IDs in URLs without ownership check
4. **Soft Delete**: Phase II uses hard delete; soft delete deferred to future phase

---

## Database Constraints

### Foreign Key Constraints

```sql
ALTER TABLE tasks
ADD CONSTRAINT fk_tasks_user_id
FOREIGN KEY (user_id) REFERENCES users(id)
ON DELETE CASCADE;  -- Delete all tasks when user is deleted
```

### Check Constraints

```sql
ALTER TABLE tasks
ADD CONSTRAINT chk_title_not_empty
CHECK (LENGTH(TRIM(title)) > 0);

ALTER TABLE tasks
ADD CONSTRAINT chk_description_length
CHECK (description IS NULL OR LENGTH(description) <= 2000);
```

---

## Entity Relationship Diagram

```
┌─────────────────────────┐
│        User             │
├─────────────────────────┤
│ id (PK, UUID)           │
│ email (UNIQUE)          │
│ hashed_password         │
│ created_at              │
│ updated_at              │
└─────────────────────────┘
           │
           │ 1
           │
           │ owns
           │
           │ *
           ▼
┌─────────────────────────┐
│        Task             │
├─────────────────────────┤
│ id (PK, UUID)           │
│ user_id (FK)            │◄─── Foreign Key to User.id
│ title                   │
│ description (nullable)  │
│ is_completed            │
│ created_at              │
│ updated_at              │
└─────────────────────────┘
```

**Cardinality**: One User has Many Tasks (1:N relationship)

---

## Migration Strategy

### Initial Migration (Alembic)

```python
# alembic/versions/001_initial_schema.py
"""Initial schema: users and tasks tables

Revision ID: 001
Create Date: 2026-01-07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_users_email', 'users', [sa.text('LOWER(email)')], unique=True)

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_created_at', 'tasks', ['created_at'], postgresql_ops={'created_at': 'DESC'})
    op.create_index('idx_tasks_user_created', 'tasks', ['user_id', 'created_at'])

def downgrade():
    op.drop_table('tasks')
    op.drop_table('users')
```

---

## Pydantic Schemas (Request/Response)

### User Schemas

```python
# schemas/user.py
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str  # Min 8 chars, validated in endpoint

class UserResponse(BaseModel):
    id: UUID
    email: str
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)
```

### Task Schemas

```python
# schemas/task.py
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    is_completed: Optional[bool] = None

class TaskResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

---

## Data Isolation Enforcement

### Query Pattern (CRITICAL)

**ALL task queries MUST include user_id filter**:

```python
# ✅ CORRECT: Filter by authenticated user
async def get_user_tasks(db: AsyncSession, user_id: UUID):
    result = await db.execute(
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.created_at.desc())
    )
    return result.scalars().all()

# ❌ WRONG: No user_id filter (security vulnerability!)
async def get_all_tasks(db: AsyncSession):
    result = await db.execute(select(Task))
    return result.scalars().all()
```

### Ownership Validation Pattern

**Before update/delete, verify ownership**:

```python
async def delete_task(db: AsyncSession, task_id: UUID, user_id: UUID):
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.delete(task)
    await db.commit()
```

---

## Summary

- **2 Entities**: User (authentication) and Task (todo items)
- **1:N Relationship**: One user owns many tasks
- **Security**: Strict data isolation via user_id filtering
- **Validation**: Pydantic schemas enforce constraints at API boundary
- **Indexes**: Optimized for user-specific queries with date ordering
- **Migration**: Alembic manages schema evolution

This data model supports all functional requirements from spec.md while maintaining constitutional principles of User Isolation and Security First.
