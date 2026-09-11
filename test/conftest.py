# flake8: noqa
import pytest
from httpx2 import ASGITransport, AsyncClient

from app.dependencies.deps import uow
from app.helper.help import Repository
from app.models.enum_model import StatusMasterCheck, StatusOrders
from app.models.models import Base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.database import settings
from app.services.orders_case import OrderCommandService
from app.main import app
from app.shemas.shemas import (
    MastListValid)
from app.repositories.master_list_rep import MasterListRep




@pytest.fixture(scope="session")
async def crt_engine():
    settings.db_name = "SOM_TEST"
    eng = create_async_engine(url=settings.database_url)
    async with eng.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()
    return eng

@pytest.fixture
async def asession(crt_engine):
    async with crt_engine.connect() as conn:
        async with conn.begin() as trans:
            session = async_sessionmaker(bind=conn)    
            yield session()
            await trans.rollback()

@pytest.fixture
def repo(asession):
    print(f'ID SESSION {id(asession)} repo fixture')
    return Repository(asession) 

@pytest.fixture
async def one_master(asession, repo):
    async with asession.begin_nested() as trans:
        print(f'ID TRANSACTION {id(trans)} and ID SESSION {id(asession)} one_master fixture')
        req = repo.master_list.add_master(name="Test_name", status=StatusMasterCheck.FREE)
    return req