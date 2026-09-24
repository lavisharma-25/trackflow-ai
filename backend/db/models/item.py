from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, new_id, utc_now

if TYPE_CHECKING:
    from db.models.collection import Collection


class Item(Base):
    __tablename__ = "items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    collection_id: Mapped[str] = mapped_column(
        ForeignKey("collections.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(300))
    body: Mapped[str] = mapped_column(Text, default="")
    properties: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    collection: Mapped[Collection] = relationship(back_populates="items")


class ItemLink(Base):
    __tablename__ = "item_links"
    __table_args__ = (
        UniqueConstraint("source_item_id", "target_item_id", "link_type"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    source_item_id: Mapped[str] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"))
    target_item_id: Mapped[str] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"))
    link_type: Mapped[str] = mapped_column(String(80), default="related")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
