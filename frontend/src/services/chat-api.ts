/**
 * Chat API client - Final Version
 * Fixed for HTTPS, Trailing Slashes, and Unified Prefixes
 */
import { ChatRequest, ChatResponse, Conversation, ConversationDetail } from "@/types/chat";

// Ensure this is HTTPS to avoid "Mixed Content" browser blocks
const API_BASE_URL = "https://janabkakarot-todo-console-application-phase-iii.hf.space";

function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  // Ensure this matches the key used in client-auth.ts
  return localStorage.getItem("auth_token");
}

const getUrl = (path: string) => {
  // 1. Force use of HTTPS and remove any trailing slash from base
  const cleanBase = API_BASE_URL.replace(/\/$/, "").replace("http://", "https://");
  
  // 2. Ensure path starts with a slash
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  
  // 3. Force trailing slash BEFORE query parameters to satisfy FastAPI
  // Example: /api/chat -> /api/chat/
  // Example: /api/conversations?limit=20 -> /api/conversations/?limit=20
  let finalPath = cleanPath;
  if (cleanPath.includes('?')) {
    finalPath = cleanPath.replace('?', '/?');
  } else {
    finalPath = cleanPath.endsWith('/') ? cleanPath : `${cleanPath}/`;
  }
    
  return `${cleanBase}${finalPath}`;
};

/**
 * Send a message to the AI chatbot
 */
export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const token = getAuthToken();
  if (!token) throw new Error("Not authenticated.");

  // Hits: https://.../api/chat/
  const response = await fetch(getUrl('/api/chat'), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Chat failed. Check backend logs.");
  }

  return response.json();
}

/**
 * List all conversations for the authenticated user
 */
export async function listConversations(limit: number = 20, offset: number = 0): Promise<Conversation[]> {
  const token = getAuthToken();
  if (!token) throw new Error("Not authenticated.");

  // Hits: https://.../api/conversations/?limit=20&offset=0
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

  // Hits: https://.../api/conversations/{id}/
  const response = await fetch(getUrl(`/api/conversations/${conversationId}`), {
    method: "GET",
    headers: { "Authorization": `Bearer ${token}` }
  });

  if (!response.ok) throw new Error("Failed to fetch conversation");
  return response.json();
}