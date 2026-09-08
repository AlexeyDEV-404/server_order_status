from sqlalchemy.ext.asyncio import AsyncSession

from app.helper.help import Repository


class MasterSkillsQueryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = Repository(self.session)

    async def add(self, master_id: int, skill_id: int):
        async with self.session.begin():
            check = await self.repo.master_skills.quick_check_existence(
                master_id=master_id, skill_id=skill_id)

            if check is True:
                raise ValueError("Такая связь мастер-навык уже существует")
            else:
                self.repo.master_skills_orm.add_skills(
                    master_id=master_id, skill_id=skill_id)
                return True
