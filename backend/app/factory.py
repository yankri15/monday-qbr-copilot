"""Application factory helpers for local and Vercel entrypoints."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routes import api_router
from app.routes.accounts import router as accounts_router
from app.routes.export import router as export_router
from app.routes.qbr import router as qbr_router
from app.routes.upload import router as upload_router


def _add_common_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
        ],
        allow_origin_regex=r"https://.*\.vercel\.app|https?://(localhost|127\.0\.0\.1):\d+",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def _register_common_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_request: Request, _exc: Exception) -> JSONResponse:
        """Return a safe fallback response for unexpected errors."""

        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )


def create_app(*, api_prefix: str = "/api") -> FastAPI:
    """Create the FastAPI application with a configurable API prefix."""

    app = FastAPI(
        title="monday.com QBR Co-Pilot API",
        version="0.1.0",
    )
    _add_common_middleware(app)
    _register_common_handlers(app)

    if api_prefix:
        app.include_router(api_router)
    else:
        app.include_router(accounts_router)
        app.include_router(export_router)
        app.include_router(qbr_router)
        app.include_router(upload_router)

    return app
