from functools import lru_cache

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from ai.prompts import ASSISTANT_SYSTEM_PROMPT
from ai.tools import (
    add_item_to_collection,
    create_new_collection,
    list_available_collections,
    search_saved_items,
)
from core.settings import settings


class LLMConfigurationError(RuntimeError):
    pass


def create_llm(model_name: str | None = None) -> ChatGoogleGenerativeAI:
    """Create the model lazily so the non-AI API works without credentials."""
    credentials = settings.google_credentials()
    project = settings.GOOGLE_CLOUD_PROJECT
    if credentials is not None:
        project = project or credentials.project_id

    if credentials is None and not project:
        raise LLMConfigurationError(
            "Configure SERVICE_ACCOUNT_PATH or GOOGLE_CLOUD_PROJECT before using /assistant"
        )

    return ChatGoogleGenerativeAI(
        model=model_name or settings.GEMINI_MODEL_FLASH,
        project=project,
        credentials=credentials,
        location=settings.LOCATION,
        vertexai=True,
        temperature=0,
    )


@lru_cache
def build_assistant_agent():
    return create_agent(
        model=create_llm(),
        system_prompt=ASSISTANT_SYSTEM_PROMPT,
        tools=[
            list_available_collections,
            create_new_collection,
            add_item_to_collection,
            search_saved_items,
        ],
    )
