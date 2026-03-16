from database import service
from database.Repository import orders_db
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

