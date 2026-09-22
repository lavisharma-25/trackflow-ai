import { useState, type FormEvent } from "react";

import { ModalShell } from "../../shared/components/ModalShell";
import { Icon } from "../../shared/icons/Icon";
import type {
  CollectionInput,
  FieldDefinition,
  FieldType,
} from "../../shared/types";

interface CollectionFormProps {
  onClose: () => void;
  onSubmit: (input: CollectionInput) => Promise<void>;
}

export function CollectionForm({ onClose, onSubmit }: CollectionFormProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [fields, setFields] = useState<FieldDefinition[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  function addField() {
    setFields((current) => [
      ...current,
      { key: "", label: "", type: "string", required: false, options: [] },
    ]);
  }

  function updateField(index: number, patch: Partial<FieldDefinition>) {
    setFields((current) =>
      current.map((field, position) =>
        position === index ? { ...field, ...patch } : field,
      ),
    );
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setFormError(null);
    try {
      await onSubmit({ name, description, fields });
    } catch (reason) {
      setFormError(
        reason instanceof Error ? reason.message : "Unable to create collection",
      );
      setSubmitting(false);
    }
  }

  return (
    <ModalShell
      title="New collection"
      subtitle="Create a reusable structure for anything you want to track."
      onClose={onClose}
    >
      <form onSubmit={submit} className="modal-form">
        {formError && <div className="inline-error">{formError}</div>}
        <label className="form-field">
          <span>Name</span>
          <input
            autoFocus
            required
            maxLength={120}
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="e.g. Reading list"
          />
        </label>
        <label className="form-field">
          <span>Description <small>Optional</small></span>
          <textarea
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            placeholder="What belongs in this collection?"
            rows={2}
          />
        </label>
        <div className="field-builder">
          <div className="field-builder-heading">
            <div>
              <strong>Custom fields</strong>
              <span>Define the information every item can hold.</span>
            </div>
            <button type="button" onClick={addField}>
              <Icon name="plus" size={15} />Add field
            </button>
          </div>
          {fields.map((field, index) => (
            <div className="field-row" key={index}>
              <input
                required
                value={field.label}
                onChange={(event) => {
                  const label = event.target.value;
                  updateField(index, {
                    label,
                    key: label
                      .toLowerCase()
                      .trim()
                      .replace(/[^a-z0-9]+/g, "_")
                      .replace(/^_+|_+$/g, ""),
                  });
                }}
                placeholder="Field label"
                aria-label="Field label"
              />
              <input
                required
                pattern="[a-z][a-z0-9_]*"
                value={field.key}
                onChange={(event) =>
                  updateField(index, {
                    key: event.target.value.toLowerCase().replace(/\s+/g, "_"),
                  })
                }
                placeholder="field_key"
                aria-label="Field key"
              />
              <select
                value={field.type}
                onChange={(event) =>
                  updateField(index, {
                    type: event.target.value as FieldType,
                    options: [],
                  })
                }
                aria-label="Field type"
              >
                <option value="string">Text</option>
                <option value="integer">Integer</option>
                <option value="number">Number</option>
                <option value="boolean">Yes / No</option>
                <option value="date">Date</option>
                <option value="datetime">Date &amp; time</option>
                <option value="url">URL</option>
                <option value="select">Select</option>
                <option value="multi_select">Multi-select</option>
              </select>
              <label className="required-check">
                <input
                  type="checkbox"
                  checked={field.required}
                  onChange={(event) =>
                    updateField(index, { required: event.target.checked })
                  }
                />
                <span>Required</span>
              </label>
              <button
                className="remove-field"
                type="button"
                onClick={() =>
                  setFields((current) =>
                    current.filter((_, position) => position !== index),
                  )
                }
                aria-label="Remove field"
              >
                <Icon name="close" size={15} />
              </button>
              {(field.type === "select" || field.type === "multi_select") && (
                <input
                  className="options-input"
                  required
                  value={field.options.join(", ")}
                  onChange={(event) =>
                    updateField(index, {
                      options: event.target.value
                        .split(",")
                        .map((option) => option.trim())
                        .filter(Boolean),
                    })
                  }
                  placeholder="Options separated by commas"
                  aria-label="Select options"
                />
              )}
            </div>
          ))}
          {!fields.length && (
            <button className="empty-fields" type="button" onClick={addField}>
              <Icon name="plus" />Add fields such as status, date, amount, or category
            </button>
          )}
        </div>
        <div className="modal-actions">
          <button type="button" className="ghost-button" onClick={onClose}>Cancel</button>
          <button className="primary-button" disabled={submitting}>
            {submitting ? "Creating…" : "Create collection"}
          </button>
        </div>
      </form>
    </ModalShell>
  );
}
