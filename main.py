from fastapi import FastAPI
from app.api.routers.authentication_router import authentication_router
from app.api.routers.countries_router import countries_router
from app.api.routers.cities_router import cities_router
from app.api.routers.recommendations_router import recommendations_router
from app.api.routers.attractions_router import attractions_router
from app.service.embedding import load_glove_model
from app.db.session import get_db
from app.utils.redis import get_redis_client
from app.service.recommendations.utils import RecommendationsHelper

app = FastAPI()


@app.on_event("startup")
async def load_glove_model_on_startup():
    """Load the glove model once during startup"""
    app.state.glove_model = load_glove_model()
    db = next(get_db())
    redis_client = get_redis_client()
    RecommendationsHelper(db, redis_client).create_user_interactions_matrix()


@app.on_event("shutdown")
async def cleanup():
    app.state.glove_model = None


app.include_router(authentication_router)
app.include_router(countries_router)
app.include_router(cities_router)
app.include_router(recommendations_router)

app.include_router(attractions_router)
