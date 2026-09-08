from sqlalchemy import and_, exists, select

from app.models.enum_model import StatusOrders
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from app.models.models import Orders


tablename = Orders.__tablename__


class OrdersRepORM:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_inform(
        self, order_id: int, block_select: bool
    ) -> Orders:
        """
        Запрос на получение информации по заказу.
        ВНИМАНИЕ!! Обращение идет через AsyncSession.add() и НЕ использует
        flush() или commit(). Если хотите использовать значения используйте
        команды flush() или commit() ЯВНО после вызова этого метода.
        """
        if block_select is False:
            stmt = await self.session.get(
                Orders, order_id,
                options=[joinedload(Orders.orders_skills)],
                with_for_update=block_select)
        else:
            stmt = await self.session.get(
                Orders, order_id,
                options=[selectinload(Orders.orders_skills)],
                with_for_update=block_select)
        if not stmt:
            raise ValueError("ХУЯКАНАМАНА РЕЗУЛЬТАТА НЭЭЭМАА")
        return stmt

    def create(self, skill_id: int, description: str) -> Orders:
        """
        Создание заказа и добавления его в базу данных.
        ВНИМАНИЕ!! Обращение идет через AsyncSession.add() и НЕ использует
        flush() или commit(). Если хотите использовать значения используйте
        команды flush() или commit() ЯВНО после вызова этого метода.
        """
        stmt = Orders(
            skill_id=skill_id,
            description=description,
            status=StatusOrders.NEW,
            )

        self.session.add(stmt)
        return stmt


class OrdersRep:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def fast_chek(self, order_id: int) -> bool:
        """
        Быстрая проверка на существования заказа по по ID-заказа (order_id)
        """
        result = await self.session.scalar(select(
                exists().where(Orders.id == order_id)))
        return bool(result)

    async def fast_chek_new_order(
            self, skill_id: int, description: str
            ) -> bool:
        """
        Быстрая проверка на существования заказа
        по ID-навыков (skill_id) и описания (description)
        """
        result = await self.session.scalar(select(
                exists().where(
                    and_(
                        Orders.skill_id == skill_id,
                        Orders.description == description
                        ))))
        return bool(result)
