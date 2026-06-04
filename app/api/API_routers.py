from fastapi import APIRouter, Depends
from database.service import server_order_create_new, server_display_master_skills, server_specific_order, server_all_orders, server_order_master_assinged, server_order_in_progress, server_order_complet, server_search_master, server_services, server_cancel_order, server_delete_order, server_add_master_in_db, server_master_info, server_add_master_skills, server_all_table, server_insert_skill
from app.api.pydantic_ import UserInput, AssingMaster
from SQLAlchemy_work_db.enusm import StatusMasterCheck
from SQLAlchemy_work_db.engine_and_models  import get_db
from sqlalchemy.orm import Session


router = APIRouter(prefix="/user", tags=["User"])


@router.post("/order/new")
def new_order(user_input: UserInput, db: Session = Depends(get_db)):
    return server_order_create_new(category=user_input.category, service=user_input.services, description=user_input.description, db = db)

@router.post("/order/{id_order}/assinged")
def assinged(id_order, data: AssingMaster, db: Session = Depends(get_db)):
    return server_order_master_assinged(orderID=id_order, masterID=data.masterID, db = db)

@router.post("/order/{id_order}/in_progress")
def in_progress(id_order, db: Session = Depends(get_db)):
    return server_order_in_progress(orderID=id_order, db = db)

@router.post("/order/{id_order}/completed")
def completed(id_order, db: Session = Depends(get_db)):
    return server_order_complet(orderID=id_order, db = db)

@router.post("/order/{id_order}/cancel")
def cancel(id_order, db: Session = Depends(get_db)):
    return server_cancel_order(id_order, db = db)

@router.post("/order/{id_order}/delete")
def delete_order(id_order, db: Session = Depends(get_db)):
    return server_delete_order(id_order, db = db)

@router.post("/add_master")
def add_master_in_db(name: str, status = StatusMasterCheck.FREE, db: Session = Depends(get_db)):
    return server_add_master_in_db(name=name, status=status, db = db)

@router.post("/add_master_skill")
def add_master_skills(master_id, skill_id, db: Session = Depends(get_db)):
    return server_add_master_skills(master_id = master_id, skill_id = skill_id, db = db)

@router.post("/insert_skill")
def insert_skill(category: str, service: str, db: Session = Depends(get_db)):
    return server_insert_skill(category=category, service=service, db = db)

# @router.get("/master_info/master/{id}")
# def master_info(id, db: Session = Depends(get_db)):
#     return id, db = db

@router.get("/order/{id_order}")
def order(id_order: int, db: Session = Depends(get_db)):
    return server_specific_order(orderID=id_order, db = db)

    
@router.get("/table_skill_master")
def all_table_skills_master(db: Session = Depends(get_db)):
    return server_all_table(db = db)

@router.get("/orders")
def orders_list(db: Session = Depends(get_db)):
    return server_all_orders(db = db)
 
@router.get("/master_list")
def display(db: Session = Depends(get_db)):
    return server_display_master_skills(db = db)
 
@router.get("/search_master")
def search_master(category: str, services: str, db: Session = Depends(get_db)):
    return server_search_master(category=category, service=services, db = db)
 
@router.get("/service")
def service(db: Session = Depends(get_db)):
    return server_services(db = db)


