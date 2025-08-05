"""Main FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from src.shared.infrastructure.config import get_settings
from src.user.presentation.user_routes import router as user_router
from src.pokemon.presentation.pokemon_routes import router as pokemon_router


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="Pokemon Ecommerce API",
        description="Backend API for Pokemon Ecommerce with Hexagonal Architecture",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Security middleware
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["localhost", "127.0.0.1", "*.vercel.app"]
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "pokemon-ecommerce-api"}

    # Include routers
    app.include_router(user_router, prefix="/api/v1/users", tags=["users"])
    app.include_router(pokemon_router, prefix="/api/v1/pokemon", tags=["pokemon"])

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
