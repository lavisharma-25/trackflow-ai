import { useEffect, useMemo, useRef, useState } from "react";
import { api } from "./api";
import type {
  ChatEntry,
  Collection,
  CollectionInput,
  FieldDefinition,
  FieldType,
  Item,
  ItemInput,
} from "./types";

type IconName =
  | "archive"
  | "book"
  | "check"
  | "chevron"
  | "close"
  | "grid"
  | "inbox"
  | "list"
  | "plus"
  | "search"
  | "send"
  | "sparkles";

function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  const paths: Record<IconName, React.ReactNode> = {
    archive: <><path d="M4 7h16v13H4z"/><path d="M2.5 4h19v3h-19zM9 11h6"/></>,
    book: <><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21.5z"/><path d="M4 5.5v16"/></>,
    check: <path d="m5 12 4 4L19 6"/>,
    chevron: <path d="m9 18 6-6-6-6"/>,
    close: <path d="M18 6 6 18M6 6l12 12"/>,
    grid: <><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></>,
    inbox: <><path d="M4 4h16l2 12H16l-2 3h-4l-2-3H2z"/><path d="M9 9h6"/></>,
    list: <><path d="M8 6h13M8 12h13M8 18h13"/><circle cx="3.5" cy="6" r=".5"/><circle cx="3.5" cy="12" r=".5"/><circle cx="3.5" cy="18" r=".5"/></>,
    plus: <path d="M12 5v14M5 12h14"/>,
    search: <><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></>,
    send: <><path d="m22 2-7 20-4-9-9-4z"/><path d="M22 2 11 13"/></>,
    sparkles: <><path d="m12 3 1.3 3.7L17 8l-3.7 1.3L12 13l-1.3-3.7L7 8l3.7-1.3z"/><path d="m5 14 .8 2.2L8 17l-2.2.8L5 20l-.8-2.2L2 17l2.2-.8zM19 13l.6 1.4L21 15l-1.4.6L19 17l-.6-1.4L17 15l1.4-.6z"/></>,
  };

  return (
    <svg
      aria-hidden="true"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {paths[name]}
    </svg>
  );
}

function initials(name: string) {
  return name
    .split(/\s+/)
    .map((word) => word[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

function formatValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (Array.isArray(value)) return value.join(", ");
  return String(value);
}

function relativeDate(value: string) {
  const delta = Date.now() - new Date(value).getTime();
  const minutes = Math.max(1, Math.floor(delta / 60_000));
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return days === 1 ? "Yesterday" : `${days}d ago`;
}

function App() {
  const [collections, setCollections] = useState<Collection[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [items, setItems] = useState<Item[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [itemsLoading, setItemsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modal, setModal] = useState<"collection" | "item" | null>(null);
  const [assistantOpen, setAssistantOpen] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [view, setView] = useState<"table" | "cards">("table");

  const selected = useMemo(
    () => collections.find((collection) => collection.id === selectedId) ?? null,
    [collections, selectedId],
  );

  async function refreshCollections(preferredId?: string) {
    const data = await api.listCollections();
    setCollections(data);
    setSelectedId((current) => {
      const next = preferredId ?? current;
      return data.some((collection) => collection.id === next) ? next : data[0]?.id ?? null;
    });
    return data;
  }

  useEffect(() => {
    refreshCollections()
      .catch((reason: Error) => setError(reason.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    function openAssistant(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setAssistantOpen(true);
      }
    }
    window.addEventListener("keydown", openAssistant);
    return () => window.removeEventListener("keydown", openAssistant);
  }, []);

  useEffect(() => {
    if (!selectedId) {
      setItems([]);
      return;
    }
    setItemsLoading(true);
    const timer = window.setTimeout(() => {
      api
        .listItems(selectedId, search)
        .then(setItems)
        .catch((reason: Error) => setError(reason.message))
        .finally(() => setItemsLoading(false));
    }, 220);
    return () => window.clearTimeout(timer);
  }, [selectedId, search]);

  async function handleCollectionCreate(input: CollectionInput) {
    const created = await api.createCollection(input);
    await refreshCollections(created.id);
    setModal(null);
  }

  async function handleItemCreate(input: ItemInput) {
    if (!selected) return;
    await api.createItem(selected.id, input);
    setItems(await api.listItems(selected.id, search));
    setModal(null);
  }

  async function handleArchive(item: Item) {
    if (!selected || !window.confirm(`Archive “${item.title}”? You can restore it through the API.`)) {
      return;
    }
    try {
      await api.archiveItem(selected.id, item.id);
      setItems((current) => current.filter((entry) => entry.id !== item.id));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to archive item");
    }
  }

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="brand-row">
          <div className="brand-mark"><Icon name="sparkles" size={19} /></div>
          <div><strong>TrackFlow</strong><span>AI second brain</span></div>
          <button className="icon-button sidebar-close" onClick={() => setSidebarOpen(false)} aria-label="Close navigation">
            <Icon name="close" />
          </button>
        </div>

        <nav className="primary-nav" aria-label="Primary navigation">
          <button className="nav-item active"><Icon name="inbox" /><span>Workspace</span></button>
          <button className="nav-item" onClick={() => setAssistantOpen(true)}><Icon name="sparkles" /><span>Ask TrackFlow</span><kbd>⌘K</kbd></button>
        </nav>

        <div className="sidebar-section">
          <div className="section-label"><span>Collections</span><button onClick={() => setModal("collection")} aria-label="New collection"><Icon name="plus" size={15} /></button></div>
          <div className="collection-nav">
            {collections.map((collection, index) => (
              <button
                className={`collection-link ${collection.id === selectedId ? "selected" : ""}`}
                key={collection.id}
                onClick={() => { setSelectedId(collection.id); setSearch(""); setSidebarOpen(false); }}
              >
                <span className={`collection-dot dot-${index % 5}`}>{initials(collection.name)}</span>
                <span>{collection.name}</span>
                <small>{collection.field_definitions.length}</small>
              </button>
            ))}
          </div>
          {!collections.length && !loading && <p className="sidebar-empty">Create your first collection to start organizing.</p>}
        </div>

        <div className="sidebar-footer">
          <div className="profile-avatar">LS</div>
          <div><strong>My workspace</strong><span>Local & private</span></div>
          <Icon name="chevron" size={15} />
        </div>
      </aside>

      {sidebarOpen && <button className="sidebar-scrim" onClick={() => setSidebarOpen(false)} aria-label="Close navigation" />}

      <main className="main-content">
        <header className="topbar">
          <button className="mobile-menu" onClick={() => setSidebarOpen(true)} aria-label="Open navigation"><Icon name="list" /></button>
          <div className="breadcrumbs"><span>Workspace</span><Icon name="chevron" size={13} /><strong>{selected?.name ?? "Home"}</strong></div>
          <div className="topbar-actions">
            <div className="connection-pill"><span /><span>Local</span></div>
            <button className="assistant-trigger" onClick={() => setAssistantOpen(true)}><Icon name="sparkles" size={17} /><span>Ask AI</span></button>
          </div>
        </header>

        {error && (
          <div className="error-banner" role="alert">
            <span>{error}</span><button onClick={() => setError(null)}><Icon name="close" size={16} /></button>
          </div>
        )}

        {loading ? (
          <LoadingState />
        ) : selected ? (
          <section className="workspace-page">
            <div className="page-heading">
              <div>
                <div className="eyebrow"><span className="eyebrow-dot" />Live collection</div>
                <h1>{selected.name}</h1>
                <p>{selected.description || "A flexible place for everything you want to remember."}</p>
              </div>
              <button className="primary-button" onClick={() => setModal("item")}><Icon name="plus" /><span>New item</span></button>
            </div>

            <div className="stat-row">
              <article className="stat-card"><div className="stat-icon indigo"><Icon name="inbox" /></div><div><strong>{items.length}</strong><span>{search ? "Matches" : "Active items"}</span></div></article>
              <article className="stat-card"><div className="stat-icon amber"><Icon name="grid" /></div><div><strong>{selected.field_definitions.length}</strong><span>Custom fields</span></div></article>
              <article className="stat-card"><div className="stat-icon mint"><Icon name="check" /></div><div><strong>{items[0] ? relativeDate(items[0].updated_at) : "—"}</strong><span>Last updated</span></div></article>
            </div>

            <div className="content-card">
              <div className="content-toolbar">
                <div className="search-box"><Icon name="search" size={17} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder={`Search ${selected.name.toLowerCase()}…`} /></div>
                <div className="view-toggle" aria-label="Change view">
                  <button className={view === "table" ? "active" : ""} onClick={() => setView("table")} aria-label="Table view"><Icon name="list" size={17} /></button>
                  <button className={view === "cards" ? "active" : ""} onClick={() => setView("cards")} aria-label="Card view"><Icon name="grid" size={16} /></button>
                </div>
              </div>

              {itemsLoading ? <ItemsSkeleton /> : items.length ? (
                view === "table" ? (
                  <ItemsTable collection={selected} items={items} onArchive={handleArchive} />
                ) : (
                  <ItemsGrid collection={selected} items={items} onArchive={handleArchive} />
                )
              ) : (
                <EmptyItems searching={Boolean(search)} onCreate={() => setModal("item")} />
              )}
            </div>
          </section>
        ) : (
          <WelcomeState onCreate={() => setModal("collection")} onAssistant={() => setAssistantOpen(true)} />
        )}
      </main>

      {modal === "collection" && <CollectionModal onClose={() => setModal(null)} onSubmit={handleCollectionCreate} />}
      {modal === "item" && selected && <ItemModal collection={selected} onClose={() => setModal(null)} onSubmit={handleItemCreate} />}
      <AssistantPanel
        open={assistantOpen}
        onClose={() => setAssistantOpen(false)}
        onDataChanged={async () => {
          const data = await refreshCollections();
          const activeId = selectedId && data.some((entry) => entry.id === selectedId) ? selectedId : data[0]?.id;
          if (activeId) setItems(await api.listItems(activeId, search));
        }}
      />
      <button className="floating-ai" onClick={() => setAssistantOpen(true)} aria-label="Open AI assistant"><Icon name="sparkles" size={21} /></button>
    </div>
  );
}

function LoadingState() {
  return <div className="page-loading"><div className="loader-mark"><Icon name="sparkles" size={26} /></div><strong>Opening your workspace</strong><span>Connecting to your second brain…</span></div>;
}

function ItemsSkeleton() {
  return <div className="skeleton-list">{[1, 2, 3].map((row) => <div className="skeleton-row" key={row}><span /><span /><span /></div>)}</div>;
}

function EmptyItems({ searching, onCreate }: { searching: boolean; onCreate: () => void }) {
  return (
    <div className="empty-state">
      <div className="empty-illustration"><Icon name={searching ? "search" : "book"} size={27} /></div>
      <h3>{searching ? "No matching items" : "A blank page, ready for ideas"}</h3>
      <p>{searching ? "Try a broader phrase or clear your search." : "Add your first item manually or ask TrackFlow AI to capture it for you."}</p>
      {!searching && <button className="secondary-button" onClick={onCreate}><Icon name="plus" size={17} />Add first item</button>}
    </div>
  );
}

function WelcomeState({ onCreate, onAssistant }: { onCreate: () => void; onAssistant: () => void }) {
  return (
    <section className="welcome-state">
      <div className="welcome-orbit"><span /><span /><div><Icon name="sparkles" size={32} /></div></div>
      <div className="eyebrow"><span className="eyebrow-dot" />Your knowledge, connected</div>
      <h1>Build a second brain<br />that thinks with you.</h1>
      <p>Capture expenses, habits, books, ideas, or anything else. TrackFlow gives every thought a place and makes it easy to find again.</p>
      <div className="welcome-actions"><button className="primary-button" onClick={onCreate}><Icon name="plus" />Create a collection</button><button className="secondary-button" onClick={onAssistant}><Icon name="sparkles" />Start with AI</button></div>
    </section>
  );
}

function ItemsTable({ collection, items, onArchive }: { collection: Collection; items: Item[]; onArchive: (item: Item) => void }) {
  return (
    <div className="table-scroll">
      <table className="items-table">
        <thead><tr><th>Title</th>{collection.field_definitions.map((field) => <th key={field.key}>{field.label}</th>)}<th>Updated</th><th><span className="sr-only">Actions</span></th></tr></thead>
        <tbody>{items.map((item) => (
          <tr key={item.id}>
            <td><div className="title-cell"><span>{initials(item.title)}</span><div><strong>{item.title}</strong>{item.body && <small>{item.body}</small>}</div></div></td>
            {collection.field_definitions.map((field) => <td key={field.key}><PropertyValue field={field} value={item.properties[field.key]} /></td>)}
            <td className="muted-cell">{relativeDate(item.updated_at)}</td>
            <td><button className="row-action" onClick={() => onArchive(item)} title="Archive item" aria-label={`Archive ${item.title}`}><Icon name="archive" size={16} /></button></td>
          </tr>
        ))}</tbody>
      </table>
    </div>
  );
}

function ItemsGrid({ collection, items, onArchive }: { collection: Collection; items: Item[]; onArchive: (item: Item) => void }) {
  return <div className="items-grid">{items.map((item) => (
    <article className="item-card" key={item.id}>
      <div className="item-card-top"><span className="item-monogram">{initials(item.title)}</span><button className="row-action" onClick={() => onArchive(item)} aria-label={`Archive ${item.title}`}><Icon name="archive" size={16} /></button></div>
      <h3>{item.title}</h3>{item.body && <p>{item.body}</p>}
      <dl>{collection.field_definitions.slice(0, 4).map((field) => <div key={field.key}><dt>{field.label}</dt><dd><PropertyValue field={field} value={item.properties[field.key]} /></dd></div>)}</dl>
      <footer>Updated {relativeDate(item.updated_at)}</footer>
    </article>
  ))}</div>;
}

function PropertyValue({ field, value }: { field: FieldDefinition; value: unknown }) {
  if (field.type === "boolean" && value !== undefined) return <span className={`status-pill ${value ? "positive" : "neutral"}`}><span />{value ? "Yes" : "No"}</span>;
  if ((field.type === "select" || field.type === "multi_select") && value) return <span className="tag-pill">{formatValue(value)}</span>;
  if (field.type === "url" && typeof value === "string") return <a className="property-link" href={value} target="_blank" rel="noreferrer">Open link</a>;
  return <>{formatValue(value)}</>;
}

function ModalShell({ title, subtitle, onClose, children }: { title: string; subtitle: string; onClose: () => void; children: React.ReactNode }) {
  return <div className="modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}><section className="modal" role="dialog" aria-modal="true"><header><div><h2>{title}</h2><p>{subtitle}</p></div><button className="icon-button" onClick={onClose} aria-label="Close"><Icon name="close" /></button></header>{children}</section></div>;
}

function CollectionModal({ onClose, onSubmit }: { onClose: () => void; onSubmit: (input: CollectionInput) => Promise<void> }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [fields, setFields] = useState<FieldDefinition[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  function addField() {
    setFields((current) => [...current, { key: "", label: "", type: "string", required: false, options: [] }]);
  }

  function updateField(index: number, patch: Partial<FieldDefinition>) {
    setFields((current) => current.map((field, position) => position === index ? { ...field, ...patch } : field));
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault(); setSubmitting(true); setFormError(null);
    try { await onSubmit({ name, description, fields }); }
    catch (reason) { setFormError(reason instanceof Error ? reason.message : "Unable to create collection"); setSubmitting(false); }
  }

  return (
    <ModalShell title="New collection" subtitle="Create a reusable structure for anything you want to track." onClose={onClose}>
      <form onSubmit={submit} className="modal-form">
        {formError && <div className="inline-error">{formError}</div>}
        <label className="form-field"><span>Name</span><input autoFocus required maxLength={120} value={name} onChange={(event) => setName(event.target.value)} placeholder="e.g. Reading list" /></label>
        <label className="form-field"><span>Description <small>Optional</small></span><textarea value={description} onChange={(event) => setDescription(event.target.value)} placeholder="What belongs in this collection?" rows={2} /></label>
        <div className="field-builder">
          <div className="field-builder-heading"><div><strong>Custom fields</strong><span>Define the information every item can hold.</span></div><button type="button" onClick={addField}><Icon name="plus" size={15} />Add field</button></div>
          {fields.map((field, index) => (
            <div className="field-row" key={index}>
              <input required value={field.label} onChange={(event) => { const label = event.target.value; updateField(index, { label, key: label.toLowerCase().trim().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "") }); }} placeholder="Field label" aria-label="Field label" />
              <input required pattern="[a-z][a-z0-9_]*" value={field.key} onChange={(event) => updateField(index, { key: event.target.value.toLowerCase().replace(/\s+/g, "_") })} placeholder="field_key" aria-label="Field key" />
              <select value={field.type} onChange={(event) => updateField(index, { type: event.target.value as FieldType, options: [] })} aria-label="Field type">
                <option value="string">Text</option><option value="integer">Integer</option><option value="number">Number</option><option value="boolean">Yes / No</option><option value="date">Date</option><option value="datetime">Date & time</option><option value="url">URL</option><option value="select">Select</option><option value="multi_select">Multi-select</option>
              </select>
              <label className="required-check"><input type="checkbox" checked={field.required} onChange={(event) => updateField(index, { required: event.target.checked })} /><span>Required</span></label>
              <button className="remove-field" type="button" onClick={() => setFields((current) => current.filter((_, position) => position !== index))} aria-label="Remove field"><Icon name="close" size={15} /></button>
              {(field.type === "select" || field.type === "multi_select") && <input className="options-input" required value={field.options.join(", ")} onChange={(event) => updateField(index, { options: event.target.value.split(",").map((option) => option.trim()).filter(Boolean) })} placeholder="Options separated by commas" aria-label="Select options" />}
            </div>
          ))}
          {!fields.length && <button className="empty-fields" type="button" onClick={addField}><Icon name="plus" />Add fields such as status, date, amount, or category</button>}
        </div>
        <div className="modal-actions"><button type="button" className="ghost-button" onClick={onClose}>Cancel</button><button className="primary-button" disabled={submitting}>{submitting ? "Creating…" : "Create collection"}</button></div>
      </form>
    </ModalShell>
  );
}

function ItemModal({ collection, onClose, onSubmit }: { collection: Collection; onClose: () => void; onSubmit: (input: ItemInput) => Promise<void> }) {
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [values, setValues] = useState<Record<string, unknown>>({});
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  async function submit(event: React.FormEvent) {
    event.preventDefault(); setSubmitting(true); setFormError(null);
    const properties: Record<string, unknown> = {};
    collection.field_definitions.forEach((field) => {
      const raw = values[field.key];
      if (field.type === "boolean") { properties[field.key] = Boolean(raw); return; }
      if (raw === "" || raw === undefined) return;
      if (field.type === "integer") properties[field.key] = Number.parseInt(String(raw), 10);
      else if (field.type === "number") properties[field.key] = Number(raw);
      else if (field.type === "multi_select") properties[field.key] = String(raw).split(",").map((part) => part.trim()).filter(Boolean);
      else properties[field.key] = raw;
    });
    try { await onSubmit({ title, body, properties }); }
    catch (reason) { setFormError(reason instanceof Error ? reason.message : "Unable to create item"); setSubmitting(false); }
  }

  return (
    <ModalShell title={`Add to ${collection.name}`} subtitle="Capture it now. You can refine it later." onClose={onClose}>
      <form onSubmit={submit} className="modal-form">
        {formError && <div className="inline-error">{formError}</div>}
        <label className="form-field"><span>Title</span><input autoFocus required value={title} onChange={(event) => setTitle(event.target.value)} placeholder="What do you want to remember?" /></label>
        <label className="form-field"><span>Notes <small>Optional</small></span><textarea rows={3} value={body} onChange={(event) => setBody(event.target.value)} placeholder="Add context, details, or thoughts…" /></label>
        {collection.field_definitions.length > 0 && <div className="dynamic-fields"><strong>Properties</strong><div className="dynamic-grid">{collection.field_definitions.map((field) => <DynamicField key={field.key} field={field} value={values[field.key]} onChange={(value) => setValues((current) => ({ ...current, [field.key]: value }))} />)}</div></div>}
        <div className="modal-actions"><button type="button" className="ghost-button" onClick={onClose}>Cancel</button><button className="primary-button" disabled={submitting}>{submitting ? "Saving…" : "Save item"}</button></div>
      </form>
    </ModalShell>
  );
}

function DynamicField({ field, value, onChange }: { field: FieldDefinition; value: unknown; onChange: (value: unknown) => void }) {
  if (field.type === "boolean") return <label className="boolean-field"><input type="checkbox" checked={Boolean(value)} onChange={(event) => onChange(event.target.checked)} /><span><strong>{field.label}</strong><small>{field.required ? "Required" : "Optional"}</small></span></label>;
  if (field.type === "select") return <label className="form-field"><span>{field.label}{field.required && <b>*</b>}</span><select required={field.required} value={String(value ?? "")} onChange={(event) => onChange(event.target.value)}><option value="">Choose an option</option>{field.options.map((option) => <option key={option}>{option}</option>)}</select></label>;
  if (field.type === "multi_select") return <label className="form-field"><span>{field.label}{field.required && <b>*</b>}</span><input required={field.required} value={String(value ?? "")} onChange={(event) => onChange(event.target.value)} placeholder={`Comma-separated: ${field.options.join(", ")}`} /></label>;
  const inputType = field.type === "date" ? "date" : field.type === "datetime" ? "datetime-local" : field.type === "url" ? "url" : ["number", "integer"].includes(field.type) ? "number" : "text";
  return <label className="form-field"><span>{field.label}{field.required && <b>*</b>}</span><input type={inputType} step={field.type === "integer" ? "1" : field.type === "number" ? "any" : undefined} required={field.required} value={String(value ?? "")} onChange={(event) => onChange(event.target.value)} placeholder={`Enter ${field.label.toLowerCase()}`} /></label>;
}

function AssistantPanel({ open, onClose, onDataChanged }: { open: boolean; onClose: () => void; onDataChanged: () => Promise<void> }) {
  const [messages, setMessages] = useState<ChatEntry[]>([{ id: "welcome", role: "assistant", content: "Hi — I’m your TrackFlow assistant. Tell me what you want to capture or find." }]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<string>();
  const [sending, setSending] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);
  useEffect(() => endRef.current?.scrollIntoView({ behavior: "smooth" }), [messages, open]);

  async function send(event: React.FormEvent) {
    event.preventDefault(); const text = input.trim(); if (!text || sending) return;
    setInput(""); setSending(true);
    const userEntry: ChatEntry = { id: crypto.randomUUID(), role: "user", content: text };
    const pendingId = crypto.randomUUID();
    setMessages((current) => [...current, userEntry, { id: pendingId, role: "assistant", content: "Thinking", pending: true }]);
    try {
      const response = await api.askAssistant(text, conversationId);
      setConversationId(response.conversation_id);
      setMessages((current) => current.map((entry) => entry.id === pendingId ? { id: pendingId, role: "assistant", content: response.message } : entry));
      await onDataChanged();
    } catch (reason) {
      const message = reason instanceof Error ? reason.message : "The assistant is unavailable.";
      setMessages((current) => current.map((entry) => entry.id === pendingId ? { id: pendingId, role: "assistant", content: message } : entry));
    } finally { setSending(false); }
  }

  return (
    <aside className={`assistant-panel ${open ? "open" : ""}`} aria-hidden={!open}>
      <header><div className="assistant-avatar"><Icon name="sparkles" size={18} /></div><div><strong>TrackFlow AI</strong><span><i />Ready to help</span></div><button className="icon-button" onClick={onClose} aria-label="Close assistant"><Icon name="close" /></button></header>
      <div className="chat-context"><Icon name="book" size={15} />Has access to your active collections</div>
      <div className="chat-messages">{messages.map((message) => <div key={message.id} className={`chat-message ${message.role}`}><div>{message.pending ? <span className="typing"><i /><i /><i /></span> : message.content}</div></div>)}<div ref={endRef} /></div>
      <div className="prompt-chips"><button onClick={() => setInput("Create a habit tracker for me")}>Create a habit tracker</button><button onClick={() => setInput("What have I saved recently?")}>Recent items</button></div>
      <form className="chat-input" onSubmit={send}><textarea rows={1} value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} placeholder="Capture or ask anything…" /><button disabled={!input.trim() || sending} aria-label="Send message"><Icon name="send" size={17} /></button></form>
      <small className="ai-disclaimer">AI can make mistakes. Verify important information.</small>
    </aside>
  );
}

export default App;
