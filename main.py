from fastapi import FastAPI
import importlib
from app.db.session import get_db
from app.utils.redis import get_redis_client
from app.service.embedding import load_glove_model



router_modules = [
    "app.api.authentication",
    "app.api.countries",
    "app.api.cities",
    "app.api.attractions",
    "app.api.recommendations",
]
app = FastAPI()

for module in router_modules:
    imported_module = importlib.import_module(module)
    if hasattr(imported_module, "router"):
        app.include_router(imported_module.router)

@app.on_event("startup")
async def load_glove_model_on_startup():
    """Load the glove model once during startup"""
    app.state.glove_model = load_glove_model()

    db = next(get_db())
    redis_client = await get_redis_client()


@app.on_event("shutdown")
async def cleanup():
    app.state.glove_model = None
