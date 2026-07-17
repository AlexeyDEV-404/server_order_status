# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
from fastapi import FastAPI

from app.api.API_routers import router
from SQLAlchemy_work_db.engine_and_models import Base, engine

app = FastAPI()
app.include_router(router)


async def create_Base():
    async with engine.begin() as conn:
        return await conn.run_sync(Base.metadata.create_all)


async def drop_Base():
    async with engine.begin() as conn:
        return await conn.run_sync(Base.metadata.drop_all)


@app.get("/")
async def root():
    return {"status": "ok"}
