import { Icon } from "../icons/Icon";


export function LoadingState() {
  return (
    <div className="page-loading">
      <div className="loader-mark"><Icon name="sparkles" size={26} /></div>
      <strong>Opening your workspace</strong>
      <span>Connecting to your second brain…</span>
    </div>
  );
}


export function ItemsSkeleton() {
  return (
    <div className="skeleton-list">
      {[1, 2, 3].map((row) => (
        <div className="skeleton-row" key={row}><span /><span /><span /></div>
      ))}
    </div>
  );
}


export function EmptyItems({
  searching,
  onCreate,
}: {
  searching: boolean;
  onCreate: () => void;
}) {
  return (
    <div className="empty-state">
      <div className="empty-illustration">
        <Icon name={searching ? "search" : "book"} size={27} />
      </div>
      <h3>{searching ? "No matching items" : "A blank page, ready for ideas"}</h3>
      <p>
        {searching
          ? "Try a broader phrase or clear your search."
          : "Add your first item manually or ask TrackFlow AI to capture it for you."}
      </p>
      {!searching && (
        <button className="secondary-button" onClick={onCreate}>
          <Icon name="plus" size={17} />Add first item
        </button>
      )}
    </div>
  );
}


export function WelcomeState({
  onCreate,
  onAssistant,
}: {
  onCreate: () => void;
  onAssistant: () => void;
}) {
  return (
    <section className="welcome-state">
      <div className="welcome-orbit">
        <span /><span /><div><Icon name="sparkles" size={32} /></div>
      </div>
      <div className="eyebrow"><span className="eyebrow-dot" />Your knowledge, connected</div>
      <h1>Build a second brain<br />that thinks with you.</h1>
      <p>
        Capture expenses, habits, books, ideas, or anything else. TrackFlow gives
        every thought a place and makes it easy to find again.
      </p>
      <div className="welcome-actions">
        <button className="primary-button" onClick={onCreate}>
          <Icon name="plus" />Create a collection
        </button>
        <button className="secondary-button" onClick={onAssistant}>
          <Icon name="sparkles" />Start with AI
        </button>
      </div>
    </section>
  );
}
