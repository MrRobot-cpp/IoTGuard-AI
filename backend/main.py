from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from db.database import init_db
from routes import gateway, attacks, mitigations, results

app = FastAPI(title="IoTGuard-AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gateway.router, prefix="/gateway", tags=["gateway"])
app.include_router(attacks.router, prefix="/attacks", tags=["attacks"])
app.include_router(mitigations.router, prefix="/mitigations", tags=["mitigations"])
app.include_router(results.router, prefix="/results", tags=["results"])


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}
