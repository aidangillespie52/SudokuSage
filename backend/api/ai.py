# backend/api/ai.py

# imports
from fastapi import APIRouter, Request, HTTPException, status
from typing import List, Dict, Any
from pydantic import BaseModel

# local imports
from backend.database.db_driver import log_step
from backend.services.ai import call_llm, validate_query_params, add_board_to_messages, ChatMessage
from backend.services.board import solve_board
from backend.services.hints import extract_hint_fields
from backend.utils import load_prompt
from backend.utils import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/ai")

# model for request body
class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    board: str
    puzzle_id: str
    session_id: str

# helper to check if last message requests a single hint
def last_message_has_single_hint(messages: List[ChatMessage]) -> bool:
    TARGET = "Give me a single cell hint for the current board."
    
    if not messages:
        return False
    
    last = messages[-1]
    return last.role == "user" and TARGET in last.content

@router.post("/query")
async def query_endpoint(req: ChatRequest) -> Dict[str, Any]:
    data = req.model_dump()
    board = data.get("board")
    puzzle_id = data.get("puzzle_id")
    session_id = data.get("session_id")
    logger.info(f"Received /ai/query for puzzle_id={puzzle_id}, session_id={session_id}")
    messages = req.messages
    
    # validate inputs
    try:
        messages = validate_query_params(
            board=board,
            session_id=session_id,
            messages=messages
        )
    except HTTPException as e:
        raise e
    
    solved_board = solve_board(board)
    messages = add_board_to_messages(messages, board, solved_board)
    hint_btn_pressed = last_message_has_single_hint(messages)
    
    logger.info(f"Original board: {board}")
    logger.info(f"Solved board: {solved_board}")
    logger.debug(f"Messages for LLM: {messages}")

    # call llm
    try:
        response = await call_llm([msg.model_dump() for msg in messages])
        
    except Exception as e:
        logger.exception("Unexpected error in /ai/query")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected server error."
        )
    
    if not hint_btn_pressed:
        logger.info("Successfully responded without hint extraction.")
        return {"reply": response}
    
    hint = extract_hint_fields(response)
    
    # log the step
    log_step(
        puzzle=puzzle_id,
        session_id=session_id,
        hint_text=response,
        r=hint.r,
        c=hint.c,
        value=hint.value,
        method_used=hint.method_used
    )
    
    logger.info("Successfully extracted hint fields and logged step.")
    
    return {
        "reply": response,
        "r": hint.r,
        "c": hint.c,
        "value": hint.value,
        "method_used": hint.method_used
    }