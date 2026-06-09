import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[0]
ROOT_DIRECTORY = BASE_DIR.parent

if ROOT_DIRECTORY not in  sys.path:
  sys.path.append(str(ROOT_DIRECTORY))

from SQLAlchemy_work_db.engine_and_models import Base, engine
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.API_routers import router


app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
  Base.metadata.create_all(engine)
  import uvicorn
  uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
  

@app.exception_handler(ValueError)
def value_error_castom(request: Request, exc: ValueError):
  return JSONResponse(status_code=400, 
        content={
          "msg": str(exc),
          "ТЕСТ": "КАКОЕ_ТО ОПИСАНИЕ ИЛИ СООБЩЕНИЕ"
          })
