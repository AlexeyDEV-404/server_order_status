from SQLAlchemy_work_db import repository
from SQLAlchemy_work_db.engine_and_models import Base, Orders

from app.api.deps import async_get_db

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport
from sqlalchemy import StaticPool
from SQLAlchemy_work_db.enusm import StatusOrders, StatusMasterCheck

from database.service import Service
from app.main import app
import pytest

OrdRep = repository.OrderRepository
MastListRep = repository.MasterListRepository
MastSkillsRep = repository.MasterSkillsRepository
SkillsRepo = repository.SkillsRepository

URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def Create_Session_Factory():
    async with TestingSessionLocal() as conn:
        async def override_get_db():
            yield conn

        app.dependency_overrides[async_get_db] = override_get_db

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            yield client

        app.dependency_overrides.clear


@pytest.fixture(scope="function", autouse=True)
async def clean_database_after_test():
    """
    Эта фикстура автоматически приходит на КАЖДЫЙ тест.
    Она ничего не делает ДО теста, но ПОСЛЕ теста берет и
    вычищает данные из всех таблиц, чтобы следующий тест зашел в девственно
    чистую базу.
    """
    yield  # Тут запускается и отрабатывает твой тест

    # А вот тут тест уже закончился, и мы прибираемся:
    async with engine.begin() as conn:
        # Перебираем все твои модели SQLAlchemy и удаляем из них строки
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest.fixture(scope="function")
async def test_db():
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture(scope="function")
async def order_one(test_db):
    return await OrdRep(test_db).add_order(
        category="Сантехника", service="замена труб",
        description="Протечка", status=StatusOrders.NEW
    )


@pytest.fixture
async def orders_many(test_db):
    category = ["Сантехника", "Электрика", "Ремонт"]
    service = ["Замена труб", "Замена розеток", "Поклейка обоев"]
    for catg, serv in zip(category, service):
        await OrdRep(test_db).add_order(
            category=catg, service=serv,
            description="Какое-то тестовое описание", status=StatusOrders.NEW
        )

# _____________MasterListRepository__________start


@pytest.fixture(scope="function")
async def add_master(test_db):
    """ Добавим мастера по имени Анидрей со статусом FREE """
    return await MastListRep(test_db).add(
        name="Андрей", status=StatusMasterCheck.FREE)


@pytest.fixture
async def assing_master_order(orderID, test_db):
    return await Service(test_db).server_order_in_progress(orderID)

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
        "Бытовая техника": ["Ремонт холодильника", "Ремонт стиральной машины",
                            "Подключение плиты"]
    }

    for key, value in categories_services.items():
        for x in value:
            await SkillsRepo(test_db).insert_skill(key, x)
    await test_db.commit()


@pytest.fixture
async def insert_work(test_db):
    return await SkillsRepo(test_db).insert_skill(
        category="Сантехника", service="Ремонт трубы")

# _____________MastSkillsRep__________start


@pytest.fixture
async def add_master_skills(test_db, insert_work, add_master):
    return await MastSkillsRep(test_db).add_master_skills(
        master_id=add_master, skill_id=insert_work)

# _____________MastSkillsRep__________end


@pytest.fixture
def create_order_for_mocktest():
    return Orders(id=1, category="Test_cat",
                  service="Test_serv", description="Test_desc",
                  status="ASSINGED", master=1)
