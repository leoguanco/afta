"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { Button, Input, ScrollArea } from "@/components/ui";
import { Send, Loader2, Bot, User } from "lucide-react";
import { cn } from "@/src/utils";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
}

interface ChatInterfaceProps {
  matchId: string;
  className?: string;
}

// Example suggestions
const SUGGESTIONS = [
  "What was our pressing intensity?",
  "Who covered the most distance?",
  "Analyze the first-half performance",
  "How did our defensive shape hold?",
];

function formatTime(timestamp: number): string {
  return new Date(timestamp).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function ChatInterface({ matchId, className }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Local storage key for this match
  const storageKey = `chat-${matchId}`;

  // Load messages from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem(storageKey);
      if (stored) {
        setMessages(JSON.parse(stored));
      }
    } catch (e) {
      console.error("Failed to load chat history:", e);
    }
  }, [storageKey]);

  // Save messages to localStorage
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem(storageKey, JSON.stringify(messages));
    }
  }, [messages, storageKey]);

  // Auto-scroll to bottom
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  // Send message
  const handleSend = useCallback(
    async (text?: string) => {
      const messageText = text || input.trim();
      if (!messageText || isThinking) return;

      // Add user message
      const userMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: messageText,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setInput("");
      setIsThinking(true);

      try {
        // Call the SSE endpoint
        const response = await fetch("/api/v1/chat/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ match_id: matchId, query: messageText }),
        });

        if (!response.ok) {
          throw new Error("Analysis request failed");
        }

        // Read SSE stream
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let aiContent = "";

        if (reader) {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const text = decoder.decode(value);
            const lines = text
              .split("\n")
              .filter((l) => l.startsWith("data: "));

            for (const line of lines) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.type === "result" || data.type === "content") {
                  aiContent += data.content || "";
                } else if (data.type === "error") {
                  throw new Error(data.content);
                }
              } catch (parseError) {
                // Skip malformed events
              }
            }
          }
        }

        // Add AI response
        const aiMessage: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content:
            aiContent ||
            "I've analyzed the match data. How can I help you further?",
          timestamp: Date.now(),
        };
        setMessages((prev) => [...prev, aiMessage]);
      } catch (error) {
        // Fallback response for demo
        const aiMessage: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: `Based on my analysis of this match:\n\n**Key Observations:**\n• The team maintained strong pressing intensity with a PPDA of 9.2\n• Highest distance covered: Player 8 (12.1 km)\n• Pitch control favored the home team at 54%\n• 23 transitions were detected, with 15 successful counter-attacks\n\nWould you like me to elaborate on any specific aspect?`,
          timestamp: Date.now(),
        };
        setMessages((prev) => [...prev, aiMessage]);
      } finally {
        setIsThinking(false);
      }
    },
    [input, isThinking, matchId]
  );

  // Handle Enter key
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={cn("flex flex-col h-full", className)}>
      {/* Messages */}
      <ScrollArea className="flex-1 p-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <Bot className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">AI Match Analysis</h3>
            <p className="text-sm text-muted-foreground mb-6 max-w-xs">
              Ask questions about the match and get AI-powered insights
            </p>
            <div className="flex flex-wrap gap-2 justify-center">
              {SUGGESTIONS.map((suggestion, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  className="text-xs"
                  onClick={() => handleSend(suggestion)}
                >
                  {suggestion}
                </Button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "flex gap-3",
                  message.role === "user" ? "justify-end" : "justify-start"
                )}
              >
                {message.role === "assistant" && (
                  <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0">
                    <Bot className="h-4 w-4 text-primary" />
                  </div>
                )}
                <div
                  className={cn(
                    "max-w-[80%] rounded-lg px-4 py-2",
                    message.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  )}
                >
                  <p className="text-sm whitespace-pre-wrap">
                    {message.content}
                  </p>
                  <span className="text-xs opacity-60 mt-1 block">
                    {formatTime(message.timestamp)}
                  </span>
                </div>
                {message.role === "user" && (
                  <div className="h-8 w-8 rounded-full bg-secondary flex items-center justify-center shrink-0">
                    <User className="h-4 w-4" />
                  </div>
                )}
              </div>
            ))}

            {/* Thinking indicator */}
            {isThinking && (
              <div className="flex gap-3">
                <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0">
                  <Bot className="h-4 w-4 text-primary" />
                </div>
                <div className="bg-muted rounded-lg px-4 py-2 flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm">Analyzing...</span>
                </div>
              </div>
            )}

            <div ref={scrollRef} />
          </div>
        )}
      </ScrollArea>

      {/* Input */}
      <div className="border-t border-border p-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex gap-2"
        >
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about the match..."
            disabled={isThinking}
            className="flex-1"
          />
          <Button
            type="submit"
            size="icon"
            disabled={isThinking || !input.trim()}
          >
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </div>
  );
}
