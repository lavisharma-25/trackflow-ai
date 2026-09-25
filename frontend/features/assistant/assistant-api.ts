import { request } from "../../shared/api/client";

export interface LlmModelOption {
  id: string;
  name: string;
}

export interface LlmProviderOption {
  id: string;
  name: string;
  available: boolean;
  default_model: string | null;
  models: LlmModelOption[];
}

export interface LlmProviderCatalog {
  default_provider: string | null;
  providers: LlmProviderOption[];
}

export interface AssistantSelection {
  provider: string;
  model: string;
}

interface AssistantResponse {
  conversation_id: string;
  message: string;
  // These stay optional until the backend tutorial has been applied.
  provider?: string;
  model?: string;
}

export const assistantApi = {
  listProviders: () => request<LlmProviderCatalog>("/llm/providers"),

  ask: (
    message: string,
    conversationId?: string,
    selection?: AssistantSelection,
  ) =>
    request<AssistantResponse>("/assistant", {
      method: "POST",
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        ...(selection ?? {}),
      }),
    }),
};
