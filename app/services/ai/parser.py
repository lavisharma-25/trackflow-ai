import re

from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.schemas.action import ParsedAction


class IntentParser:
    def parse(self, message: str, tracker: str) -> ParsedAction:
        raise NotImplementedError


class GeminiIntentParser(IntentParser):
    def __init__(self, api_key: str | None = None, model: str = GEMINI_MODEL):
        self.api_key = api_key or GEMINI_API_KEY
        self.model = model
        self.fallback = RuleBasedIntentParser()

    def parse(self, message: str, tracker: str) -> ParsedAction:
        if not self.api_key:
            return self.fallback.parse(message, tracker)
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError:
            return self.fallback.parse(message, tracker)

        prompt = (
            "Extract a TrackFlow watchlist action from the user message. "
            "Return only fields supported by the schema. "
            "Use intent create, list, get, update, delete, or unknown. "
            f"Tracker context: {tracker}. User message: {message}"
        )
        model = ChatGoogleGenerativeAI(
            model=self.model,
            google_api_key=self.api_key,
            temperature=0,
        )
        response = model.with_structured_output(ParsedAction).invoke(prompt)
        if isinstance(response, ParsedAction):
            return response
        return ParsedAction.model_validate(response)


class RuleBasedIntentParser(IntentParser):
    def parse(self, message: str, tracker: str) -> ParsedAction:
        text = message.strip()
        lowered = text.lower()
        status = self._extract_status(lowered)
        rating = self._extract_rating(lowered)

        if any(word in lowered for word in ["list", "show", "what is in", "all"]):
            return ParsedAction(intent="list")
        if lowered.startswith(("delete ", "remove ")):
            return ParsedAction(intent="delete", entity=self._strip_command(text, ["delete", "remove"]))
        if any(word in lowered for word in ["mark ", "update ", "set "]):
            return ParsedAction(
                intent="update",
                entity=self._extract_entity_for_update(text),
                status=status,
                rating=rating,
            )
        if lowered.startswith(("get ", "find ", "details ")):
            return ParsedAction(intent="get", entity=self._strip_command(text, ["get", "find", "details"]))
        if lowered.startswith(("add ", "save ", "track ", "watch ")):
            return ParsedAction(
                intent="create",
                entity=self._strip_command(text, ["add", "save", "track", "watch"]),
                media_type=self._extract_media_type(lowered),
            )
        return ParsedAction(intent="unknown", entity=text)

    def _strip_command(self, text: str, commands: list[str]) -> str:
        pattern = r"^\s*(?:" + "|".join(commands) + r")\s+"
        return re.sub(pattern, "", text, flags=re.IGNORECASE).strip()

    def _extract_media_type(self, lowered: str) -> str | None:
        if any(word in lowered for word in ["show", "series", "tv"]):
            return "tv"
        if any(word in lowered for word in ["movie", "film"]):
            return "movie"
        return None

    def _extract_status(self, lowered: str) -> str | None:
        for status in ["planned", "watching", "watched", "dropped"]:
            if status in lowered:
                return status
        if "complete" in lowered or "finished" in lowered:
            return "watched"
        return None

    def _extract_rating(self, lowered: str) -> float | None:
        match = re.search(r"(\d+(?:\.\d+)?)\s*/\s*10", lowered)
        if not match:
            return None
        return float(match.group(1))

    def _extract_entity_for_update(self, text: str) -> str:
        cleaned = self._strip_command(text, ["mark", "update", "set"])
        cleaned = re.sub(r"\b(as|to)\b\s+(planned|watching|watched|dropped|complete|finished)\b", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\b(planned|watching|watched|dropped|complete|finished)\b\s*$", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\brated?\b\s+\d+(?:\.\d+)?\s*/\s*10", "", cleaned, flags=re.IGNORECASE)
        return cleaned.strip()
