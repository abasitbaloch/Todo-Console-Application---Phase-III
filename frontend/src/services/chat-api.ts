import { ChatRequest, ChatResponse, Conversation, ConversationDetail } from "@/types/chat";

const API_BASE_URL = "https://janabkakarot-todo-console-application-phase-iii.hf.space";

function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("auth_token");
}

const getUrl = (path: string) => {
  const cleanBase = API_BASE_URL.replace(/\/$/, ""); 
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  
  // For the Chat POST request, we do NOT want a trailing slash to avoid 307
  if (cleanPath === '/api/chat') {
    return `${cleanBase}${cleanPath}`;
  }
    
  // Conversations list usually works fine with the slash
  return `${cleanBase}${cleanPath.endsWith('/') ? cleanPath : cleanPath + '/'}`;
};

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

  if (!response.ok) throw new Error("Chat connection failed.");
  return response.json();
}

export async function listConversations(limit: number = 20, offset: number = 0): Promise<Conversation[]> {
  const token = getAuthToken();
  if (!token) return [];
  const response = await fetch(getUrl(`/api/conversations?limit=${limit}&offset=${offset}`), {
    method: "GET",
    headers: { "Authorization": `Bearer ${token}` }
  });
  return response.ok ? response.json() : [];
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