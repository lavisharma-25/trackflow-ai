export type FieldType =
  | "string"
  | "integer"
  | "number"
  | "boolean"
  | "date"
  | "datetime"
  | "url"
  | "select"
  | "multi_select";

export interface FieldDefinition {
  key: string;
  label: string;
  type: FieldType;
  required: boolean;
  options: string[];
}

export interface Collection {
  id: string;
  name: string;
  description: string;
  field_definitions: FieldDefinition[];
  created_at: string;
  updated_at: string;
  archived_at: string | null;
}

export interface Item {
  id: string;
  collection_id: string;
  title: string;
  body: string;
  properties: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  archived_at: string | null;
}

export interface CollectionInput {
  name: string;
  description: string;
  fields: FieldDefinition[];
}

export interface ItemInput {
  title: string;
  body: string;
  properties: Record<string, unknown>;
}

export interface ChatEntry {
  id: string;
  role: "user" | "assistant";
  content: string;
  pending?: boolean;
}
