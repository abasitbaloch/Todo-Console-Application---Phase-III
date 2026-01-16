/**
 * Unified API Client - Final Production Version
 * Fixes: Timezone (UTC), 307 Redirects, and Task Toggle Logic
 */
import { ChatRequest, ChatResponse, Conversation, ConversationDetail } from "@/types/chat";

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

  // Fix for Time/Sidebar: Ensure slash is BEFORE the query string
  if (cleanPath.includes('?')) {
    const [route, query] = cleanPath.split('?');
    const routeWithSlash = route.endsWith('/') ? route : `${route}/`;
    return `${cleanBase}${routeWithSlash}?${query}`;
  }

  // Handle Chat POST (No trailing slash usually preferred for specific POST routes)
  if (cleanPath === '/api/chat') {
    return `${cleanBase}${cleanPath}`; 
  }

  // Default: Always enforce trailing slash to avoid 307 Redirects
  return `${cleanBase}${cleanPath.endsWith('/') ? cleanPath : cleanPath + '/'}`;
};

/**
 * 1. FIX: Task Toggle (The Checkbox)
 * This must use a PUT request and a perfectly formatted URL.
 */
export async function updateTaskStatus(taskId: string, completed: boolean) {
  const token = getAuthToken();
  
  // Explicitly ensuring the slash is after the ID: /tasks/ID/
  const url = getUrl(`/tasks/${taskId}`); 

  const response = await fetch(url, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ is_completed: completed })
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to update task.");
  }

  return await response.json();
}

/**
 * 2. FIX: Chat Messages
 */
export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const token = getAuthToken();
  const response = await fetch(getUrl('/api/chat'), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify(request)
  });

  if (!response.ok) throw new Error("AI is busy or server error.");
  return response.json();
}

/**
 * 3. FIX: Sidebar Time (List Conversations)
 */
export async function listConversations(limit: number = 20, offset: number = 0): Promise<Conversation[]> {
  const token = getAuthToken();
  if (!token) return [];

  const response = await fetch(getUrl(`/api/conversations?limit=${limit}&offset=${offset}`), {
    method: "GET",
    headers: { "Authorization": `Bearer ${token}` }
  });

  if (!response.ok) return [];
  
  const data = await response.json();
  
  /**
   * IMPORTANT: The "5 hours ago" fix.
   * We ensure the string is treated as a Date object so the browser
   * converts UTC (from backend) to your local Karachi time.
   */
  return data.map((conv: any) => ({
    ...conv,
    // Ensure we parse the string properly
    updated_at: new Date(conv.updated_at).toISOString() 
  }));
}

export async function getConversation(conversationId: string): Promise<ConversationDetail> {
  const token = getAuthToken();
  const response = await fetch(getUrl(`/api/conversations/${conversationId}`), {
    method: "GET",
    headers: { "Authorization": `Bearer ${token}` }
  });

  if (!response.ok) throw new Error("Failed to load history.");
  return response.json();
}