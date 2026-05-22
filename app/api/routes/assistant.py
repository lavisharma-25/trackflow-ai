from fastapi import APIRouter, Depends

from app.api.dependencies import get_watchlist_workflow
from app.schemas.action import AssistantMessageRequest, AssistantMessageResponse
from app.workflows.watchlist import WatchlistWorkflow

router = APIRouter()


@router.post("/assistant/message", response_model=AssistantMessageResponse)
async def handle_assistant_message(
    payload: AssistantMessageRequest,
    workflow: WatchlistWorkflow = Depends(get_watchlist_workflow),
):
    return workflow.invoke(
        conversation_id=payload.conversation_id,
        tracker=payload.tracker,
        message=payload.message,
    )
