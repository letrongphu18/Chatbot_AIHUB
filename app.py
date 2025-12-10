#file chứa fastapi app
#uvicorn app:app --host 0.0.0.0 --port 8000

from fastapi import FastAPI
from backend.api.webhook_routes import router as webhook_router
from backend.api.conversation_routes import router as conversation_router
from backend.api.page_config_routes import router as page_config_routes
from frontend.routes.page_config_routes import router as page_config_frontend_routes

app = FastAPI()

app.include_router(webhook_router)
app.include_router(conversation_router)
app.include_router(page_config_routes)
app.include_router(page_config_frontend_routes)

@app.get("/")
def home():
    return {"message": "Chatbot AIHUB is running!", "status": "ok"}
