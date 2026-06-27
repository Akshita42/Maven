# ─────────────────────────────────────────────────────────────────
# src/main.py
# ─────────────────────────────────────────────────────────────────
#
# Main application entry point for the FastAPI AI Service.
# Configures middleware, exception handlers, routers, and triggers
# the developer experience startup banner.
# ─────────────────────────────────────────────────────────────────

import time
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.router import api_router
from src.config.settings import settings
from src.constants.api import SERVICE_NAME, VERSION, STATUS_ERROR
from src.constants import error_codes
from src.utils.logger import logger
from src.utils.response import send_error

# Initialize FastAPI application
app = FastAPI(
    title="maven-ai-service",
    description="Stateless intelligence layer for investment recommendation pipeline.",
    version=VERSION,
    docs_url="/docs",
    redoc_url=None
)

# ── Middleware ─────────────────────────────────────────────────────────────
# Allows Node.js backend to query FastAPI from different port/host configs
# (Only required if called cross-origin from frontend, but standard safety)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Node.js backend to Python backend is internal server-to-server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Route Logging Middleware ────────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)
    
    # Log incoming request path, status, and duration
    status_code = response.status_code
    path = request.url.path
    method = request.method
    
    log_meta = {"status": status_code, "duration": f"{duration_ms}ms"}
    
    if status_code >= 500:
        logger.error(f"{method} {path}", meta=log_meta)
    elif status_code >= 400:
        logger.warn(f"{method} {path}", meta=log_meta)
    else:
        logger.info(f"{method} {path}", meta=log_meta)
        
    return response

# ── Centralized Exception Handlers ─────────────────────────────────────────

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handles standard FastAPI/Starlette HTTP exceptions (like 404 Not Found)."""
    status_code = exc.status_code
    message = exc.detail
    
    # Map status codes to machine-readable error codes
    code = error_codes.INTERNAL_SERVER_ERROR
    if status_code == 404:
        code = error_codes.ROUTE_NOT_FOUND
        message = "The requested endpoint does not exist."
    elif status_code == 401:
        code = "UNAUTHORIZED"
    elif status_code == 403:
        code = "FORBIDDEN"
        
    return send_error(
        code=code,
        message=message,
        status_code=status_code
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles Pydantic validation errors on incoming requests."""
    errors = []
    for err in exc.errors():
        field = " -> ".join(str(x) for x in err["loc"])
        errors.append({"field": field, "message": err["msg"]})
        
    return send_error(
        code=error_codes.VALIDATION_ERROR,
        message="Request validation failed.",
        details={"validation_errors": errors},
        status_code=422
    )

@app.exception_handler(Exception)
async def catchall_exception_handler(request: Request, exc: Exception):
    """Last line of defense for unhandled exceptions. Prevents process crash."""
    logger.error(f"Unhandled system error: {str(exc)}")
    
    # Expose stack details ONLY in non-production
    details = None
    if settings.env != "production":
        import traceback
        details = {"stack": traceback.format_exc()}
        
    return send_error(
        code=error_codes.INTERNAL_SERVER_ERROR,
        message="An unexpected server error occurred.",
        details=details,
        status_code=500
    )

# ── Mounting Router ────────────────────────────────────────────────────────
app.include_router(api_router)

# ── Startup Events & Developer Banner ──────────────────────────────────────
@app.on_event("startup")
def startup_event():
    # Print clean terminal banner for Developer Experience
    # Replaced Unicode ═ and ◆ with ASCII equivalents to prevent UnicodeEncodeError on Windows
    divider = f"\033[36m\033[1m{'=' * 54}\033[0m"
    label = lambda k, v, c="\033[0m": f"  \033[33m{k:<14}\033[0m{c}{v}\033[0m"
    
    print(f"\n{divider}")
    print("  \033[32m\033[1m*  maven-ai-service\033[0m")
    print(divider)
    print(label("Service", SERVICE_NAME, "\033[32m"))
    print(label("Version", VERSION))
    print(label("Environment", settings.env, "\033[33m" if settings.env == "production" else "\033[0m"))
    print(label("Host", settings.host))
    print(label("Port", str(settings.port)))
    print(label("Health", f"http://{settings.host}:{settings.port}/api/v1/health", "\033[36m"))
    print(f"{divider}\n")
    
    logger.info("AI Service is ready to accept queries.")
