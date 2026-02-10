from __future__ import annotations

import json
from datetime import datetime
from typing import Optional


def dt_to_str(value: Optional[datetime]) -> Optional[str]:
    return value.isoformat() if value else None


def str_to_dt(value: Optional[str]) -> Optional[datetime]:
    return datetime.fromisoformat(value) if value else None


def list_to_json(values: list[str]) -> str:
    return json.dumps(values)


def list_from_json(value: str) -> list[str]:
    return json.loads(value) if value else []
