"use client";

import { cn } from "@/lib/utils";
import type { Message } from "@/lib/api-client";

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn("flex w-full mb-4", isUser ? "justify-end" : "justify-start")}
    >
      <div
        className={cn(
          "max-w-[80%] rounded-lg px-4 py-3 shadow-sm",
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-muted text-muted-foreground"
        )}
      >
        <div className="flex flex-col gap-1">
          <div className="text-xs opacity-70">
            {isUser ? "あなた" : "AI アシスタント"}
          </div>
          <div className="text-sm whitespace-pre-wrap">{message.content}</div>
          <div className="text-xs opacity-50 mt-1">
            {new Date(message.timestamp).toLocaleTimeString("ja-JP")}
          </div>
        </div>
      </div>
    </div>
  );
}
