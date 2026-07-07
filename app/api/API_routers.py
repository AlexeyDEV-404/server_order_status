from fastapi import APIRouter, Depends, HTTPException
from database.service import Service
from app.api.pydantic_ import UserInput, AssingMaster
from SQLAlchemy_work_db.enusm import StatusMasterCheck
from app.api.deps import Repository, get_repository

from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from app.api.pydantic_ import (TableMasterSkills, TableOrders)



router = APIRouter(prefix="/user", tags=["User"])


@router.post("/order/new")
async def new_order(user_input: UserInput, repo: Repository = Depends(get_repository)):
    return (await Service(repo).server_order_create_new(category=user_input.category, service=user_input.services, description=user_input.description))

@router.post("/order/{order_id}/assinged", response_model=TableOrders)
async def assinged(order_id: int, data: AssingMaster, repo: Repository = Depends(get_repository)):
    return (await Service(repo).server_order_master_assinged(orderID=order_id, masterID=data.masterID))

@router.post("/order/{order_id}/in_progress", response_model=TableOrders)
async def in_progress(order_id: int,repo: Repository = Depends(get_repository)):
    return (await Service(repo).server_order_in_progress(orderID=order_id))

@router.post("/order/{order_id}/completed", response_model=TableOrders)
async def completed(order_id: int, repo: Repository = Depends(get_repository)):
    return (await Service(repo).server_order_complet(orderID=order_id))

@router.post("/order/{order_id}/cancel")
async def cancel(order_id: int, repo: Repository = Depends(get_repository)):
    return (await Service(repo).server_cancel_order(orderID=order_id))

@router.post("/order/{order_id}/delete")
async def delete_order(order_id: int, repo: Repository = Depends(get_repository)):
    return (await Service(repo).server_delete_order(orderID=order_id))

@router.post("/add_master")
async def add_master_in_db(name: str, status = StatusMasterCheck.FREE, repo: Repository = Depends(get_repository)) -> int|None:
    try: return (await Service(repo).server_add_master_in_db(name=name, status=status))
    except (NoResultFound, MultipleResultsFound) as e: raise HTTPException(status_code=404, detail=f"{e}")

@router.post("/add_master_skill", response_model=TableMasterSkills)
async def add_master_skills(master_id: int, skill_id: int, repo: Repository = Depends(get_repository)):
    try: return (await Service(repo).server_add_master_skills(master_id = master_id, skill_id = skill_id))
    except ValueError as e: raise HTTPException(status_code=409, detail=f"{e}")

@router.post("/insert_skill")
async def insert_skill(category: str, service: str, repo: Repository = Depends(get_repository)) -> int:
    try: return (await Service(repo).server_insert_skill(category=category, service=service))
    except ValueError as e: raise HTTPException(status_code=409, detail=f"{e}")

@router.get("/order/{order_id}", response_model=TableOrders)
async def order(order_id: int, repo: Repository = Depends(get_repository)):
    try: return (await Service(repo).server_specific_order(orderID=order_id))
    except ValueError as e: raise HTTPException(status_code=404, detail=f"Данные ошибки: {e}")
    
@router.get("/table_skill_master")
async def all_table_skills_master(repo: Repository = Depends(get_repository)):
    try: return (await Service(repo).server_all_table())
    except ValueError as e: raise HTTPException(status_code=404, detail=f"{e}") 

@router.get("/orders", response_model=list[TableOrders])
async def orders_list(repo: Repository = Depends(get_repository)):
    try: return (await Service(repo).server_all_orders())
    except ValueError as e: raise HTTPException(status_code=404, detail=f"{e}")

@router.get("/master_list")
async def display(repo: Repository = Depends(get_repository)):
    try: return (await Service(repo).server_display_master_skills())
    except ValueError as e:  raise HTTPException(status_code=404, detail=f"{e}")
    
@router.get("/search_master")
async def search_master(category: str, services: str, repo: Repository = Depends(get_repository)):
    try: return (await Service(repo).server_search_master(category=category, service=services))
    except ValueError as e:  raise HTTPException(status_code=404, detail=f"{e}")

@router.get("/service")
async def service(repo: Repository = Depends(get_repository)):
    try: return (await Service(repo).server_services())
    except ValueError as e:  raise HTTPException(status_code=404, detail=f"{e}")


