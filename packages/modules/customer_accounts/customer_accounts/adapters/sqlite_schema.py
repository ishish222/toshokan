from __future__ import annotations

import sqlite3


def ensure_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY,
            stripe_customer_id TEXT NOT NULL,
            tokens INTEGER NOT NULL,
            name TEXT,
            contact_json TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            archived_at TEXT
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            customer_ids_json TEXT NOT NULL,
            cognito_id TEXT NOT NULL,
            email TEXT NOT NULL,
            roles_json TEXT NOT NULL,
            timezone TEXT,
            created_at TEXT NOT NULL,
            archived_at TEXT
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS invitations (
            id TEXT PRIMARY KEY,
            token TEXT NOT NULL UNIQUE,
            customer_id TEXT NOT NULL,
            email TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            accepted_at TEXT
        )
        """
    )
    connection.execute("CREATE INDEX IF NOT EXISTS idx_invitations_token ON invitations (token)")

    # -- migrations for existing databases --
    _add_column_if_missing(connection, "users", "timezone", "TEXT")

    connection.commit()


def _add_column_if_missing(
    connection: sqlite3.Connection,
    table: str,
    column: str,
    col_type: str,
) -> None:
    columns = [row[1] for row in connection.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in columns:
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
