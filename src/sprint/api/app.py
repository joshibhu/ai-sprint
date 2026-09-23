"""FastAPI application factory."""

import logging

from fastapi import FastAPI

from .routes import router

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def create_app() -> FastAPI:
    """Build the app. A factory, not a module-level singleton, so tests can
    construct a fresh instance with different settings."""
    app = FastAPI(
        title="sprint",
        description="Invoice extraction and a tool-calling agent.",
        version="0.1.0",
    )
    app.include_router(router)
    return app


app = create_app()
