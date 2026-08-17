from sqlalchemy import and_, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import MasterSkills


class MasterSkillsRepORM:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def add_skills(self, master_id: int, skill_id: int) -> MasterSkills:
        add = MasterSkills(master_id=master_id, skill_id=skill_id)
        self.session.add(add)
        return add


class MasterSkillsRep:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def quick_check_existence(
        self, master_id: int, skill_id: int
    ) -> bool:
        result = await self.session.scalar(
            select(exists().where(and_(
                MasterSkills.master_id == master_id,
                MasterSkills.skill_id == skill_id))))
        return bool(result)
