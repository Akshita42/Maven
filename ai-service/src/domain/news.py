# ─────────────────────────────────────────────────────────────────
# src/domain/news.py
# ─────────────────────────────────────────────────────────────────
#
# Core Domain Model representing a News item.
# Independent of Yahoo Finance or any external vendor.
# ─────────────────────────────────────────────────────────────────

from pydantic import BaseModel

class NewsItem(BaseModel):
    """Authoritative business model for corporate news updates and feed items."""
    headline: str
    publisher: str
    publishedAt: str  # ISO 8601 string
    url: str
