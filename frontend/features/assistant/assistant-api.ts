import { request } from "../../shared/api/client";

interface AssistantResponse {
  conversation_id: string;
  message: string;
}

export const assistantApi = {
  ask: (message: string, conversationId?: string) =>
    request<AssistantResponse>("/assistant", {
      method: "POST",
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
      }),
    }),
};
