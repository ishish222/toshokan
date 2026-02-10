from __future__ import annotations

import os
from pathlib import Path

import uvicorn

from .main import create_app

# Default cert directory (relative to the api app location)
# apps/api/src/navigator_api -> ../../../.. -> apps -> .. -> cert
DEFAULT_CERT_DIR = Path(__file__).parent.parent.parent.parent.parent.parent / "cert"


def main() -> None:
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    
    # SSL configuration
    ssl_enabled = os.getenv("SSL_ENABLED", "false").lower() in ("true", "1", "yes")
    
    ssl_kwargs = {}
    if ssl_enabled:
        ssl_keyfile = os.getenv("SSL_KEYFILE", str(DEFAULT_CERT_DIR / "api.local.key"))
        ssl_certfile = os.getenv("SSL_CERTFILE", str(DEFAULT_CERT_DIR / "api.local.crt"))
        ssl_kwargs = {
            "ssl_keyfile": ssl_keyfile,
            "ssl_certfile": ssl_certfile,
        }
    
    uvicorn.run(create_app(), host=host, port=port, **ssl_kwargs)


if __name__ == "__main__":
    main()
