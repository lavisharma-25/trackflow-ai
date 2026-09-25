import { useEffect, useRef, useState, type FormEvent } from "react";

import { Icon } from "../../shared/icons/Icon";
import type { ChatEntry } from "../../shared/types";
import {
  assistantApi,
  type AssistantSelection,
  type LlmProviderCatalog,
  type LlmProviderOption,
} from "./assistant-api";

interface AssistantPanelProps {
  open: boolean;
  onClose: () => void;
  onDataChanged: () => Promise<void>;
}

const WELCOME_MESSAGE: ChatEntry = {
  id: "welcome",
  role: "assistant",
  content: "Hi — I’m your TrackFlow assistant. Tell me what you want to capture or find.",
};

type ProviderStatus = "idle" | "loading" | "ready" | "legacy";

function availableProviders(catalog: LlmProviderCatalog | null) {
  return catalog?.providers.filter(
    (provider) => provider.available && provider.models.length > 0,
  ) ?? [];
}

function defaultProvider(catalog: LlmProviderCatalog | null) {
  const providers = availableProviders(catalog);
  return providers.find((provider) => provider.id === catalog?.default_provider)
    ?? providers[0]
    ?? null;
}

function defaultModel(provider: LlmProviderOption | null) {
  return provider?.models.find((model) => model.id === provider.default_model)?.id
    ?? provider?.models[0]?.id
    ?? "";
}

export function AssistantPanel({ open, onClose, onDataChanged }: AssistantPanelProps) {
  const [messages, setMessages] = useState<ChatEntry[]>([WELCOME_MESSAGE]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<string>();
  const [sending, setSending] = useState(false);
  const [providerStatus, setProviderStatus] = useState<ProviderStatus>("idle");
  const [providerCatalog, setProviderCatalog] = useState<LlmProviderCatalog | null>(null);
  const [providerError, setProviderError] = useState<string>();
  const [selectedProviderId, setSelectedProviderId] = useState("");
  const [selectedModelId, setSelectedModelId] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  const providers = availableProviders(providerCatalog);
  const selectedProvider = providers.find(
    (provider) => provider.id === selectedProviderId,
  ) ?? null;
  const selectionLocked = Boolean(conversationId);
  const selectionReady = providerStatus === "legacy"
    || (providerStatus === "ready" && Boolean(selectedProvider && selectedModelId));

  useEffect(() => {
    if (!open || providerStatus !== "idle") return;

    setProviderStatus("loading");
    assistantApi.listProviders()
      .then((catalog) => {
        const provider = defaultProvider(catalog);
        setProviderCatalog(catalog);
        setSelectedProviderId(provider?.id ?? "");
        setSelectedModelId(defaultModel(provider));
        setProviderError(undefined);
        setProviderStatus("ready");
      })
      .catch(() => {
        // The original backend has no provider-discovery endpoint. Keep it
        // working by omitting provider/model from assistant requests.
        setProviderCatalog(null);
        setSelectedProviderId("");
        setSelectedModelId("");
        setProviderError("Provider options are unavailable. Using the server default.");
        setProviderStatus("legacy");
      });
  }, [open, providerStatus]);

  useEffect(() => {
    // Keep this callback return value undefined. Some Chromium builds return a
    // value from scrollIntoView that React can mistake for an effect cleanup.
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, open]);

  function changeProvider(providerId: string) {
    const provider = providers.find((entry) => entry.id === providerId) ?? null;
    setSelectedProviderId(provider?.id ?? "");
    setSelectedModelId(defaultModel(provider));
  }

  function startNewChat() {
    const provider = defaultProvider(providerCatalog);
    setMessages([WELCOME_MESSAGE]);
    setInput("");
    setConversationId(undefined);
    setSelectedProviderId(provider?.id ?? "");
    setSelectedModelId(defaultModel(provider));
  }

  async function send(event: FormEvent) {
    event.preventDefault();
    const text = input.trim();
    if (!text || sending || !selectionReady) return;

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
      const selection: AssistantSelection | undefined = providerStatus === "ready"
        ? { provider: selectedProviderId, model: selectedModelId }
        : undefined;
      const response = await assistantApi.ask(text, conversationId, selection);
      setConversationId(response.conversation_id);
      if (response.provider) setSelectedProviderId(response.provider);
      if (response.model) setSelectedModelId(response.model);
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
        <div>
          <strong>TrackFlow AI</strong>
          <span>
            <i />
            {selectedProvider?.name
              ?? (providerStatus === "loading" ? "Loading services" : "Ready to help")}
          </span>
        </div>
        <button
          className="new-chat-button"
          onClick={startNewChat}
          disabled={sending}
          type="button"
        >
          New chat
        </button>
        <button className="icon-button" onClick={onClose} aria-label="Close assistant">
          <Icon name="close" />
        </button>
      </header>
      <div className="assistant-config">
        <label>
          <span>Service</span>
          <select
            value={providerStatus === "legacy" ? "server-default" : selectedProviderId}
            onChange={(event) => changeProvider(event.target.value)}
            disabled={providerStatus !== "ready" || selectionLocked || sending || !providers.length}
          >
            {providerStatus === "loading" && <option value="">Loading...</option>}
            {providerStatus === "legacy" && (
              <option value="server-default">Server default</option>
            )}
            {providerStatus === "ready" && !providers.length && (
              <option value="">No services configured</option>
            )}
            {providerCatalog?.providers.map((provider) => (
              <option
                key={provider.id}
                value={provider.id}
                disabled={!provider.available || !provider.models.length}
              >
                {provider.name}
                {provider.available && provider.models.length ? "" : " (unavailable)"}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>Model</span>
          <select
            value={providerStatus === "legacy" ? "server-default" : selectedModelId}
            onChange={(event) => setSelectedModelId(event.target.value)}
            disabled={providerStatus !== "ready" || selectionLocked || sending || !selectedProvider}
          >
            {providerStatus === "loading" && <option value="">Loading...</option>}
            {providerStatus === "legacy" && (
              <option value="server-default">Server default</option>
            )}
            {providerStatus === "ready" && !selectedProvider && (
              <option value="">No models available</option>
            )}
            {selectedProvider?.models.map((model) => (
              <option key={model.id} value={model.id}>{model.name}</option>
            ))}
          </select>
        </label>
      </div>
      <div
        className={`chat-context ${providerStatus === "ready" && !providers.length ? "error" : ""}`}
      >
        <Icon name="book" size={15} />
        {providerStatus === "ready" && !providers.length
          ? "No LLM service is configured on the backend."
          : providerError ?? (selectionLocked
            ? "Service and model are locked for this conversation."
            : "Has access to your active collections")}
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
        <button disabled={!input.trim() || sending || !selectionReady} aria-label="Send message">
          <Icon name="send" size={17} />
        </button>
      </form>
      <small className="ai-disclaimer">AI can make mistakes. Verify important information.</small>
    </aside>
  );
}
