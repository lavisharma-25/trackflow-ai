import { useState, type FormEvent } from "react";

import { ModalShell } from "../../shared/components/ModalShell";
import type { Collection, FieldDefinition, ItemInput } from "../../shared/types";

interface ItemFormProps {
  collection: Collection;
  onClose: () => void;
  onSubmit: (input: ItemInput) => Promise<void>;
}

export function ItemForm({ collection, onClose, onSubmit }: ItemFormProps) {
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [values, setValues] = useState<Record<string, unknown>>({});
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setFormError(null);
    const properties: Record<string, unknown> = {};
    collection.field_definitions.forEach((field) => {
      const raw = values[field.key];
      if (field.type === "boolean") {
        properties[field.key] = Boolean(raw);
        return;
      }
      if (raw === "" || raw === undefined) return;
      if (field.type === "integer") {
        properties[field.key] = Number.parseInt(String(raw), 10);
      } else if (field.type === "number") {
        properties[field.key] = Number(raw);
      } else if (field.type === "multi_select") {
        properties[field.key] = String(raw)
          .split(",")
          .map((part) => part.trim())
          .filter(Boolean);
      } else {
        properties[field.key] = raw;
      }
    });

    try {
      await onSubmit({ title, body, properties });
    } catch (reason) {
      setFormError(reason instanceof Error ? reason.message : "Unable to create item");
      setSubmitting(false);
    }
  }

  return (
    <ModalShell
      title={`Add to ${collection.name}`}
      subtitle="Capture it now. You can refine it later."
      onClose={onClose}
    >
      <form onSubmit={submit} className="modal-form">
        {formError && <div className="inline-error">{formError}</div>}
        <label className="form-field">
          <span>Title</span>
          <input
            autoFocus
            required
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="What do you want to remember?"
          />
        </label>
        <label className="form-field">
          <span>Notes <small>Optional</small></span>
          <textarea
            rows={3}
            value={body}
            onChange={(event) => setBody(event.target.value)}
            placeholder="Add context, details, or thoughts…"
          />
        </label>
        {collection.field_definitions.length > 0 && (
          <div className="dynamic-fields">
            <strong>Properties</strong>
            <div className="dynamic-grid">
              {collection.field_definitions.map((field) => (
                <DynamicField
                  key={field.key}
                  field={field}
                  value={values[field.key]}
                  onChange={(value) =>
                    setValues((current) => ({ ...current, [field.key]: value }))
                  }
                />
              ))}
            </div>
          </div>
        )}
        <div className="modal-actions">
          <button type="button" className="ghost-button" onClick={onClose}>Cancel</button>
          <button className="primary-button" disabled={submitting}>
            {submitting ? "Saving…" : "Save item"}
          </button>
        </div>
      </form>
    </ModalShell>
  );
}

function DynamicField({
  field,
  value,
  onChange,
}: {
  field: FieldDefinition;
  value: unknown;
  onChange: (value: unknown) => void;
}) {
  if (field.type === "boolean") {
    return (
      <label className="boolean-field">
        <input
          type="checkbox"
          checked={Boolean(value)}
          onChange={(event) => onChange(event.target.checked)}
        />
        <span><strong>{field.label}</strong><small>{field.required ? "Required" : "Optional"}</small></span>
      </label>
    );
  }
  if (field.type === "select") {
    return (
      <label className="form-field">
        <span>{field.label}{field.required && <b>*</b>}</span>
        <select
          required={field.required}
          value={String(value ?? "")}
          onChange={(event) => onChange(event.target.value)}
        >
          <option value="">Choose an option</option>
          {field.options.map((option) => <option key={option}>{option}</option>)}
        </select>
      </label>
    );
  }
  if (field.type === "multi_select") {
    return (
      <label className="form-field">
        <span>{field.label}{field.required && <b>*</b>}</span>
        <input
          required={field.required}
          value={String(value ?? "")}
          onChange={(event) => onChange(event.target.value)}
          placeholder={`Comma-separated: ${field.options.join(", ")}`}
        />
      </label>
    );
  }

  const inputType = field.type === "date"
    ? "date"
    : field.type === "datetime"
      ? "datetime-local"
      : field.type === "url"
        ? "url"
        : ["number", "integer"].includes(field.type)
          ? "number"
          : "text";

  return (
    <label className="form-field">
      <span>{field.label}{field.required && <b>*</b>}</span>
      <input
        type={inputType}
        step={field.type === "integer" ? "1" : field.type === "number" ? "any" : undefined}
        required={field.required}
        value={String(value ?? "")}
        onChange={(event) => onChange(event.target.value)}
        placeholder={`Enter ${field.label.toLowerCase()}`}
      />
    </label>
  );
}
