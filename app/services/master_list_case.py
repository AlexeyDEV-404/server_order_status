from sqlalchemy.ext.asyncio import AsyncSession
from app.helper.help import Repository
from app.shemas.shemas import MastListValid, MasterListOut
from app.models.enum_model import StatusMasterCheck


class MasterListQueryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = Repository(self.session)

    async def create(
        self,  name: str, status: StatusMasterCheck
    ) -> MastListValid:
        async with self.session.begin():
            master = self.repo.master_list.add_master(
                name=name, status=status)
            await self.session.flush()
            result = MastListValid.model_validate(master)
        return result

    async def all_free_master(
            self, status: StatusMasterCheck
            ) -> list[MastListValid]:
        """
        Поиск по status без релиационных связей
        """
        async with self.session:
            request = await self.repo.master_list_core.search(status)
            result = [MastListValid.model_validate(s) for s in request]

            return result

    async def all_table(self):
        async with self.session:
            master = await self.repo.master_list_core.all_info()
            result = [MasterListOut.from_orm_master(m) for m in master]
            return result
