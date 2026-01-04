"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { Button, Input, ScrollArea } from "@/components/ui";
import { Send, Loader2, Bot, User, AlertCircle } from "lucide-react";
import { cn } from "@/src/utils";
import { apiClient } from "@/src/api";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  isError?: boolean;
}

interface ChatInterfaceProps {
  matchId: string;
  className?: string;
}

// Suggestion prompts for the user
const SUGGESTIONS = [
  "Analyze the pressing intensity",
  "Who covered the most distance?",
  "How did the first half compare to second?",
  "What were the key tactical patterns?",
];

function formatTime(timestamp: number): string {
  return new Date(timestamp).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

// Strip markdown code fences that wrap entire content
// Some AI models return responses wrapped in ```markdown ... ``` which prevents proper rendering
function stripCodeFences(content: string): string {
  // Match content wrapped in code fences like ```markdown\n...\n``` or just ```\n...\n```
  const codeFencePattern = /^```(?:markdown|md)?\s*\n?([\s\S]*?)\n?```$/;
  const match = content.trim().match(codeFencePattern);
  return match ? match[1].trim() : content;
}

export function ChatInterface({ matchId, className }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Local storage key for this match
  const storageKey = `chat-${matchId}`;

  // Set mounted state on client
  useEffect(() => {
    setMounted(true);
  }, []);

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

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      abortControllerRef.current?.abort();
    };
  }, []);

  // Send message to backend
  const handleSend = useCallback(
    async (text?: string) => {
      const messageText = text || input.trim();
      if (!messageText || isThinking) return;

      // Reset error state
      setConnectionError(null);

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

      // Create abort controller for this request
      abortControllerRef.current = new AbortController();

      try {
        // Call the SSE endpoint
        const response = await fetch(
          `${apiClient.defaults.baseURL}/chat/analyze`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-Correlation-ID": crypto.randomUUID().slice(0, 8),
            },
            body: JSON.stringify({
              match_id: matchId,
              query: messageText,
            }),
            signal: abortControllerRef.current.signal,
          }
        );

        if (!response.ok) {
          throw new Error(
            `Analysis request failed: ${response.status} ${response.statusText}`
          );
        }

        // Check if it's a streaming response
        const contentType = response.headers.get("content-type");

        if (contentType?.includes("text/event-stream")) {
          // Handle SSE stream
          const reader = response.body?.getReader();
          const decoder = new TextDecoder();
          let aiContent = "";

          if (reader) {
            try {
              while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const text = decoder.decode(value, { stream: true });
                const lines = text.split("\n");

                for (const line of lines) {
                  if (line.startsWith("data: ")) {
                    try {
                      const data = JSON.parse(line.slice(6));

                      if (data.type === "content" || data.type === "result") {
                        aiContent += data.content || data.text || "";
                      } else if (data.type === "thinking") {
                        // Update thinking status
                      } else if (data.type === "error") {
                        throw new Error(data.content || "Stream error");
                      } else if (data.type === "done") {
                        break;
                      }
                    } catch (parseError) {
                      // Skip malformed JSON
                    }
                  }
                }
              }
            } finally {
              reader.releaseLock();
            }
          }

          // Add AI response
          if (aiContent) {
            const aiMessage: ChatMessage = {
              id: crypto.randomUUID(),
              role: "assistant",
              content: aiContent,
              timestamp: Date.now(),
            };
            setMessages((prev) => [...prev, aiMessage]);
          }
        } else {
          // Handle regular JSON response
          const data = await response.json();

          const aiMessage: ChatMessage = {
            id: crypto.randomUUID(),
            role: "assistant",
            content:
              data.result ||
              data.message ||
              data.content ||
              "Analysis complete. Please provide more specific questions about the match.",
            timestamp: Date.now(),
          };
          setMessages((prev) => [...prev, aiMessage]);
        }
      } catch (error) {
        if ((error as Error).name === "AbortError") {
          // Request was cancelled
          return;
        }

        console.error("Chat error:", error);

        // Add error message
        const errorMessage: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: `Unable to connect to the analysis service. Error: ${
            (error as Error).message
          }`,
          timestamp: Date.now(),
          isError: true,
        };
        setMessages((prev) => [...prev, errorMessage]);
        setConnectionError("Backend service may be unavailable");
      } finally {
        setIsThinking(false);
        abortControllerRef.current = null;
      }
    },
    [input, isThinking, matchId]
  );

  // Cancel current request
  const handleCancel = useCallback(() => {
    abortControllerRef.current?.abort();
    setIsThinking(false);
  }, []);

  // Handle Enter key
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Clear chat history
  const handleClear = () => {
    setMessages([]);
    localStorage.removeItem(storageKey);
    setConnectionError(null);
  };

  return (
    <div className={cn("flex flex-col h-full", className)}>
      {/* Connection error banner */}
      {connectionError && (
        <div className="bg-destructive/10 border-b border-destructive/30 px-4 py-2 text-sm text-destructive flex items-center gap-2">
          <AlertCircle className="h-4 w-4" />
          {connectionError}
        </div>
      )}

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
                  <div
                    className={cn(
                      "h-8 w-8 rounded-full flex items-center justify-center shrink-0",
                      message.isError ? "bg-destructive/20" : "bg-primary/20"
                    )}
                  >
                    {message.isError ? (
                      <AlertCircle className="h-4 w-4 text-destructive" />
                    ) : (
                      <Bot className="h-4 w-4 text-primary" />
                    )}
                  </div>
                )}
                <div
                  className={cn(
                    "max-w-[80%] rounded-lg px-4 py-2",
                    message.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : message.isError
                      ? "bg-destructive/10 border border-destructive/30"
                      : "bg-muted"
                  )}
                >
                  {message.role === "assistant" ? (
                    <div className="text-sm space-y-2">
                      <ReactMarkdown
                        components={{
                          h1: ({ children }) => (
                            <h1 className="text-lg font-bold mt-3 mb-2">
                              {children}
                            </h1>
                          ),
                          h2: ({ children }) => (
                            <h2 className="text-base font-semibold mt-2 mb-1">
                              {children}
                            </h2>
                          ),
                          h3: ({ children }) => (
                            <h3 className="text-sm font-medium mt-2 mb-1">
                              {children}
                            </h3>
                          ),
                          p: ({ children }) => (
                            <p className="text-sm mb-2 last:mb-0">{children}</p>
                          ),
                          ul: ({ children }) => (
                            <ul className="list-disc list-inside text-sm mb-2 space-y-1">
                              {children}
                            </ul>
                          ),
                          ol: ({ children }) => (
                            <ol className="list-decimal list-inside text-sm mb-2 space-y-1">
                              {children}
                            </ol>
                          ),
                          li: ({ children }) => (
                            <li className="text-sm">{children}</li>
                          ),
                          pre: ({ children }) => (
                            <pre className="bg-black/40 p-3 rounded-md my-2 overflow-x-auto text-xs">
                              {children}
                            </pre>
                          ),
                          code: ({ children, className, ...props }) => {
                            // If wrapped in pre (has className with language), it's a code block
                            // Otherwise it's inline code
                            const isCodeBlock =
                              className?.includes("language-");
                            if (isCodeBlock) {
                              return (
                                <code className="font-mono">{children}</code>
                              );
                            }
                            // Inline code
                            return (
                              <code className="bg-black/30 px-1.5 py-0.5 rounded text-xs font-mono">
                                {children}
                              </code>
                            );
                          },
                          strong: ({ children }) => (
                            <strong className="font-semibold">
                              {children}
                            </strong>
                          ),
                          table: ({ children }) => (
                            <table className="text-xs border-collapse my-2 w-full">
                              {children}
                            </table>
                          ),
                          th: ({ children }) => (
                            <th className="border border-border/50 px-2 py-1 bg-muted/50 text-left">
                              {children}
                            </th>
                          ),
                          td: ({ children }) => (
                            <td className="border border-border/50 px-2 py-1">
                              {children}
                            </td>
                          ),
                        }}
                      >
                        {stripCodeFences(message.content)}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <p className="text-sm whitespace-pre-wrap">
                      {message.content}
                    </p>
                  )}
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
                  <span className="text-sm">Analyzing match data...</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleCancel}
                    className="h-6 px-2 text-xs"
                  >
                    Cancel
                  </Button>
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
        {messages.length > 0 && (
          <button
            onClick={handleClear}
            className="text-xs text-muted-foreground hover:text-foreground mt-2"
          >
            Clear history
          </button>
        )}
      </div>
    </div>
  );
}
