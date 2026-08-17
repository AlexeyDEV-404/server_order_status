import pytest
from httpx2 import ASGITransport, AsyncClient
from app.core.unit_of_work import UnitOfWork

from app.dependencies.deps import uow as dep_uow
from app.models.enum_model import StatusMasterCheck, StatusOrders
from app.models.models import Base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.database import settings
from app.services.orders_case import OrderCommandService
from app.main import app
from app.shemas.shemas import (
    MastListValid, MasterSkillValid)


@pytest.fixture(scope="session", autouse=True)
def engine():
    settings.db_name = "SOM_TEST"
    return create_async_engine(url=settings.database_url)


@pytest.fixture(scope="session", autouse=True)
async def init_database(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def init_uow(engine):
    async with engine.connect() as conn:
        trans = await conn.begin()

        test_session_factory = async_sessionmaker(
            bind=conn,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False)

        yield UnitOfWork(test_session_factory)

        await trans.rollback()


@pytest.fixture
async def client(engine):
    async with engine.connect() as conn:
        tranc = await conn.begin()
        asession = async_sessionmaker(
            bind=engine,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False,
            )

        async def overrid_uow():
            async with UnitOfWork(session_factory=asession) as uow:
                yield uow

        app.dependency_overrides[dep_uow] = overrid_uow

        transport = ASGITransport(app=app, raise_app_exceptions=True)

        async with AsyncClient(
                transport=transport, base_url="http://test") as ac:
            yield ac

        await tranc.rollback()
        app.dependency_overrides.clear()


@pytest.fixture
async def create_skills(init_uow: UnitOfWork):
    async with init_uow as conn:
        conn.repo.skills_rep_orm.add(
            category="Plumbing",
            service="replacement of internal building pipes")
        skill = await conn.repo.skills_rep.get_skill_from_db(
             category="Plumbing",
             service="replacement of internal building pipes"
        )
    return skill


@pytest.fixture
async def create_some_skills(init_uow: UnitOfWork):
    async with init_uow as conn:
        conn.repo.skills_rep_orm.add(
            category="Plumbing",
            service="replacement of internal building pipes.")
        conn.repo.skills_rep_orm.add(
            category="Electrics", service="wiring replacement.")
        conn.repo.skills_rep_orm.add(
            category="Painting", service="wall painting")


@pytest.fixture
async def one_order(init_uow: UnitOfWork, create_skills):
    async with init_uow as conn:
        skills_id = create_skills.id
        order = conn.repo.order_repo_orm.create(
            skill_id=skills_id, description="desriptor order.")
    return order


@pytest.fixture
async def create_master(init_uow: UnitOfWork):
    async with init_uow as uow:
        result = uow.repo.master_list.add_master(
            name="Иван", status=StatusMasterCheck.FREE)

    return result


@pytest.fixture
async def create_master_busy(init_uow: UnitOfWork):
    async with init_uow as uow:
        result = uow.repo.master_list.add_master(
            name="Иван", status=StatusMasterCheck.BUSY)

    return result


@pytest.fixture
async def one_order_assign(
    init_uow: UnitOfWork, create_skills, create_master, one_order
):

    logic = OrderCommandService(uow=init_uow)
    ord_id = one_order.id
    master_id = create_master.id
    print(master_id, "----------------")
    test_func = await logic.order_lifecycle(
        new_status=StatusOrders.ASSIGNED,
        order_id=ord_id,
        master_id=master_id)
    return test_func


@pytest.fixture
async def one_order_in_progress(
    init_uow: UnitOfWork, one_order_assign
):
    logic = OrderCommandService(uow=init_uow)
    ord_id = one_order_assign.id
    master_id = one_order_assign.master_id
    test_func = await logic.order_lifecycle(
        new_status=StatusOrders.IN_PROGRESS,
        order_id=ord_id,
        master_id=master_id)
    return test_func


@pytest.fixture
async def skills_client(client):
    skills = await client.post(
        "/catalog_skills/add",
        json={
            "category": "Электрика",
            "service": "Замена проводки"})
    print(skills, "222222", skills.json(), "3333333")
    # skills = SkillsValidNoID(
    #     category=skills.json()["category"],
    #     service=skills.json()["service"])
    return skills


@pytest.fixture
async def master_client(client):
    master = await client.post("/masters/create", json={
        "name": "Иван",
        "status": "FREE"
    })
    master_res = MastListValid.model_validate(master.json())
    return master_res


@pytest.fixture
async def add_skills(client, skills_client, master_client):
    request = await client.post("/master_skills/add", json={
            "master_id": master_client.id,
            "skill_id": skills_client.id
        })
    master_skills = MasterSkillValid.model_validate(request)
    return master_skills
