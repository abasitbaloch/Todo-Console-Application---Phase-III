# Tasks: Phase II Full-Stack Web Application

**Input**: Design documents from `/specs/001-fullstack-web-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT included in this task list as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below follow monorepo structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend directory structure with src/, tests/, alembic/ folders
- [X] T002 Create frontend directory structure with src/app/, src/components/, src/lib/ folders
- [X] T003 [P] Initialize backend Python project with pyproject.toml and dependencies (FastAPI, SQLModel, python-jose, asyncpg, Alembic, uvicorn)
- [X] T004 [P] Initialize frontend Node.js project with package.json and dependencies (Next.js 16+, React 18+, Better Auth, Tailwind CSS, lucide-react)
- [X] T005 [P] Create backend/.env.example with DATABASE_URL, JWT_SECRET, CORS_ORIGINS, ENVIRONMENT placeholders
- [X] T006 [P] Create frontend/.env.local.example with AUTH_SECRET, NEXT_PUBLIC_API_URL, BETTER_AUTH_URL placeholders
- [X] T007 [P] Create root package.json with concurrently script for parallel dev servers
- [X] T008 [P] Create .gitignore with backend/.env, frontend/.env.local, node_modules/, __pycache__/, .next/ entries

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 Create User model (SQLModel) in backend/src/models/user.py with id, email, hashed_password, created_at, updated_at fields
- [X] T010 Create Task model (SQLModel) in backend/src/models/task.py with id, user_id, title, description, is_completed, created_at, updated_at fields
- [X] T011 Create database configuration in backend/src/core/database.py with asyncpg engine, connection pooling (pool_size=5, max_overflow=10, pool_recycle=3600), and async session maker
- [X] T012 Create environment configuration in backend/src/core/config.py with DATABASE_URL, JWT_SECRET, JWT_ALGORITHM, CORS_ORIGINS settings
- [X] T013 Initialize Alembic in backend/ with alembic init alembic command
- [X] T014 Create initial database migration in backend/alembic/versions/ for users and tasks tables with indexes
- [X] T015 Create JWT verification utilities in backend/src/core/security.py with verify_token function using python-jose
- [X] T016 Create dependency injection helpers in backend/src/api/deps.py with get_db (database session) and get_current_user (JWT verification) functions
- [X] T017 Create FastAPI application in backend/src/main.py with CORS middleware, health check endpoint, and API router registration
- [X] T018 [P] Create TypeScript type definitions in frontend/src/lib/types.ts for User, Task, AuthResponse interfaces
- [X] T019 [P] Create API client utilities in frontend/src/lib/api.ts with fetch wrapper that injects Authorization header from Better Auth session

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration & Authentication (Priority: P1) 🎯 MVP

**Goal**: Enable users to register accounts, login, and access protected routes with JWT-based authentication

**Independent Test**: Register a new account, logout, login again, verify session persistence, attempt to access dashboard without auth (should redirect to login)

### Implementation for User Story 1

- [X] T020 [P] [US1] Create User Pydantic schemas in backend/src/schemas/user.py with UserCreate, UserResponse, UserLogin models
- [X] T021 [US1] Implement user registration endpoint POST /api/auth/register in backend/src/api/auth.py with email validation, password hashing (bcrypt), and duplicate email check
- [X] T022 [US1] Implement user login endpoint POST /api/auth/login in backend/src/api/auth.py with credential verification and JWT token issuance
- [X] T023 [US1] Implement get current user endpoint GET /api/auth/me in backend/src/api/auth.py with JWT verification dependency
- [X] T024 [P] [US1] Configure Better Auth in frontend/src/lib/auth.ts with shared secret (AUTH_SECRET), JWT settings (HS256, 24h expiration), and database configuration
- [X] T025 [P] [US1] Create Better Auth API route handler in frontend/src/app/api/auth/[...all]/route.ts
- [X] T026 [P] [US1] Create root layout in frontend/src/app/layout.tsx with Tailwind CSS imports and metadata
- [X] T027 [US1] Create landing/login page in frontend/src/app/page.tsx with AuthForm component for login
- [X] T028 [US1] Create registration page in frontend/src/app/register/page.tsx with AuthForm component for signup
- [X] T029 [US1] Create AuthForm component in frontend/src/components/AuthForm.tsx with email/password inputs, validation, and Better Auth integration
- [X] T030 [US1] Create protected route middleware in frontend/src/app/dashboard/layout.tsx that checks Better Auth session and redirects to login if unauthenticated
- [X] T031 [US1] Create placeholder dashboard page in frontend/src/app/dashboard/page.tsx with "Welcome" message and logout button

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can register, login, logout, and access protected dashboard.

---

## Phase 4: User Story 2 - Task Creation & Viewing (Priority: P2)

**Goal**: Enable authenticated users to create new tasks and view their complete task list ordered by creation date

**Independent Test**: Login, create multiple tasks with different titles and descriptions, verify they appear in list ordered by newest first, logout and login again to verify persistence

### Implementation for User Story 2

- [X] T032 [P] [US2] Create Task Pydantic schemas in backend/src/schemas/task.py with TaskCreate, TaskResponse models
- [X] T033 [US2] Implement get all tasks endpoint GET /api/tasks in backend/src/api/tasks.py with user_id filtering from JWT and ordering by created_at DESC
- [X] T034 [US2] Implement create task endpoint POST /api/tasks in backend/src/api/tasks.py with title/description validation and user_id from JWT
- [X] T035 [US2] Update dashboard page in frontend/src/app/dashboard/page.tsx to fetch tasks via Server Component and pass to TaskList
- [X] T036 [US2] Create TaskList component in frontend/src/components/TaskList.tsx as Client Component with state management for tasks array
- [X] T037 [US2] Create TaskForm component in frontend/src/components/TaskForm.tsx with title and description inputs for creating new tasks
- [X] T038 [US2] Implement create task handler in TaskList component that calls POST /api/tasks and updates local state optimistically
- [X] T039 [US2] Create TaskItem component in frontend/src/components/TaskItem.tsx to display individual task with title, description, and completion status

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Users can authenticate and manage a basic task list with create and view operations.

---

## Phase 5: User Story 3 - Task Management Operations (Priority: P3)

**Goal**: Enable users to update task details, mark tasks as complete/incomplete, and delete tasks

**Independent Test**: Create a task, edit its title/description, mark it complete, unmark it, delete it, verify all operations work without page refresh

### Implementation for User Story 3

- [X] T040 [P] [US3] Create TaskUpdate Pydantic schema in backend/src/schemas/task.py with optional title, description, is_completed fields
- [X] T041 [US3] Implement get single task endpoint GET /api/tasks/{task_id} in backend/src/api/tasks.py with ownership validation (403 if user_id mismatch)
- [X] T042 [US3] Implement update task endpoint PUT /api/tasks/{task_id} in backend/src/api/tasks.py with ownership validation and field updates
- [X] T043 [US3] Implement delete task endpoint DELETE /api/tasks/{task_id} in backend/src/api/tasks.py with ownership validation
- [X] T044 [US3] Add edit mode state and form to TaskItem component in frontend/src/components/TaskItem.tsx with inline editing for title and description
- [X] T045 [US3] Implement update task handler in TaskItem component that calls PUT /api/tasks/{task_id} and updates local state
- [X] T046 [US3] Add completion checkbox to TaskItem component with handler that calls PUT /api/tasks/{task_id} with is_completed toggle
- [X] T047 [US3] Add delete button to TaskItem component with confirmation and handler that calls DELETE /api/tasks/{task_id} and removes from local state
- [X] T048 [US3] Add visual styling for completed tasks in TaskItem component (strikethrough text, different background color)

**Checkpoint**: All user stories (1, 2, 3) should now be independently functional. Users have complete CRUD operations on tasks.

---

## Phase 6: User Story 4 - Responsive User Interface (Priority: P4)

**Goal**: Ensure interface works seamlessly on mobile (320px+) and desktop (1920px+) devices with polished visual design

**Independent Test**: Access application on mobile device, verify layout adapts and all features work, resize browser window from 320px to 1920px and verify smooth responsive behavior

### Implementation for User Story 4

- [X] T049 [P] [US4] Configure Tailwind CSS in frontend/tailwind.config.ts with responsive breakpoints and custom theme colors
- [X] T050 [P] [US4] Create global styles in frontend/src/app/globals.css with Tailwind imports and custom CSS variables for consistent spacing
- [X] T051 [US4] Add responsive layout utilities to dashboard page in frontend/src/app/dashboard/page.tsx with mobile-first grid/flex layouts
- [X] T052 [US4] Add responsive styling to TaskList component with mobile-friendly spacing and touch-friendly tap targets (min 44px)
- [X] T053 [US4] Add responsive styling to TaskItem component with mobile layout (stacked) and desktop layout (horizontal)
- [X] T054 [US4] Add responsive styling to TaskForm component with full-width inputs on mobile and constrained width on desktop
- [X] T055 [US4] Add responsive styling to AuthForm component with mobile-optimized form layout
- [X] T056 [US4] Add loading states to all async operations (spinners, disabled buttons) in TaskList and TaskItem components
- [X] T057 [US4] Add error message display to TaskList component for failed API calls with user-friendly messages
- [X] T058 [US4] Add success feedback for task operations (toast notifications or inline messages) in TaskList component
- [X] T059 [US4] Add hover states and focus indicators to all interactive elements (buttons, inputs, checkboxes) for accessibility

**Checkpoint**: All user stories should now be independently functional with polished, responsive UI across all device sizes.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final documentation

- [X] T060 [P] Create backend README.md in backend/ with setup instructions, environment variables, migration commands, and API documentation links
- [X] T061 [P] Create frontend README.md in frontend/ with setup instructions, environment variables, development server commands, and build instructions
- [X] T062 [P] Update root README.md with project overview, monorepo structure explanation, quick start guide, and links to backend/frontend READs
- [X] T063 [P] Add comprehensive error handling to all backend endpoints with consistent error response format (detail field)
- [X] T064 [P] Add input sanitization to all backend endpoints to prevent XSS and SQL injection attacks
- [X] T065 [P] Add request validation error messages to frontend forms with inline field-level error display
- [X] T066 Verify all API endpoints return correct HTTP status codes (200, 201, 400, 401, 403, 404, 500) per contracts/
- [X] T067 Run quickstart.md validation tests (health check, registration, login, auth testing, CRUD operations, data isolation)
- [X] T068 Verify constitution compliance (all 7 principles) and document any deviations in plan.md Complexity Tracking

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - No dependencies on other stories (independent)
  - User Story 3 (P3): Can start after Foundational - No dependencies on other stories (independent)
  - User Story 4 (P4): Can start after Foundational - Enhances all stories but doesn't block them
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independently testable (requires auth from US1 for testing, but implementation is independent)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independently testable (builds on US2 endpoints but can be implemented in parallel)
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Enhances all stories with responsive design

### Within Each User Story

- Models and schemas before endpoints
- Backend endpoints before frontend components
- Core components before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003-T008)
- All Foundational tasks marked [P] can run in parallel within their dependencies (T018-T019)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within User Story 1: T020, T024, T025, T026 can run in parallel
- Within User Story 2: T032, T035 can run in parallel after T033-T034 complete
- Within User Story 3: T040, T041 can run in parallel
- Within User Story 4: All tasks marked [P] can run in parallel (T049-T050)
- All Polish tasks marked [P] can run in parallel (T060-T065)

---

## Parallel Example: User Story 1 (Authentication)

```bash
# Launch parallelizable tasks for User Story 1 together:
Task T020: "Create User Pydantic schemas in backend/src/schemas/user.py"
Task T024: "Configure Better Auth in frontend/src/lib/auth.ts"
Task T025: "Create Better Auth API route handler in frontend/src/app/api/auth/[...all]/route.ts"
Task T026: "Create root layout in frontend/src/app/layout.tsx"

# Then proceed with sequential tasks:
Task T021: "Implement user registration endpoint" (depends on T020)
Task T022: "Implement user login endpoint" (depends on T020, T021)
Task T023: "Implement get current user endpoint" (depends on T020)
Task T027: "Create landing/login page" (depends on T024, T026)
Task T028: "Create registration page" (depends on T024, T026)
Task T029: "Create AuthForm component" (depends on T024)
Task T030: "Create protected route middleware" (depends on T024)
Task T031: "Create placeholder dashboard page" (depends on T030)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T019) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T020-T031)
4. **STOP and VALIDATE**: Test User Story 1 independently per quickstart.md
5. Deploy/demo if ready

**MVP Deliverable**: Users can register, login, logout, and access protected dashboard. This validates the authentication architecture and monorepo setup.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Auth) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (Task Create/View) → Test independently → Deploy/Demo
4. Add User Story 3 (Task Management) → Test independently → Deploy/Demo
5. Add User Story 4 (Responsive UI) → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T019)
2. Once Foundational is done:
   - Developer A: User Story 1 (T020-T031)
   - Developer B: User Story 2 (T032-T039) - can start in parallel
   - Developer C: User Story 3 (T040-T048) - can start in parallel
   - Developer D: User Story 4 (T049-T059) - can start in parallel
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group with Task ID reference (e.g., "Implementing T020")
- Stop at any checkpoint to validate story independently
- Tests are NOT included as they were not requested in the specification
- All tasks follow strict checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
- Total: 68 tasks across 7 phases
- MVP scope: Phases 1-3 (T001-T031) = 31 tasks for authentication foundation
