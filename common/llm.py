"""Shared LLM factory for all agents.

Uses OpenRouter API via ChatOpenAI client.
"""

import os

from langchain_openai import ChatOpenAI


def get_llm():
    """Return a ChatOpenAI client configured for OpenRouter."""
    return ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
    )