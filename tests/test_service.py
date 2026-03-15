# ТЕСТИРОВАНИЕ ФАЙЛА database/order_db.py
# pytest tests/test_service.py -v
from database import service
from database.Repository import master_skills_db, skills_db, master_list_db
from database.Repository.orders_db import add_order
from datetime import datetime

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
    id = add_order(connect=db, category="Сантехника", services="Замена труб", 
                   description="Течёт труба", status="NEW", 
                   created_at=str(datetime.now()), master=None)
    result = service.server_specific_order(id_order = id is not None)
    assert result is not None
    assert len(result) > 0

def test_server_search_master(monkeypatch, db):
    monkeypatch.setattr("database.service.connect_db", lambda: db)
    add_skill = skills_db.insept_works(category="Сантехника", service="Замена труб", connect=db)
    master_id = master_list_db.add_master(connect=db, Name="Иванов") # исправлено, теперь возвращает lastrowid
    master_skills_db.insert_master_skill(skill_id=add_skill, master_id=master_id, connect=db)
    result = service.server_search_master(category="Сантехника", service="Замена труб")
    assert any(master[1] == "Иванов" for master in result)


