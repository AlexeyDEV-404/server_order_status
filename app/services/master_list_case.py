from app.core.unit_of_work import UnitOfWork
from app.shemas.shemas import MastListValid, MasterListOut
from app.models.enum_model import StatusMasterCheck


class MasterListQueryService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def create(
        self,  name: str, status: StatusMasterCheck
    ) -> MastListValid:
        async with self.uow:
            master = self.uow.repo.master_list.add_master(
                name=name, status=status)
            await self.uow.session.flush()
        result = MastListValid.model_validate(master)
        return result

    async def all_free_master(
            self, status: StatusMasterCheck
            ) -> list[MastListValid]:
        """
        Поиск по status без релиационных связей
        """
        async with self.uow:
            request = await self.uow.repo.master_list_core.search(status)
            result = [MastListValid.model_validate(s) for s in request]

            return result

    async def all_table(self):
        async with self.uow:
            master = await self.uow.repo.master_list_core.all_info()
            result = [MasterListOut.from_orm_master(m) for m in master]
            return result
