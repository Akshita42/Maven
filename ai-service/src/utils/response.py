# ─────────────────────────────────────────────────────────────────
# src/utils/response.py
# ─────────────────────────────────────────────────────────────────
#
# Standardised HTTP response helpers matching the backend.
# Enforces a uniform success/error structure for all route handlers.
# ─────────────────────────────────────────────────────────────────

from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from src.constants.api import STATUS_SUCCESS, STATUS_ERROR

def send_success(
    data: Any = None, 
    meta: Optional[Dict[str, Any]] = None, 
    status_code: int = 200
) -> JSONResponse:
    """
    Returns a standardized JSON success response.
    
    Format:
    {
        "status": "success",
        "data": { ... },
        "meta": { ... }
    }
    """
    if data is None:
        data = {}
    if meta is None:
        meta = {}
        
    return JSONResponse(
        status_code=status_code,
        content={
            "status": STATUS_SUCCESS,
            "data": jsonable_encoder(data),
            "meta": jsonable_encoder(meta)
        }
    )

def send_error(
    code: str, 
    message: str, 
    details: Optional[Dict[str, Any]] = None, 
    status_code: int = 500
) -> JSONResponse:
    """
    Returns a standardized JSON error response.
    
    Format:
    {
        "status": "error",
        "error": {
            "code": "...",
            "message": "...",
            "details": { ... }
        }
    }
    """
    error_payload = {
        "code": code,
        "message": message
    }
    if details is not None:
        error_payload["details"] = jsonable_encoder(details)
        
    return JSONResponse(
        status_code=status_code,
        content={
            "status": STATUS_ERROR,
            "error": error_payload
        }
    )
