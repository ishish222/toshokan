from __future__ import annotations

from pathlib import Path

import uvicorn
from dotenv import load_dotenv

from .main import app


def run() -> None:
    env_path = Path(__file__).resolve().parents[3] / ".env"
    load_dotenv(env_path)
    repo_root = Path(__file__).resolve().parents[4]
    cert_path = repo_root / "cert" / "server.crt"
    key_path = repo_root / "cert" / "server.key"
    ssl_kwargs = {}
    if cert_path.exists() and key_path.exists():
        ssl_kwargs = {
            "ssl_certfile": str(cert_path),
            "ssl_keyfile": str(key_path),
        }
    uvicorn.run(app, host="0.0.0.0", port=8000, **ssl_kwargs)


if __name__ == "__main__":
    run()
