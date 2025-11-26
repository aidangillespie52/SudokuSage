# backend/utils.py

# imports
from pathlib import Path
import logging
import sys
from typing import Optional
from colorama import init as colorama_init, Fore, Style

PROMPT_DIR = Path(__file__).parent / "prompts"
colorama_init(autoreset=True) # initialize colorama for Windows

class ColorFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG:    Fore.BLUE,
        logging.INFO:     Fore.CYAN,
        logging.WARNING:  Fore.YELLOW,
        logging.ERROR:    Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def format(self, record: logging.LogRecord) -> str:
        level_color = self.LEVEL_COLORS.get(record.levelno, "")
        levelname = f"{level_color}{record.levelname}{Style.RESET_ALL}"

        # Basic format: [LEVEL] module: message
        fmt = f"[{levelname}] {record.name}: {record.getMessage()}"
        if record.exc_info:
            # If there's an exception, use default formatter to include traceback
            return f"{fmt}\n{super().formatException(record.exc_info)}"
        return fmt

def load_prompt(name: str) -> str:
    path = PROMPT_DIR / f"{name}"
    return path.read_text(encoding="utf-8")

# single shared handler for all loggers created via get_logger
_stream_handler: Optional[logging.Handler] = None

def _get_stream_handler() -> logging.Handler:
    global _stream_handler
    if _stream_handler is None:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(ColorFormatter())
        _stream_handler = handler
    return _stream_handler


# returns a logger with colored output
def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger with colored output.
    Call this from any module: logger = get_logger(__name__).
    """
    logger = logging.getLogger(name or "app")
    logger.setLevel(logging.DEBUG)

    # Avoid adding multiple handlers if called many times
    handler = _get_stream_handler()
    if handler not in logger.handlers:
        logger.addHandler(handler)

    # Let uvicorn/system also handle logs if needed
    logger.propagate = False
    return logger