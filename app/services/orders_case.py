from sqlalchemy.exc import NoResultFound

from app.core.unit_of_work import UnitOfWork

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
from app.shemas.shemas import OrderValid


class OrderQueryService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def get_inf_order(self, order_id: int):
        async with self.uow:
            result = await self.uow.repo.order_repo_orm.get_inform(
                order_id=order_id, block_select=False)
        return OrderValid.model_validate(result)

    async def post_in_db(self, skill_id: int, description: str) -> bool:
        async with self.uow:
            self.uow.repo.order_repo_orm.create(
                skill_id=skill_id, description=description)
            await self.uow.session.flush()
            result = await self.uow.repo.order_repo.fast_chek_new_order(
                skill_id=skill_id, description=description)
        return result


class OrderCommandService:

    TRANSAСTION_MAP = {
        (StatusOrders.NEW, StatusOrders.ASSIGNED): "assign",
        (StatusOrders.ASSIGNED, StatusOrders.IN_PROGRESS): "in_progress",
        (StatusOrders.IN_PROGRESS, StatusOrders.COMPLETED): "complete",
        (StatusOrders.NEW, StatusOrders.CANCEL): "cancel"
    }

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def order_lifecycle(
            self, new_status: StatusOrders,
            order_id: int, master_id: int, **kwargs):
        """
        Функция агрегатор, которая направляет текущее выполнение в зависимости
        от этапа жизненного цикла заказа.
        """
        async with self.uow:
            order = await self.uow.repo.order_repo_orm.get_inform(
                order_id=order_id, block_select=True)

            master = await self.uow.repo.master_list.get_inform(
                        master_id=master_id, block_select=True)

            if master is None:
                raise MasterNoFoundError(
                    f"Error: master with id - {master_id}, no found.")

            if order is None:
                raise NoResultFound(
                    f"Ошибка: заказ с id - {order_id} не найден")

            handler_name = self.TRANSAСTION_MAP.get((order.status, new_status))

            if handler_name is None:
                raise OrderStatusError(
                    "Ошибка: неизвестная операция"
                    f"{order.status} -> {new_status}")

            handler = getattr(self, handler_name)

            handler(order=order, master=master, **kwargs)
            order.status = new_status
        return order

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

    def cancel(
            self, order: Orders, **kwargs) -> None:
        pass

    async def delete(self, order_id: int, **kwargs) -> str:
        """
        ОГРАНИЧИТЬ ИСПОЛЬЗОВАНИЯ ЭТОГО ЗАПРОСА
        ЧЕРЕЗ ВВЕДЕНИЕ РОЛЕЙ ПОЛЬЗОВАТЕЛЕЙ
        """
        async with self.uow:
            try:
                order = await self.uow.repo.order_repo_orm.get_inform(
                    order_id=order_id, block_select=True)
                await self.uow.session.delete(order)
            except NoResultFound:
                raise
        return "Запись успешно удалена"
