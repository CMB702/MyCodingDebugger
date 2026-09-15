"""Application configuration loaded exclusively from environment variables."""

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    ai_api_key: str
    ai_base_url: str
    ai_model: str
    database_path: Path


def get_settings() -> Settings:
    """Load and validate the configuration without logging sensitive values."""
    values = {
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
        "AI_API_KEY": os.getenv("AI_API_KEY", "").strip(),
        "AI_BASE_URL": os.getenv("AI_BASE_URL", "").strip(),
        "AI_MODEL": os.getenv("AI_MODEL", "").strip(),
    }
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise RuntimeError("Missing required environment variables: " + ", ".join(missing))

    return Settings(
        telegram_bot_token=values["TELEGRAM_BOT_TOKEN"],
        ai_api_key=values["AI_API_KEY"],
        ai_base_url=values["AI_BASE_URL"].rstrip("/"),
        ai_model=values["AI_MODEL"],
        # Set DATABASE_PATH=/var/data/debugger.db on Render when using its disk.
        database_path=Path(os.getenv("DATABASE_PATH", str(BASE_DIR / "debugger.db"))),
    )
