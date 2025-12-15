from fastapi import FastAPI
from frontend.routes.page_config_routes import router as page_config_frontend_routes
from frontend.routes.conversation_routes import router as conversation_frontend_routes

def create_frontend_app() -> FastAPI:
    app = FastAPI()
    # Gắn router
    app.include_router(page_config_frontend_routes)
    app.include_router(conversation_frontend_routes)

    return app