from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload, selectinload
from app.models.models import MasterList, MasterSkills
from app.models.enum_model import StatusMasterCheck


tablename = MasterList.__tablename__


class MasterListRep():
    def __init__(self, session: AsyncSession):
        self.session = session

    def add_master(self, name: str, status: StatusMasterCheck) -> MasterList:
        """
        Метод репозитория добавляет мастера в таблицу MasterList.
        ВНИМАНИЕ!! Обращение идет через AsyncSession.add() и НЕ использует
        flush() или commit(). Если хотите использовать значения используйте
        команды flush() или commit() ЯВНО после вызова этого метода
        """
        add = MasterList(name=name, status=status)
        self.session.add(add)
        return add

    async def get_inform(
            self, master_id: int, block_select: bool
            ) -> MasterList | None:
        if block_select is False:
            stmt = await self.session.get(
                MasterList, master_id,
                options=[joinedload(MasterList.master_skills)],
                with_for_update=block_select)
        elif block_select is True:
            stmt = await self.session.get(
                MasterList, master_id,
                with_for_update=block_select,
                options=[selectinload(MasterList.master_skills)])
        return stmt


class MasterListCoreRep:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search(
        self, status: StatusMasterCheck
    ):
        """
        Аналогичен методу get_inform, но поиск происходит по полю status,
        а не master_id
        """
        stmt = await self.session.scalars(
            select(MasterList).where(MasterList.status == status))
        result = stmt.all()

        if result is not None:
            return result
        else:
            raise NoResultFound

    async def all_info(self) -> Sequence[MasterList]:
        """
        Загружает полную информацию про всех мастеров
        """
        stmt = select(MasterList).options(
            joinedload(MasterList.master_skills)
            .joinedload(MasterSkills.skills))
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()
