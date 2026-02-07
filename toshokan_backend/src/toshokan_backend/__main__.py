from __future__ import annotations

from pathlib import Path

import uvicorn
from dotenv import load_dotenv

from .main import app


def run() -> None:
    env_path = Path(__file__).resolve().parents[3] / ".env"
    load_dotenv(env_path)
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run()
