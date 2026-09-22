import { initials } from "../../shared/formatters";
import { Icon } from "../../shared/icons/Icon";
import type { Collection } from "../../shared/types";

interface CollectionSidebarProps {
  collections: Collection[];
  selectedId: string | null;
  loading: boolean;
  open: boolean;
  onClose: () => void;
  onSelect: (collectionId: string) => void;
  onCreate: () => void;
  onAssistant: () => void;
}

export function CollectionSidebar({
  collections,
  selectedId,
  loading,
  open,
  onClose,
  onSelect,
  onCreate,
  onAssistant,
}: CollectionSidebarProps) {
  return (
    <>
      <aside className={`sidebar ${open ? "sidebar-open" : ""}`}>
        <div className="brand-row">
          <div className="brand-mark"><Icon name="sparkles" size={19} /></div>
          <div><strong>TrackFlow</strong><span>AI second brain</span></div>
          <button className="icon-button sidebar-close" onClick={onClose} aria-label="Close navigation">
            <Icon name="close" />
          </button>
        </div>

        <nav className="primary-nav" aria-label="Primary navigation">
          <button className="nav-item active"><Icon name="inbox" /><span>Workspace</span></button>
          <button className="nav-item" onClick={onAssistant}>
            <Icon name="sparkles" /><span>Ask TrackFlow</span><kbd>⌘K</kbd>
          </button>
        </nav>

        <div className="sidebar-section">
          <div className="section-label">
            <span>Collections</span>
            <button onClick={onCreate} aria-label="New collection"><Icon name="plus" size={15} /></button>
          </div>
          <div className="collection-nav">
            {collections.map((collection, index) => (
              <button
                className={`collection-link ${collection.id === selectedId ? "selected" : ""}`}
                key={collection.id}
                onClick={() => onSelect(collection.id)}
              >
                <span className={`collection-dot dot-${index % 5}`}>{initials(collection.name)}</span>
                <span>{collection.name}</span>
                <small>{collection.field_definitions.length}</small>
              </button>
            ))}
          </div>
          {!collections.length && !loading && (
            <p className="sidebar-empty">Create your first collection to start organizing.</p>
          )}
        </div>

        <div className="sidebar-footer">
          <div className="profile-avatar">LS</div>
          <div><strong>My workspace</strong><span>Local &amp; private</span></div>
          <Icon name="chevron" size={15} />
        </div>
      </aside>

      {open && <button className="sidebar-scrim" onClick={onClose} aria-label="Close navigation" />}
    </>
  );
}
