from pathlib import Path
import aiohttp
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from backend.utils import get_logger
from backend.api.routes_ai import router as ai_router
from backend.api.routes_board import router as board_router

BASE_DIR = Path(__file__).resolve().parent
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    app.state.session = aiohttp.ClientSession()
    logger.info("GLOBAL SESSION CREATED")

    try:
        yield  # app runs while this is active
        
    finally:
        # shutdown (always run, even on Ctrl+C)
        await app.state.session.close()
        print("GLOBAL SESSION CLOSED")

app = FastAPI(lifespan=lifespan)

# static files
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "frontend" / "static")),
    name="static",
)

# templates
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend" / "templates"))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# routes
app.include_router(ai_router)
app.include_router(board_router)