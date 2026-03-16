# ТЕСТИРОВАНИЕ ФАЙЛА database/order_db.py
# pytest tests/test_service.py -v
from database import service
from database.Repository import master_skills_db, skills_db, master_list_db, orders_db
from datetime import datetime
import pytest, sqlite3



def test_server_order_create_new(monkeypatch, db):
    monkeypatch.setattr("database.service.connect_db", lambda: db)
    result = service.server_order_create_new(category="Сантехника", services="замена труб", description="Протечка")
    assert result == "Заказ создан и сохранен в базу данных"

def test_server_all_orders(monkeypatch,  db):
    monkeypatch.setattr("database.service.connect_db", lambda: db)
    service.server_order_create_new(category="Сантехника", services="Замена труб", description="Течёт труба под раковиной")
    service.server_order_create_new(category="Электрика", services="Замена розетки", description="Искрит розетка на кухне")
    service.server_order_create_new(category="Диагностика", services="Проверка проводки", description="Мигает свет в комнате")
    result = service.server_all_orders()
    assert result is not None

def test_server_specific_order(monkeypatch,  db):
    monkeypatch.setattr("database.service.connect_db", lambda: db)
    id = orders_db.add_order(connect=db, category="Сантехника", services="Замена труб", 
                   description="Течёт труба", status="NEW", 
                   created_at=str(datetime.now()), master=None)
    result = service.server_specific_order(id_order = id)
    assert result is not None
    assert len(result) > 0

def test_server_search_master(monkeypatch, db):
    monkeypatch.setattr("database.service.connect_db", lambda: db)
    add_skill = skills_db.insept_works(category="Сантехника", service="Замена труб", connect=db)
    master_id = master_list_db.add_master(connect=db, name="Иванов") # исправлено, теперь возвращает lastrowid
    master_skills_db.insert_master_skill(skill_id=add_skill, master_id=master_id, connect=db)
    result = service.server_search_master(category="Сантехника", service="Замена труб")
    assert any(master[1] == "Иванов" for master in result)

def test_order_master_assinged(db, order_one, add_master_and_order_assinged):
    result = orders_db.specific_order(connect=db, id_order=order_one)
    assert result is not None
    assert result["status"] == "ASSINGED"

def test_server_order_in_progress(db, order_in_progress):
    order_one = order_in_progress["order"]
    result = orders_db.specific_order(connect=db, id_order=order_one)
    assert result is not None
    assert result["status"] == 'IN_PROGRESS'

def test_complete_order(db, add_master_and_order_assinged, order_in_progress):
    id_master = add_master_and_order_assinged["id_master"]
    order = order_in_progress["order"]
    service.server_order_complet(id_order=order, masterID=id_master)
    result = orders_db.specific_order(connect=db, id_order=order)
    assert result is not None
    assert result["status"] == 'COMPLETED'

def test_server_display_master_skills(monkeypatch, master, db, order_in_progress):
    monkeypatch.setattr("database.service.connect_db", lambda: db)
    db.row_factory = sqlite3.Row
    skill = skills_db.insept_works(connect=db, category="Сантехника", service="Замена труб")
    master_skills_db.insert_master_skill(connect=db, master_id=master, skill_id=skill)
    rows = service.server_display_master_skills()
    result = [dict(row) for row in rows]
    
    for res in result:
        assert res["name"] == "Андрей"
        assert res["status"] == "FREE"
        assert res["category"] == "Сантехника"


def test_server_service(monkeypatch, db):
    monkeypatch.setattr("database.service.connect_db", lambda: db)
    db.row_factory = sqlite3.Row
    skills_db.insept_works(connect=db, category="Сантехника", service="Замена труб")
    skills_db.insept_works(connect=db, category="Сантехника", service="Установка труб")
    data = service.server_services()

    result = [dict(dat) for dat in data]
    assert result[0]["category"] == "Сантехника" 

def test_cancel_order(monkeypatch, db, order_one):
    monkeypatch.setattr("database.service.connect_db", lambda: db)
    service.server_cancel(id_order=order_one)
    result = service.server_specific_order(id_order=order_one)
    assert result is not None
    assert result["status"] == "CANCEL"

