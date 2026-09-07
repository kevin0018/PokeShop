"""Main FastAPI application entry point."""

import json
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.pokemon.presentation.pokemon_routes import router as pokemon_router


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    load_dotenv()

    app = FastAPI(
        title="Pokemon Ecommerce API",
        description="Backend API for Pokemon Ecommerce with Hexagonal Architecture",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Security middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=json.loads(
            os.getenv(
                "ALLOWED_HOSTS",
                '["localhost", "127.0.0.1", "backend", "*.vercel.app"]',
            )
        ),
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=json.loads(
            os.getenv(
                "ALLOWED_ORIGINS",
                '["http://localhost:5173", "http://localhost:3000"]',
            )
        ),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "pokemon-ecommerce-api"}

    app.include_router(pokemon_router, prefix="/api/v1/pokemon", tags=["pokemon"])

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
