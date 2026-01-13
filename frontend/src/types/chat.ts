/**
 * TypeScript types for chat functionality
 */

export enum MessageRole {
  USER = "user",
  ASSISTANT = "assistant",
  SYSTEM = "system"
}

export interface ToolCall {
  id: string;
  type: string;
  function: {
    name: string;
    arguments: string;
  };
}

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  created_at: string;
  tool_calls?: ToolCall[];
}

export interface ChatRequest {
  conversation_id: string | null;
  message: string;
}

export interface ChatResponse {
  conversation_id: string;
  message: string;
  tool_calls?: ToolCall[];
}

export interface Conversation {
  id: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
}

export interface ConversationDetail extends Conversation {
  messages: Message[];
}
