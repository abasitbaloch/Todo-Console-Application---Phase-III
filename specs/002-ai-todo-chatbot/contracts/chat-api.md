# Chat API Contract

**Version**: 1.0.0
**Base URL**: `/api`
**Authentication**: JWT Bearer Token (required for all endpoints)

## Endpoints

### POST /api/chat

Send a message to the AI chatbot and receive a response.

**Authentication**: Required (JWT)

**Request Body**:
```json
{
  "conversation_id": "uuid | null",
  "message": "string"
}
```

**Request Schema**:
```typescript
interface ChatRequest {
  conversation_id: string | null;  // null to start new conversation
  message: string;                 // User's natural language input (max 1000 chars)
}
```

**Response Body** (Success):
```json
{
  "conversation_id": "uuid",
  "message": "string",
  "tool_calls": [
    {
      "tool": "string",
      "arguments": {},
      "result": {}
    }
  ] | null,
  "created_at": "ISO 8601 timestamp"
}
```

**Response Schema**:
```typescript
interface ChatResponse {
  conversation_id: string;         // Conversation UUID
  message: string;                 // AI agent's response
  tool_calls: ToolCall[] | null;  // Tools executed (if any)
  created_at: string;              // ISO 8601 timestamp
}

interface ToolCall {
  tool: string;                    // Tool name (e.g., "add_task")
  arguments: Record<string, any>; // Tool input parameters
  result: Record<string, any>;    // Tool execution result
}
```

**Status Codes**:
- `200 OK`: Message processed successfully
- `400 Bad Request`: Invalid request body or message too long
- `401 Unauthorized`: Missing or invalid JWT token
- `404 Not Found`: Conversation not found or doesn't belong to user
- `500 Internal Server Error`: OpenAI API error or database error

**Error Response**:
```json
{
  "error": "string",
  "message": "string",
  "suggestions": ["string"]
}
```

**Example Request**:
```bash
curl -X POST https://api.example.com/api/chat \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": null,
    "message": "Add a task to buy groceries"
  }'
```

**Example Response**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "I've created a task for you: 'buy groceries'. Is there anything else you'd like to add?",
  "tool_calls": [
    {
      "tool": "add_task",
      "arguments": {
        "title": "buy groceries"
      },
      "result": {
        "success": true,
        "task_id": "660e8400-e29b-41d4-a716-446655440001",
        "title": "buy groceries"
      }
    }
  ],
  "created_at": "2026-01-11T10:30:00Z"
}
```

**Validation Rules**:
- `message` is required and cannot be empty
- `message` max length: 1000 characters
- `conversation_id` must be valid UUID or null
- If `conversation_id` is provided, it must belong to the authenticated user

**Behavior**:
- If `conversation_id` is null, a new conversation is created
- If `conversation_id` is provided, the message is added to existing conversation
- Conversation history (last 50 messages) is retrieved and sent to OpenAI agent
- Agent may call zero or more MCP tools based on user intent
- All messages and tool calls are persisted to database
- Response includes agent's natural language reply and tool execution details

---

### GET /api/conversations

List all conversations for the authenticated user.

**Authentication**: Required (JWT)

**Query Parameters**:
```
limit: integer (default: 20, max: 100)
offset: integer (default: 0)
```

**Response Body**:
```json
{
  "conversations": [
    {
      "id": "uuid",
      "created_at": "ISO 8601 timestamp",
      "updated_at": "ISO 8601 timestamp",
      "last_message": "string",
      "message_count": integer
    }
  ],
  "total": integer,
  "limit": integer,
  "offset": integer
}
```

**Response Schema**:
```typescript
interface ConversationsResponse {
  conversations: ConversationSummary[];
  total: number;
  limit: number;
  offset: number;
}

interface ConversationSummary {
  id: string;
  created_at: string;
  updated_at: string;
  last_message: string;      // Preview of last message (max 100 chars)
  message_count: number;
}
```

**Status Codes**:
- `200 OK`: Conversations retrieved successfully
- `401 Unauthorized`: Missing or invalid JWT token
- `500 Internal Server Error`: Database error

**Example Request**:
```bash
curl -X GET "https://api.example.com/api/conversations?limit=10&offset=0" \
  -H "Authorization: Bearer eyJhbGc..."
```

**Example Response**:
```json
{
  "conversations": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2026-01-11T10:00:00Z",
      "updated_at": "2026-01-11T10:30:00Z",
      "last_message": "I've created a task for you: 'buy groceries'",
      "message_count": 4
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

---

### GET /api/conversations/{conversation_id}

Get full conversation history including all messages.

**Authentication**: Required (JWT)

**Path Parameters**:
- `conversation_id`: UUID of the conversation

**Query Parameters**:
```
limit: integer (default: 50, max: 100)
offset: integer (default: 0)
```

**Response Body**:
```json
{
  "id": "uuid",
  "created_at": "ISO 8601 timestamp",
  "updated_at": "ISO 8601 timestamp",
  "messages": [
    {
      "id": "uuid",
      "role": "user | assistant | system",
      "content": "string",
      "tool_calls": [] | null,
      "tool_results": [] | null,
      "created_at": "ISO 8601 timestamp"
    }
  ],
  "total_messages": integer
}
```

**Response Schema**:
```typescript
interface ConversationDetail {
  id: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
  total_messages: number;
}

interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  tool_calls: any[] | null;
  tool_results: any[] | null;
  created_at: string;
}
```

**Status Codes**:
- `200 OK`: Conversation retrieved successfully
- `401 Unauthorized`: Missing or invalid JWT token
- `404 Not Found`: Conversation not found or doesn't belong to user
- `500 Internal Server Error`: Database error

**Example Request**:
```bash
curl -X GET "https://api.example.com/api/conversations/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer eyJhbGc..."
```

**Example Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-11T10:00:00Z",
  "updated_at": "2026-01-11T10:30:00Z",
  "messages": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440002",
      "role": "user",
      "content": "Add a task to buy groceries",
      "tool_calls": null,
      "tool_results": null,
      "created_at": "2026-01-11T10:30:00Z"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440003",
      "role": "assistant",
      "content": "I've created a task for you: 'buy groceries'",
      "tool_calls": [
        {
          "id": "call_123",
          "function": {
            "name": "add_task",
            "arguments": "{\"title\": \"buy groceries\"}"
          }
        }
      ],
      "tool_results": [
        {
          "tool_call_id": "call_123",
          "content": "{\"success\": true, \"task_id\": \"uuid\"}"
        }
      ],
      "created_at": "2026-01-11T10:30:05Z"
    }
  ],
  "total_messages": 2
}
```

---

## MCP Tool Contracts

These are internal tool definitions used by the OpenAI agent. They are not directly exposed as HTTP endpoints.

### Tool: add_task

**Description**: Create a new task for the user.

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "The task title",
      "maxLength": 500
    }
  },
  "required": ["title"]
}
```

**Returns**:
```json
{
  "success": true,
  "task_id": "uuid",
  "title": "string"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "string"
}
```

---

### Tool: list_tasks

**Description**: List all tasks for the user.

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "filter": {
      "type": "string",
      "enum": ["all", "completed", "incomplete"],
      "description": "Filter tasks by completion status",
      "default": "all"
    }
  }
}
```

**Returns**:
```json
{
  "success": true,
  "tasks": [
    {
      "task_id": "uuid",
      "title": "string",
      "is_completed": boolean,
      "created_at": "ISO 8601 timestamp"
    }
  ],
  "count": integer
}
```

---

### Tool: complete_task

**Description**: Mark a task as completed.

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "task_identifier": {
      "type": "string",
      "description": "Task title or partial match"
    }
  },
  "required": ["task_identifier"]
}
```

**Returns**:
```json
{
  "success": true,
  "task_id": "uuid",
  "title": "string",
  "is_completed": true
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Task not found",
  "suggestion": "Would you like to see your current tasks?"
}
```

---

### Tool: update_task

**Description**: Update a task's title.

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "task_identifier": {
      "type": "string",
      "description": "Current task title or partial match"
    },
    "new_title": {
      "type": "string",
      "description": "New task title",
      "maxLength": 500
    }
  },
  "required": ["task_identifier", "new_title"]
}
```

**Returns**:
```json
{
  "success": true,
  "task_id": "uuid",
  "old_title": "string",
  "new_title": "string"
}
```

---

### Tool: delete_task

**Description**: Delete a task permanently.

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "task_identifier": {
      "type": "string",
      "description": "Task title or partial match"
    }
  },
  "required": ["task_identifier"]
}
```

**Returns**:
```json
{
  "success": true,
  "task_id": "uuid",
  "title": "string",
  "deleted": true
}
```

---

## Security Considerations

**Authentication**:
- All endpoints require valid JWT token in `Authorization: Bearer <token>` header
- JWT must contain `user_id` claim
- JWT signature verified using shared secret with Better Auth
- Invalid/expired tokens return 401 Unauthorized

**Data Isolation**:
- All database queries filtered by `user_id` from JWT
- Users cannot access other users' conversations or tasks
- Conversation ownership verified before any operation

**Input Validation**:
- All request bodies validated using Pydantic schemas
- String length limits enforced
- UUID format validation
- SQL injection prevented by parameterized queries

**Rate Limiting** (Future):
- Not implemented in Phase III MVP
- Consider adding in future phases: 100 requests/minute per user

---

## Error Handling

**Standard Error Response Format**:
```json
{
  "error": "error_code",
  "message": "User-friendly error message",
  "suggestions": ["Helpful suggestion 1", "Helpful suggestion 2"]
}
```

**Common Error Codes**:
- `invalid_request`: Malformed request body
- `unauthorized`: Missing or invalid JWT token
- `not_found`: Resource not found or doesn't belong to user
- `openai_error`: OpenAI API failure
- `database_error`: Database connection or query failure
- `tool_error`: MCP tool execution failure

**Error Messages**:
- Never expose technical details (stack traces, SQL queries, API keys)
- Provide user-friendly explanations
- Include actionable suggestions when possible
- Log full technical details server-side for debugging

---

## Versioning

**Current Version**: 1.0.0

**Versioning Strategy**:
- API version included in base URL: `/api/v1/chat` (future)
- Phase III uses unversioned `/api/chat` for simplicity
- Breaking changes will require new version: `/api/v2/chat`

**Backward Compatibility**:
- Additive changes (new optional fields) are backward compatible
- Removing fields or changing types requires new version
- Deprecation notices provided 30 days before removal

---

## Testing

**Contract Tests**:
- Validate request/response schemas match OpenAPI spec
- Test all status codes (200, 400, 401, 404, 500)
- Verify error response format consistency
- Test JWT authentication enforcement

**Integration Tests**:
- Full chat flow: send message → receive response → verify persistence
- Multi-turn conversation with context maintenance
- Tool execution verification (task actually created in DB)
- User isolation (User A cannot access User B's data)

**Example Test Cases**:
1. Create new conversation with first message
2. Continue existing conversation with context
3. Invalid JWT token returns 401
4. Non-existent conversation returns 404
5. Message too long returns 400
6. OpenAI API failure returns 500 with friendly message
7. Tool execution creates/modifies database records
