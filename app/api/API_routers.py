from fastapi import APIRouter, HTTPException
from database.service import server_order_create_new, server_display_master_skills, server_specific_order, server_all_orders, server_order_master_assinged, server_order_in_progress, server_order_complet, server_search_master, server_services, server_cancel_order, server_delete_order, server_add_master_in_db, server_master_info, server_add_master_skills, server_all_table, server_insert_skill
from app.api.pydantic_ import UserInput, AssingMaster
from SQLAlchemy_work_db.enusm import StatusMasterCheck, StatusOrders


router = APIRouter(prefix="/user", tags=["User"])


@router.post("/order/new")
def new_order(user_input: UserInput):
    return server_order_create_new(category=user_input.category, service=user_input.services, description=user_input.description)

@router.post("/order/{id_order}/assinged")
def assinged(id_order, data: AssingMaster):
    return server_order_master_assinged(orderID=id_order, masterID=data.masterID)

@router.post("/order/{id_order}/in_progress")
def in_progress(id_order):
    return server_order_in_progress(orderID=id_order)

@router.post("/order/{id_order}/completed")
def completed(id_order, data: AssingMaster):
    return server_order_complet(orderID=id_order,  masterID=data.masterID)

@router.post("/order/{id_order}/cancel")
def cancel(id_order):
    return server_cancel_order(id_order)

@router.post("/order/{id_order}/delete")
def delete_order(id_order):
    return server_delete_order(id_order)

@router.post("/add_master")
def add_master_in_db(name: str, status = StatusMasterCheck.FREE):
    return server_add_master_in_db(name=name, status=status)

@router.post("/add_master_skill")
def add_master_skills(master_id, skill_id):
    return server_add_master_skills(master_id = master_id, skill_id = skill_id)

@router.post("/insert_skill")
def insert_skill(category: str, service: str):
    return server_insert_skill(category=category, service=service)

@router.get("/master_info/master/{id}")
def master_info(id):
    return server_master_info(id)

@router.get("/orders/{id_order}")
def order(id_order: int):
    try:
        return server_specific_order(orderID=id_order)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.get("/table_skill_master")
def all_table_skills_master():
    return server_all_table()

@router.get("/orders")
def orders_list():
    return server_all_orders()
 
@router.get("/master_list")
def display():
    return server_display_master_skills()
 
@router.get("/search_master")
def search_master(category: str, services: str):
    return server_search_master(category=category, service=services)
 
@router.get("/service")
def service():
    return server_services()


