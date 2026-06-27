# ─────────────────────────────────────────────────────────────────
# src/config/settings.py
# ─────────────────────────────────────────────────────────────────
#
# Configuration management via Pydantic Settings.
# Enforces validation at import time (startup fail-fast).
# ─────────────────────────────────────────────────────────────────

import sys
from typing import Literal
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Validates and registers all configuration variables.
    Reads from environment variables or a local .env file.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    env: Literal["development", "production", "test"] = Field(
        default="development",
        alias="ENV"
    )
    
    host: str = Field(
        default="127.0.0.1",
        alias="HOST"
    )
    
    port: int = Field(
        default=8000,
        alias="PORT",
        ge=1,
        le=65535
    )

# ─── Configuration Validation ─────────────────────────────────────────────
try:
    settings = Settings()
except ValidationError as e:
    # Print a red console banner with clear validation diagnostics on failure
    # Replaced Unicode box-drawing double lines with ASCII equals sign to prevent UnicodeEncodeError
    divider = "\033[31m" + "=" * 54 + "\033[0m"
    print(f"\n{divider}")
    print("\033[31m  FATAL: Maven AI Service cannot start                \033[0m")
    print("\033[31m  Invalid or missing environment configuration.        \033[0m")
    print(divider)
    
    for error in e.errors():
        loc = " -> ".join(str(x) for x in error["loc"])
        print(f"\033[31m  [Config Error]\033[0m Field: \033[33m{loc}\033[0m | Message: {error['msg']}")
        
    print("\n\033[33m  -> Check your .env file or environment variables.\033[0m\n")
    sys.exit(1)
except Exception as e:
    print(f"\n\033[31m  FATAL: Unexpected configuration error: {str(e)}\033[0m\n")
    sys.exit(1)
