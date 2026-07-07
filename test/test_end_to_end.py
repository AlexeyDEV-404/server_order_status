from SQLAlchemy_work_db import repository


OrdRep = repository.OrderRepository
MastListRep = repository.MasterListRepository
MastSkillsRep = repository.MasterSkillsRepository
SkillsRepo = repository.SkillsRepository

async def test_lifecycle_order(test_db, add_master, insert_work):
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
    async with test_db as conn:
        await MastSkillsRep(conn).add_master_skills(master_id=add_master, skill_id=insert_work)
        order = await OrdRep(conn).add_order(category="Сантехника", service = "Ремонт трубы", description="Какое-то описание")
        search0 = (await OrdRep(conn).specific_order(order))
        if search0.status != "NEW":
            raise Exception("Ошибка в поле status заказа.")
        search_by_skil = await MastSkillsRep(conn).search_master(category="Сантехника", service = "Ремонт трубы")
        await OrdRep(conn).update_master_order(master_id=search_by_skil[0].id, order_id=order)
        ord2 = await OrdRep(conn).assinged_order(order)
        search1 = (await OrdRep(conn).specific_order(order))
        if search1.status != "ASSINGED":
            raise Exception("Ошибка при обновлении статуса заказа с NEW на ASSINGED")
        ord3 = await OrdRep(conn).in_progress_orders(order)
        search2 = await OrdRep(conn).specific_order(order)
        if search2.status != "IN_PROGRESS":
            raise Exception("Ошибка при обновлении статуса заказа с ASSINGED на на IN_PROGRESS")
        ord4 = await OrdRep(conn).complete_order(order)
        search3 = await OrdRep(conn).specific_order(order)
        if search3.status != "COMPLETED":
            raise Exception("Ошибка при обновлении статуса заказа с IN_PROGRESS в COMPLETED")
        await conn.commit()

    assert search0.status == "NEW"
    assert search1.status == "ASSINGED"
    assert search2.status == "IN_PROGRESS"
    assert search3.status == "COMPLETED"

