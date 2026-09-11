from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.api.ws import router as ws_router
from app.engine import service


@asynccontextmanager
async def lifespan(_app: FastAPI):
    service.start()
    yield
    service.stop()


app = FastAPI(title="UNKNOWN", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(api_router)
app.include_router(ws_router)


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}
