from langchain_google_genai import ChatGoogleGenerativeAI

from src.core.settings import settings


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
