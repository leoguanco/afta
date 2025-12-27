from fastapi import FastAPI
from prometheus_client import make_asgi_app

app = FastAPI(title="Football Intelligence Engine API", version="0.1.0")

# Observability
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/")
async def root():
    return {"message": "Welcome to AFTA API", "system": "operational"}

@app.get("/health")
async def health():
    return {"status": "ok", "db": "unknown", "redis": "unknown"}
