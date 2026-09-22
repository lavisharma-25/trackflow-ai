import { request } from "../../shared/api/client";
import type { Item, ItemInput } from "../../shared/types";

export const itemApi = {
  list: (collectionId: string, search = "") => {
    const query = search.trim()
      ? `?search=${encodeURIComponent(search.trim())}`
      : "";
    return request<Item[]>(`/collections/${collectionId}/items${query}`);
  },

  create: (collectionId: string, input: ItemInput) =>
    request<Item>(`/collections/${collectionId}/items`, {
      method: "POST",
      body: JSON.stringify(input),
    }),

  archive: (collectionId: string, itemId: string) =>
    request<Item>(
      `/collections/${collectionId}/items/${itemId}?confirmed=true`,
      { method: "DELETE" },
    ),
};
