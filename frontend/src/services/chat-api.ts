/**
 * Chat API client - Fixed to match Backend main.py prefixes
 */
import { ChatRequest, ChatResponse, Conversation, ConversationDetail } from "@/types/chat";

const API_BASE_URL = "https://janabkakarot-todo-console-application-phase-iii.hf.space";

function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("auth_token");
}

const getUrl = (path: string) => {
  const cleanBase = API_BASE_URL.replace(/\/$/, ""); 
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  
  // Ensure trailing slash BEFORE query parameters
  const baseWithSlash = cleanPath.includes('?') 
    ? cleanPath.replace('?', '/?') 
    : cleanPath.endsWith('/') ? cleanPath : `${cleanPath}/`;
    
  return `${cleanBase}${baseWithSlash}`;
};

/**
 * Send a message - ADDED /api prefix back
 */
export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const token = getAuthToken();
  if (!token) throw new Error("Not authenticated.");

  // This calls https://.../api/chat/
  const response = await fetch(getUrl('/api/chat'), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    throw new Error("Chat failed. Check if backend is awake.");
  }

  return response.json();
}

/**
 * List conversations - ADDED /api prefix back
 */
export async function listConversations(limit: number = 20, offset: number = 0): Promise<Conversation[]> {
  const token = getAuthToken();
  if (!token) throw new Error("Not authenticated.");

  // This calls https://.../api/conversations/
  const response = await fetch(getUrl(`/api/conversations?limit=${limit}&offset=${offset}`), {
    method: "GET",
    headers: { "Authorization": `Bearer ${token}` }
  });

  if (!response.ok) throw new Error("Failed to fetch conversations");
  return response.json();
}

/**
 * Get conversation detail - ADDED /api prefix back
 */
export async function getConversation(conversationId: string): Promise<ConversationDetail> {
  const token = getAuthToken();
  if (!token) throw new Error("Not authenticated.");

  // This calls https://.../api/conversations/{id}/
  const response = await fetch(getUrl(`/api/conversations/${conversationId}`), {
    method: "GET",
    headers: { "Authorization": `Bearer ${token}` }
  });

  if (!response.ok) throw new Error("Failed to fetch conversation");
  return response.json();
}