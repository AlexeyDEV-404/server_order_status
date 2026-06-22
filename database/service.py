from database.doman_rules import  chek_value_master_order_free
from SQLAlchemy_work_db import repository
from SQLAlchemy_work_db.enusm import StatusMasterCheck, StatusOrders
from app.api.pydantic_ import TableMasterSkills
from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound, MultipleResultsFound

from app.api.pydantic_ import TableOrders

OrdRep = repository.OrderRepository
MastListRep = repository.MasterListRepository
MastSkillsRep = repository.MasterSkillsRepository
SkillsRepo = repository.SkillsRepository


async def server_order_create_new(category: str, service: str,  description: str, db: AsyncSession):
    """ Создаем новый заказ."""
    add = await OrdRep(db).add_order(category=category, service=service, description=description, status=StatusOrders.NEW)
    await db.commit()
    return add

async def server_order_master_assinged(masterID: int, orderID: int, db: AsyncSession):
    """ Проверяем мастера, закреплен он за выполнением заказа. Проверяем, если статус у мастера BUSY, падаем с ошибкой. Если прошли проверки, меняем статус у заказа на 'ASSINGED'. Закрепляем мастера, за заказом. Меняем статус у мастера на 'BUSY'. Проверяем что изменение внесены, rowcount > 1, если нет, падаем с ошибкой."""
    await OrdRep(db).master_chek_order_count(master_id=masterID)
    check_status_per_craftsman = await MastListRep(db).what_is_the_status(id=masterID)
    chek_value_master_order_free(check_status_per_craftsman)
    # result = await OrdRep(db).assinged_order(order_id=orderID) # Меняем статус заказа 'NEW' -> 'ASSINGED'
    await OrdRep(db).assinged_order(order_id=orderID) # Меняем статус заказа 'NEW' -> 'ASSINGED'
    try:
        result = await OrdRep(db).specific_order(order_id=orderID)
    except Exception as e:
        raise Exception(f'Ошибка запроса произошла в server_order_master_assinged. Текст ошибка - {e}')

    if result.status != "ASSINGED":
        await db.rollback()
        raise ValueError((f"Ошибка: полученное значение {result.status} не соответствует ожидаемому {StatusOrders.ASSINGED}."))
    mast_ord = await OrdRep(db).update_master_order(master_id=masterID, order_id=orderID)
    if mast_ord is None:
        await db.rollback()
        raise ValueError("Ошибка: мастер не назначен за заказ.")
    update_status_in_db = await MastListRep(db).update_busy_status_master(id=masterID)
    if update_status_in_db != StatusMasterCheck.BUSY:
        await db.rollback()
        raise ValueError(f"Ошибка: полученное значение {update_status_in_db} не соответствует ожидаемому {StatusMasterCheck.BUSY}.")
    await db.commit()
    return TableOrders.model_validate(result)

async def server_order_in_progress(orderID, db: AsyncSession): # Заказ в процессе выполнения
    """ Переводчи статус заказа с ASSINGED в IN_PROGRESS. """
    result = await OrdRep(db).in_progress_orders(order_id=orderID)
    if result is None:
        raise ValueError("Ошибка, рельзутат None или неверный статус заказа.")
    await db.commit()
    return result

async def server_order_complet(orderID: int, db: AsyncSession):
    """ Переводим заказ в статус "Выполнено" и освобождаем мастера, переводим его статус с "BUSY" на "FREE"  """
    order = await OrdRep(db).complete_order(order_id=orderID)
    if order is None:
        raise ValueError("Ошибка запоса: не удалось перевести значение в статус COMPLETED. БД вернула None.")
    if order.master is None:
        raise HTTPException(status_code=404, detail="Ошибка: недопустимое значение None для поля master в заказе")
    master = await MastListRep(db).update_free_status_master(id=order.master)
    if master != StatusMasterCheck.FREE:
        raise ValueError(f"Ошибка: поченное значение {master} не соответствует ожидаемому {StatusMasterCheck.FREE}.")
    await db.commit()
    return order

async def server_display_master_skills(db: AsyncSession):
    """ Какими навыками работ обладает мастер. """
    result = await MastSkillsRep(db).informarion_about_craftsmen()    
    if result == []:
        raise ValueError("Error: response cannot be empty")
    return result

async def server_specific_order(orderID: int, db: AsyncSession): # Найти указанный заказ № id_order
    """ Поиск заказа по ID. """
    result = await OrdRep(db).specific_order(order_id = orderID)
    if result is None:
        raise ValueError(f"Заказ с ID {orderID} не найден")
    return TableOrders.model_validate(result)


async def server_all_orders(db: AsyncSession):
    """ Показать всю таблицу с заказами. """     
    orders = await OrdRep(db).all_orders()
    x = [TableOrders.model_validate(order) for order in orders]
    print(orders, "=================================", type(orders), "and =========", orders[0])
    if orders == []:
        raise ValueError("Error: response cannot be empty")
    
    return x

async def server_search_master(category, service, db: AsyncSession):    
    """ Ищем всех мастеров, которую предостовляют услугу. """ 
    result = await MastSkillsRep(db).search_master(category=category, service=service)
    if result == []:
        raise ValueError("Данные отсутствуют")        
    return [{"id": r.id, "name": r.name} for r in result]

async def server_services(db: AsyncSession):
    """ Список выполняемых работ."""    
    results = await SkillsRepo(db).select_works()
    if results == []:
        raise ValueError("Данные отсутствуют")  
    return [{"category": r[0], "service": r[1].split(", ")} for r in results]

async def server_cancel_order(orderID, db: AsyncSession): # Отмена заказа
    """ Отмена заказа с статусом "NEW". """
    order = await OrdRep(db).specific_order(orderID)
    if order.status != "NEW":
        raise ValueError("Ошибка: отменить можно только заказ с статусом 'NEW'")
    result = await OrdRep(db).cancel_order(order_id=orderID)
    await db.commit()
    return result

async def server_delete_order(orderID, db: AsyncSession):
    """ Удаляем заказ по id и взвращаем str-уведомление про успешное удаление этого заказа."""
    order = await OrdRep(db).specific_order(orderID)
    if order:
        result = await OrdRep(db).delete_order(orderID)
        await db.commit()
        return result
    else:
        raise ValueError("Заказа не существует.")
    

async def server_add_master_in_db(name, status: StatusMasterCheck, db: AsyncSession):
    """ Добавляет в таблицу нового мастера. """
    try:
        result = await MastListRep(db).add(name = name, status = status)
        await db.commit()
        return result
    except NoResultFound:
        raise NoResultFound("Ошика: отсутствует результат запроса. Адрес ошибки: server.py::server_add_master_in_db") 
    except MultipleResultsFound:
        raise MultipleResultsFound("Ошика: недопустимый результат, метод вернул больше одного значения. Адрес ошибки: server.py::server_add_master_in_db")

async def server_master_info(id, db: AsyncSession):
    """ Возвращает строку про мастера. id должен соответствовать текущему мастеру, который есть в БД."""
    result = await MastListRep(db).master_info(id)
    if result is None or result == []:
        raise TypeError("Ошибка: Пустой результат")
    return result
        
async def server_add_master_skills(master_id: int, skill_id: int, db: AsyncSession) -> TableMasterSkills:
    """ Серверный слой: Вставляем новый навык мастеру в таблицу MasterSkills """
    try:
        result = await MastSkillsRep(db).add_master_skills(master_id=master_id, skill_id=skill_id)
        await db.commit()
        return TableMasterSkills.model_validate(result)         
    except IntegrityError as e:
        await db.rollback()
        if "duplicate key" in str(e.orig):
            raise ValueError("Навык уже существует")
        else:
            raise ValueError("Ошибка целостности данных")
    

async def server_all_table(db: AsyncSession):
    """ Возвращает всю таблицу навыков мастеров."""
    results = await MastSkillsRep(db).all_table()
    if not results:
        raise ValueError("Error: response cannot be empty")
    return results
        
async def server_insert_skill(category, service, db: AsyncSession):
    """ Добавляем строку в таблицу со всеми навыками """
    try:
        result = await SkillsRepo(db).insert_skill(category = category, service = service)   
        await db.commit()   
        return result
    except IntegrityError as e:
        await db.rollback()
        f"Ошибка - {e}"
        raise ValueError("Error: duplicate data")
    