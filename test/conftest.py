from SQLAlchemy_work_db import repository, engine_and_models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from SQLAlchemy_work_db.enusm import StatusOrders, StatusMasterCheck
from database.service import server_order_in_progress
from app.main import app

import pytest


OrdRep = repository.OrderRepository
MastListRep = repository.MasterListRepository
MastSkillsRep = repository.MasterSkillsRepository
SkillsRepo = repository.SkillsRepository

Base = engine_and_models.Base

@pytest.fixture(scope="function")
def engine(): 
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture(scope="function")
def db(engine):
    with sessionmaker(bind=engine)() as session:
        yield session

@pytest.fixture
def client_app():
    return TestClient(app)

@pytest.fixture
def order_one(db):
    return OrdRep(db).add_order(category="Сантехника", service="замена труб", description="Протечка", status=StatusOrders.NEW)

@pytest.fixture
def orders_many(db):
    category = ["Сантехника", "Электрика", "Ремонт"]
    service = ["Замена труб", "Замена розеток", "Поклейка обоев"]
    for catg, serv in zip(category, service):
        OrdRep(db).add_order(category=catg, service=serv, description="Какое-то тестовое описание", status=StatusOrders.NEW)

# _____________MasterListRepository__________start

@pytest.fixture
def add_master(db):
    """ Добавим мастера по имени Анидрей со статусом FREE """
    return MastListRep(db).add(name = "Андрей", status = StatusMasterCheck.FREE)

@pytest.fixture
def assing_master_order(orderID):
    return server_order_in_progress(orderID)

# _____________MasterListRepository__________end
# _____________SkillsRepository__________start

@pytest.fixture
def insert_works(db):
    categories_services = {
    "Сантехника": ["Замена труб", "Устранение засора", "Замена смесителя"],
    "Электрика": ["Замена розеток", "Замена проводки", "Установка люстры"],
    "Ремонт": ["Поклейка обоев", "Покраска стен", "Укладка плитки"],
    "Уборка": ["Генеральная уборка", "Мытьё окон", "Химчистка мебели"],
    "Мебель": ["Сборка мебели", "Ремонт мебели", "Установка шкафа"],
    "Бытовая техника": ["Ремонт холодильника", "Ремонт стиральной машины", "Подключение плиты"]
    }

    for key, value in categories_services.items():
        for x in value:
            SkillsRepo(db).insert_skill(key, x)
    db.commit()

@pytest.fixture
def insert_work(db):
    return SkillsRepo(db).insert_skill(category="Сантехника", service = "Ремонт трубы")
     


# _____________MastSkillsRep__________start

@pytest.fixture
def add_master_skills(db, insert_work, add_master):
    return MastSkillsRep(db).add_master_skills(master_id=add_master, skill_id=insert_work)

# _____________MastSkillsRep__________end