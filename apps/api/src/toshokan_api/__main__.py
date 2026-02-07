from __future__ import annotations

import uvicorn
from dotenv import find_dotenv, load_dotenv

from .main import app


def run() -> None:
    load_dotenv(find_dotenv())
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run()
