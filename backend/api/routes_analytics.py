# backend/api/routes_ai.py

from fastapi import APIRouter, HTTPException
from backend.utils import get_logger
from backend.services.analytics_service import get_solve_steps

from backend.database.db_driver import create_puzzle

logger = get_logger(__name__)
router = APIRouter(prefix="/analytics")

@router.get("/steps")
async def steps():
    try:
        data = get_solve_steps()
        
    except Exception as e:
        logger.exception("Failed to fetch solve steps.")
        raise HTTPException(status_code=500, detail="Failed to fetch solve steps.")
    
    return data