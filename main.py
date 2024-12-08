from fastapi import FastAPI
from app.api.routers.authentication_router import authentication_router
from app.api.routers.countries_router import countries_router
from app.api.routers.cities_router import cities_router
from app.api.routers.recommendations_router import recommendations_router
from app.service.embedding import load_glove_model

app = FastAPI()


@app.on_event("startup")
async def load_glove_model_on_startup():
    """Load the glove model once during startup"""
    app.state.glove_model = load_glove_model()


@app.on_event("shutdown")
async def cleanup():
    app.state.glove_model = None


app.include_router(authentication_router)
app.include_router(countries_router)
app.include_router(cities_router)
app.include_router(recommendations_router)
