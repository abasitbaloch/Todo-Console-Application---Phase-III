/**
 * Chat API client - Final Production Version
 * Fixes: Mixed Content, 307 Redirects, and Graceful 429/500 Error Handling
 */
import { ChatRequest, ChatResponse, Conversation, ConversationDetail } from "@/types/chat";

// FORCE HTTPS to prevent browser "Mixed Content" blocks
const API_BASE_URL = "https://janabkakarot-todo-console-application-phase-iii.hf.space";

function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("auth_token");
}

/**
 * Smart URL builder to satisfy FastAPI's strict trailing slash requirements
 */
const getUrl = (path: string) => {
  const cleanBase = API_BASE_URL.replace(/\/$/, "");
  const cleanPath = path.startsWith('/') ? path : `/${path}`;

  // Handle Query Parameters (e.g., /api/conversations/?limit=20)
  if (cleanPath.includes('?')) {
    const [route, query] = cleanPath.split('?');
    const routeWithSlash = route.endsWith('/') ? route : `${route}/`;
    return `${cleanBase}${routeWithSlash}?${query}`;
  }

  // Handle Chat POST (Match backend chat.py @router.post(""))
  if (cleanPath === '/api/chat') {
    return `${cleanBase}${cleanPath}`; 
  }

  // Default: Add trailing slash for GET requests
  return `${cleanBase}${cleanPath.endsWith('/') ? cleanPath : cleanPath + '/'}`;
};

/**
 * Send a message - Robust error handling for Free Tier Rate Limits
 */
export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const token = getAuthToken();
  if (!token) throw new Error("Please log in to chat.");

  try {
    const response = await fetch(getUrl('/api/chat'), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify(request)
    });

    if (response.status === 429) {
      throw new Error("The AI is currently busy (Free Tier limit). Please wait 30 seconds and try again.");
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "The AI encountered an error. Please try a shorter message.");
    }

    return await response.json();
  } catch (error: any) {
    // Catch network errors or the thrown errors above
    throw new Error(error.message || "Could not connect to the AI server.");
  }
}

/**
 * List conversations - Silent fail (returns empty array) on error
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
    return await response.json();
  } catch (err) {
    console.error("Sidebar load failed:", err);
    return [];
  }
}

/**
 * Get conversation history
 */
export async function getConversation(conversationId: string): Promise<ConversationDetail> {
  const token = getAuthToken();
  if (!token) throw new Error("Session expired.");

  const response = await fetch(getUrl(`/api/conversations/${conversationId}`), {
    method: "GET",
    headers: { "Authorization": `Bearer ${token}` }
  });

  if (!response.ok) throw new Error("Failed to load chat history.");
  return await response.json();
}