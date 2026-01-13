/**
 * MessageBubble component for displaying chat messages
 */

import React from "react";
import { Message, MessageRole } from "@/types/chat";

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === MessageRole.USER;
  const isAssistant = message.role === MessageRole.ASSISTANT;

  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}
    >
      <div
        className={`max-w-[70%] rounded-lg px-4 py-2 ${
          isUser
            ? "bg-blue-600 text-white"
            : isAssistant
            ? "bg-gray-200 text-gray-900"
            : "bg-gray-100 text-gray-600 text-sm italic"
        }`}
      >
        <div className="whitespace-pre-wrap break-words">
          {message.content}
        </div>

        {message.tool_calls && message.tool_calls.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-300 text-xs opacity-75">
            <span className="font-semibold">Tools used:</span>{" "}
            {message.tool_calls.map((tc) => tc.function.name).join(", ")}
          </div>
        )}

        <div className="text-xs opacity-75 mt-1">
          {new Date(message.created_at).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit"
          })}
        </div>
      </div>
    </div>
  );
}
