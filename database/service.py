from database.doman_rules import rowcount_examinator, chek_fetchone_master_order_count, chek_fetchone_master_order_free
from SQLAlchemy_work_db import repository, engine_and_models
from SQLAlchemy_work_db.enusm import StatusOrders

SESSION = engine_and_models.SESSION

OrdRep = repository.OrderRepository
MastListRep = repository.MasterListRepository
MastSkillsRep = repository.MasterSkillsRepository
SkillsRepo = repository.SkillsRepository

DATA_BASE = "database/DATABASE.db"

def connect_db(): return SESSION

def server_order_create_new(category: str, service: str,  description: str):
    with connect_db() as connect:
        add = OrdRep(connect).add_order(category=category, service=service, description=description, status=StatusOrders.NEW)
        rowcount_examinator(rowcount=add)
        connect.commit()
    return f"Заказ создан и сохранен в базу данных. ID заказа {add}"

def server_order_master_assinged(masterID: int, orderID: int):  
    with connect_db() as connect:
        check_orders_per_craftsman = OrdRep(connect).master_chek_order_count(master_id=masterID) 
        chek_fetchone_master_order_count(check_orders_per_craftsman)
        check_status_per_craftsman = MastListRep(connect).what_is_the_status(id=masterID)
        chek_fetchone_master_order_free(check_status_per_craftsman)
        result = OrdRep(connect).assinged_order(order_id=orderID)
        OrdRep(connect).update_master_order(master_id=masterID, order_id=orderID)
        update_status_in_db = MastListRep(connect).update_busy_status_master(id=masterID)
        rowcount_examinator(update_status_in_db)
    return result

def server_order_in_progress(orderID): # Заказ в процессе выполнения
    with connect_db() as connect:
        OrdRep(connect).in_progress_orders(order_id=orderID)
        # in_progress_orders(connect=connect, id_order=id_order)


def server_order_complet(masterID: int, orderID: int): # Перевести заказ в статус "выполнен" (complet)
    with connect_db() as connect:
        order = OrdRep(connect).complete_order(order_id=orderID)
        rowcount_examinator(order)
        master = MastListRep(connect).update_free_status_master(id=masterID)
        rowcount_examinator(master)

def server_display_master_skills(): # Какими навыками работ обладает мастер
    with connect_db() as connect:
        result = MastSkillsRep(connect).informarion_about_craftsmen()
    return result

def server_specific_order(orderID: int): # Найти указанный заказ № id_order
    with connect_db() as connect:
        result = OrdRep(connect).specific_order(order_id = orderID)
    return result

def server_all_orders(): 
    with connect_db() as connect:
        result = OrdRep(connect).all_orders()
    return result

def server_search_master(category, service): 
    with connect_db() as connect:
        result = MastSkillsRep(connect).search_master(category=category, service=service)
    return result

def server_services(): #Список выполняемых работ
    with connect_db() as connect:
        result = SkillsRepo(connect).select_works()
    return result

def server_cancel(orderID): # Отмена заказа
    with connect_db() as connect:
        result = OrdRep(connect).cancel_order(order_id=orderID)
    return result
