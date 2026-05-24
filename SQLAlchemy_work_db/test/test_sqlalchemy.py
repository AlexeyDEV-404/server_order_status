# pytest -s SQLAlchemy_work_db\test\test_sqlalchemy.py -v
# pytest -s SQLAlchemy_work_db\test\test_sqlalchemy.py::test_MastSkillsRep_all_table -v

from SQLAlchemy_work_db import repository
from SQLAlchemy_work_db.enusm import StatusMasterCheck, StatusOrders
from SQLAlchemy_work_db.engine_and_models import MasterList, MasterSkills, Skills, Orders


OrdRep = repository.OrderRepository
MastListRep = repository.MasterListRepository
MastSkillsRep = repository.MasterSkillsRepository
SkillsRepo = repository.SkillsRepository



# _____________MasterListRepository__________start

def test_MastListRep_add(add_master, db):
    assert type(add_master) == int
    assert add_master > 0

def test_MastListRep_what_is_the_status(db, add_master):
    result = MastListRep(db).what_is_the_status(add_master)
    assert result in StatusMasterCheck

def test_MastListRep_master_info(db, add_master):
    result = MastListRep(db).master_info(add_master)

    assert result is not None
    assert isinstance(result[0], MasterList)

def test_MastListRep_update_free_status_master(db, add_master):
    MastListRep(db).update_busy_status_master(add_master)
    result = MastListRep(db).update_free_status_master(add_master)
    assert result > 0

def test_MastListRep_update_busy_status_master(db, add_master):
    result = MastListRep(db).update_busy_status_master(add_master)
    assert result > 0

# _____________MasterListRepository__________end
# ==============================================================
# _____________SkillsRepo__________start

def test_SkillsRepo_insert_works(db, insert_works):
    """ Тестируем работу insert_works (вставка скилов в таблицу)."""
    result = SkillsRepo(db).insert_works(category="Сантехника", service = "Ремонт трубы")
    assert result == None or result > 0

def test_SkillsRepo_select_works(db, insert_works):
    """ Загружаем данные о навыках через фикстуру и тестируем метод."""
    result = SkillsRepo(db).select_works()
    assert len(result) > 0
    assert result[0][0] == 'Бытовая техника'

    
# _____________SkillsRepo__________end
# ==============================================================
# _____________MastSkillsRep__________start

def test_MastSkillsRep_add_master_skills(db, insert_works, add_master):
    skills = [1, 2, 5, 14, 9, 8]
    count = 0
    for x in skills:
        result = MastSkillsRep(db).add_master_skills(master_id=add_master, skill_id=x)
        count += result
    assert count == len(skills)
    
def test_MastSkillsRep_all_table(db, insert_works, add_master):
    SkillsRepo(db).insert_works(category="Сантехника", service = "Ремонт трубы")
    db.commit()
    add = MastSkillsRep(db).add_master_skills(master_id=add_master, skill_id=1)
    result = MastSkillsRep(db).all_table()

    print(result)
    print(type(result))
    print(type(result[0]))
    print(result[0].master_id)
    assert result[0][0].master_id > 0
    # assert isinstance(result[0], MasterSkills)

def test_MastSkillsRep_master_skills(db, add_master): 
    mast = SkillsRepo(db).insert_works(category="Сантехника", service = "Ремонт трубы")
    add = MastSkillsRep(db).add_master_skills(master_id=add_master, skill_id=1)
    result = MastSkillsRep(db).master_skills(add_master)
    db.commit()
    assert result[0][0].master_id > 0
    # assert isinstance(result[0], MasterSkills)

def test_MastSkillsRep_search_master(db, add_master):
    skil = SkillsRepo(db).insert_works(category="Сантехника", service = "Ремонт трубы")
    MastSkillsRep(db).add_master_skills(master_id=add_master, skill_id=skil)
    result = MastSkillsRep(db).search_master(category="Сантехника", service = "Ремонт трубы")
    
    assert type(result[0].id) == int
    assert result[0].name == 'Андрей' 

def test_MastSkillsRep_informarion_about_craftsmen(db, add_master_skills, insert_work):
    result = MastSkillsRep(db).informarion_about_craftsmen()

    assert result[0].name == "Андрей"
    assert result[0].category == "Сантехника"
    assert result[0].service == "Ремонт трубы"
    assert result[0].status == StatusMasterCheck.FREE

# _____________MastSkillsRep__________end
# ==============================================================
# _____________OrdRep__________start

def test_OrdRep_add_order(db, order_one):
    
    assert isinstance(order_one, int)
    assert order_one > 0

def test_OrdRep_all_orders(db, orders_many):
    result = OrdRep(db).all_orders()
    assert isinstance(result[0][0], Orders)
    assert isinstance(result[-1][0], Orders)


def test_OrdRep_specific_order(db, order_one):
    result = OrdRep(db).specific_order(order_one)
    assert isinstance(result.id, int)
    assert result.id > 0
    assert result.description == "Протечка"

def test_OrdRep_master_chek_order_count(db, order_one, add_master):
    result = OrdRep(db).master_chek_order_count(add_master)
    assert result in [0, 1]

def test_OrdRep_update_master_order(db, order_one, add_master):
    result = OrdRep(db).update_master_order(order_id=order_one, master_id=add_master)
    assert result > 0

def test_OrdRep_delete_order(db, order_one):
    result = OrdRep(db).delete_order(order_one)
    assert result > 0

def test_OrdRep_assinged_order(db, order_one):
    result = OrdRep(db).assinged_order(order_one)

    assert result > 0 

def test_OrdRep_in_progress_orders(db, order_one):
    OrdRep(db).assinged_order(order_one)
    result = OrdRep(db).in_progress_orders(order_one)
    db.commit()
    assert result > 0 

def test_OrdRep_complete_order(db, order_one):
    OrdRep(db).assinged_order(order_one)
    OrdRep(db).in_progress_orders(order_one)
    result = OrdRep(db).complete_order(order_one)
    db.commit()
    assert result > 0 

def test_OrdRep_cancel_order(db, order_one):
    result = OrdRep(db).cancel_order(order_one)
    assert result == StatusOrders.CANCEL

# _____________OrdRep__________end
