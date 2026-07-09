from fastapi import Depends

from SQLAlchemy_work_db.engine_and_models import AsyncSessionFactory
from sqlalchemy.ext.asyncio import AsyncSession
from SQLAlchemy_work_db.repository import (
    MasterListRepository,
    MasterSkillsRepository,
    OrderRepository,
    SkillsRepository
)


async def async_get_db():
    async with AsyncSessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


class Repository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.MastListRep = MasterListRepository(db)
        self.MastSkillsRep = MasterSkillsRepository(db)
        self.OrderRepo = OrderRepository(db)
        self.SkillsRepo = SkillsRepository(db)


async def get_repository(db: AsyncSession = Depends(async_get_db)):
    return Repository(db=db)