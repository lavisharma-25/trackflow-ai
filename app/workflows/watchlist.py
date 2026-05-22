from typing import Any, Literal, TypedDict

from langgraph.graph import END, StateGraph

from app.core.trackers import get_tracker
from app.schemas.action import (
    AssistantMessageResponse,
    ParsedAction,
    TMDBChoice,
    WatchlistUpdate,
)
from app.services.ai.parser import GeminiIntentParser, IntentParser
from app.services.tmdb.client import TMDBClient, TMDBClientError
from app.services.watchlist.service import (
    DuplicateWatchlistEntry,
    WatchlistNotFound,
    WatchlistService,
)
from app.storage.json_store import JsonStore


class WatchlistWorkflowState(TypedDict, total=False):
    conversation_id: str
    tracker: str
    message: str
    action: ParsedAction
    response: AssistantMessageResponse
    next_step: Literal["pending", "parse", "execute", "end"]


class WatchlistWorkflow:
    def __init__(
        self,
        store: JsonStore | None = None,
        parser: IntentParser | None = None,
        tmdb_client: TMDBClient | None = None,
        watchlist_service: WatchlistService | None = None,
    ):
        self.store = store or JsonStore()
        self.parser = parser or GeminiIntentParser()
        self.tmdb = tmdb_client or TMDBClient()
        self.watchlist = watchlist_service or WatchlistService(self.store)
        self.graph = self._build_graph()

    def invoke(self, conversation_id: str, tracker: str, message: str) -> AssistantMessageResponse:
        result = self.graph.invoke(
            {
                "conversation_id": conversation_id,
                "tracker": tracker,
                "message": message,
            }
        )
        return result["response"]

    def _build_graph(self):
        graph = StateGraph(WatchlistWorkflowState)
        graph.add_node("validate_table_context", self._validate_table_context)
        graph.add_node("resolve_pending_selection", self._resolve_pending_selection)
        graph.add_node("parse_user_intent", self._parse_user_intent)
        graph.add_node("execute_action", self._execute_action)
        graph.set_entry_point("validate_table_context")
        graph.add_conditional_edges(
            "validate_table_context",
            lambda state: state["next_step"],
            {"pending": "resolve_pending_selection", "parse": "parse_user_intent", "end": END},
        )
        graph.add_conditional_edges(
            "resolve_pending_selection",
            lambda state: state["next_step"],
            {"end": END, "parse": "parse_user_intent"},
        )
        graph.add_edge("parse_user_intent", "execute_action")
        graph.add_edge("execute_action", END)
        return graph.compile()

    def _validate_table_context(self, state: WatchlistWorkflowState) -> WatchlistWorkflowState:
        tracker = get_tracker(state["tracker"])
        if not tracker:
            state["response"] = AssistantMessageResponse(
                status="invalid_tracker",
                message="That tracker is not supported. Select Watchlist, Games, Finance, or Project.",
            )
            state["next_step"] = "end"
            return state
        if not tracker["implemented"]:
            state["response"] = AssistantMessageResponse(
                status="not_implemented",
                message=f"{tracker['name']} is recognized but not implemented yet.",
            )
            state["next_step"] = "end"
            return state
        pending = self.store.get_conversation(state["conversation_id"])
        state["next_step"] = "pending" if pending else "parse"
        return state

    def _resolve_pending_selection(self, state: WatchlistWorkflowState) -> WatchlistWorkflowState:
        pending = self.store.get_conversation(state["conversation_id"])
        if not pending or pending.get("type") != "tmdb_selection":
            state["next_step"] = "parse"
            return state
        message = state["message"].strip()
        if message.lower() in {"cancel", "no", "stop"}:
            self.store.clear_conversation(state["conversation_id"])
            state["response"] = AssistantMessageResponse(status="cancelled", message="Selection cancelled.")
            state["next_step"] = "end"
            return state
        choices = [TMDBChoice(**choice) for choice in pending.get("choices", [])]
        selected = self._select_choice(message, choices)
        if not selected:
            state["response"] = AssistantMessageResponse(
                status="needs_selection",
                message="I could not match that selection. Choose one of the returned options.",
                choices=[choice.model_dump() for choice in choices],
            )
            state["next_step"] = "end"
            return state
        self.store.clear_conversation(state["conversation_id"])
        state["response"] = self._save_choice(selected)
        state["next_step"] = "end"
        return state

    def _parse_user_intent(self, state: WatchlistWorkflowState) -> WatchlistWorkflowState:
        state["action"] = self.parser.parse(state["message"], state["tracker"])
        return state

    def _execute_action(self, state: WatchlistWorkflowState) -> WatchlistWorkflowState:
        action = state["action"]
        if action.intent == "create":
            state["response"] = self._create_from_action(state["conversation_id"], action)
        elif action.intent == "list":
            entries = [entry.model_dump() for entry in self.watchlist.list_entries()]
            state["response"] = AssistantMessageResponse(status="ok", message="Watchlist entries loaded.", data=entries)
        elif action.intent == "get":
            state["response"] = self._get_from_action(action)
        elif action.intent == "update":
            state["response"] = self._update_from_action(action)
        elif action.intent == "delete":
            state["response"] = self._delete_from_action(action)
        else:
            state["response"] = AssistantMessageResponse(
                status="unsupported_intent",
                message="I could not turn that into a supported watchlist action.",
            )
        return state

    def _create_from_action(self, conversation_id: str, action: ParsedAction) -> AssistantMessageResponse:
        if not action.entity:
            return AssistantMessageResponse(status="missing_entity", message="Tell me which movie or show to add.")
        try:
            choices = self.tmdb.search(action.entity, action.media_type)
        except TMDBClientError as exc:
            return AssistantMessageResponse(status="metadata_error", message=str(exc))
        if not choices:
            return AssistantMessageResponse(status="not_found", message="I could not find matching TMDB metadata.")
        if len(choices) > 1:
            self.store.set_conversation(
                conversation_id,
                {
                    "type": "tmdb_selection",
                    "choices": [choice.model_dump() for choice in choices],
                },
            )
            return AssistantMessageResponse(
                status="needs_selection",
                message="I found multiple matches. Reply with a number, year, or title.",
                choices=[choice.model_dump() for choice in choices],
            )
        return self._save_choice(choices[0])

    def _save_choice(self, choice: TMDBChoice) -> AssistantMessageResponse:
        payload = self.tmdb.details_from_choice(choice)
        try:
            entry = self.watchlist.create_entry(payload)
        except DuplicateWatchlistEntry as exc:
            return AssistantMessageResponse(status="duplicate", message=str(exc))
        return AssistantMessageResponse(
            status="saved",
            message=f"Added {entry.title} to the watchlist.",
            data=entry.model_dump(),
        )

    def _get_from_action(self, action: ParsedAction) -> AssistantMessageResponse:
        try:
            entry = self.watchlist.get_entry(action.target_id) if action.target_id else self.watchlist.find_by_title(action.entity or "")
        except WatchlistNotFound as exc:
            return AssistantMessageResponse(status="not_found", message=str(exc))
        return AssistantMessageResponse(status="ok", message="Watchlist entry loaded.", data=entry.model_dump())

    def _update_from_action(self, action: ParsedAction) -> AssistantMessageResponse:
        try:
            entry = self.watchlist.get_entry(action.target_id) if action.target_id else self.watchlist.find_by_title(action.entity or "")
            update_values = {
                key: value
                for key, value in {
                    "status": action.status,
                    "notes": action.notes,
                    "rating": action.rating,
                }.items()
                if value is not None
            }
            if not update_values:
                return AssistantMessageResponse(
                    status="missing_update",
                    message="Tell me what to update for that watchlist entry.",
                )
            updated = self.watchlist.update_entry(
                entry.id,
                WatchlistUpdate(**update_values),
            )
        except WatchlistNotFound as exc:
            return AssistantMessageResponse(status="not_found", message=str(exc))
        return AssistantMessageResponse(status="updated", message=f"Updated {updated.title}.", data=updated.model_dump())

    def _delete_from_action(self, action: ParsedAction) -> AssistantMessageResponse:
        try:
            entry = self.watchlist.get_entry(action.target_id) if action.target_id else self.watchlist.find_by_title(action.entity or "")
            removed = self.watchlist.delete_entry(entry.id)
        except WatchlistNotFound as exc:
            return AssistantMessageResponse(status="not_found", message=str(exc))
        return AssistantMessageResponse(status="deleted", message=f"Deleted {removed.title}.", data=removed.model_dump())

    def _select_choice(self, message: str, choices: list[TMDBChoice]) -> TMDBChoice | None:
        if message.isdigit():
            index = int(message) - 1
            if 0 <= index < len(choices):
                return choices[index]
        for choice in choices:
            if choice.release_date and choice.release_date.startswith(message):
                return choice
            if choice.title.lower() == message.lower():
                return choice
        return None
