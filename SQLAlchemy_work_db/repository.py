from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update, delete, and_, func
from sqlalchemy.dialects.sqlite import insert as insert_dialects
from SQLAlchemy_work_db.engine_and_models import MasterList, MasterSkills, Skills, Orders
from SQLAlchemy_work_db.enusm import StatusMasterCheck, StatusOrders
from sqlalchemy.engine import CursorResult
from typing import cast

class MasterListRepository:
    def __init__(self, session_manag : Session):
        self.session_manag = session_manag
    
    def add(self, name :str, status : StatusMasterCheck | None = None):
        """ Добавляет в таблицу нового мастера."""
        result = self.session_manag.execute(insert(MasterList).values(name=name, status=status).returning(MasterList.id))
        return result.scalar()
    
    def what_is_the_status(self, id: int):
        """ Отвечает на вопрос, какой статус у мастера? Где параметр метода id - существующего мастера."""
        result = self.session_manag.execute(select(MasterList.status).where(MasterList.id == id)).scalar_one()
        return result
    
    def master_info(self, id: int):
        """ Возвращает информацию про конкретного мастера. id - долежн быть целым числом и относится к конкретному мастеру. """
        return self.session_manag.execute(select(MasterList).where(MasterList.id == id)).first()
    
    def update_free_status_master(self, id: int):
        """ Смена статуса мастера с  BUSY на FREE"""
        result = cast(CursorResult, self.session_manag.execute(update(MasterList).where(and_(MasterList.status == "BUSY", MasterList.id == id)).values(status = "FREE")))
        return result.rowcount

    def update_busy_status_master(self, id: int):
        """ Смена статуса мастера с  FREE на BUSY"""
        result = cast(CursorResult, self.session_manag.execute(update(MasterList).where(and_(MasterList.status == "FREE", MasterList.id == id)).values(status = "BUSY")))
        return result.rowcount

class MasterSkillsRepository:
    def __init__(self, session_manag : Session):
        self.session_manag = session_manag

    def add_master_skills(self, master_id, skill_id):
        """ Делает вставку навыка мастера. ID мастера и ID конкретного навыка."""
        return cast(CursorResult, self.session_manag.execute(insert(MasterSkills).values(master_id = master_id, skill_id = skill_id))).rowcount

    def all_table(self):
        """ Возвращает всю таблицу навыков мастеров."""
        return self.session_manag.execute(select(MasterSkills)).all()
    
    def master_skills(self, master_id: int):
        """ Делаем запрос - 'Какими навыками обладает мастер?'"""
        return self.session_manag.execute(select(MasterSkills).where(MasterSkills.master_id == master_id)).all()
    
    def search_master(self, category: str, service: str):
        """ Ищем всех мастеров, которые могут оказать определенную услугу. Возвращает [(id, name)]"""
        return self.session_manag.execute(
            select(MasterList.id, MasterList.name).
            join(MasterSkills).join(Skills).
            where(and_(Skills.category == category, Skills.service == service, MasterList.status == StatusMasterCheck.FREE))).all()

    def informarion_about_craftsmen(self):
        """ Создаем таблицу через join с полями name|category|service|status. Переименованный метод join_display_master_skills"""
        return self.session_manag.execute(
            select(MasterList.name, Skills.category, Skills.service, MasterList.status)
            .select_from(MasterList)
            .join(MasterSkills)
            .join(Skills)
            ).all()

class OrderRepository:
    def __init__(self, session_manag : Session):
        self.session_manag = session_manag

    
    def add_order(self, category: str, service: str, description: str, status = StatusOrders.NEW,  master=None):
        """ Добавить заказ к таблицу. Возвращает .scalar()"""
        return self.session_manag.execute(insert(Orders).values(category=category, service=service, description = description, status = status,  master = master).returning(Orders.id)).scalar_one()
    
    def all_orders(self):
        """ Показать всю таблицу с заказами."""
        return self.session_manag.execute(select(Orders)).all()
    
    def specific_order(self, order_id):
        """ Показать конкретную строку (заказ) из таблицы. Возвращает .scalar_one()"""
        return self.session_manag.execute(select(Orders).where(Orders.id == order_id)).scalar_one()
    
    def master_chek_order_count(self, master_id):
        """ Возвращает скалярное значение int, всех заказов со статусом IN_PROGRESS у мастера. Возвращает .scalar_one()"""
        return self.session_manag.execute(select(func.count(Orders.id)).where(and_(Orders.master == master_id, Orders.status == StatusOrders.IN_PROGRESS))).scalar_one()
    
    def update_master_order(self, master_id: int, order_id: int):
        """ Закрепить за заказом, мастера. Возвращает .rowcount() """
        return cast(CursorResult, self.session_manag.execute(update(Orders).values(master = master_id).where(Orders.id == order_id))).rowcount
    
    def delete_order(self, id):
        """ Удаляем заказ из базы данных. Возвращает .rowcount()"""
        return cast(CursorResult ,self.session_manag.execute((delete(Orders).where(Orders.id == id)))).rowcount
    
    def assinged_order(self, order_id: int):
        """Меняем статус заказа на - 'ASSINGED', у которого статус заказа - 'NEW'. Возвращает .rowcount()"""
        return cast(CursorResult, self.session_manag.execute(update(Orders).values(status = StatusOrders.ASSINGED).where(and_(Orders.status == StatusOrders.NEW, Orders.id == order_id)))).rowcount

    def in_progress_orders(self, order_id: int):
        """ Переводчи статус заказа с ASSINGED на IN_PROGRESS. Возвращает .rowcount()"""
        return cast(CursorResult, self.session_manag.execute(update(Orders).values(status = StatusOrders.IN_PROGRESS).where(and_(Orders.status == StatusOrders.ASSINGED, Orders.id == order_id)))).rowcount

    def complete_order(self, order_id: int):
        """ Переводчи статус заказа с IN_PROGRESS в COMPLETED. Возвращает .rowcount()"""
        return cast(CursorResult, self.session_manag.execute(update(Orders).values(status = StatusOrders.COMPLETED).where(and_(Orders.status == StatusOrders.IN_PROGRESS, Orders.id == order_id)))).rowcount

    def cancel_order(self, order_id: int):
        """ Переводчи статус заказа с NEW в  CANCEL"""
        return cast(CursorResult, self.session_manag.execute(update(Orders).values(status = StatusOrders.CANCEL).where(and_(Orders.status == StatusOrders.NEW, Orders.id == order_id)).returning(Orders.status))).scalar_one()

class SkillsRepository:
    def __init__(self, session_manag : Session):
        self.session_manag = session_manag

    def insert_skill(self, category, service):
        """ Добавляем строку в таблицу со всеми навыками """
        return self.session_manag.execute(insert_dialects(Skills).values(category = category, service = service).on_conflict_do_nothing().returning(Skills.id)).scalar()
    
    def select_works(self):
        """ Делаем запрос к БД и возвращаем список выполняемых работ в виде [("категория", "перечисление, видов, услуг, через, запятую")]. Возвращает .fetchall()"""
        return self.session_manag.execute(select(Skills.category, func.group_concat(Skills.service, ', ')).group_by(Skills.category)).fetchall()

    
    