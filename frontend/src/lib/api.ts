/**
 * Unified API Client - Phase III Final
 * Fixes: Manual Task Creation, Bot Sync, Timezones, and 307 Redirects
 */
import { ChatRequest, ChatResponse, Conversation, ConversationDetail } from "@/types/chat";

const API_BASE_URL = "https://janabkakarot-todo-console-application-phase-iii.hf.space";

function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("auth_token");
}

/**
 * Smart URL builder to satisfy FastAPI's strict trailing slash requirements.
 * This prevents 307 Redirects which cause data loss on POST/PUT requests.
 */
const getUrl = (path: string) => {
  const cleanBase = API_BASE_URL.replace(/\/$/, "");
  const cleanPath = path.startsWith('/') ? path : `/${path}`;

  // Handle Query Parameters
  if (cleanPath.includes('?')) {
    const [route, query] = cleanPath.split('?');
    const routeWithSlash = route.endsWith('/') ? route : `${route}/`;
    return `${cleanBase}${routeWithSlash}?${query}`;
  }

  // Handle Chat POST
  if (cleanPath === '/api/chat') {
    return `${cleanBase}${cleanPath}`; 
  }

  // Default: Always add trailing slash
  return `${cleanBase}${cleanPath.endsWith('/') ? cleanPath : cleanPath + '/'}`;
};

export const api = {
  /**
   * TASK OPERATIONS
   */
  async getTasks() {
    const token = getAuthToken();
    const response = await fetch(getUrl('/tasks'), {
      headers: { "Authorization": `Bearer ${token}` }
    });
    if (!response.ok) return [];
    return response.json();
  },

  async createTask(title: string, description: string = "") {
    const token = getAuthToken();
    const response = await fetch(getUrl('/tasks'), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({ title, description })
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || "Failed to create task");
    }
    return response.json();
  },

  async updateTask(taskId: string, updates: { is_completed?: boolean; title?: string; description?: string }) {
    const token = getAuthToken();
    const response = await fetch(getUrl(`/tasks/${taskId}`), {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify(updates)
    });
    if (!response.ok) throw new Error("Failed to update task");
    return response.json();
  },

  async deleteTask(taskId: string) {
    const token = getAuthToken();
    const response = await fetch(getUrl(`/tasks/${taskId}`), {
      method: "DELETE",
      headers: { "Authorization": `Bearer ${token}` }
    });
    if (!response.ok) throw new Error("Failed to delete task");
    return true;
  },

  /**
   * CHAT OPERATIONS
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
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
  },

  async listConversations(limit: number = 20, offset: number = 0): Promise<Conversation[]> {
    const token = getAuthToken();
    if (!token) return [];
    const response = await fetch(getUrl(`/api/conversations?limit=${limit}&offset=${offset}`), {
      method: "GET",
      headers: { "Authorization": `Bearer ${token}` }
    });
    if (!response.ok) return [];
    const data = await response.json();
    return data.map((conv: any) => ({
      ...conv,
      updated_at: new Date(conv.updated_at).toISOString() 
    }));
  },

  async getConversation(conversationId: string): Promise<ConversationDetail> {
    const token = getAuthToken();
    const response = await fetch(getUrl(`/api/conversations/${conversationId}`), {
      method: "GET",
      headers: { "Authorization": `Bearer ${token}` }
    });
    if (!response.ok) throw new Error("Failed to load history.");
    return response.json();
  }
};

// Explicit exports for your ChatInterface
export const sendMessage = api.sendMessage;
export const getConversation = api.getConversation;