---
id: 002
title: Phase III Implementation Planning
stage: plan
date: 2026-01-11
surface: agent
model: claude-sonnet-4-5-20250929
feature: ai-todo-chatbot
branch: 002-ai-todo-chatbot
user: user
command: /sp.plan
labels: ["planning", "architecture", "phase-iii", "openai-agents", "mcp", "stateless", "design"]
links:
  spec: specs/002-ai-todo-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-ai-todo-chatbot/plan.md
  - specs/002-ai-todo-chatbot/research.md
  - specs/002-ai-todo-chatbot/data-model.md
  - specs/002-ai-todo-chatbot/contracts/chat-api.md
  - specs/002-ai-todo-chatbot/quickstart.md
tests:
  - none
---

## Prompt

Phase III: AI-Powered Todo Chatbot

**Goal:** Implement a stateless agentic architecture using the OpenAI Agents SDK and Model Context Protocol (MCP) to manage the Todo database via natural language.

### **1. Architecture Sketch**
* **Frontend:** ChatKit UI component sends conversation ID and messages to the backend.
* **Backend (FastAPI):** Acts as the orchestrator. It fetches history, runs the agent, and persists responses.
* **AI Layer:** OpenAI Agents SDK processes the "reasoning" and decides which tool to call.
* **MCP Server:** A separate or integrated service that exposes CRUD operations as "Tools" (`add_task`, `list_tasks`, etc.).
* **Database (Neon DB):** Shared source of truth for Tasks, Conversations, and Messages.

### **2. Key Technical Decisions**
| Decision | Option | Trade-off |
| :--- | :--- | :--- |
| **Tool Protocol** | Official MCP SDK | **Pro:** Standardization and compatibility with Claude Code. **Con:** Slightly more boilerplate than direct API calls. |
| **State Management** | DB-backed Stateless | **Pro:** High scalability and persistence across server restarts. **Con:** Requires DB fetch/save on every turn. |
| **Agent SDK** | OpenAI Agents SDK | **Pro:** Native support for tool calling and run loops. **Con:** Tightly coupled to OpenAI ecosystem. |

### **3. Implementation Roadmap**
* **Phase A: Database Schema Expansion**
    * Add `Conversation` and `Message` models (SQLModel).
    * Link all new models to `user_id` for multi-tenant security.
* **Phase B: MCP Server Development**
    * Implement `FastMCP` or standard MCP tools for CRUD operations.
    * Ensure each tool accepts `user_id` to enforce data isolation.
* **Phase C: Agent Orchestration**
    * Create a Chat endpoint `POST /api/chat`.
    * Logic: Get history → Call Agent → Process MCP tools → Save & Return.
* **Phase D: UI Integration**
    * Connect OpenAI ChatKit to the new `/api/chat` endpoint.
    * Secure the connection using existing Phase II JWT tokens.

### **4. Testing & Quality Strategy**
* **Context Retrieval Check:** Verify the agent remembers a task mentioned 3 messages ago.
* **Tool Validation:** Ensure `delete_task` via AI actually deletes the record in Neon DB.
* **Security Check:** Verify User A cannot access User B's tasks through a natural language prompt.

## Response snapshot

Created comprehensive implementation plan for Phase III AI-Powered Todo Chatbot with complete architectural design, research, data models, API contracts, and validation strategy.

**Planning Artifacts Created:**

1. **research.md** (Phase 0):
   - Resolved 5 technical unknowns through research
   - Q1: OpenAI Agents SDK integration → Embedded within FastAPI endpoints
   - Q2: MCP server architecture → Integrated module (not separate service)
   - Q3: Conversation history storage → Database-backed with 50 message limit
   - Q4: JWT verification → FastAPI dependency injection pattern
   - Q5: Error handling → Three-tier approach (MCP/OpenAI/Application)
   - Technology stack finalized: Python 3.13+, FastAPI, OpenAI SDK, MCP SDK, SQLModel

2. **data-model.md** (Phase 1):
   - 4 entities defined: User (existing), Task (existing), Conversation (new), Message (new)
   - Database migration SQL for conversations and messages tables
   - 6 indexes for performance optimization
   - Data access patterns documented with code examples
   - User isolation enforcement strategy detailed

3. **contracts/chat-api.md** (Phase 1):
   - 3 HTTP endpoints: POST /api/chat, GET /api/conversations, GET /api/conversations/{id}
   - 5 MCP tool contracts: add_task, list_tasks, complete_task, update_task, delete_task
   - Request/response schemas with TypeScript types
   - Error handling and security considerations
   - Contract test requirements

4. **quickstart.md** (Phase 1):
   - 6 test scenarios covering all user stories
   - Scenario 1: Create task via natural language (P1 MVP)
   - Scenario 2: View tasks (P2)
   - Scenario 3: Complete task (P3)
   - Scenario 4: Multi-turn context (P6)
   - Scenario 5: User isolation security test
   - Scenario 6: Error handling validation
   - Performance benchmarks and troubleshooting guide

5. **plan.md** (Final):
   - Complete implementation plan with architecture diagram
   - Constitution check: All 9 principles PASSED
   - Project structure with file-level detail
   - 4 implementation phases (A: Database, B: MCP, C: Agent, D: UI)
   - Testing strategy (unit, integration, contract, security, performance)
   - Deployment considerations and risk mitigation
   - Success metrics aligned with specification

**Key Architectural Decisions:**

1. **Integrated MCP Server**: Embedded within FastAPI backend (not separate service) for simplicity and reduced deployment complexity

2. **Stateless Backend**: No in-memory state; all conversation history and messages persisted to database and retrieved on every request

3. **OpenAI Agent as Library**: Embedded within FastAPI endpoints (not separate service) for unified error handling and authentication

4. **50 Message History Limit**: Balances context quality with token costs and latency

5. **JWT-based Authentication**: FastAPI dependency injection for user_id extraction and validation

**Constitution Compliance:**
- ✅ I. Spec-Driven Absolutism: Spec and plan complete, ready for tasks
- ✅ II. User Isolation: All queries filtered by user_id from JWT
- ✅ III. Stateless Intelligence: Database-backed persistence, no in-memory state
- ✅ IV. Architectural Decoupling: MCP tools separate from agent orchestration
- ✅ V. Safety & Confirmation: Friendly messages and graceful error handling
- ✅ VI. Monorepo Separation: Clear frontend/backend boundaries
- ✅ VII. AI-Generated Code Only: Full AI-native workflow
- ✅ VIII. Simplicity and Clarity: Integrated services, minimal abstractions
- ✅ IX. Security First: JWT authentication on all protected endpoints

**Technical Stack Summary:**
- Backend: Python 3.13+, FastAPI, OpenAI SDK, MCP SDK, SQLModel, python-jose, asyncpg
- Frontend: Next.js 16+, TypeScript, React, Tailwind CSS, Better Auth
- Database: Neon PostgreSQL (users, tasks, conversations, messages)
- Testing: pytest (backend), Jest (frontend)

**Performance Targets:**
- Response time: < 3 seconds
- Concurrent users: 100
- Context maintenance: 10+ turns
- Correct interpretation: 95% on first attempt

## Outcome

- ✅ Impact: Complete implementation plan with 5 design artifacts (plan, research, data-model, contracts, quickstart), architecture diagram, constitution compliance verification, and detailed testing strategy
- 🧪 Tests: Quickstart guide with 6 test scenarios covering all user stories and security requirements
- 📁 Files: 5 files created (plan.md, research.md, data-model.md, contracts/chat-api.md, quickstart.md)
- 🔁 Next prompts: /sp.tasks (generate implementation tasks), user approval of plan before implementation
- 🧠 Reflection: Planning phase successfully resolved all technical unknowns through systematic research. Key decision to integrate MCP server and OpenAI agent within FastAPI (rather than separate services) significantly simplifies architecture while maintaining constitutional compliance. All 9 constitutional principles satisfied without exceptions. Database schema expansion adds 2 new tables (conversations, messages) with proper indexing for performance. Ready for task generation and implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully with all artifacts generated and constitution check passed
- Graders run and results (PASS/FAIL): PASS - All constitutional gates passed (9/9), technical unknowns resolved through research, data model complete with relationships and indexes, API contracts defined with schemas, quickstart scenarios cover all user stories, architecture diagram clearly shows component interactions
- Prompt variant (if applicable): Standard /sp.plan command execution with user-provided architecture sketch and technical decisions
- Next experiment (smallest change to try): Consider creating an Architecture Decision Record (ADR) for the "Integrated MCP Server" decision, as it's architecturally significant with clear alternatives (separate service) and trade-offs (simplicity vs independent scaling)
