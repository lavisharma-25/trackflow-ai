"""Compatibility wrapper; collection and item work now uses one assistant."""

from src.agents.assistant_agent import build_assistant_agent


def build_tracker_agent():
    return build_assistant_agent()
