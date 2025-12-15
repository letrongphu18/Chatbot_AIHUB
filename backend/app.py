from fastapi import FastAPI
from backend.api.webhook_routes import router as webhook_router
from backend.api.conversation_routes import router as conversation_router
from backend.api.page_config_routes import router as page_config_routes
from backend.api.statistics_routes import router as statistics_routes


def create_app() -> FastAPI:
    app = FastAPI()

    # Gắn router
    app.include_router(webhook_router)
    app.include_router(conversation_router)
    app.include_router(page_config_routes)
    app.include_router(statistics_routes)

    @app.get("/")
    def home():
        return {"message": "Chatbot AIHUB is running!", "status": "ok"}

    return app
