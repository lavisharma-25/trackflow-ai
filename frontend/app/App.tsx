import { useEffect, useMemo, useState } from "react";

import { AssistantPanel } from "../features/assistant/AssistantPanel";
import { CollectionForm } from "../features/collections/CollectionForm";
import { CollectionSidebar } from "../features/collections/CollectionSidebar";
import { collectionApi } from "../features/collections/collection-api";
import { ItemCards } from "../features/items/ItemCards";
import { ItemForm } from "../features/items/ItemForm";
import { ItemTable } from "../features/items/ItemTable";
import { itemApi } from "../features/items/item-api";
import {
  EmptyItems,
  ItemsSkeleton,
  LoadingState,
  WelcomeState,
} from "../shared/components/WorkspaceStates";
import { relativeDate } from "../shared/formatters";
import { useDebouncedValue } from "../shared/hooks/useDebouncedValue";
import { Icon } from "../shared/icons/Icon";
import type { Collection, CollectionInput, Item, ItemInput } from "../shared/types";
import { useAppRoute } from "./routes";

function App() {
  const { collectionId: selectedId, navigateToCollection } = useAppRoute();
  const [collections, setCollections] = useState<Collection[]>([]);
  const [items, setItems] = useState<Item[]>([]);
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebouncedValue(search);
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
    const data = await collectionApi.list();
    setCollections(data);
    const requestedId = preferredId ?? selectedId;
    const nextId = data.some((collection) => collection.id === requestedId)
      ? requestedId
      : data[0]?.id ?? null;
    if (nextId !== selectedId) navigateToCollection(nextId, true);
    return { data, activeId: nextId };
  }

  useEffect(() => {
    refreshCollections()
      .catch((reason: Error) => setError(reason.message))
      .finally(() => setLoading(false));
    // Initial loading is intentionally performed once. Route changes do not
    // need to reload the collection index.
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

    let cancelled = false;
    setItemsLoading(true);
    itemApi
      .list(selectedId, debouncedSearch)
      .then((data) => {
        if (!cancelled) setItems(data);
      })
      .catch((reason: Error) => {
        if (!cancelled) setError(reason.message);
      })
      .finally(() => {
        if (!cancelled) setItemsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [selectedId, debouncedSearch]);

  function selectCollection(collectionId: string) {
    navigateToCollection(collectionId);
    setSearch("");
    setSidebarOpen(false);
  }

  async function handleCollectionCreate(input: CollectionInput) {
    const created = await collectionApi.create(input);
    await refreshCollections(created.id);
    setModal(null);
  }

  async function handleItemCreate(input: ItemInput) {
    if (!selected) return;
    await itemApi.create(selected.id, input);
    setItems(await itemApi.list(selected.id, search));
    setModal(null);
  }

  async function handleArchive(item: Item) {
    if (
      !selected ||
      !window.confirm(`Archive “${item.title}”? You can restore it through the API.`)
    ) {
      return;
    }
    try {
      await itemApi.archive(selected.id, item.id);
      setItems((current) => current.filter((entry) => entry.id !== item.id));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to archive item");
    }
  }

  async function handleAssistantDataChanged() {
    const { activeId } = await refreshCollections();
    if (activeId) setItems(await itemApi.list(activeId, search));
  }

  return (
    <div className="app-shell">
      <CollectionSidebar
        collections={collections}
        selectedId={selectedId}
        loading={loading}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onSelect={selectCollection}
        onCreate={() => setModal("collection")}
        onAssistant={() => setAssistantOpen(true)}
      />

      <main className="main-content">
        <header className="topbar">
          <button
            className="mobile-menu"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open navigation"
          >
            <Icon name="list" />
          </button>
          <div className="breadcrumbs">
            <span>Workspace</span><Icon name="chevron" size={13} />
            <strong>{selected?.name ?? "Home"}</strong>
          </div>
          <div className="topbar-actions">
            <div className="connection-pill"><span /><span>Local</span></div>
            <button className="assistant-trigger" onClick={() => setAssistantOpen(true)}>
              <Icon name="sparkles" size={17} /><span>Ask AI</span>
            </button>
          </div>
        </header>

        {error && (
          <div className="error-banner" role="alert">
            <span>{error}</span>
            <button onClick={() => setError(null)}><Icon name="close" size={16} /></button>
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
              <button className="primary-button" onClick={() => setModal("item")}>
                <Icon name="plus" /><span>New item</span>
              </button>
            </div>

            <div className="stat-row">
              <article className="stat-card">
                <div className="stat-icon indigo"><Icon name="inbox" /></div>
                <div><strong>{items.length}</strong><span>{search ? "Matches" : "Active items"}</span></div>
              </article>
              <article className="stat-card">
                <div className="stat-icon amber"><Icon name="grid" /></div>
                <div><strong>{selected.field_definitions.length}</strong><span>Custom fields</span></div>
              </article>
              <article className="stat-card">
                <div className="stat-icon mint"><Icon name="check" /></div>
                <div><strong>{items[0] ? relativeDate(items[0].updated_at) : "—"}</strong><span>Last updated</span></div>
              </article>
            </div>

            <div className="content-card">
              <div className="content-toolbar">
                <div className="search-box">
                  <Icon name="search" size={17} />
                  <input
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                    placeholder={`Search ${selected.name.toLowerCase()}…`}
                  />
                </div>
                <div className="view-toggle" aria-label="Change view">
                  <button
                    className={view === "table" ? "active" : ""}
                    onClick={() => setView("table")}
                    aria-label="Table view"
                  >
                    <Icon name="list" size={17} />
                  </button>
                  <button
                    className={view === "cards" ? "active" : ""}
                    onClick={() => setView("cards")}
                    aria-label="Card view"
                  >
                    <Icon name="grid" size={16} />
                  </button>
                </div>
              </div>

              {itemsLoading ? (
                <ItemsSkeleton />
              ) : items.length ? (
                view === "table" ? (
                  <ItemTable collection={selected} items={items} onArchive={handleArchive} />
                ) : (
                  <ItemCards collection={selected} items={items} onArchive={handleArchive} />
                )
              ) : (
                <EmptyItems searching={Boolean(search)} onCreate={() => setModal("item")} />
              )}
            </div>
          </section>
        ) : (
          <WelcomeState
            onCreate={() => setModal("collection")}
            onAssistant={() => setAssistantOpen(true)}
          />
        )}
      </main>

      {modal === "collection" && (
        <CollectionForm onClose={() => setModal(null)} onSubmit={handleCollectionCreate} />
      )}
      {modal === "item" && selected && (
        <ItemForm
          collection={selected}
          onClose={() => setModal(null)}
          onSubmit={handleItemCreate}
        />
      )}
      <AssistantPanel
        open={assistantOpen}
        onClose={() => setAssistantOpen(false)}
        onDataChanged={handleAssistantDataChanged}
      />
      <button
        className="floating-ai"
        onClick={() => setAssistantOpen(true)}
        aria-label="Open AI assistant"
      >
        <Icon name="sparkles" size={21} />
      </button>
    </div>
  );
}

export default App;
