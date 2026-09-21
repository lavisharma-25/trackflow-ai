"""Compatibility constant for code written against the original prototype."""

SUPERVISOR_SYSTEM_PROMPT = """
This supervisor prompt is deprecated. TrackFlow now uses the single assistant defined
in src.prompts.assistant so that all collection and item operations share one context.
"""
