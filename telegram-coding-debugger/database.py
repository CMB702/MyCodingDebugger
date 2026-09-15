"""Small asynchronous SQLite persistence layer for debugging requests."""

import asyncio
import sqlite3
from pathlib import Path


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path

    async def initialize(self) -> None:
        await asyncio.to_thread(self._initialize_sync)

    def _initialize_sync(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS debug_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    language TEXT NOT NULL,
                    submission TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    async def save_request(self, user_id: int, language: str, submission: str) -> None:
        await asyncio.to_thread(self._save_request_sync, user_id, language, submission)

    def _save_request_sync(self, user_id: int, language: str, submission: str) -> None:
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                "INSERT INTO debug_requests (user_id, language, submission) VALUES (?, ?, ?)",
                (user_id, language, submission),
            )
