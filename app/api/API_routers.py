from fastapi import APIRouter, HTTPException
from database.service import server_order_create_new, server_display_master_skills, service_specific_order, server_all_orders, server_order_master_assinged, server_order_in_progress, server_order_complet
from app.api.pydantic_ import UserInput, AssingMaster

router = APIRouter(prefix="/user", tags=["User"])

@router.get("/master")
def master_category():
    return server_display_master_skills()

@router.post("/order/new")
def new_order(user_input: UserInput):
    return server_order_create_new(category=user_input.category, services=user_input.services, description=user_input.description)

@router.post("/order/{id_order}/assinged")
def assinged(id_order, master: AssingMaster):
    return server_order_master_assinged(id_order=id_order, masterID=master.masterID)

@router.post("/order/{id_order}/in_progress")
def in_progress(id_order):
    return server_order_in_progress(id_order=id_order)

@router.post("/order/{id_order}/completed")
def completed(id_order):
    return server_order_complet(id_order=id_order,  masterID=AssingMaster.masterID)

@router.get("/orders/{id_order}")
def order(id_order: int):
    try:
        return service_specific_order(id_order=id_order)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.get("/orders")
def orders_list():
    return server_all_orders()
