from SQLAlchemy_work_db import repository
from SQLAlchemy_work_db.engine_and_models import get_db, Base

from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from SQLAlchemy_work_db.enusm import StatusOrders, StatusMasterCheck

from database.service import server_order_in_progress
from app.main import app
import pytest

OrdRep = repository.OrderRepository
MastListRep = repository.MasterListRepository
MastSkillsRep = repository.MasterSkillsRepository
SkillsRepo = repository.SkillsRepository


@pytest.fixture
def Create_Session_Factory():
    engine = create_engine("sqlite:///test/test.db")
    SessionLocalFactory = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    
    def override_get_db():
        with SessionLocalFactory() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def test_engine(): 
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture(scope="function")
def test_db(test_engine):
    SessionFactoryTests = sessionmaker(bind=test_engine)
    with SessionFactoryTests() as session:
         yield session

@pytest.fixture(scope="function")
def order_one(test_db):
    return OrdRep(test_db).add_order(category="Сантехника", service="замена труб", description="Протечка", status=StatusOrders.NEW)

@pytest.fixture
def orders_many(test_db):
    category = ["Сантехника", "Электрика", "Ремонт"]
    service = ["Замена труб", "Замена розеток", "Поклейка обоев"]
    for catg, serv in zip(category, service):
        OrdRep(test_db).add_order(category=catg, service=serv, description="Какое-то тестовое описание", status=StatusOrders.NEW)

# _____________MasterListRepository__________start

@pytest.fixture(scope="function")
def add_master(test_db):
    """ Добавим мастера по имени Анидрей со статусом FREE """
    print("\n=== СОЗДАЁМ НОВОГО МАСТЕРА ===")
    return MastListRep(test_db).add(name = "Андрей", status = StatusMasterCheck.FREE)

@pytest.fixture
def assing_master_order(orderID, test_db):
    return server_order_in_progress(orderID, db = test_db)

# _____________MasterListRepository__________end
# _____________SkillsRepository__________start

@pytest.fixture
def insert_works(test_db):
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
            SkillsRepo(test_db).insert_skill(key, x)
    test_db.commit()

@pytest.fixture
def insert_work(test_db):
    return SkillsRepo(test_db).insert_skill(category="Сантехника", service = "Ремонт трубы")
     


# _____________MastSkillsRep__________start

@pytest.fixture
def add_master_skills(test_db, insert_work, add_master):
    return MastSkillsRep(test_db).add_master_skills(master_id=add_master, skill_id=insert_work)

# _____________MastSkillsRep__________end