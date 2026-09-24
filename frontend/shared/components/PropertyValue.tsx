import { formatValue } from "../formatters";
import type { FieldDefinition } from "../types";

export function PropertyValue({
  field,
  value,
}: {
  field: FieldDefinition;
  value: unknown;
}) {
  if (field.type === "boolean" && value !== undefined) {
    return (
      <span className={`status-pill ${value ? "positive" : "neutral"}`}>
        <span />{value ? "Yes" : "No"}
      </span>
    );
  }
  if ((field.type === "select" || field.type === "multi_select") && value) {
    return <span className="tag-pill">{formatValue(value)}</span>;
  }
  if (field.type === "url" && typeof value === "string") {
    return (
      <a className="property-link" href={value} target="_blank" rel="noreferrer">
        Open link
      </a>
    );
  }
  return <>{formatValue(value)}</>;
}
