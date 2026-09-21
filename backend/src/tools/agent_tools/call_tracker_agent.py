from langchain_core.messages import HumanMessage

from src.agents.assistant_agent import build_assistant_agent


def call_tracker_agent(query: str):
    """Backward-compatible entry point for the original prototype."""
    return build_assistant_agent().invoke(
        {"messages": [HumanMessage(content=query)]}
    )
