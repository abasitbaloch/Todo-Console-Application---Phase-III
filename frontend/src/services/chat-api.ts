/**
 * Chat API client for communicating with Phase-III backend
 */
import { ChatRequest, ChatResponse, Conversation, ConversationDetail } from "@/types/chat";

// FIX: Point directly to your Phase-III Hugging Face Space
const API_BASE_URL = "https://janabkakarot-todo-console-application-phase-iii.hf.space";

/**
 * Get JWT token from localStorage
 */
function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("auth_token");
}

/**
 * Helper to ensure no double slashes and FORCE trailing slashes
 * FastAPI often requires the trailing / to avoid 404s
 */
const getUrl = (path: string) => {
  const cleanBase = API_BASE_URL.replace(/\/$/, ""); 
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  
  // Logic: Ensure the path ends with a slash before adding query parameters
  // This turns '/api/chat' into '/api/chat/'
  const baseWithSlash = cleanPath.includes('?') 
    ? cleanPath.replace('?', '/?') 
    : cleanPath.endsWith('/') ? cleanPath : `${cleanPath}/`;
    
  return `${cleanBase}${baseWithSlash}`;
};

/**
 * Send a message to the AI chatbot
 */
export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const token = getAuthToken();

  if (!token) {
    throw new Error("Not authenticated. Please log in.");
  }

  // This will now call https://.../api/chat/
  const response = await fetch(getUrl('/api/chat'), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    // If we get a 404 here, it means the /api/chat/ route literally doesn't exist on the backend
    const error = await response.json().catch(() => ({ detail: "Route not found on server" }));
    throw new Error(error.detail || "Failed to send message");
  }

  return response.json();
}

/**
 * List all conversations for the authenticated user
 */
export async function listConversations(limit: number = 20, offset: number = 0): Promise<Conversation[]> {
  const token = getAuthToken();
  if (!token) throw new Error("Not authenticated.");

  const response = await fetch(getUrl(`/api/conversations?limit=${limit}&offset=${offset}`), {
    method: "GET",
    headers: { "Authorization": `Bearer ${token}` }
  });

  if (!response.ok) throw new Error("Failed to fetch conversations");
  return response.json();
}

/**
 * Get a specific conversation with all messages
 */
export async function getConversation(conversationId: string): Promise<ConversationDetail> {
  const token = getAuthToken();
  if (!token) throw new Error("Not authenticated.");

  const response = await fetch(getUrl(`/api/conversations/${conversationId}`), {
    method: "GET",
    headers: { "Authorization": `Bearer ${token}` }
  });

  if (!response.ok) throw new Error("Failed to fetch conversation");
  return response.json();
}