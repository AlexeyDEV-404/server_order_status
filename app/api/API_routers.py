from fastapi import APIRouter, HTTPException
from database.service import server_order_create_new, server_display_master_skills, server_specific_order, server_all_orders, server_order_master_assinged, server_order_in_progress, server_order_complet, server_search_master, server_services, server_cancel
from app.api.pydantic_ import UserInput, AssingMaster

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
    return server_cancel(id_order)

@router.get("/orders/{id_order}")
def order(id_order: int):
    try:
        return server_specific_order(orderID=id_order)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

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
