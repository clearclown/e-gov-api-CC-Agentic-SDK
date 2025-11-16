"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChatMessage } from "./ChatMessage";
import { apiClient, type Message, type LLMProvider } from "@/lib/api-client";
import { toast } from "sonner";

export function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [provider, setProvider] = useState<LLMProvider>("anthropic");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Create session on mount
  useEffect(() => {
    const initSession = async () => {
      try {
        const session = await apiClient.createSession();
        setSessionId(session.session_id);
        toast.success("セッションを開始しました");
      } catch (error) {
        console.error("Failed to create session:", error);
        toast.error("セッションの作成に失敗しました");
      }
    };

    initSession();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim() || !sessionId) {
      return;
    }

    const userMessage: Message = {
      role: "user",
      content: input.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      let assistantContent = "";
      const assistantMessage: Message = {
        role: "assistant",
        content: "",
        timestamp: new Date().toISOString(),
      };

      // Add placeholder for assistant message
      setMessages((prev) => [...prev, assistantMessage]);

      // Stream the response with selected provider
      for await (const chunk of apiClient.chat(userMessage.content, sessionId, provider)) {
        if (chunk.type === "text" && chunk.content) {
          assistantContent += chunk.content;

          // Update the last message (assistant's message)
          setMessages((prev) => {
            const newMessages = [...prev];
            newMessages[newMessages.length - 1] = {
              ...assistantMessage,
              content: assistantContent,
            };
            return newMessages;
          });
        }
      }
    } catch (error) {
      console.error("Chat error:", error);
      toast.error("メッセージの送信に失敗しました");

      // Remove the placeholder assistant message on error
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full h-[600px] flex flex-col">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>法律相談 AI チャット</span>
          {sessionId && (
            <span className="text-xs font-normal text-muted-foreground">
              Session: {sessionId.slice(0, 8)}...
            </span>
          )}
        </CardTitle>
        {/* LLM Provider Selector */}
        <div className="flex items-center gap-2 mt-2">
          <label
            htmlFor="llm-provider"
            className="text-sm font-medium text-muted-foreground"
          >
            LLMプロバイダー:
          </label>
          <select
            id="llm-provider"
            value={provider}
            onChange={(e) => setProvider(e.target.value as LLMProvider)}
            disabled={isLoading}
            className="rounded-md border border-input bg-background px-3 py-1 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <option value="anthropic">Anthropic Claude</option>
            <option value="deepseek">DeepSeek AI</option>
            <option value="gemini">Google Gemini</option>
          </select>
        </div>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col p-4 gap-4">
        {/* Messages area */}
        <div className="flex-1 overflow-y-auto space-y-2 pr-2">
          {messages.length === 0 && (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              <div className="text-center">
                <p className="text-lg mb-2">👋 こんにちは！</p>
                <p className="text-sm">
                  法律に関する質問があればお聞きください。
                </p>
              </div>
            </div>
          )}

          {messages.map((message, index) => (
            <ChatMessage key={`${message.timestamp}-${index}`} message={message} />
          ))}

          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="メッセージを入力..."
            disabled={isLoading || !sessionId}
            className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          />
          <Button
            type="submit"
            size="icon"
            disabled={isLoading || !sessionId || !input.trim()}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
