"""Compatibility wrapper for the original supervisor module."""

from src.agents.assistant_agent import build_assistant_agent


def build_supervisor_agent():
    return build_assistant_agent()
