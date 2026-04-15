"""Shared OpenAI + LangChain helpers for the QBR workflow."""

import os
from functools import lru_cache
from pathlib import Path
from typing import TypeVar

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"

SchemaT = TypeVar("SchemaT", bound=BaseModel)


@lru_cache(maxsize=1)
def _load_environment() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=False)


def _ensure_api_key_present() -> None:
    _load_environment()
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not configured. Add it to the project root .env file."
        )


def _get_model_name() -> str:
    _load_environment()
    return os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)


_load_environment()
AGENT_MODEL_CONFIG = {
    "extractor": os.getenv("OPENAI_MODEL_EXTRACTOR", "gpt-4.1-mini"),
    "thinker": os.getenv("OPENAI_MODEL_THINKER", "gpt-4.1"),
}


def build_chat_model(*, temperature: float = 0.0, model: str | None = None) -> ChatOpenAI:
    """Create a chat model client for text generation."""

    _ensure_api_key_present()
    return ChatOpenAI(model=model or _get_model_name(), temperature=temperature)


def invoke_structured_output(
    *,
    system_prompt: str,
    user_prompt: str,
    schema: type[SchemaT],
    temperature: float = 0.0,
    model: str | None = None,
) -> SchemaT:
    """Invoke the model and validate its structured response."""

    chain = build_chat_model(temperature=temperature, model=model).with_structured_output(
        schema,
        method="json_schema",
        strict=True,
    )
    result = chain.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
    )
    if isinstance(result, schema):
        return result
    return schema.model_validate(result)


def invoke_text_output(
    *,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
    model: str | None = None,
) -> str:
    """Invoke the model and normalize the returned text content."""

    response = build_chat_model(temperature=temperature, model=model).invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
    )
    content = response.content
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        text_parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if text:
                    text_parts.append(str(text))
        return "\n".join(part.strip() for part in text_parts if part.strip()).strip()
    return str(content).strip()
