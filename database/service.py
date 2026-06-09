from database.doman_rules import rowcount_examinator, chek_fetchone_master_order_count, chek_fetchone_master_order_free
from SQLAlchemy_work_db import repository
from SQLAlchemy_work_db.enusm import StatusMasterCheck, StatusOrders
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, NoResultFound, MultipleResultsFound
from app.api.pydantic_ import TableOrders

OrdRep = repository.OrderRepository
MastListRep = repository.MasterListRepository
MastSkillsRep = repository.MasterSkillsRepository
SkillsRepo = repository.SkillsRepository


def server_order_create_new(category: str, service: str,  description: str, db: Session):
    """ Создаем новый заказ."""
    add = OrdRep(db).add_order(category=category, service=service, description=description, status=StatusOrders.NEW)
    rowcount_examinator(rowcount=add)
    db.commit()
    return add

def server_order_master_assinged(masterID: int, orderID: int, db: Session):
    """ Проверяем мастера, закреплен он за выполнением заказа. Проверяем, если статус у мастера BUSY, падаем с ошибкой. Если прошли проверки, меняем статус у заказа на 'ASSINGED'. Закрепляем мастера, за заказом. Меняем статус у мастера на 'BUSY'. Проверяем что изменение внесены, rowcount > 1, если нет, падаем с ошибкой."""
    check_orders_per_craftsman = OrdRep(db).master_chek_order_count(master_id=masterID) 
    chek_fetchone_master_order_count(check_orders_per_craftsman)
    check_status_per_craftsman = MastListRep(db).what_is_the_status(id=masterID)
    chek_fetchone_master_order_free(check_status_per_craftsman)
    result = OrdRep(db).assinged_order(order_id=orderID) # Меняем статус заказа 'NEW' -> 'ASSINGED'
    if result.status != StatusOrders.ASSINGED:
        db.rollback()
        raise ValueError((f"Ошибка: полученное значение {result.status} не соответствует ожидаемому {StatusOrders.ASSINGED}."))
    mast_ord = OrdRep(db).update_master_order(master_id=masterID, order_id=orderID)
    if mast_ord is None:
        db.rollback()
        raise ValueError("Ошибка: мастер не назначен за заказ.")
    update_status_in_db = MastListRep(db).update_busy_status_master(id=masterID)
    if update_status_in_db != StatusMasterCheck.BUSY:
        db.rollback()
        raise ValueError(f"Ошибка: полученное значение {update_status_in_db} не соответствует ожидаемому {StatusMasterCheck.BUSY}.")
    db.commit()
    return result

def server_order_in_progress(orderID, db: Session) -> str: # Заказ в процессе выполнения
    """ Переводчи статус заказа с ASSINGED в IN_PROGRESS. """
    result = OrdRep(db).in_progress_orders(order_id=orderID)
    db.commit()
    return result.status

def server_order_complet(orderID: int, db: Session):
    """ Переводим заказ в статус "Выполнено" и освобождаем мастера, переводим его статус с "BUSY" на "FREE"  """
    order = OrdRep(db).complete_order(order_id=orderID)
    if order.status != StatusOrders.COMPLETED:
        raise ValueError("Ошибка: поле status не обновлено.")
    ord = OrdRep(db).specific_order(orderID)
    if ord.master is None:
        raise HTTPException(status_code=404, detail="Ошибка: недопустимое значение None для поля master в заказе")
    master = MastListRep(db).update_free_status_master(id=ord.master)
    if master != StatusMasterCheck.FREE:
        raise ValueError(f"Ошибка: поченное значение {master} не соответствует ожидаемому {StatusMasterCheck.FREE}.")
    db.commit()
    return order

def server_display_master_skills(db: Session):
    """ Какими навыками работ обладает мастер. """
    result = MastSkillsRep(db).informarion_about_craftsmen()    
    if result == []:
        raise ValueError("Error: response cannot be empty")
    return result

def server_specific_order(orderID: int, db: Session) -> TableOrders: # Найти указанный заказ № id_order
    """ Поиск заказа по ID. """
    result = OrdRep(db).specific_order(order_id = orderID)
    if result is None:
        raise ValueError(f"Заказ с ID {orderID} не найден")
    return TableOrders.model_validate(result)

def server_all_orders(db: Session):
    """ Показать всю таблицу с заказами. """     
    orders = OrdRep(db).all_orders()
    if orders == []:
        raise ValueError("Error: response cannot be empty")
    x = [TableOrders.model_validate(order) for order in orders]
    return x

def server_search_master(category, service, db: Session):    
    """ Ищем всех мастеров, которую предостовляют услугу. """ 
    result = MastSkillsRep(db).search_master(category=category, service=service)
    if result == []:
        raise ValueError("Данные отсутствуют")        
    return [{"id": r.id, "name": r.name} for r in result]

def server_services(db: Session):
    """ Список выполняемых работ."""    
    results = SkillsRepo(db).select_works()
    if results == []:
        raise ValueError("Данные отсутствуют")    
    return [{"category": r[0], "service": r[1].split(", ")} for r in results]

def server_cancel_order(orderID, db: Session): # Отмена заказа
    """ Отмена заказа с статусом "NEW". """

    order = OrdRep(db).specific_order(orderID)
    if order.status != StatusOrders.NEW:
        raise ValueError("Ошибка: отменить можно только заказ с статусом 'NEW'")
    result = OrdRep(db).cancel_order(order_id=orderID)
    db.commit()
    return result

def server_delete_order(orderID, db: Session):
    """ Удаляем заказ по id и взвращаем str-уведомление про успешное удаление этого заказа."""
    order = OrdRep(db).specific_order(orderID)
    if order:
        result = OrdRep(db).delete_order(orderID)
        db.commit()
        return result
    else:
        raise ValueError("Заказа не существует.")
    

def server_add_master_in_db(name, status: StatusMasterCheck, db: Session):
    """ Добавляет в таблицу нового мастера. """
    
    try:
        result = MastListRep(db).add(name = name, status = status)
        db.commit()
        return result
    except NoResultFound:
        raise NoResultFound("Ошика: отсутствует результат запроса. Адрес ошибки: server.py::server_add_master_in_db") 
    except MultipleResultsFound:
        raise MultipleResultsFound("Ошика: недопустимый результат, метод вернул больше одного значения. Адрес ошибки: server.py::server_add_master_in_db")

def server_master_info(id, db: Session):
    """ Возвращает строку про мастера. id должен соответствовать текущему мастеру, который есть в БД."""
    result = MastListRep(db).master_info(id)
    if result is not None:
        return result[0]
        
def server_add_master_skills(master_id: int, skill_id: int, db: Session):
    """ Серверный слой: Вставляем новый навык мастеру в таблицу MasterSkills """
    db.commit()
    try:
        return MastSkillsRep(db).add_master_skills(master_id=master_id, skill_id=skill_id)         
    except IntegrityError:
        db.rollback()
        raise ValueError("Навык уже существует")
    

def server_all_table(db: Session):
    """ Возвращает всю таблицу навыков мастеров."""
    results = MastSkillsRep(db).all_table()
    if results == []:
        raise ValueError("Error: response cannot be empty")
    else:
        return results
        
def server_insert_skill(category, service, db: Session):
    """ Добавляем строку в таблицу со всеми навыками """
    try:
        result = SkillsRepo(db).insert_skill(category = category, service = service)
        db.commit()
        return result
    except IntegrityError as e:
        db.rollback()
        f"Ошибка - {e}"
        raise ValueError("Error: duplicate data")
    