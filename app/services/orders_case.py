from sqlalchemy.exc import NoResultFound

from app.models.models import (
    MasterList,
    Orders)
from app.models.enum_model import (
    StatusMasterCheck,
    StatusOrders)

from app.core.exception import (
    MasterStatusError,
    OrderStatusError,
    MasterNoFoundError)
from app.shemas.shemas import OrderValid, OrderValid2

from sqlalchemy.ext.asyncio import AsyncSession

from app.helper.help import Repository


class OrderQueryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = Repository(self.session)

    async def get_inf_order(self, order_id: int):
        async with self.session.begin():
            request = await self.repo.order_repo_orm.get_inform(
                order_id=order_id, block_select=False)
            result = OrderValid.model_validate(request)
        return result

    async def post_in_db(self, skill_id: int, description: str) -> bool:
        async with self.session.begin():
            self.repo.order_repo_orm.create(
                skill_id=skill_id, description=description)
            await self.session.flush()
            result = await self.repo.order_repo.fast_chek_new_order(
                skill_id=skill_id, description=description)
        return result


class OrderCommandService:

    TRANSACTION_MAP = {
        (StatusOrders.NEW, StatusOrders.ASSIGNED): "assign",
        (StatusOrders.ASSIGNED, StatusOrders.IN_PROGRESS): "in_progress",
        (StatusOrders.IN_PROGRESS, StatusOrders.COMPLETED): "complete",
        # (StatusOrders.NEW, StatusOrders.CANCEL): "cancel"
    }

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = Repository(self.session)

    async def order_lifecycle(
            self, new_status: StatusOrders,
            order_id: int, master_id: int, **kwargs):
        """
        Функция агрегатор, которая направляет текущее выполнение в зависимости
        от этапа жизненного цикла заказа.
        """
        async with self.session.begin():
            order = await self.repo.order_repo_orm.get_inform(
                order_id=order_id, block_select=True)
            
            master = await self.repo.master_list.get_inform(
                        master_id=master_id, block_select=True)

            if master is None:
                raise MasterNoFoundError(
                    f"Error: master with id - {master_id}, no found.")

            if order is None:
                raise NoResultFound(
                    f"Ошибка: заказ с id - {order_id} не найден")

            handler_name = self.TRANSACTION_MAP.get((order.status, new_status))

            if handler_name is None:
                raise OrderStatusError(
                    "Ошибка: неизвестная операция"
                    f"{order.status} -> {new_status}")

            handler = getattr(self, handler_name)

            handler(order=order, master=master, **kwargs)
            order.status = new_status
            order_finish = OrderValid2.model_validate(order)
        return order_finish

    def assign(
            self, order: Orders, master: MasterList, **kwargs
            ) -> None:
        """
        Проки: статус мастера, текущий заказ (есть ли нету).
        После успешных проверок меняем статус мастера и закрепляем за заказом
        """
        if master.status == StatusMasterCheck.BUSY:
            raise MasterStatusError(
                "Error: The master is busy and cannot take order")
        master.status = StatusMasterCheck.BUSY
        order.master_id = master.id

    def in_progress(self, **kwargs) -> None:
        pass

    def complete(
            self, master: MasterList, **kwargs
                       ) -> None:
        if master.status == StatusMasterCheck.BUSY:
            master.status = StatusMasterCheck.FREE
        else:
            raise MasterStatusError("Ошибка: статус мастера уже FREE.")

    async def cancel(self, order_id: int):
        async with self.session.begin() as conn:
            order = await self.repo.order_repo_orm.get_inform(
                order_id=order_id, block_select=True)
            if order.status == StatusOrders.NEW:
                order.status = StatusOrders.CANCEL
            else:
                raise OrderStatusError("Error: Invalid status")
            order_finish = OrderValid.model_validate(order)
        return order_finish

    async def delete(self, order_id: int, **kwargs) -> str:
        """
        ОГРАНИЧИТЬ ИСПОЛЬЗОВАНИЯ ЭТОГО ЗАПРОСА
        ЧЕРЕЗ ВВЕДЕНИЕ РОЛЕЙ ПОЛЬЗОВАТЕЛЕЙ
        """
        async with self.session.begin():
            try:
                order = await self.repo.order_repo_orm.get_inform(
                    order_id=order_id, block_select=True)
                await self.session.delete(order)
            except NoResultFound:
                raise
        return "Запись успешно удалена"
