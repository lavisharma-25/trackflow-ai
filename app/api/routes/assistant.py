from fastapi import APIRouter
from app.models.tracker import AgentRequest
from app.agents.orchestrator import AgentOrchestrator

router = APIRouter(prefix="/assistant", tags=["Assistant"])


@router.get("/greeting")
def greeting():

    return {
        "message": (
            "Hi! I'm TrackFlow AI. "
            "I can help you manage trackers and structured data."
        ),
        "examples": [
            "Create a movies tracker",
            "Add Interstellar to movies",
            "Show all movies",
            "Delete movie with id 1"
        ]
    }


@router.post("/chat")
def chat(request: AgentRequest):

    return AgentOrchestrator.process(request.query)


# from fastapi import APIRouter, Depends

# from app.api.dependencies import get_watchlist_workflow
# from app.schemas.action import AssistantMessageRequest, AssistantMessageResponse
# from app.workflows.watchlist import WatchlistWorkflow

# router = APIRouter()


# @router.post("/assistant/message", response_model=AssistantMessageResponse)
# async def handle_assistant_message(
#     payload: AssistantMessageRequest,
#     workflow: WatchlistWorkflow = Depends(get_watchlist_workflow),
# ):
#     return workflow.invoke(
#         conversation_id=payload.conversation_id,
#         tracker=payload.tracker,
#         message=payload.message,
#     )
