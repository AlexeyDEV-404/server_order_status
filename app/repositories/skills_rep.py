from typing import Sequence

from sqlalchemy import and_, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Skills


class SkillRepORM():
    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, category: str, service: str) -> Skills:
        """
        Метод репозитория добавляет навыки в таблицу Skills.
        ВНИМАНИЕ!! Обращение идет через AsyncSession.add() и НЕ использует
        flush() или commit(). Если хотите использовать значения используйте
        команды flush() или commit() ЯВНО после вызова этого метода
        """
        adding = Skills(
            category=category,
            service=service
        )
        self.session.add(adding)
        return adding


class SkillRep():
    def __init__(self, session: AsyncSession):
        self.session = session

    async def exists_or_not(self,  category: str, service: str) -> bool:

        request = await self.session.scalar(select(exists().where(and_(
            Skills.category == category, Skills.service == service))))

        return bool(request)

    async def all_table(self):
        request = await self.session.execute(select(Skills))
        return request.scalars().all()

    async def get_skill_from_db(
        self, category: str, service: str
    ) -> Skills | None:
        get = await self.session.execute(
            select(Skills).where(
                and_(Skills.category == category, Skills.service == service)))
        return get.scalar_one_or_none()
