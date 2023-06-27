from fastapi import FastAPI

from app.chat.router import router as chat_router
from app.config import settings
from app.tutor.router import router as tutor_router
from app.user.router import router as user_router


def create_app() -> FastAPI:
    """
    Create and return a FastAPI instance with the specified routes and settings.

    Returns:
        FastAPI: A FastAPI instance with the specified routes and settings.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url="/openapi.json" if settings.show_docs else None,
    )

    app.include_router(user_router, prefix="/users")  # TODO: consider removing prefix
    app.include_router(chat_router)
    app.include_router(tutor_router)

    @app.get("/_health")
    async def health():
        return {"status": "ok"}

    return app
