
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Initialize Phoenix observability BEFORE importing LangChain components
from backend.observability.phoenix import init_phoenix
init_phoenix()

from backend.api.routes import router as api_router
from backend.api.websocket import router as ws_router

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    app = FastAPI(title="Antigravirt Backend", version="0.1.0")
    
    # Global Exception Handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error", "detail": str(exc)},
        )

    # CORS Configuration
    origins = [
        "http://localhost:5173", # Frontend dev server
        "http://localhost:3000",
        "*"
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include Routers
    app.include_router(api_router, prefix="/api")
    app.include_router(ws_router)
    
    return app

app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
