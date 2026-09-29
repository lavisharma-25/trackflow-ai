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


def get_provider(provider_name: str | None = None) -> dict:
    configuration = load_llm_config()
    providers = configuration.get("providers", {})
    provider = (provider_name or configuration.get("default_provider"))
    llm_config = providers.get(provider)
    print(f"Selected provider: {provider}\nConfiguration: {llm_config}")

    if provider is None:
        raise LLMConfigurationError(f"Unknown LLM provider: {provider_name}")

    return llm_config


def list_providers() -> list[dict]:
    config = load_llm_config()
    providers = config.get("provider", {})

    result = []

    for provider_id, provider in providers.items():
        model = os.getenv(provider["model"])
        api_key = os.getenv(provider["api_key"])
        base_url = (
            os.getenv(provider["base_url"])
            if provider.get("base_url")
            else None
        )

        available = bool(
            model
            and api_key
            and (
                not provider.get("base_url")
                or base_url
            )
        )

        result.append(
            {
                "id": provider_id,
                "display_name": provider["display_name"],
                "model": model,
                "available": available,
            }
        )

    return result

if __name__ == "__main__":

    print(load_llm_config())

    get_provider("openrouter")

    print(list_providers())