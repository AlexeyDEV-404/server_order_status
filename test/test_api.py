import pytest
#  НЕ РАБОЧИЙ КОД!!!
# pytest test/test_api.py -v
# pytest test/test_api.py::test_order_list -v -s

@pytest.fixture
async def new_order(Create_Session_Factory):
    return await Create_Session_Factory.post("/user/order/new", json={
        "category": "Сантехника",
        "services": "замена труб",
        "description": "Протечка"
    })

@pytest.fixture
async def add_master(Create_Session_Factory):
    return await Create_Session_Factory.post("/user/add_master", params={
        "name": "Андрей"
    })

async def test_new_order(new_order):    
    assert new_order.status_code == 200
    assert type(new_order.json()) == int

async def test_assinged(Create_Session_Factory, new_order, add_master):
    response = await Create_Session_Factory.post(f"/user/order/{new_order.json()}/assinged", json={"masterID": add_master.json()})
    assert response.status_code == 200
    assert response.json()["status"] == "ASSINGED"

async def test_in_progress(Create_Session_Factory, new_order, add_master):
    await Create_Session_Factory.post(f"/user/order/{new_order.json()}/assinged", json={"masterID": add_master.json()})
    response = await Create_Session_Factory.post(f"/user/order/{new_order.json()}/in_progress")
    assert response.status_code == 200
    assert response.json()["status"] == "IN_PROGRESS"

async def test_completed(Create_Session_Factory, new_order, add_master):
    await Create_Session_Factory.post(f"/user/order/{new_order.json()}/assinged", json={"masterID": add_master.json()})
    await Create_Session_Factory.post(f"/user/order/{new_order.json()}/in_progress")
    response = await Create_Session_Factory.post(f"/user/order/{new_order.json()}/completed")
    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"


async def test_cancel(Create_Session_Factory, new_order):
    response = await Create_Session_Factory.post(f"/user/order/{new_order.json()}/cancel")
    assert response.status_code == 200
    assert response.json() == "CANCEL"

async def test_delete_order(Create_Session_Factory, new_order):
    response = await Create_Session_Factory.post(f"/user/order/{new_order.json()}/delete")
    assert response.status_code == 200
    assert response.json() > 0

async def test_add_master_skills(Create_Session_Factory):
    response = await Create_Session_Factory.post("/user/insert_skill", params={"category":"Электрика", "service": "Ремонт электрощитка"})

    assert response.status_code == 200
    assert response.json() > 0

async def test_insert_skills_and_table_skills(Create_Session_Factory, add_master):
    skills = await Create_Session_Factory.post("/user/insert_skill", params={"category":"Электрика", "service": "Ремонт электрощитка"})
    response = await Create_Session_Factory.post("/user/add_master_skill", params={
        "master_id": add_master.json(),
        "skill_id": skills.json()
        })
    assert response.status_code == 200
    table_skills = await Create_Session_Factory.get("/user/table_skill_master")
    assert table_skills.status_code == 200
    assert table_skills.json()[0]["master_id"] > 0
    assert table_skills.json()[0]["skill_id"] > 0

async def test_order(Create_Session_Factory, new_order):
    resp = await Create_Session_Factory.get(f"/user/order/{new_order.json()}")
    
    assert resp.status_code == 200
    assert resp.json()["category"] == "Сантехника"
    assert resp.json()["status"] == "NEW"

async def test_order_list(Create_Session_Factory, new_order):
    resp = await Create_Session_Factory.get("/user/orders")

    assert resp.status_code == 200
    assert resp.json()[0]["category"] == "Сантехника"
    assert resp.json()[0]["status"] == "NEW"



    






