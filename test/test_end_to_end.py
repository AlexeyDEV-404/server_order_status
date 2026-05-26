from SQLAlchemy_work_db import repository
from SQLAlchemy_work_db.enusm import StatusMasterCheck, StatusOrders
from SQLAlchemy_work_db.engine_and_models import MasterList, MasterSkills, Skills, Orders


OrdRep = repository.OrderRepository
MastListRep = repository.MasterListRepository
MastSkillsRep = repository.MasterSkillsRepository
SkillsRepo = repository.SkillsRepository

def test_lifecycle_order(db, add_master, insert_work):
    """  
    Создать мастера.
    Создать навык.
    Назначить навык мастеру.
    Создать заказ.
    Найти мастера по навыку.
    Назначить мастера.
    Выполнить заказ.
    Проверить статусы.
    """
    with db as conn:
        MastSkillsRep(conn).add_master_skills(master_id=add_master, skill_id=insert_work)
        order = OrdRep(conn).add_order(category="Сантехника", service = "Ремонт трубы", description="Какое-то описание")
        search0 = OrdRep(conn).specific_order(order).status
        if search0 != StatusOrders.NEW:
            raise Exception("Ошибка в поле status заказа.")
        search_by_skil = MastSkillsRep(conn).search_master(category="Сантехника", service = "Ремонт трубы")
        OrdRep(conn).update_master_order(master_id=search_by_skil[0].id, order_id=order)
        ord2 = OrdRep(conn).assinged_order(order)
        search1 = OrdRep(conn).specific_order(ord2).status
        if search1 != StatusOrders.ASSINGED:
            raise Exception("Ошибка при обновлении статуса заказа с NEW на ASSINGED")
        ord3 = OrdRep(conn).in_progress_orders(order)
        search2 = OrdRep(conn).specific_order(ord3).status
        if search2 != StatusOrders.IN_PROGRESS:
            raise Exception("Ошибка при обновлении статуса заказа с ASSINGED на на IN_PROGRESS")
        ord4 = OrdRep(conn).complete_order(order)
        search3 = OrdRep(conn).specific_order(ord4).status
        if search3 != StatusOrders.COMPLETED:
            raise Exception("Ошибка при обновлении статуса заказа с IN_PROGRESS в COMPLETED")
        conn.commit()

    assert search0 == StatusOrders.NEW
    assert search1 == StatusOrders.ASSINGED
    assert search2 == StatusOrders.IN_PROGRESS
    assert search3 == StatusOrders.COMPLETED



