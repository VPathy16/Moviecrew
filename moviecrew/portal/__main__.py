"""`python -m moviecrew.portal` — run the portal's FastAPI app under uvicorn.

Binds to 127.0.0.1 (local-only by default) on $PORT, or 8000 if unset.
"""

from __future__ import annotations

import os

import uvicorn


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("moviecrew.portal.app:app", host="127.0.0.1", port=port)


if __name__ == "__main__":
    main()
