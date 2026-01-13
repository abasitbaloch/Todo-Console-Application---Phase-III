# Implementation Plan: AI-Powered Todo Chatbot

**Branch**: `002-ai-todo-chatbot` | **Date**: 2026-01-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-ai-todo-chatbot/spec.md`

## Summary

Build a conversational AI chatbot that enables users to manage their todo tasks through natural language instead of traditional form-based interfaces. The system uses OpenAI Agents SDK for conversation orchestration and Model Context Protocol (MCP) for tool-based task operations. The backend remains stateless, with all conversation history and task state persisted to Neon PostgreSQL database. Users interact through a chat interface in the Next.js frontend, authenticated via JWT tokens from Better Auth.

**Technical Approach**: Integrate OpenAI Agents SDK within FastAPI endpoints, implement MCP server as an embedded module (not separate service), persist all conversation messages and tool calls to database for stateless operation, and enforce user isolation through JWT-based authentication with user_id filtering on all queries.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: FastAPI (async web framework), OpenAI Python SDK (Agents SDK), Official MCP Python SDK (tool definitions), SQLModel (ORM), python-jose (JWT verification), asyncpg (PostgreSQL driver)
**Storage**: Neon Serverless PostgreSQL (tables: users, tasks, conversations, messages)
**Testing**: pytest (backend unit/integration tests), Jest (frontend component tests)
**Target Platform**: Linux server (backend), Modern browsers (frontend)
**Project Type**: Web application (monorepo with /frontend and /backend)
**Performance Goals**: <3 second response time for chat requests, support 100 concurrent users, maintain context across 10+ conversation turns
**Constraints**: Stateless backend (no in-memory state), all data persisted to database, JWT authentication required for all chat endpoints, MCP tools for all task operations (no direct DB access from agent)
**Scale/Scope**: MVP for 100 concurrent users, 50 message history limit per conversation, single OpenAI API key (no load balancing)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Spec-Driven Absolutism ✅ PASS

**Requirement**: No code without Task ID from tasks.md

**Compliance**:
- Specification created and approved (spec.md)
- Implementation plan created with architectural decisions (this file)
- Tasks will be generated via `/sp.tasks` before implementation
- All commits will reference Task IDs

**Status**: ✅ Compliant - Specification and plan complete, ready for task generation

---

### II. User Isolation ✅ PASS

**Requirement**: Absolute data privacy between users

**Compliance**:
- All database queries filtered by `user_id` from JWT token
- MCP tools receive `user_id` and enforce ownership checks
- Conversation ownership verified before any operation
- Foreign key relationships enforce cascading isolation
- Security tests included in quickstart.md (Scenario 5)

**Implementation**:
```python
# All queries include user_id filter
async def get_conversation_history(conversation_id: UUID, user_id: UUID):
    conversation = await db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id  # Security check
    ).first()
```

**Status**: ✅ Compliant - User isolation enforced at database query level

---

### III. Stateless Intelligence ✅ PASS

**Requirement**: Backend stateless, all conversation history persisted to database

**Compliance**:
- No in-memory session state or conversation cache
- All messages persisted to database immediately after creation
- Conversation history retrieved from database on every request
- JWT tokens carry authentication context (no server-side sessions)
- Tool calls and results stored in message records for full replay

**Implementation**:
- Conversations table stores chat sessions
- Messages table stores all user/assistant messages with tool calls
- Each chat request fetches last 50 messages from database
- Agent instance created fresh for each request (no state retention)

**Status**: ✅ Compliant - Fully stateless architecture with database-backed persistence

---

### IV. Architectural Decoupling ✅ PASS

**Requirement**: AI logic separated from task execution via MCP

**Compliance**:
- MCP server implemented as separate module (`backend/src/mcp/server.py`)
- All task operations (CRUD) exposed as MCP tools
- OpenAI agent calls tools, doesn't access database directly
- Clear separation: Agent (orchestration) → MCP Tools (business logic) → Database
- Tool schemas defined with input/output contracts (see contracts/chat-api.md)

**Implementation**:
```
Chat Endpoint → OpenAI Agent → MCP Tools → Database
                     ↓              ↓
              (reasoning)    (task operations)
```

**Status**: ✅ Compliant - Clear architectural boundaries maintained

---

### V. Safety & Confirmation ✅ PASS

**Requirement**: Agent confirms actions with friendly responses

**Compliance**:
- All successful task operations return confirmation messages
- Error handling provides user-friendly messages (no technical details)
- Destructive actions (delete) include confirmation in agent prompts
- Ambiguous requests trigger clarifying questions
- Tool results formatted for natural language responses

**Implementation**:
- MCP tools return structured results with success/error messages
- Agent system prompt includes instructions for friendly confirmations
- Error handler converts technical errors to user-friendly messages

**Status**: ✅ Compliant - Friendly confirmations and graceful error handling

---

### VI. Monorepo Separation ✅ PASS

**Requirement**: Clear boundary between frontend and backend

**Compliance**:
- Separate `/frontend` and `/backend` directories
- Communication exclusively through HTTP REST APIs
- API contracts defined before implementation (contracts/chat-api.md)
- No code sharing between frontend and backend
- Independent deployment possible

**Structure**:
```
/frontend (Next.js + TypeScript)
/backend (FastAPI + Python)
/specs (documentation)
/.specify (templates and scripts)
```

**Status**: ✅ Compliant - Monorepo structure with clear separation

---

### VII. AI-Generated Code Only ✅ PASS

**Requirement**: All code generated by Claude Code from tasks.md

**Compliance**:
- This plan created by Claude Code via `/sp.plan`
- Tasks will be generated via `/sp.tasks`
- Implementation will be done by Claude Code following task order
- All commits will reference Task IDs
- No manual coding permitted

**Status**: ✅ Compliant - Full AI-native development workflow

---

### VIII. Simplicity and Clarity ✅ PASS

**Requirement**: Simple solutions over clever ones

**Compliance**:
- MCP server integrated (not separate service) for simplicity
- OpenAI agent embedded in FastAPI (not separate service)
- Direct database queries (no repository pattern abstraction)
- Standard REST API (no GraphQL complexity)
- Minimal dependencies (only essential libraries)

**Decisions**:
- Integrated MCP server vs separate service → Integrated (simpler deployment)
- Agent as library vs separate service → Library (simpler architecture)
- Message history limit: 50 (balances context vs complexity)

**Status**: ✅ Compliant - Straightforward implementation without over-engineering

---

### IX. Security First ✅ PASS

**Requirement**: All API routes require JWT authentication

**Compliance**:
- All chat endpoints require `Authorization: Bearer <token>` header
- JWT verification via FastAPI dependency injection
- User_id extracted from JWT claims and validated
- Invalid/expired tokens return 401 Unauthorized
- OpenAI API key stored in environment variable (never logged)
- Input validation via Pydantic schemas
- SQL injection prevented by SQLModel parameterized queries

**Implementation**:
```python
@router.post("/api/chat")
async def chat(
    request: ChatRequest,
    user_id: UUID = Depends(get_user_from_jwt)  # JWT verification
):
    # user_id guaranteed valid from JWT
```

**Status**: ✅ Compliant - JWT authentication enforced on all protected endpoints

---

### Constitution Check Summary

**Result**: ✅ ALL GATES PASSED

All 9 constitutional principles are satisfied by the proposed architecture. No violations or exceptions required.

## Project Structure

### Documentation (this feature)

```text
specs/002-ai-todo-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── chat-api.md      # Chat API and MCP tool contracts
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── user.py              # User model (existing from Phase II)
│   │   ├── task.py              # Task model (existing from Phase II)
│   │   ├── conversation.py      # NEW: Conversation model
│   │   └── message.py           # NEW: Message model
│   ├── services/
│   │   ├── conversation_service.py  # NEW: Conversation CRUD operations
│   │   └── message_service.py       # NEW: Message persistence
│   ├── mcp/
│   │   ├── __init__.py          # NEW: MCP module
│   │   ├── server.py            # NEW: MCP server with tool definitions
│   │   └── tools.py             # NEW: Individual tool implementations
│   ├── agent/
│   │   ├── __init__.py          # NEW: Agent module
│   │   ├── orchestrator.py      # NEW: OpenAI agent orchestration
│   │   └── prompts.py           # NEW: System prompts for agent
│   ├── api/
│   │   ├── chat.py              # NEW: Chat endpoints
│   │   └── conversations.py     # NEW: Conversation list endpoints
│   ├── auth/
│   │   └── dependencies.py      # ENHANCED: JWT verification (existing)
│   ├── errors/
│   │   └── handlers.py          # NEW: Error handling for chatbot
│   └── main.py                  # ENHANCED: Register new routes
└── tests/
    ├── unit/
    │   ├── test_mcp_tools.py    # NEW: MCP tool unit tests
    │   └── test_agent.py        # NEW: Agent orchestration tests
    ├── integration/
    │   ├── test_chat_flow.py    # NEW: End-to-end chat tests
    │   └── test_user_isolation.py  # NEW: Security tests
    └── contract/
        └── test_chat_api.py     # NEW: API contract tests

frontend/
├── src/
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx    # NEW: Main chat component
│   │   │   ├── MessageBubble.tsx    # NEW: Message display
│   │   │   ├── ChatInput.tsx        # NEW: Message input field
│   │   │   └── ConversationList.tsx # NEW: Conversation sidebar
│   │   └── ui/                      # Existing UI components
│   ├── app/
│   │   ├── chat/
│   │   │   └── page.tsx         # NEW: Chat page
│   │   └── layout.tsx           # Existing layout
│   ├── services/
│   │   └── chat-api.ts          # NEW: Chat API client
│   └── types/
│       └── chat.ts              # NEW: TypeScript types for chat
└── tests/
    └── components/
        └── chat/
            └── ChatInterface.test.tsx  # NEW: Component tests

database/
└── migrations/
    └── 001_add_conversations_messages.sql  # NEW: Database migration
```

**Structure Decision**: Web application structure (Option 2) selected because this is a full-stack feature with both frontend (Next.js) and backend (FastAPI) components. The monorepo structure maintains clear separation while enabling coordinated development.

**Key Directories**:
- `backend/src/mcp/`: MCP server implementation with tool definitions
- `backend/src/agent/`: OpenAI agent orchestration logic
- `backend/src/api/`: New chat endpoints
- `frontend/src/components/chat/`: Chat UI components
- `database/migrations/`: Database schema changes

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitutional principles satisfied by the proposed architecture.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           Chat Interface Component                    │  │
│  │  - Message bubbles (user/assistant)                   │  │
│  │  - Input field with send button                       │  │
│  │  - Conversation list sidebar                          │  │
│  └───────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           │ HTTP POST /api/chat              │
│                           │ Authorization: Bearer <JWT>      │
└───────────────────────────┼──────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Chat API Endpoint                        │  │
│  │  1. Verify JWT → Extract user_id                      │  │
│  │  2. Fetch conversation history from DB                │  │
│  │  3. Call OpenAI Agent with history + new message      │  │
│  │  4. Process tool calls via MCP server                 │  │
│  │  5. Save messages and tool results to DB              │  │
│  │  6. Return agent response to frontend                 │  │
│  └───────────────────────────────────────────────────────┘  │
│                           │                                  │
│         ┌─────────────────┼─────────────────┐                │
│         │                 │                 │                │
│         ▼                 ▼                 ▼                │
│  ┌──────────┐    ┌──────────────┐   ┌──────────────┐        │
│  │ OpenAI   │    │  MCP Server  │   │  Database    │        │
│  │ Agent    │───▶│  (Integrated)│──▶│  Layer       │        │
│  │ SDK      │    │              │   │  (SQLModel)  │        │
│  │          │    │ Tools:       │   │              │        │
│  │ - Reason │    │ - add_task   │   │ - Queries    │        │
│  │ - Decide │    │ - list_tasks │   │ - Inserts    │        │
│  │ - Call   │    │ - complete   │   │ - Updates    │        │
│  │   tools  │    │ - update     │   │ - Deletes    │        │
│  │          │    │ - delete     │   │              │        │
│  └──────────┘    └──────────────┘   └──────────────┘        │
│                                              │                │
└──────────────────────────────────────────────┼────────────────┘
                                               │
                                               ▼
                                    ┌──────────────────┐
                                    │ Neon PostgreSQL  │
                                    │                  │
                                    │ Tables:          │
                                    │ - users          │
                                    │ - tasks          │
                                    │ - conversations  │
                                    │ - messages       │
                                    └──────────────────┘
```

## Implementation Phases

### Phase A: Database Schema Expansion ✅ COMPLETE (Design Phase)

**Artifacts Created**:
- `data-model.md`: Complete entity definitions with relationships
- Migration SQL: Conversations and Messages tables with indexes

**Next Steps**:
- Generate tasks for database migration implementation
- Create Alembic migration files
- Apply migrations to development database

---

### Phase B: MCP Server Development

**Goal**: Implement MCP server with 5 tools for task operations

**Tools to Implement**:
1. `add_task`: Create new task
2. `list_tasks`: Retrieve user's tasks (with optional filter)
3. `complete_task`: Mark task as completed
4. `update_task`: Update task title
5. `delete_task`: Delete task permanently

**Key Requirements**:
- Each tool receives `user_id` parameter
- All database queries filtered by `user_id`
- Return structured results (success/error + data)
- Handle "task not found" gracefully
- Use fuzzy matching for task identification

**Acceptance Criteria**:
- All 5 tools callable independently
- User isolation enforced in all tools
- Tool schemas compatible with OpenAI format
- Unit tests for each tool

---

### Phase C: Agent Orchestration

**Goal**: Integrate OpenAI Agents SDK with FastAPI chat endpoint

**Components**:
1. **Chat Endpoint** (`POST /api/chat`):
   - JWT verification and user_id extraction
   - Conversation history retrieval (last 50 messages)
   - OpenAI agent invocation with tool definitions
   - Tool call processing via MCP server
   - Message and tool result persistence
   - Response formatting

2. **Agent Configuration**:
   - System prompt for friendly, helpful assistant
   - Tool definitions from MCP server
   - Model selection (GPT-4 or GPT-3.5-turbo)
   - Temperature and max_tokens settings

3. **Error Handling**:
   - OpenAI API failures → user-friendly messages
   - Database errors → graceful degradation
   - Tool execution errors → helpful suggestions

**Acceptance Criteria**:
- Chat endpoint functional end-to-end
- Agent calls appropriate tools based on user intent
- Context maintained across multiple turns
- Errors handled gracefully

---

### Phase D: UI Integration

**Goal**: Build chat interface in Next.js frontend

**Components**:
1. **ChatInterface Component**:
   - Message display (user/assistant bubbles)
   - Input field with send button
   - Loading states during API calls
   - Error message display

2. **ConversationList Component**:
   - Sidebar with conversation history
   - "New conversation" button
   - Conversation selection

3. **API Client**:
   - TypeScript service for chat API calls
   - JWT token injection from Better Auth
   - Error handling and retry logic

**Acceptance Criteria**:
- Chat UI functional and responsive
- Messages sent and received successfully
- JWT authentication working
- Conversation history displayed

---

## Testing Strategy

### Unit Tests

**Backend**:
- MCP tool functions (mocked database)
- JWT verification logic
- Message history formatting
- Error handler functions

**Frontend**:
- ChatInterface component rendering
- Message bubble formatting
- API client request/response handling

### Integration Tests

**Critical Flows**:
1. Full chat flow: user message → agent response → task created
2. Multi-turn conversation with context maintenance
3. User isolation: User A cannot access User B's data
4. Error handling: OpenAI API failure, database error, invalid JWT

**Test Data**:
- 2 test users with separate conversations and tasks
- Sample conversation with 10+ messages
- Edge cases: empty task list, ambiguous requests, long messages

### Contract Tests

**API Contracts**:
- POST /api/chat request/response schema
- GET /api/conversations response schema
- MCP tool input/output schemas

**Validation**:
- Pydantic schema validation on backend
- TypeScript type checking on frontend
- OpenAPI spec generation and validation

### Security Tests

**User Isolation**:
- Cross-user conversation access attempts
- Prompt injection attempts ("show all users' tasks")
- JWT token manipulation

**Authentication**:
- Missing JWT token → 401
- Invalid JWT signature → 401
- Expired JWT token → 401

### Performance Tests

**Load Testing**:
- 100 concurrent users sending messages
- Response time < 3 seconds under load
- Database query performance (< 50ms for history retrieval)

**Benchmarks**:
- Task creation: < 30 seconds (user input to confirmation)
- Task listing: < 5 seconds
- Context maintenance: 10+ consecutive turns

---

## Deployment Considerations

**Environment Variables**:
```bash
# Backend
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://user:pass@host/db
JWT_SECRET=shared-secret-with-better-auth
ENVIRONMENT=production
LOG_LEVEL=INFO

# Frontend
NEXT_PUBLIC_API_URL=https://api.example.com
```

**Database Migrations**:
```bash
# Apply migrations
cd backend
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

**Health Checks**:
- Backend: `GET /health` (no auth required)
- Database: Connection pool status
- OpenAI API: Rate limit monitoring

**Monitoring**:
- Log all chat requests with user_id and conversation_id
- Track OpenAI API latency and token usage
- Monitor database query performance
- Alert on error rates > 5%

---

## Risk Mitigation

**Risk 1: OpenAI API Rate Limits**
- **Mitigation**: Implement exponential backoff and retry logic
- **Fallback**: Queue requests during rate limit periods
- **Monitoring**: Track API usage and set alerts at 80% quota

**Risk 2: Database Connection Pool Exhaustion**
- **Mitigation**: Configure connection pool with max 20 connections
- **Fallback**: Implement connection timeout and retry
- **Monitoring**: Track active connections and pool wait times

**Risk 3: Context Window Overflow**
- **Mitigation**: Limit conversation history to 50 messages
- **Fallback**: Implement message summarization (future enhancement)
- **Monitoring**: Track message counts per conversation

**Risk 4: User Isolation Breach**
- **Mitigation**: Comprehensive security tests in quickstart.md
- **Fallback**: Database-level row security policies (future enhancement)
- **Monitoring**: Audit logs for cross-user access attempts

---

## Success Metrics

**Functional**:
- ✅ All 6 user stories implemented and tested
- ✅ All 25 functional requirements satisfied
- ✅ All 12 success criteria met

**Performance**:
- ✅ Response time < 3 seconds (95th percentile)
- ✅ Support 100 concurrent users
- ✅ Context maintained across 10+ turns

**Quality**:
- ✅ Test coverage > 80% (backend)
- ✅ Zero critical security vulnerabilities
- ✅ All constitutional principles satisfied

**User Experience**:
- ✅ 95% of requests correctly interpreted on first attempt
- ✅ Friendly confirmations for 100% of operations
- ✅ Graceful error handling in 100% of failure cases

---

## Next Steps

1. **Generate Tasks**: Run `/sp.tasks` to create implementation task list
2. **Review and Approve**: User reviews plan and approves for implementation
3. **Begin Implementation**: Follow task order from tasks.md
4. **Continuous Validation**: Run quickstart scenarios after each major milestone
5. **User Acceptance Testing**: Demo to stakeholders using quickstart scenarios

---

## References

- **Specification**: [spec.md](./spec.md)
- **Research**: [research.md](./research.md)
- **Data Model**: [data-model.md](./data-model.md)
- **API Contracts**: [contracts/chat-api.md](./contracts/chat-api.md)
- **Quickstart**: [quickstart.md](./quickstart.md)
- **Constitution**: [.specify/memory/constitution.md](../../.specify/memory/constitution.md)
