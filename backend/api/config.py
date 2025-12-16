# backend/api/config.py

# imports
from fastapi import APIRouter, PlainTextResponse

# local imports
from backend.utils import get_logger
from backend.config.hints import SINGLE_HINT

logger = get_logger(__name__)
router = APIRouter(prefix="/config")

@router.get("/single-hint", response_class=PlainTextResponse)
def single_hint() -> str:
    return SINGLE_HINT