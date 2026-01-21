# backend/api/analytics.py

# imports
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

# local imports
from backend.utils import get_logger
from backend.services.analytics import get_solve_steps
from backend.database.db_driver import create_puzzle

logger = get_logger(__name__)
router = APIRouter(prefix="/analytics")

@router.get("/steps")
async def steps() -> List[Dict[str, Any]]:
    try:
        data = get_solve_steps()
        
    except Exception as _:
        logger.exception("Failed to fetch solve steps.")
        raise HTTPException(status_code=500, detail="Failed to fetch solve steps.")
    
    return data

@router.post("/ingest")
async def ingest(location_data: str):
    print(location_data)
    