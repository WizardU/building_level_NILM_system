"""Small time helpers so every API timestamp is explicit UTC."""

from __future__ import annotations

from datetime import datetime, timezone


def utcnow() -> datetime:
    """Naive UTC, matching the columns stored by SQLite."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def ensure_utc(value: datetime) -> datetime:
    """Treat naive values as UTC and convert aware values to UTC (naive out)."""
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def to_iso(value: datetime | None) -> str | None:
    """Serialize as an ISO-8601 string that always carries a ``Z`` suffix."""
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_utc(value: str | datetime | None) -> datetime | None:
    """Parse an API timestamp and normalize it to naive UTC for DB queries."""
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        value = datetime.fromisoformat(text)
    return ensure_utc(value)
