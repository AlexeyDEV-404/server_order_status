from database.doman_rules import rowcount_examinator, chek_fetchone_master_order_count, chek_fetchone_master_order_free
from SQLAlchemy_work_db import repository, engine_and_models
from SQLAlchemy_work_db.engine_and_models import Orders 

from SQLAlchemy_work_db.enusm import StatusMasterCheck, StatusOrders


SESSION = engine_and_models.session

OrdRep = repository.OrderRepository
MastListRep = repository.MasterListRepository
MastSkillsRep = repository.MasterSkillsRepository
SkillsRepo = repository.SkillsRepository


def server_order_create_new(category: str, service: str,  description: str):
    with SESSION() as connect:
        add = OrdRep(connect).add_order(category=category, service=service, description=description, status=StatusOrders.NEW)
        rowcount_examinator(rowcount=add)
        connect.commit()
    return f"Заказ создан и сохранен в базу данных. ID заказа {add}"

def server_order_master_assinged(masterID: int, orderID: int):  
    with SESSION() as connect:
        """ Проверяем мастера, закреплен он за выполнением заказа. Проверяем, если статус у мастера BUSY, падаем с ошибкой. Если прошли проверки, меняем статус у заказа на 'ASSINGED'. Закрепляем мастера, за заказом. Меняем статус у мастера на 'BUSY'. Проверяем что изменение внесены, rowcount > 1, если нет, падаем с ошибкой."""
        check_orders_per_craftsman = OrdRep(connect).master_chek_order_count(master_id=masterID) 
        chek_fetchone_master_order_count(check_orders_per_craftsman)
        check_status_per_craftsman = MastListRep(connect).what_is_the_status(id=masterID)
        chek_fetchone_master_order_free(check_status_per_craftsman)
        result = OrdRep(connect).assinged_order(order_id=orderID)
        OrdRep(connect).update_master_order(master_id=masterID, order_id=orderID)
        update_status_in_db = MastListRep(connect).update_busy_status_master(id=masterID)
        rowcount_examinator(update_status_in_db)
        connect.commit()
    return result

def server_order_in_progress(orderID): # Заказ в процессе выполнения
    """ Переводчи статус заказа с ASSINGED в IN_PROGRESS """
    with SESSION() as connect:
        OrdRep(connect).in_progress_orders(order_id=orderID)
        connect.commit()


def server_order_complet(masterID: int, orderID: int): # Перевести заказ в статус "выполнен" (complet)
    with SESSION() as connect:
        order = OrdRep(connect).complete_order(order_id=orderID)
        rowcount_examinator(order)
        master = MastListRep(connect).update_free_status_master(id=masterID)
        rowcount_examinator(master)
        connect.commit()

def server_display_master_skills(): # Какими навыками работ обладает мастер
    with SESSION() as connect:
        result = MastSkillsRep(connect).informarion_about_craftsmen()
        
    return result

def server_specific_order(orderID: int): # Найти указанный заказ № id_order
    with SESSION() as connect:
        result = OrdRep(connect).specific_order(order_id = orderID)
        if result is None:
            return {"error": f"Заказ с ID {orderID} не найден"}
        x = result.to_dict()    
    return x

def server_all_orders(): 
    with SESSION() as connect:
        orders = OrdRep(connect).all_orders()
        x = [order.to_dict() for order in orders]
    return x

def server_search_master(category, service): 
    with SESSION() as connect:
        result = MastSkillsRep(connect).search_master(category=category, service=service)
        
    return [{"id": r.id, "name": r.name} for r in result]

def server_services(): #Список выполняемых работ
    with SESSION() as connect:
        results = SkillsRepo(connect).select_works()
    return [{"category": r[0], "service": r[1].split(", ")} for r in results]

def server_cancel_order(orderID): # Отмена заказа
    with SESSION() as connect:
        result = OrdRep(connect).cancel_order(order_id=orderID)
        connect.commit()
    return result

def server_delete_order(orderID):
    with SESSION() as connect:
        OrdRep(connect).delete_order(orderID)
        connect.commit()

def server_add_master_in_db(name, status: StatusMasterCheck):
    """ Добавляет в таблицу нового мастера. """
    with SESSION() as connect:
        MastListRep(connect).add(name = name, status = status)
        connect.commit()
    return "Мастер добавлен."

def server_master_info(id):
    """ Возвращает строку про мастера. id должен соответствовать текущему мастеру, который есть в БД."""
    with SESSION() as connect:
        result = MastListRep(connect).master_info(id)
        if result is not None:
            return result[0]


def server_add_master_skills(master_id: int, skill_id: int):
    """ Серверный слой: Вставляем новый навык мастеру в таблицу MasterSkills """
    with SESSION() as connect:
        result = MastSkillsRep(connect).add_master_skills(master_id=master_id, skill_id=skill_id)
        connect.commit()

def server_all_table():
    """ Возвращает всю таблицу навыков мастеров."""
    with SESSION() as connect:
        results = MastSkillsRep(connect).all_table()
        x = [result.to_dict() for result in results]
    return x
    
def server_insert_skill(category, service):
    """ Добавляем строку в таблицу со всеми навыками """
    with SESSION() as connect:
        SkillsRepo(connect).insert_skill(category = category, service = service)
        connect.commit()