from __future__ import annotations

import sys
from pathlib import Path

import uvicorn

_root = Path(__file__).resolve().parents[1]
_src = _root / "src"
if _src.exists() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))


def run() -> None:
    uvicorn.run("toshokan_backend.main:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run()