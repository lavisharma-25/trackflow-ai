from functools import lru_cache

from langchain.agents import create_agent

from src.prompts import ASSISTANT_SYSTEM_PROMPT
from src.services.llm_service import create_llm
from src.tools.assistant_tools import (
    add_item_to_collection,
    create_new_collection,
    list_available_collections,
    search_saved_items,
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
