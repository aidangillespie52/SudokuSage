# backend/api/routes_ai.py

from fastapi import APIRouter, Request, HTTPException, status
from backend.services.ai_service import call_llm
from backend.services.board_service import solve_board
from typing import List, Literal
from pydantic import BaseModel
from backend.utils import load_prompt
import asyncio
import aiohttp
from backend.utils import get_logger

INCLUDE_SOLVED = True

logger = get_logger(__name__)
router = APIRouter(prefix="/ai")

# data models
class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    board: str

# system prompt
SYS_PROMPT = load_prompt("system")
SYS_MESSAGE = ChatMessage(role="system", content=SYS_PROMPT)

def ensure_system_prompt(messages: List[ChatMessage]) -> List[ChatMessage]:
    if not messages or messages[0].role != "system":
        return [SYS_MESSAGE] + messages
    
    return messages

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

@router.post("/query")
async def query_endpoint(req: ChatRequest, request: Request):
    data = req.model_dump()   # THIS RETURNS A DICT
    board = data.get("board") # or data["board"]
    
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
    
    solved_board = solve_board(board)
    messages = ensure_system_prompt(req.messages)
    add_board_to_messages(messages, board, solved_board)
    logger.info(f"Original board: {board}")
    logger.info(f"Solved board: {solved_board}")
    
    logger.debug(f"Messages for LLM: {messages}")

    try:
        response = await call_llm([msg.model_dump() for msg in messages])
        
    except Exception as e:
        # catch-all (keep this last)
        logger.exception("Unexpected error in /ai/query")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected server error."
        )

    # 3) Normal success path
    return {"reply": response}