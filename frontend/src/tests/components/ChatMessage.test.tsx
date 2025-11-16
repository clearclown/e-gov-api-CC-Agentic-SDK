import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ChatMessage } from "@/components/chat/ChatMessage";
import type { Message } from "@/lib/api-client";

describe("ChatMessage", () => {
  it("renders user message correctly", () => {
    const message: Message = {
      role: "user",
      content: "こんにちは",
      timestamp: new Date().toISOString(),
    };

    render(<ChatMessage message={message} />);

    expect(screen.getByText("こんにちは")).toBeInTheDocument();
    expect(screen.getByText("あなた")).toBeInTheDocument();
  });

  it("renders assistant message correctly", () => {
    const message: Message = {
      role: "assistant",
      content: "AIアシスタントです",
      timestamp: new Date().toISOString(),
    };

    render(<ChatMessage message={message} />);

    expect(screen.getByText("AIアシスタントです")).toBeInTheDocument();
    expect(screen.getByText("AI アシスタント")).toBeInTheDocument();
  });

  it("applies correct styling for user messages", () => {
    const message: Message = {
      role: "user",
      content: "テスト",
      timestamp: new Date().toISOString(),
    };

    const { container } = render(<ChatMessage message={message} />);
    const messageContainer = container.firstChild;

    expect(messageContainer).toHaveClass("justify-end");
  });

  it("applies correct styling for assistant messages", () => {
    const message: Message = {
      role: "assistant",
      content: "テスト",
      timestamp: new Date().toISOString(),
    };

    const { container } = render(<ChatMessage message={message} />);
    const messageContainer = container.firstChild;

    expect(messageContainer).toHaveClass("justify-start");
  });
});
