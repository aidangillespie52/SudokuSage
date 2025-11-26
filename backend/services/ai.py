# backend/services/ai.py

# imports
import os
from dotenv import load_dotenv
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# local imports
from backend.utils import get_logger, load_prompt

logger = get_logger(__name__)
load_dotenv()

# model for chat message
class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

INCLUDE_SOLVED = os.getenv("INCLUDE_SOLVED_BOARD_IN_PROMPT", "true").lower() == "true"
MODEL = os.getenv("OPENAI_MODEL", "gpt-5-nano")
SYS_PROMPT = load_prompt("system.md")
SYS_MESSAGE = ChatMessage(role="system", content=SYS_PROMPT)

llm = ChatOpenAI(
    model=MODEL,
    use_responses_api=True,
    temperature=0.2,
    max_retries=3,
    reasoning = {"effort": "medium"},
    verbosity = "low",
)

logger.info(f"Using LLM model: {MODEL}")

# convert list of dict messages to LangChain message objects
def _to_lc_messages(messages: List[Dict[str, str]]) -> List[Any]:
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

# convert various content formats to plain text
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

# validate query parameters
def validate_query_params(board: Optional[str], session_id: Optional[str], messages: List[ChatMessage]) -> None:
    if board is None:
        logger.warning("No board string provided in query parameters.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Board string is required as a query parameter."
        )
    
    if board == "":
        logger.warning("No board string provided in query parameters.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Board string is required as a query parameter."
        )
    
    if len(board) != 81 or not all(c.isdigit() for c in board):
        logger.warning(f"Invalid board string provided: {board}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid board string. Must be exactly 81 digits (0-9)."
        )

    if not session_id:
        logger.warning("No session_id provided in query parameters.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="session_id is required as a query parameter."
        )
        
    if not messages or messages[0].role != "system":
        return [SYS_MESSAGE] + messages
    
    return messages

# add board and solution to messages
def add_board_to_messages(messages: List[ChatMessage], board: str, solution: str) -> None:
    board_info = (
        "Here is the Sudoku board you need to solve:\n"
        f"{board}\n\n"
    )
    
    if INCLUDE_SOLVED:
        board_info += (
            "Here is the solved Sudoku board for your reference:\n"
            f"{solution}\n\n"
        )
    
    board_info += ("Please provide your response based on this board.")
    
    if messages[-1].role == "user":
        messages[-1].content += "\n\n" + board_info
    
    return messages

# call the LLM with messages
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


