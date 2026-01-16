/**
 * Chat API client - Fixed to match backend route structure
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
 * Send a message - REMOVED /api prefix
 */
export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const token = getAuthToken();
  if (!token) throw new Error("Not authenticated.");

  // CHANGED: /api/chat -> /chat
  const response = await fetch(getUrl('/chat'), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Chat route not found" }));
    throw new Error(error.detail || "Failed to send message");
  }

  return response.json();
}

/**
 * List conversations - REMOVED /api prefix
 */
export async function listConversations(limit: number = 20, offset: number = 0): Promise<Conversation[]> {
  const token = getAuthToken();
  if (!token) throw new Error("Not authenticated.");

  // CHANGED: /api/conversations -> /conversations
  const response = await fetch(getUrl(`/conversations?limit=${limit}&offset=${offset}`), {
    method: "GET",
    headers: { "Authorization": `Bearer ${token}` }
  });

  if (!response.ok) throw new Error("Failed to fetch conversations");
  return response.json();
}

/**
 * Get conversation detail - REMOVED /api prefix
 */
export async function getConversation(conversationId: string): Promise<ConversationDetail> {
  const token = getAuthToken();
  if (!token) throw new Error("Not authenticated.");

  // CHANGED: /api/conversations -> /conversations
  const response = await fetch(getUrl(`/conversations/${conversationId}`), {
    method: "GET",
    headers: { "Authorization": `Bearer ${token}` }
  });

  if (!response.ok) throw new Error("Failed to fetch conversation");
  return response.json();
}