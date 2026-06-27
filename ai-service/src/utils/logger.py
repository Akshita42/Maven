# ─────────────────────────────────────────────────────────────────
# src/utils/logger.py
# ─────────────────────────────────────────────────────────────────
#
# Custom colorized standard logger wrapper for FastAPI.
# Enforces structured logs and consistent logging format.
# ─────────────────────────────────────────────────────────────────

import logging
import sys
from datetime import datetime
from src.config.settings import settings

# ANSI colour escape sequences
COLOURS = {
    "reset": "\033[0m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "cyan": "\033[36m",
    "dim": "\033[2m"
}

LEVEL_COLORS = {
    "INFO": COLOURS["green"],
    "WARNING": COLOURS["yellow"],
    "ERROR": COLOURS["red"],
    "DEBUG": COLOURS["cyan"]
}

class ColorFormatter(logging.Formatter):
    """Formats log records with colors in non-production environments."""
    
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.utcfromtimestamp(record.created).isoformat() + "Z"
        level = record.levelname
        
        # Colorize level label
        color = LEVEL_COLORS.get(level, COLOURS["reset"])
        padded_level = f"{level:<7}"
        level_lbl = f"{color}{padded_level}{COLOURS['reset']}"
        
        # Format: [LEVEL] 2026-06-27T12:00:00.000Z  Message
        log_line = f"[{level_lbl}] {COLOURS['cyan']}{timestamp}{COLOURS['reset']}  {record.getMessage()}"
        
        # Append extras if metadata exists
        if hasattr(record, "meta") and record.meta:
            log_line += f" {COLOURS['dim']}{record.meta}{COLOURS['reset']}"
            
        return log_line

# Configure the logger
root_logger = logging.getLogger("maven_ai")
root_logger.setLevel(logging.DEBUG if settings.env != "production" else logging.INFO)

# Avoid adding duplicate handlers if re-imported
if not root_logger.handlers:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColorFormatter())
    root_logger.addHandler(console_handler)
    root_logger.propagate = False

class LoggerWrapper:
    """Wrapper that provides info, warn, error, and debug interfaces."""
    
    def info(self, message: str, meta: dict = None):
        root_logger.info(message, extra={"meta": meta})
        
    def warn(self, message: str, meta: dict = None):
        root_logger.warning(message, extra={"meta": meta})
        
    def error(self, message: str, meta: dict = None):
        root_logger.error(message, extra={"meta": meta})
        
    def debug(self, message: str, meta: dict = None):
        # Debug is suppressed in production environment
        if settings.env != "production":
            root_logger.debug(message, extra={"meta": meta})

# Expose a single logger instance
logger = LoggerWrapper()
