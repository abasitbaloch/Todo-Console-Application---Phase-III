/**
 * ChatInterface component - main chat UI container with conversation history
 */

"use client";

import React, { useState, useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";
import ConversationList from "./ConversationList";
import { Message, MessageRole } from "@/types/chat";
import { sendMessage, getConversation } from "@/services/chat-api";

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSidebar, setShowSidebar] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (messageText: string) => {
    setIsLoading(true);
    setError(null);

    // Add user message to UI immediately
    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      role: MessageRole.USER,
      content: messageText,
      created_at: new Date().toISOString()
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      // Send message to backend
      const response = await sendMessage({
        conversation_id: conversationId,
        message: messageText
      });

      // Update conversation ID if this was the first message
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response to UI
      const assistantMessage: Message = {
        id: `response-${Date.now()}`,
        role: MessageRole.ASSISTANT,
        content: response.message,
        created_at: new Date().toISOString(),
        tool_calls: response.tool_calls
      };
      setMessages((prev) => [...prev, assistantMessage]);

    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");

      // Add error message to UI
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
      // Fetch conversation history
      const conversation = await getConversation(selectedConversationId);

      // Update state
      setConversationId(selectedConversationId);
      setMessages(conversation.messages);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load conversation");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      {showSidebar && (
        <ConversationList
          currentConversationId={conversationId}
          onSelectConversation={handleSelectConversation}
          onNewConversation={handleNewConversation}
        />
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-300 p-4 flex justify-between items-center">
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
        <div className="flex-1 overflow-y-auto p-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-500">
              <div className="text-6xl mb-4">💬</div>
              <h2 className="text-2xl font-semibold mb-2">Welcome to AI Todo Assistant</h2>
              <p className="text-center max-w-md">
                Start a conversation to manage your tasks with natural language.
                Try saying &quot;Add a task to buy groceries&quot; or &quot;Show me my tasks&quot;.
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
          <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mx-4 mb-4">
            <p className="font-bold">Error</p>
            <p>{error}</p>
          </div>
        )}

        {/* Input Area */}
        <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
      </div>
    </div>
  );
}