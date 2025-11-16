import { ChatWindow } from "@/components/chat/ChatWindow";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-background to-muted p-4 md:p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold tracking-tight">
            📚 e-gov 法律相談 AI
          </h1>
          <p className="text-muted-foreground">
            Claude Agent SDK を活用した法律相談チャットシステム
          </p>
        </div>

        {/* Chat Window */}
        <ChatWindow />

        {/* Footer */}
        <div className="text-center text-sm text-muted-foreground">
          <p>
            Powered by{" "}
            <a
              href="https://www.anthropic.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              Claude Agent SDK
            </a>
          </p>
        </div>
      </div>
    </main>
  );
}
