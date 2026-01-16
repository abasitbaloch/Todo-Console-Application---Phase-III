/**
 * Chat API client - Professional Production Version
 * Fixes: Mixed Content (HTTPS), 307 Redirects, and Pagination Paths
 */
import { ChatRequest, ChatResponse, Conversation, ConversationDetail } from "@/types/chat";

// FORCE HTTPS to stop the "Mixed Content" error in Chrome
const API_BASE_URL = "https://janabkakarot-todo-console-application-phase-iii.hf.space";

function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("auth_token");
}

/**
 * Smart URL builder to match FastAPI routing perfectly
 */
const getUrl = (path: string) => {
  const cleanBase = API_BASE_URL.replace(/\/$/, "");
  const cleanPath = path.startsWith('/') ? path : `/${path}`;

  // Logic for Query Parameters (Conversations List)
  if (cleanPath.includes('?')) {
    // Splits /api/conversations?limit=20 into path and query
    const [route, query] = cleanPath.split('?');
    // Ensures path has a slash BEFORE the ? (e.g., /api/conversations/?)
    const routeWithSlash = route.endsWith('/') ? route : `${route}/`;
    return `${cleanBase}${routeWithSlash}?${query}`;
  }

  // Logic for POST /api/chat
  // We match exactly what is in your chat.py @router.post("")
  if (cleanPath === '/api/chat') {
    return `${cleanBase}${cleanPath}`; 
  }

  // Logic for GET /api/conversations/{id}/
  return `${cleanBase}${cleanPath.endsWith('/') ? cleanPath : cleanPath + '/'}`;
};

/**
 * Send a message - No trailing slash to match chat.py @router.post("")
 */
export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const token = getAuthToken();
  if (!token) throw new Error("Not authenticated.");

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
    throw new Error(errorData.detail || "Chat failed. See backend logs.");
  }

  return response.json();
}

/**
 * List conversations - Ensures slash before query params
 */
export async function listConversations(limit: number = 20, offset: number = 0): Promise<Conversation[]> {
  const token = getAuthToken();
  if (!token) return [];

  try {
    const response = await fetch(getUrl(`/api/conversations?limit=${limit}&offset=${offset}`), {
      method: "GET",
      headers: { "Authorization": `Bearer ${token}` }
    });

    if (!response.ok) return [];
    return response.json();
  } catch (err) {
    console.error("Sidebar load failed:", err);
    return [];
  }
}

/**
 * Get conversation detail
 */
export async function getConversation(conversationId: string): Promise<ConversationDetail> {
  const token = getAuthToken();
  if (!token) throw new Error("Not authenticated.");

  const response = await fetch(getUrl(`/api/conversations/${conversationId}`), {
    method: "GET",
    headers: { "Authorization": `Bearer ${token}` }
  });

  if (!response.ok) throw new Error("Failed to fetch conversation history");
  return response.json();
}