import type { Collection, CollectionInput, Item, ItemInput } from "./types";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000/api/v1";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });
  } catch {
    throw new Error("Cannot reach the TrackFlow backend. Is it running on port 8000?");
  }

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    const detail = payload?.detail;
    const message = Array.isArray(detail)
      ? detail.map((entry) => entry.msg).join(", ")
      : detail || `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export const api = {
  listCollections: () => request<Collection[]>("/collections"),

  createCollection: (input: CollectionInput) =>
    request<Collection>("/collections", {
      method: "POST",
      body: JSON.stringify(input),
    }),

  listItems: (collectionId: string, search = "") => {
    const query = search.trim() ? `?search=${encodeURIComponent(search.trim())}` : "";
    return request<Item[]>(`/collections/${collectionId}/items${query}`);
  },

  createItem: (collectionId: string, input: ItemInput) =>
    request<Item>(`/collections/${collectionId}/items`, {
      method: "POST",
      body: JSON.stringify(input),
    }),

  archiveItem: (collectionId: string, itemId: string) =>
    request<Item>(`/collections/${collectionId}/items/${itemId}?confirmed=true`, {
      method: "DELETE",
    }),

  askAssistant: (message: string, conversationId?: string) =>
    request<{ conversation_id: string; message: string }>("/assistant", {
      method: "POST",
      body: JSON.stringify({ message, conversation_id: conversationId }),
    }),
};
