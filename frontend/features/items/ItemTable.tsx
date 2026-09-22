import { PropertyValue } from "../../shared/components/PropertyValue";
import { initials, relativeDate } from "../../shared/formatters";
import { Icon } from "../../shared/icons/Icon";
import type { Collection, Item } from "../../shared/types";

export function ItemTable({
  collection,
  items,
  onArchive,
}: {
  collection: Collection;
  items: Item[];
  onArchive: (item: Item) => void;
}) {
  return (
    <div className="table-scroll">
      <table className="items-table">
        <thead>
          <tr>
            <th>Title</th>
            {collection.field_definitions.map((field) => <th key={field.key}>{field.label}</th>)}
            <th>Updated</th>
            <th><span className="sr-only">Actions</span></th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              <td>
                <div className="title-cell">
                  <span>{initials(item.title)}</span>
                  <div><strong>{item.title}</strong>{item.body && <small>{item.body}</small>}</div>
                </div>
              </td>
              {collection.field_definitions.map((field) => (
                <td key={field.key}>
                  <PropertyValue field={field} value={item.properties[field.key]} />
                </td>
              ))}
              <td className="muted-cell">{relativeDate(item.updated_at)}</td>
              <td>
                <button
                  className="row-action"
                  onClick={() => onArchive(item)}
                  title="Archive item"
                  aria-label={`Archive ${item.title}`}
                >
                  <Icon name="archive" size={16} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
