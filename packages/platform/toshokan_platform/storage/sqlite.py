from __future__ import annotations

import sqlite3
from functools import lru_cache


@lru_cache
def get_sqlite_connection(path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
