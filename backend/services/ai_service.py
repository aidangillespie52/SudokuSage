# backend/services/ai_service.py

import os
import asyncio
from dotenv import load_dotenv
from backend.utils import get_logger
from typing import List, Dict, Any, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

logger = get_logger(__name__)
load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Initialize once (LangChain reads OPENAI_API_KEY from env automatically)
llm = ChatOpenAI(
    model=MODEL,
    use_responses_api=True,     # key change
    temperature=0.2,
    max_retries=3,
    model_kwargs={
        # Responses API style
        "reasoning": {"effort": "medium"},
        "verbosity": "low",
    },
)

def _to_lc_messages(messages: List[Dict[str, str]]):
    """
    Convert OpenAI-style messages:
      [{"role":"user","content":"hi"}, ...]
    into LangChain message objects.
    """
    out = []
    for m in messages:
        role = m.get("role")
        content = m.get("content", "")
        if role == "system":
            out.append(SystemMessage(content=content))
        elif role == "assistant":
            out.append(AIMessage(content=content))
        else:  # default to user
            out.append(HumanMessage(content=content))
    return out

def _content_to_text(content) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                # OpenAI / LangChain content blocks
                if item.get("type") == "text" and "text" in item:
                    parts.append(item["text"])
                elif "content" in item and isinstance(item["content"], str):
                    parts.append(item["content"])
        return "".join(parts)
    # fallback
    return str(content)


async def call_llm(messages: List[Dict[str, str]]) -> str:
    lc_messages = _to_lc_messages(messages)
    resp = await llm.ainvoke(lc_messages)

    logger.debug(f"Raw LLM resp repr: {repr(resp)}")
    logger.debug(f"Raw LLM resp content type: {type(resp.content)}")
    logger.debug(f"Raw LLM resp content: {resp.content}")
    logger.debug(f"Raw LLM resp additional_kwargs: {resp.additional_kwargs}")
    logger.debug(f"Raw LLM resp response_metadata: {getattr(resp, 'response_metadata', None)}")

    text = _content_to_text(resp.content)

    if not text.strip():
        logger.debug("Model returned empty content.")
        return "(no reply from model)"

    return text


