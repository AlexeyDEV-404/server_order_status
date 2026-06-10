import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[0]
ROOT_DIRECTORY = BASE_DIR.parent

if ROOT_DIRECTORY not in  sys.path:
  sys.path.append(str(ROOT_DIRECTORY))

from SQLAlchemy_work_db.engine_and_models import Base, engine
from fastapi import FastAPI
from app.api.API_routers import router


app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
  Base.metadata.create_all(engine)
  import uvicorn
  uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
  
