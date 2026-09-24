import { request } from "../../shared/api/client";
import type { Collection, CollectionInput } from "../../shared/types";

export const collectionApi = {
  list: () => request<Collection[]>("/collections"),

  create: (input: CollectionInput) =>
    request<Collection>("/collections", {
      method: "POST",
      body: JSON.stringify(input),
    }),
};
