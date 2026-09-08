from sqlalchemy.ext.asyncio import AsyncSession

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

    @property
    def order_repo(self) -> OrdersRep:
        return OrdersRep(self.session)

    @property
    def order_repo_orm(self) -> OrdersRepORM:
        return OrdersRepORM(self.session)

    @property
    def master_list(self) -> MasterListRep:
        return MasterListRep(self.session)

    @property
    def master_list_core(self) -> MasterListCoreRep:
        return MasterListCoreRep(self.session)

    @property
    def master_skills_orm(self) -> MasterSkillsRepORM:
        return MasterSkillsRepORM(self.session)

    @property
    def master_skills(self) -> MasterSkillsRep:
        return MasterSkillsRep(self.session)

    @property
    def skills_rep_orm(self) -> SkillRepORM:
        return SkillRepORM(self.session)

    @property
    def skills_rep(self) -> SkillRep:
        return SkillRep(self.session)
