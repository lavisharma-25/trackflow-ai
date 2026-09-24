import { PropertyValue } from "../../shared/components/PropertyValue";
import { initials, relativeDate } from "../../shared/formatters";
import { Icon } from "../../shared/icons/Icon";
import type { Collection, Item } from "../../shared/types";

export function ItemCards({
  collection,
  items,
  onArchive,
}: {
  collection: Collection;
  items: Item[];
  onArchive: (item: Item) => void;
}) {
  return (
    <div className="items-grid">
      {items.map((item) => (
        <article className="item-card" key={item.id}>
          <div className="item-card-top">
            <span className="item-monogram">{initials(item.title)}</span>
            <button
              className="row-action"
              onClick={() => onArchive(item)}
              aria-label={`Archive ${item.title}`}
            >
              <Icon name="archive" size={16} />
            </button>
          </div>
          <h3>{item.title}</h3>
          {item.body && <p>{item.body}</p>}
          <dl>
            {collection.field_definitions.slice(0, 4).map((field) => (
              <div key={field.key}>
                <dt>{field.label}</dt>
                <dd><PropertyValue field={field} value={item.properties[field.key]} /></dd>
              </div>
            ))}
          </dl>
          <footer>Updated {relativeDate(item.updated_at)}</footer>
        </article>
      ))}
    </div>
  );
}
