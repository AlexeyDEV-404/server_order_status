from app.core.unit_of_work import UnitOfWork


class MasterSkillsQueryService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def add(self, master_id: int, skill_id: int):
        async with self.uow:
            check = await self.uow.repo.master_skills.quick_check_existence(
                master_id=master_id, skill_id=skill_id)

            if check is True:
                raise ValueError("Такая связь мастер-навык уже существует")
            else:
                self.uow.repo.master_skills_orm.add_skills(
                    master_id=master_id, skill_id=skill_id)
                return True
