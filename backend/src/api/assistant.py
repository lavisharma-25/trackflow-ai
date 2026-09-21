from fastapi import APIRouter, Depends
from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy.orm import Session

from src.agents.assistant_agent import build_assistant_agent
from src.db.database import get_db
from src.schemas.assistant import AssistantRequest, AssistantResponse
from src.services.conversation_service import (
    add_message,
    get_or_create_conversation,
    list_messages,
)


router = APIRouter(prefix="/api/v1")


def _content_to_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("text"):
                parts.append(str(block["text"]))
        return "\n".join(parts)
    return str(content)


@router.post("/assistant", response_model=AssistantResponse)
def talk_to_assistant(
    request: AssistantRequest,
    db: Session = Depends(get_db),
):
    conversation = get_or_create_conversation(
        db, request.conversation_id, request.message
    )
    history = list_messages(db, conversation.id)
    messages = [
        HumanMessage(content=message.content)
        if message.role == "user"
        else AIMessage(content=message.content)
        for message in history
    ]
    messages.append(HumanMessage(content=request.message))
    add_message(db, conversation.id, "user", request.message)

    result = build_assistant_agent().invoke({"messages": messages})
    response_text = _content_to_text(result["messages"][-1].content)
    add_message(db, conversation.id, "assistant", response_text)
    return AssistantResponse(
        conversation_id=conversation.id,
        message=response_text,
    )
