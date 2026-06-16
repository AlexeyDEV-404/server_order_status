# pytest -s test\test_sqlalchemy.py -v
# pytest test\test_sqlalchemy.py::test_MastSkillsRep_master_skills -v -s

from SQLAlchemy_work_db import repository
from SQLAlchemy_work_db.enusm import StatusMasterCheck, StatusOrders
from SQLAlchemy_work_db.engine_and_models import MasterList, MasterSkills, Skills, Orders


OrdRep = repository.OrderRepository
MastListRep = repository.MasterListRepository
MastSkillsRep = repository.MasterSkillsRepository
SkillsRepo = repository.SkillsRepository



# _____________MasterListRepository__________start

async def test_MastListRep_add(add_master):
    assert type(add_master) == int
    assert add_master > 0

async def test_MastListRep_what_is_the_status(test_db, add_master):
    result = await MastListRep(test_db).what_is_the_status(add_master)
    assert result in StatusMasterCheck

async def test_MastListRep_master_info(test_db, add_master):
    result = await MastListRep(test_db).master_info(add_master)

    assert result is not None
    assert isinstance(result[0], MasterList)

async def test_MastListRep_update_free_status_master(test_db, add_master):
    await MastListRep(test_db).update_busy_status_master(add_master)
    result = await MastListRep(test_db).update_free_status_master(add_master)
    assert result == StatusMasterCheck.FREE

async def test_MastListRep_update_busy_status_master(test_db, add_master):
    result = await MastListRep(test_db).update_busy_status_master(add_master)
    assert result == StatusMasterCheck.BUSY

# _____________MasterListRepository__________end
# ==============================================================
# _____________SkillsRepo__________start

async def test_SkillsRepo_insert_works(test_db, insert_works):
    """ Тестируем работу insert_works (вставка скилов в таблицу)."""
    result = await SkillsRepo(test_db).insert_skill(category="Сантехника", service = "Ремонт трубы")
    assert result == None or result > 0

async def test_SkillsRepo_select_works(test_db, insert_works):
    """ Загружаем данные о навыках через фикстуру и тестируем метод."""
    result = await SkillsRepo(test_db).select_works()
    assert len(result) > 0
    assert result[0][0] == 'Бытовая техника'

    
# _____________SkillsRepo__________end
# ==============================================================
# _____________MastSkillsRep__________start

async def test_MastSkillsRep_add_master_skills(test_db, insert_works, add_master):
    x = 1
    result = await MastSkillsRep(test_db).add_master_skills(master_id=add_master, skill_id=x)

    assert result.skill_id > 0
    assert result.master_id > 0
    
async def test_MastSkillsRep_all_table(test_db, insert_works, add_master):
    await SkillsRepo(test_db).insert_skill(category="Сантехника", service = "Ремонт трубы")
    test_db.commit()
    add = await MastSkillsRep(test_db).add_master_skills(master_id=add_master, skill_id=1)
    result = await MastSkillsRep(test_db).all_table()

    print(result)
    print(type(result))
    print(type(result[0]))
    print(result[0].master_id)

    assert result[0].master_id > 0


async def test_MastSkillsRep_master_skills(test_db, add_master): 
    await SkillsRepo(test_db).insert_skill(category="Сантехника", service = "Ремонт трубы")
    await MastSkillsRep(test_db).add_master_skills(master_id=add_master, skill_id=1)
    result = await MastSkillsRep(test_db).master_skills(add_master)

    assert result[0][0].master_id > 0


async def test_MastSkillsRep_search_master(test_db, add_master):
    skil = await SkillsRepo(test_db).insert_skill(category="Сантехника", service = "Ремонт трубы")
    await MastSkillsRep(test_db).add_master_skills(master_id=add_master, skill_id=skil)
    result = await MastSkillsRep(test_db).search_master(category="Сантехника", service = "Ремонт трубы")
    
    assert type(result[0].id) == int
    assert result[0].name == 'Андрей' 

async def test_MastSkillsRep_informarion_about_craftsmen(test_db, add_master_skills, insert_work):
    result = await MastSkillsRep(test_db).informarion_about_craftsmen()
    
    print(result[0])

    assert result[0].name == "Андрей"
    assert result[0].category == "Сантехника"
    assert result[0].service == "Ремонт трубы"
    assert result[0].status == "FREE"

# _____________MastSkillsRep__________end
# ==============================================================
# _____________OrdRep__________start

async def test_OrdRep_add_order(test_db, order_one):
    
    assert isinstance(order_one, int)
    assert order_one > 0

async def test_OrdRep_all_orders(test_db, orders_many):
    result = await OrdRep(test_db).all_orders()
    print(result[0].category, result[0].master)

    assert result[0].category == "Сантехника"
    assert result[1].category == "Электрика"



async def test_OrdRep_specific_order(test_db, order_one):
    result = await OrdRep(test_db).specific_order(order_one)
    assert isinstance(result.id, int)
    assert result.id > 0
    assert result.description == "Протечка"

async def test_OrdRep_master_chek_order_count(test_db, order_one, add_master):
    result = await OrdRep(test_db).master_chek_order_count(add_master)
    assert result in [0, 1]

async def test_OrdRep_update_master_order(test_db, order_one, add_master):
    result = await OrdRep(test_db).update_master_order(order_id=order_one, master_id=add_master)
    assert result is not None
    assert result > 0

async def test_OrdRep_delete_order(test_db, order_one):
    result = await OrdRep(test_db).delete_order(order_one)
    assert result is not None
    assert result > 0

async def test_OrdRep_assinged_order(test_db, order_one):
    result = await OrdRep(test_db).assinged_order(order_one)
    assert result.status == StatusOrders.ASSINGED 

async def test_OrdRep_in_progress_orders(test_db, order_one):
    await OrdRep(test_db).assinged_order(order_one)
    result = await OrdRep(test_db).in_progress_orders(order_one)
    test_db.commit()
    assert result.status == StatusOrders.IN_PROGRESS 

async def test_OrdRep_complete_order(test_db, order_one):
    await OrdRep(test_db).assinged_order(order_one)
    await OrdRep(test_db).in_progress_orders(order_one)
    result = await OrdRep(test_db).complete_order(order_one)
    test_db.commit()
    assert result.id > 0
    assert result.status == StatusOrders.COMPLETED 

async def test_OrdRep_cancel_order(test_db, order_one):
    result = await OrdRep(test_db).cancel_order(order_one)
    assert result == StatusOrders.CANCEL

# _____________OrdRep__________end
