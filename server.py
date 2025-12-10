import uvicorn
from app import app
import os

if __name__ == "__main__":
    uvicorn.run("app:app",
                host="127.0.0.1",
                port=int(os.getenv("PORT", 8000)),
                reload=True)
