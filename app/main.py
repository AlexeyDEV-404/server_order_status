# flake8: noqa
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.api.master import router as rout_master
from app.api.master_skills import router as rout_ms
from app.api.orders import router as rout_ord
from app.api.skills import router as rout_skills
from app.core.database import engine
from app.models.models import Base


from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("STARTUP")
    await create_BASE()
    yield
    # await drop_BASE()


app = FastAPI(lifespan=lifespan)


app.include_router(rout_master)
app.include_router(rout_ms)
app.include_router(rout_ord)
app.include_router(rout_skills)


async def create_BASE():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_BASE():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <body>
            <h1>Моя картинка</h1>
            <img src="static/image.png" alt="image">
        </body>
    </html>
    """
