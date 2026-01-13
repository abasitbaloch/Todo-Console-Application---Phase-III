---

description: "Task list for AI-Powered Todo Chatbot implementation"
---

# Tasks: AI-Powered Todo Chatbot

**Input**: Design documents from `/specs/002-ai-todo-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the feature specification, so test tasks are not included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below follow monorepo structure from plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend directory structure per implementation plan (backend/src/models, backend/src/services, backend/src/mcp, backend/src/agent, backend/src/api, backend/src/auth, backend/src/errors)
- [ ] T002 Create frontend directory structure per implementation plan (frontend/src/components/chat, frontend/src/app/chat, frontend/src/services, frontend/src/types)
- [ ] T003 [P] Install backend dependencies in backend/requirements.txt (fastapi, openai, mcp, sqlmodel, python-jose, asyncpg, alembic, uvicorn)
- [ ] T004 [P] Install frontend dependencies in frontend/package.json (next, react, typescript, tailwindcss)
- [ ] T005 [P] Configure backend environment variables in backend/.env.example (OPENAI_API_KEY, DATABASE_URL, JWT_SECRET, ENVIRONMENT, LOG_LEVEL)
- [ ] T006 [P] Configure frontend environment variables in frontend/.env.example (NEXT_PUBLIC_API_URL)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Create Conversation model in backend/src/models/conversation.py (SQLModel with id, user_id, created_at, updated_at)
- [ ] T008 Create Message model in backend/src/models/message.py (SQLModel with id, conversation_id, role, content, tool_calls, tool_results, created_at)
- [ ] T009 Create Alembic migration for conversations and messages tables in backend/migrations/001_add_conversations_messages.py
- [ ] T010 Apply database migration to create conversations and messages tables (alembic upgrade head)
- [ ] T011 [P] Create conversation service in backend/src/services/conversation_service.py (create_conversation, get_conversation_history, list_user_conversations)
- [ ] T012 [P] Create message service in backend/src/services/message_service.py (save_message, get_messages_by_conversation)
- [ ] T013 Create MCP server base class in backend/src/mcp/server.py (TodoMCPServer with tool registration and OpenAI-compatible tool definitions)
- [ ] T014 Create agent system prompts in backend/src/agent/prompts.py (friendly assistant prompt with tool usage instructions)
- [ ] T015 Create error handler for chatbot errors in backend/src/errors/handlers.py (ChatbotError, MCPToolError, OpenAIAPIError with user-friendly messages)
- [ ] T016 Enhance JWT verification dependency in backend/src/auth/dependencies.py (get_user_from_jwt function with FastAPI Depends)
- [ ] T017 Create chat API router in backend/src/api/chat.py (empty router, will be populated in user story phases)
- [ ] T018 Create conversations API router in backend/src/api/conversations.py (GET /api/conversations endpoint)
- [ ] T019 Register new routers in backend/src/main.py (include chat and conversations routers)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create Tasks via Natural Language (Priority: P1) 🎯 MVP

**Goal**: Enable users to create tasks through conversational interface

**Independent Test**: User can open chat interface, type "Add a task to buy groceries", and receive confirmation that the task was created. Task persists in database.

### Implementation for User Story 1

- [ ] T020 [P] [US1] Implement add_task MCP tool in backend/src/mcp/tools.py (accepts title and user_id, creates task in database, returns success with task details)
- [ ] T021 [US1] Register add_task tool in MCP server in backend/src/mcp/server.py (add tool definition with schema)
- [ ] T022 [US1] Create agent orchestrator in backend/src/agent/orchestrator.py (initialize OpenAI client, build messages from history, call agent with tools, process tool calls)
- [ ] T023 [US1] Implement POST /api/chat endpoint in backend/src/api/chat.py (verify JWT, fetch history, call agent, save messages, return response)
- [ ] T024 [US1] Create ChatRequest and ChatResponse Pydantic models in backend/src/api/chat.py (conversation_id, message fields with validation)
- [ ] T025 [P] [US1] Create chat types in frontend/src/types/chat.ts (ChatRequest, ChatResponse, Message, ToolCall TypeScript interfaces)
- [ ] T026 [P] [US1] Create chat API client in frontend/src/services/chat-api.ts (sendMessage function with JWT token injection)
- [ ] T027 [US1] Create ChatInterface component in frontend/src/components/chat/ChatInterface.tsx (main chat container with state management)
- [ ] T028 [P] [US1] Create MessageBubble component in frontend/src/components/chat/MessageBubble.tsx (display user/assistant messages with styling)
- [ ] T029 [P] [US1] Create ChatInput component in frontend/src/components/chat/ChatInput.tsx (input field with send button and loading state)
- [ ] T030 [US1] Create chat page in frontend/src/app/chat/page.tsx (integrate ChatInterface component with authentication check)
- [ ] T031 [US1] Add error handling for OpenAI API failures in backend/src/agent/orchestrator.py (catch OpenAIError, raise ChatbotError with user-friendly message)
- [ ] T032 [US1] Add error handling for MCP tool failures in backend/src/mcp/tools.py (handle database errors, return structured error responses)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can create tasks via natural language.

---

## Phase 4: User Story 2 - View and List Tasks (Priority: P2)

**Goal**: Enable users to view their task list through conversation

**Independent Test**: User can type "Show me my tasks" and receive a formatted list of all their tasks. Only authenticated user's tasks shown.

### Implementation for User Story 2

- [ ] T033 [P] [US2] Implement list_tasks MCP tool in backend/src/mcp/tools.py (accepts user_id and optional filter, queries tasks filtered by user_id, returns task list)
- [ ] T034 [US2] Register list_tasks tool in MCP server in backend/src/mcp/server.py (add tool definition with filter parameter schema)
- [ ] T035 [US2] Update agent system prompt in backend/src/agent/prompts.py (add instructions for formatting task lists in readable format)
- [ ] T036 [US2] Add task list formatting logic in backend/src/agent/orchestrator.py (format tool results for natural language response)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Users can create and view tasks.

---

## Phase 5: User Story 3 - Complete Tasks (Priority: P3)

**Goal**: Enable users to mark tasks as complete through conversation

**Independent Test**: User can type "Mark 'buy groceries' as done" and the task status updates to completed. Agent confirms with friendly message.

### Implementation for User Story 3

- [ ] T037 [P] [US3] Implement complete_task MCP tool in backend/src/mcp/tools.py (accepts task_identifier and user_id, uses fuzzy matching to find task, marks is_completed=True, returns confirmation)
- [ ] T038 [US3] Register complete_task tool in MCP server in backend/src/mcp/server.py (add tool definition with task_identifier parameter)
- [ ] T039 [US3] Add fuzzy matching logic for task identification in backend/src/mcp/tools.py (helper function to match task titles with partial strings)
- [ ] T040 [US3] Add graceful error handling for task not found in backend/src/mcp/tools.py (return helpful suggestion to view current tasks)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently. Users can create, view, and complete tasks.

---

## Phase 6: User Story 4 - Update Tasks (Priority: P4)

**Goal**: Enable users to modify task titles through conversation

**Independent Test**: User can type "Change 'buy groceries' to 'buy groceries and milk'" and the task title updates. Agent confirms what changed.

### Implementation for User Story 4

- [ ] T041 [P] [US4] Implement update_task MCP tool in backend/src/mcp/tools.py (accepts task_identifier, new_title, and user_id, finds task with fuzzy matching, updates title, returns old and new titles)
- [ ] T042 [US4] Register update_task tool in MCP server in backend/src/mcp/server.py (add tool definition with task_identifier and new_title parameters)
- [ ] T043 [US4] Add confirmation message formatting in backend/src/agent/orchestrator.py (show what changed: old title → new title)

**Checkpoint**: At this point, User Stories 1-4 should all work independently. Users can create, view, complete, and update tasks.

---

## Phase 7: User Story 5 - Delete Tasks (Priority: P5)

**Goal**: Enable users to delete tasks through conversation

**Independent Test**: User can type "Delete the task about buying groceries" and the task is permanently removed. Agent confirms deletion.

### Implementation for User Story 5

- [ ] T044 [P] [US5] Implement delete_task MCP tool in backend/src/mcp/tools.py (accepts task_identifier and user_id, finds task with fuzzy matching, deletes from database, returns confirmation)
- [ ] T045 [US5] Register delete_task tool in MCP server in backend/src/mcp/server.py (add tool definition with task_identifier parameter)
- [ ] T046 [US5] Add confirmation prompt for ambiguous deletions in backend/src/agent/prompts.py (agent should ask for confirmation if multiple matches found)

**Checkpoint**: At this point, User Stories 1-5 should all work independently. Users have full CRUD operations on tasks via conversation.

---

## Phase 8: User Story 6 - Maintain Conversation Context (Priority: P6)

**Goal**: Enable multi-turn conversations with context maintenance

**Independent Test**: User can have multi-turn conversation where agent references previous messages. Example: "Add a task to buy milk" → "Change it to buy milk and eggs" (agent understands "it").

### Implementation for User Story 6

- [ ] T047 [US6] Implement conversation history retrieval in backend/src/services/conversation_service.py (get last 50 messages ordered chronologically)
- [ ] T048 [US6] Integrate history retrieval in POST /api/chat endpoint in backend/src/api/chat.py (fetch history before calling agent, include in messages array)
- [ ] T049 [US6] Implement message persistence after agent response in backend/src/api/chat.py (save user message, assistant message, tool calls, and tool results)
- [ ] T050 [US6] Add context window management in backend/src/agent/orchestrator.py (limit to 50 messages to manage token costs)
- [ ] T051 [US6] Update agent system prompt in backend/src/agent/prompts.py (add instructions for referencing previous context and using pronouns like "it", "that")
- [ ] T052 [US6] Create ConversationList component in frontend/src/components/chat/ConversationList.tsx (sidebar showing conversation history with selection)
- [ ] T053 [US6] Implement GET /api/conversations/{id} endpoint in backend/src/api/conversations.py (return full conversation with messages)
- [ ] T054 [US6] Integrate conversation selection in ChatInterface component in frontend/src/components/chat/ChatInterface.tsx (load selected conversation history)

**Checkpoint**: All user stories should now be independently functional. Full conversational AI chatbot with context maintenance.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T055 [P] Add input validation for message length in backend/src/api/chat.py (max 1000 characters, return 400 Bad Request if exceeded)
- [ ] T056 [P] Add request logging in backend/src/api/chat.py (log user_id, conversation_id, message length, response time)
- [ ] T057 [P] Add OpenAI API rate limit handling in backend/src/agent/orchestrator.py (exponential backoff and retry logic)
- [ ] T058 [P] Add database connection pool configuration in backend/src/main.py (asyncpg pool with max 20 connections)
- [ ] T059 [P] Add loading states to ChatInterface component in frontend/src/components/chat/ChatInterface.tsx (show spinner while waiting for response)
- [ ] T060 [P] Add error message display in ChatInterface component in frontend/src/components/chat/ChatInterface.tsx (show user-friendly errors from API)
- [ ] T061 [P] Add responsive design to chat components in frontend/src/components/chat/ (mobile-first Tailwind CSS styling)
- [ ] T062 [P] Add conversation creation on first message in backend/src/api/chat.py (create new conversation if conversation_id is null)
- [ ] T063 [P] Add "New conversation" button in ConversationList component in frontend/src/components/chat/ConversationList.tsx
- [ ] T064 Run quickstart validation scenarios from specs/002-ai-todo-chatbot/quickstart.md (Scenarios 1-6)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5 → P6)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories (independent)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories (independent)
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - No dependencies on other stories (independent)
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - No dependencies on other stories (independent)
- **User Story 6 (P6)**: Can start after Foundational (Phase 2) - Builds on existing chat infrastructure but independently testable

### Within Each User Story

- MCP tools before agent orchestration
- Backend API endpoints before frontend components
- Core components before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003-T006)
- All Foundational tasks marked [P] can run in parallel within their dependencies (T011-T012, T014-T015)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within each story, tasks marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch parallel tasks for User Story 1:
Task T020: Implement add_task MCP tool (backend/src/mcp/tools.py)
Task T025: Create chat types (frontend/src/types/chat.ts)
Task T026: Create chat API client (frontend/src/services/chat-api.ts)
Task T028: Create MessageBubble component (frontend/src/components/chat/MessageBubble.tsx)
Task T029: Create ChatInput component (frontend/src/components/chat/ChatInput.tsx)

# Then sequential tasks:
Task T021: Register add_task tool (depends on T020)
Task T022: Create agent orchestrator (depends on T021)
Task T023: Implement POST /api/chat (depends on T022)
Task T027: Create ChatInterface (depends on T023, T028, T029)
Task T030: Create chat page (depends on T027)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Create Tasks)
4. **STOP and VALIDATE**: Test User Story 1 independently using quickstart.md Scenario 1
5. Deploy/demo if ready

**MVP Deliverable**: Users can create tasks via natural language conversation. This demonstrates the core value proposition of Phase III.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Add User Story 6 → Test independently → Deploy/Demo
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (T020-T032)
   - Developer B: User Story 2 (T033-T036)
   - Developer C: User Story 3 (T037-T040)
3. Stories complete and integrate independently
4. Continue with remaining stories (US4, US5, US6)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group with Task ID reference
- Stop at any checkpoint to validate story independently
- Tests are NOT included as they were not explicitly requested in the specification
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Summary

**Total Tasks**: 64
**Setup Phase**: 6 tasks
**Foundational Phase**: 13 tasks (BLOCKING)
**User Story 1 (P1 - MVP)**: 13 tasks
**User Story 2 (P2)**: 4 tasks
**User Story 3 (P3)**: 4 tasks
**User Story 4 (P4)**: 3 tasks
**User Story 5 (P5)**: 3 tasks
**User Story 6 (P6)**: 8 tasks
**Polish Phase**: 10 tasks

**Parallel Opportunities**: 23 tasks marked [P] can run in parallel within their phase
**Independent Stories**: All 6 user stories can be implemented independently after Foundational phase
**MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1) = 32 tasks
