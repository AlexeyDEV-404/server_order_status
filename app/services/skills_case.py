from app.core.exception import SkillsError
from app.shemas.shemas import SkillsValid
from sqlalchemy.ext.asyncio import AsyncSession

from app.helper.help import Repository


class SkillsServiceORM:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = Repository(self.session)

    async def add(self, category: str, service: str):
        async with self.session.begin():
            check = await self.repo.skills_rep.exists_or_not(
                category=category, service=service)

            if check is True:
                raise SkillsError

            response = self.repo.skills_rep_orm.add(
                category=category, service=service)
            result = SkillsValid.model_validate(response)
        return result


class SkillsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = Repository(self.session)

    async def get_all_table(self):
        async with self.session.begin():
            result = await self.repo.skills_rep.all_table()
            valid_result = [SkillsValid.model_validate(s) for s in result]
        return valid_result