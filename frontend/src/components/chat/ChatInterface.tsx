/**
 * ChatInterface component - Fixed for Phase III Task Sync
 */

"use client";

import React, { useState, useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";
import ConversationList from "./ConversationList";
import { Message, MessageRole } from "@/types/chat";
import { sendMessage, getConversation } from "@/services/chat-api";

// 1. Define the props to accept the refresh trigger from the Dashboard
interface ChatInterfaceProps {
  onTaskCreated?: () => void;
}

export default function ChatInterface({ onTaskCreated }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSidebar, setShowSidebar] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (messageText: string) => {
    setIsLoading(true);
    setError(null);

    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      role: MessageRole.USER,
      content: messageText,
      created_at: new Date().toISOString()
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await sendMessage({
        conversation_id: conversationId,
        message: messageText
      });

      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      const assistantMessage: Message = {
        id: `response-${Date.now()}`,
        role: MessageRole.ASSISTANT,
        content: response.message,
        created_at: new Date().toISOString(),
        tool_calls: response.tool_calls
      };
      
      setMessages((prev) => [...prev, assistantMessage]);

      // 2. CRITICAL FIX: If the AI response contains tool_calls, 
      // it means a task was likely added, deleted, or updated.
      // We trigger the refresh in the Dashboard!
      if (response.tool_calls && response.tool_calls.length > 0 && onTaskCreated) {
        console.log("Tool call detected, refreshing task list...");
        onTaskCreated();
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: MessageRole.SYSTEM,
        content: `Error: ${err instanceof Error ? err.message : "Failed to send message"}`,
        created_at: new Date().toISOString()
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewConversation = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  };

  const handleSelectConversation = async (selectedConversationId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const conversation = await getConversation(selectedConversationId);
      setConversationId(selectedConversationId);
      setMessages(conversation.messages);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load conversation");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-full bg-gray-50 overflow-hidden">
      {/* Sidebar */}
      {showSidebar && (
        <ConversationList
          currentConversationId={conversationId}
          onSelectConversation={handleSelectConversation}
          onNewConversation={handleNewConversation}
        />
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Header */}
        <div className="bg-white border-b border-gray-300 p-4 flex justify-between items-center shrink-0">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className="px-3 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              {showSidebar ? "◀" : "☰"}
            </button>
            <div>
              <h1 className="text-xl font-bold text-gray-900">AI Todo Assistant</h1>
              <p className="text-sm text-gray-600">
                {conversationId ? "Active conversation" : "Start a new conversation"}
              </p>
            </div>
          </div>
          <button
            onClick={handleNewConversation}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            New Chat
          </button>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-500">
              <div className="text-6xl mb-4">💬</div>
              <h2 className="text-2xl font-semibold mb-2">Welcome</h2>
              <p className="text-center max-w-md">
                Try saying &quot;Add a task to play football&quot;.
              </p>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mx-4 mb-4 shrink-0">
            <p>{error}</p>
          </div>
        )}

        {/* Input Area */}
        <div className="shrink-0">
            <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
}