from typing import Literal

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from functools import cached_property
from app.repositories.orders_rep import (OrdersRep, OrdersRepORM)
from app.repositories.master_list_rep import (
    MasterListCoreRep, MasterListRep)
from app.repositories.master_skills_rep import (
    MasterSkillsRep,
    MasterSkillsRepORM)
from app.repositories.skills_rep import (
    SkillRepORM, SkillRep)


class Repository():
    def __init__(self, session: AsyncSession):
        self.session = session

    @cached_property
    def order_repo(self) -> OrdersRep:
        return OrdersRep(self.session)

    @cached_property
    def order_repo_orm(self) -> OrdersRepORM:
        return OrdersRepORM(self.session)

    @cached_property
    def master_list(self) -> MasterListRep:
        return MasterListRep(self.session)

    @cached_property
    def master_list_core(self) -> MasterListCoreRep:
        return MasterListCoreRep(self.session)

    @cached_property
    def master_skills_orm(self) -> MasterSkillsRepORM:
        return MasterSkillsRepORM(self.session)

    @cached_property
    def master_skills(self) -> MasterSkillsRep:
        return MasterSkillsRep(self.session)

    @cached_property
    def skills_rep_orm(self) -> SkillRepORM:
        return SkillRepORM(self.session)

    @cached_property
    def skills_rep(self) -> SkillRep:
        return SkillRep(self.session)


class UnitOfWork:
    def __init__(
            self, session_factory: async_sessionmaker[AsyncSession]
            ) -> None:
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        self.repo = Repository(self.session)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> Literal[False]:
        if exc_type is not None:
            await self.session.rollback()
        else:
            await self.session.commit()

        await self.session.close()
        return False
