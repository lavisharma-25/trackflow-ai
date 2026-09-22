import { useEffect, useRef, useState, type FormEvent } from "react";

import { Icon } from "../../shared/icons/Icon";
import type { ChatEntry } from "../../shared/types";
import { assistantApi } from "./assistant-api";

interface AssistantPanelProps {
  open: boolean;
  onClose: () => void;
  onDataChanged: () => Promise<void>;
}

export function AssistantPanel({ open, onClose, onDataChanged }: AssistantPanelProps) {
  const [messages, setMessages] = useState<ChatEntry[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Hi — I’m your TrackFlow assistant. Tell me what you want to capture or find.",
    },
  ]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<string>();
  const [sending, setSending] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Keep this callback return value undefined. Some Chromium builds return a
    // value from scrollIntoView that React can mistake for an effect cleanup.
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, open]);

  async function send(event: FormEvent) {
    event.preventDefault();
    const text = input.trim();
    if (!text || sending) return;

    setInput("");
    setSending(true);
    const userEntry: ChatEntry = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
    };
    const pendingId = crypto.randomUUID();
    setMessages((current) => [
      ...current,
      userEntry,
      { id: pendingId, role: "assistant", content: "Thinking", pending: true },
    ]);

    try {
      const response = await assistantApi.ask(text, conversationId);
      setConversationId(response.conversation_id);
      setMessages((current) =>
        current.map((entry) =>
          entry.id === pendingId
            ? { id: pendingId, role: "assistant", content: response.message }
            : entry,
        ),
      );
      await onDataChanged();
    } catch (reason) {
      const message = reason instanceof Error
        ? reason.message
        : "The assistant is unavailable.";
      setMessages((current) =>
        current.map((entry) =>
          entry.id === pendingId
            ? { id: pendingId, role: "assistant", content: message }
            : entry,
        ),
      );
    } finally {
      setSending(false);
    }
  }

  return (
    <aside className={`assistant-panel ${open ? "open" : ""}`} aria-hidden={!open}>
      <header>
        <div className="assistant-avatar"><Icon name="sparkles" size={18} /></div>
        <div><strong>TrackFlow AI</strong><span><i />Ready to help</span></div>
        <button className="icon-button" onClick={onClose} aria-label="Close assistant">
          <Icon name="close" />
        </button>
      </header>
      <div className="chat-context">
        <Icon name="book" size={15} />Has access to your active collections
      </div>
      <div className="chat-messages">
        {messages.map((message) => (
          <div key={message.id} className={`chat-message ${message.role}`}>
            <div>
              {message.pending
                ? <span className="typing"><i /><i /><i /></span>
                : message.content}
            </div>
          </div>
        ))}
        <div ref={endRef} />
      </div>
      <div className="prompt-chips">
        <button onClick={() => setInput("Create a habit tracker for me")}>Create a habit tracker</button>
        <button onClick={() => setInput("What have I saved recently?")}>Recent items</button>
      </div>
      <form className="chat-input" onSubmit={send}>
        <textarea
          rows={1}
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              event.currentTarget.form?.requestSubmit();
            }
          }}
          placeholder="Capture or ask anything…"
        />
        <button disabled={!input.trim() || sending} aria-label="Send message">
          <Icon name="send" size={17} />
        </button>
      </form>
      <small className="ai-disclaimer">AI can make mistakes. Verify important information.</small>
    </aside>
  );
}
