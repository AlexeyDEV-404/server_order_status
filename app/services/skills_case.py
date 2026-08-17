from app.core.exception import SkillsError
from app.core.unit_of_work import UnitOfWork
from app.shemas.shemas import SkillsValid


class SkillsServiceORM:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def add(self, category: str, service: str):
        async with self.uow:
            check = await self.uow.repo.skills_rep.exists_or_not(
                category=category, service=service)

            if check is True:
                raise SkillsError("Error: Skills already exists")

            response = self.uow.repo.skills_rep_orm.add(
                category=category, service=service)
        result = SkillsValid.model_validate(response)
        return result


class SkillsService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def get_all_table(self):
        async with self.uow:
            result = await self.uow.repo.skills_rep.all_table()
            return [SkillsValid.model_validate(s) for s in result]
