"""
ApplyFlow — application entry point.

To run in the development environment:
    uv run python main.py
    # or
    uv run uvicorn applyflow.api.app:app --reload
"""

import uvicorn

from applyflow.core.config import settings


def main() -> None:
    uvicorn.run(
        "applyflow.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )


if __name__ == "__main__":
    main()
