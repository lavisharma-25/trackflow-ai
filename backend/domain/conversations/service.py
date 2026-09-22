from sqlalchemy import select
from sqlalchemy.orm import Session

from core.exceptions import NotFoundError
from db.models import ChatMessage, Conversation


def get_or_create_conversation(
    db: Session, conversation_id: str | None, first_message: str
) -> Conversation:
    if conversation_id:
        conversation = db.get(Conversation, conversation_id)
        if conversation is None:
            raise NotFoundError("Conversation not found")
        return conversation

    conversation = Conversation(title=first_message.strip()[:100] or "New conversation")
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def list_messages(
    db: Session, conversation_id: str, limit: int = 30
) -> list[ChatMessage]:
    query = (
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    return list(reversed(list(db.scalars(query))))


def add_message(
    db: Session, conversation_id: str, role: str, content: str
) -> ChatMessage:
    message = ChatMessage(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
