from database import service
from database.Repository import orders_db
import pytest
# pytest tests/test_API_router.py -v

def test_new_order(monkeypatch, db, client_app):
    monkeypatch.setattr("database.service.connect_db", lambda: db)
    response = client_app.post("/user/order/new", json={
    "category": "Сантехника",
    "services": "Замена труб", 
    "description": "Течёт труба"
})
    
    assert response.status_code == 200
    assert response.json() == "Заказ создан и сохранен в базу данных"

def test_order_list(client_app ,monkeypatch, db):
    monkeypatch.setattr("database.service.connect_db", lambda: db)
    service.server_order_create_new(category="Сантехника", services="Замена труб", description="Течёт труба под раковиной")
    service.server_order_create_new(category="Электрика", services="Замена розетки", description="Искрит розетка на кухне")
    service.server_order_create_new(category="Диагностика", services="Проверка проводки", description="Мигает свет в комнате")
    
    responce = client_app.get("/user/orders")
    assert responce.status_code == 200
    assert len(responce.json()) > 0
    
def test_order(monkeypatch, db, client_app):
    monkeypatch.setattr("database.service.connect_db", lambda: db)
    id_order = orders_db.add_order(connect=db, category="Сантехника", services="Замена труб", description="Течёт труба под раковиной", status="NEW", created_at="123")
    responce = client_app.get(f"/user/orders/{id_order}")

    assert responce.status_code == 200
    assert responce.json()["category"] == "Сантехника"

def test_assinged(monkeypatch, db, master, order_one, client_app):
    monkeypatch.setattr("database.service.connect_db", lambda: db)
    responce = client_app.post(f"/user/order/{order_one}/assinged", json={"masterID": master})
    chek = orders_db.specific_order(connect=db, id_order=order_one)
    
    assert responce.status_code == 200
    assert chek is not None
    assert chek["status"] == "ASSINGED" 

def test_completed(order_in_progress, client_app, db):
    master_id = order_in_progress["id_master"]
    id_order = order_in_progress["order"]
    responce = client_app.post(f"/user/order/{id_order}/completed", json={"masterID": master_id})
    chek = orders_db.specific_order(connect=db, id_order=id_order)
    

    assert responce.status_code == 200
    assert chek is not None
    assert chek["status"] == "COMPLETED" 

def test_cancel(monkeypatch, db, order_one, client_app):
    monkeypatch.setattr("database.service.connect_db", lambda: db)
    responce = client_app.post(f"/user/order/{order_one}/cancel")
    chek = orders_db.specific_order(connect=db, id_order=order_one)
    print(chek)
    assert responce.status_code == 200
    assert chek is not None
    assert chek["status"] == "CANCEL"

@pytest.mark.parametrize('url', ["/user/master_list", "/user/service"])
def test_2_api(url, client_app):
    responce = client_app.get(url)
    assert responce.status_code == 200

