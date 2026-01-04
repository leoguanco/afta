# Implementation Plan: Chat Interface Component

> **Reference Spec:** [05_chat_interface_spec.md](./05_chat_interface_spec.md)

## Overview

AI-powered chat for natural language match analysis queries. Uses SSE streaming for real-time responses.

---

## Design Reference

Based on mockups:

- **Layout:** Right sidebar panel
- **Messages:** Bubble style (user right, AI left)
- **Input:** Fixed at bottom with send button
- **Status:** Typing indicator, loading states

---

## Component Structure

```
components/chat/
├── ChatInterface.tsx      # Main container
├── MessageList.tsx        # Scrollable message area
├── ChatMessage.tsx        # Individual message bubble
├── ChatInput.tsx          # Input field + send button
├── ThinkingIndicator.tsx  # "AI is thinking..." animation
└── hooks/
    └── useAnalysis.ts     # SSE streaming hook
```

---

## Implementation Steps

### 1. ChatInterface Container

```tsx
interface ChatInterfaceProps {
  matchId: string;
  className?: string;
}

export function ChatInterface({ matchId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isThinking, setIsThinking] = useState(false);

  // Load from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(`chat-${matchId}`);
    if (stored) setMessages(JSON.parse(stored));
  }, [matchId]);

  // Persist to localStorage
  useEffect(() => {
    localStorage.setItem(`chat-${matchId}`, JSON.stringify(messages));
  }, [messages, matchId]);

  return (
    <div className="flex flex-col h-full">
      <MessageList messages={messages} />
      {isThinking && <ThinkingIndicator />}
      <ChatInput onSend={handleSend} disabled={isThinking} />
    </div>
  );
}
```

### 2. Message List

```tsx
<ScrollArea className="flex-1 p-4">
  {messages.map((msg, idx) => (
    <ChatMessage key={idx} message={msg} />
  ))}
  <div ref={scrollRef} /> {/* Auto-scroll anchor */}
</ScrollArea>
```

### 3. Chat Message Bubble

```tsx
interface ChatMessageProps {
  message: {
    role: "user" | "assistant";
    content: string;
    timestamp: number;
  };
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={cn("mb-4 flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[80%] rounded-lg px-4 py-2",
          isUser ? "bg-primary text-primary-foreground" : "bg-muted"
        )}
      >
        <p className="text-sm">{message.content}</p>
        <span className="text-xs opacity-60">
          {formatTime(message.timestamp)}
        </span>
      </div>
    </div>
  );
}
```

### 4. Chat Input

```tsx
export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (value.trim() && !disabled) {
      onSend(value.trim());
      setValue("");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t p-4">
      <div className="flex gap-2">
        <Input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Ask about the match..."
          disabled={disabled}
        />
        <Button type="submit" disabled={disabled || !value.trim()}>
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </form>
  );
}
```

### 5. SSE Streaming Hook

```tsx
export function useAnalysisStream() {
  const streamAnalysis = async (
    matchId: string,
    query: string,
    onChunk: (chunk: StreamEvent) => void
  ) => {
    const response = await fetch("/api/v1/chat/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ match_id: matchId, query }),
    });

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader!.read();
      if (done) break;

      const text = decoder.decode(value);
      const lines = text.split("\n").filter((l) => l.startsWith("data: "));

      for (const line of lines) {
        const data = JSON.parse(line.slice(6));
        onChunk(data);
      }
    }
  };

  return { streamAnalysis };
}
```

### 6. Thinking Indicator

```tsx
export function ThinkingIndicator() {
  return (
    <div className="flex items-center gap-2 px-4 py-2 text-muted-foreground">
      <Loader2 className="h-4 w-4 animate-spin" />
      <span className="text-sm">AI is analyzing...</span>
    </div>
  );
}
```

---

## Example Queries

- "What was our pressing intensity in the first half?"
- "Who covered the most distance?"
- "Analyze the goal-scoring opportunity at minute 23"
- "How did our defensive shape change after the substitution?"

---

## Verification

- [ ] Messages render correctly (user/AI)
- [ ] SSE streaming displays chunks
- [ ] Thinking indicator appears during processing
- [ ] Chat history persists in localStorage
- [ ] Auto-scroll to latest message
- [ ] Input disabled while processing
