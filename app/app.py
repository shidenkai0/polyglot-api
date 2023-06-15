from fastapi import FastAPI
from app.config import settings
from app.user.router import router as user_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url="/openapi.json" if settings.show_docs else None,
    )

    app.include_router(user_router, prefix="/users")

    @app.get("/_health")
    async def health():
        return {"status": "ok"}

    return app
