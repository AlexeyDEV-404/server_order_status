from fastapi import APIRouter, Depends, HTTPException
from database.service import (server_order_create_new, server_display_master_skills, server_specific_order, server_all_orders, server_order_master_assinged, server_order_in_progress, server_order_complet, server_search_master, server_services, server_cancel_order, server_delete_order, server_add_master_in_db, server_master_info, server_add_master_skills, server_all_table, server_insert_skill)
from app.api.pydantic_ import UserInput, AssingMaster
from SQLAlchemy_work_db.enusm import StatusMasterCheck
from SQLAlchemy_work_db.engine_and_models  import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from app.api.pydantic_ import (TableMasterSkills, TableOrders)



router = APIRouter(prefix="/user", tags=["User"])


@router.post("/order/new")
async def new_order(user_input: UserInput, db: AsyncSession = Depends(get_db)):
    return (await server_order_create_new(category=user_input.category, service=user_input.services, description=user_input.description, db = db))

@router.post("/order/{order_id}/assinged", response_model=TableOrders)
async def assinged(order_id, data: AssingMaster, db: AsyncSession = Depends(get_db)):
    return (await server_order_master_assinged(orderID=order_id, masterID=data.masterID, db = db))

@router.post("/order/{order_id}/in_progress")
async def in_progress(order_id, db: AsyncSession = Depends(get_db)) -> str:
    return (await server_order_in_progress(orderID=order_id, db = db))

@router.post("/order/{order_id}/completed", response_model=TableOrders)
async def completed(order_id, db: AsyncSession = Depends(get_db)):
    return (await server_order_complet(orderID=order_id, db = db))

@router.post("/order/{order_id}/cancel", response_model=TableOrders)
async def cancel(order_id, db: AsyncSession = Depends(get_db)):
    return (await server_cancel_order(orderID=order_id, db = db))

@router.post("/order/{order_id}/delete")
async def delete_order(order_id, db: AsyncSession = Depends(get_db)):
    return (await server_delete_order(orderID=order_id, db = db))

@router.post("/add_master")
async def add_master_in_db(name: str, status = StatusMasterCheck.FREE, db: AsyncSession = Depends(get_db)) -> int|None:
    try: return (await server_add_master_in_db(name=name, status=status, db = db))
    except (NoResultFound, MultipleResultsFound) as e: raise HTTPException(status_code=404, detail=f"{e}")

@router.post("/add_master_skill")
async def add_master_skills(master_id:int, skill_id:int, db: AsyncSession = Depends(get_db)):
    try: return (await server_add_master_skills(master_id = master_id, skill_id = skill_id, db = db))
    except ValueError as e: raise HTTPException(status_code=409, detail=f"{e}")

@router.post("/insert_skill")
async def insert_skill(category: str, service: str, db: AsyncSession = Depends(get_db)) -> int:
    try: return (await server_insert_skill(category=category, service=service, db = db))
    except ValueError as e: raise HTTPException(status_code=409, detail=f"{e}")

@router.get("/order/{order_id}", response_model=TableOrders)
async def order(order_id: int, db: AsyncSession = Depends(get_db)):
    try: return (await server_specific_order(orderID=order_id, db = db))
    except ValueError as e: raise HTTPException(status_code=404, detail=f"{e}")
    
@router.get("/table_skill_master")
async def all_table_skills_master(db: AsyncSession = Depends(get_db)):
    try: return (await server_all_table(db = db))
    except ValueError as e: raise HTTPException(status_code=404, detail=f"{e}") 

@router.get("/orders", response_model=TableOrders)
async def orders_list(db: AsyncSession = Depends(get_db)):
    try: return (await server_all_orders(db = db))
    except ValueError as e: raise HTTPException(status_code=404, detail=f"{e}")

@router.get("/master_list")
async def display(db: AsyncSession = Depends(get_db)):
    try: return (await server_display_master_skills(db = db))
    except ValueError as e:  raise HTTPException(status_code=404, detail=f"{e}")
    
@router.get("/search_master")
async def search_master(category: str, services: str, db: AsyncSession = Depends(get_db)):
    try: return (await server_search_master(category=category, service=services, db = db))
    except ValueError as e:  raise HTTPException(status_code=404, detail=f"{e}")

@router.get("/service")
async def service(db: AsyncSession = Depends(get_db)):
    try: return (await server_services(db = db))
    except ValueError as e:  raise HTTPException(status_code=404, detail=f"{e}")


