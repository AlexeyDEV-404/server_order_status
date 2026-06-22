from SQLAlchemy_work_db import repository
from SQLAlchemy_work_db.engine_and_models import async_get_db, Base

from fastapi.testclient import TestClient

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport
from sqlalchemy import StaticPool
from SQLAlchemy_work_db.enusm import StatusOrders, StatusMasterCheck

from database.service import server_order_in_progress
from app.main import app
import pytest

OrdRep = repository.OrderRepository
MastListRep = repository.MasterListRepository
MastSkillsRep = repository.MasterSkillsRepository
SkillsRepo = repository.SkillsRepository


@pytest.fixture
async def Create_Session_Factory():
    # url = "sqlite:///test/test.db"
    url = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(url, connect_args={"check_same_thread": False},
        poolclass=StaticPool)
    AsuncSessionLocalFactory = async_sessionmaker(engine,  expire_on_commit=False)
    
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)   
    
    async def override_get_db():
        async with AsuncSessionLocalFactory() as db:
            yield db

    app.dependency_overrides[async_get_db] = override_get_db


    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
        async with engine.connect() as conn:
            await conn.run_sync(Base.metadata.drop_all)   

@pytest.fixture(scope="function")
async def test_engine(): 
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all) 
    return engine

@pytest.fixture(scope="function")
async def test_db(test_engine):
    SessionFactoryTests = async_sessionmaker(bind=test_engine)
    async with SessionFactoryTests() as session:
        yield session

@pytest.fixture(scope="function")
async def order_one(test_db):
    return await OrdRep(test_db).add_order(category="Сантехника", service="замена труб", description="Протечка", status=StatusOrders.NEW)

@pytest.fixture
async def orders_many(test_db):
    category = ["Сантехника", "Электрика", "Ремонт"]
    service = ["Замена труб", "Замена розеток", "Поклейка обоев"]
    for catg, serv in zip(category, service):
        await OrdRep(test_db).add_order(category=catg, service=serv, description="Какое-то тестовое описание", status=StatusOrders.NEW)

# _____________MasterListRepository__________start

@pytest.fixture(scope="function")
async def add_master(test_db):
    """ Добавим мастера по имени Анидрей со статусом FREE """
    print("\n=== СОЗДАЁМ НОВОГО МАСТЕРА ===")
    return (await MastListRep(test_db).add(name = "Андрей", status = StatusMasterCheck.FREE))

@pytest.fixture
async def assing_master_order(orderID, test_db):
    return await server_order_in_progress(orderID, db = test_db)

# _____________MasterListRepository__________end
# _____________SkillsRepository__________start

@pytest.fixture
async def insert_works(test_db):
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
            await SkillsRepo(test_db).insert_skill(key, x)
    await test_db.commit()

@pytest.fixture
async def insert_work(test_db):
    return await SkillsRepo(test_db).insert_skill(category="Сантехника", service = "Ремонт трубы")
     


# _____________MastSkillsRep__________start

@pytest.fixture
async def add_master_skills(test_db, insert_work, add_master):
    return await MastSkillsRep(test_db).add_master_skills(master_id=add_master, skill_id=insert_work)

# _____________MastSkillsRep__________end