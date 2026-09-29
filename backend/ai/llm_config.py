import json
import os
from functools import lru_cache
from pathlib import Path


class LLMConfigurationError(RuntimeError):
    pass


@lru_cache
def load_llm_config(config_path: Path) -> dict:
    """Load and perform basic validation of the provider configuration."""
    if not config_path.is_file():
        raise LLMConfigurationError(
            f"LLM configuration file not found: {config_path}"
        )

    try:
        with config_path.open("r", encoding="utf-8") as file:
            config = json.load(file)

    except json.JSONDecodeError as exc:
        raise LLMConfigurationError(f"Invalid JSON at line {exc.lineno}, column {exc.colno}") from exc

    providers = config.get("providers")
    if not isinstance(providers, dict) or not providers:
        raise LLMConfigurationError(
            "LLM configuration must contain a non-empty 'providers' object"
        )

    default_provider = config.get("default_provider")
    if not default_provider:
        raise LLMConfigurationError(
            "LLM configuration must define 'default_provider'"
        )

    if default_provider not in providers:
        raise LLMConfigurationError(
            f"Default provider '{default_provider}' does not exist"
        )
        
    return config


def get_provider(provider_name: str | None = None, config_path: Path | None = None) -> dict:
    config = load_llm_config(config_path)
    provider = provider_name or config["default_provider"]
    # print(f"Selected provider: {provider}")

    llm_config = config["providers"][provider]
    # print(f"Available providers: {llm_config}")

    return {"provider": provider, "config": llm_config}
