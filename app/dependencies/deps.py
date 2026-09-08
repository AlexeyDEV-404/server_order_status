from fastapi import Depends
from app.services.master_skills_case import MasterSkillsQueryService
from app.services.orders_case import (
    OrderQueryService,
    OrderCommandService)
from app.services.master_list_case import MasterListQueryService
from app.services.skills_case import SkillsService, SkillsServiceORM
from app.shemas.shemas import ParamsLForCancle, ParamsLifeCycle
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionFactory


def uow():
    return AsyncSessionFactory()


def order_query_service(
        uow: AsyncSession = Depends(uow)
        ) -> OrderQueryService:
    return OrderQueryService(uow)


def order_command_service(
        uow: AsyncSession = Depends(uow)
        ) -> OrderCommandService:
    return OrderCommandService(uow)


def master_list_service(
        uow: AsyncSession = Depends(uow)
        ) -> MasterListQueryService:
    return MasterListQueryService(uow)


def master_skills_service(
        uow: AsyncSession = Depends(uow)
        ) -> MasterSkillsQueryService:
    return MasterSkillsQueryService(uow)


def skills_service_orm(
        uow: AsyncSession = Depends(uow)
        ) -> SkillsServiceORM:
    return SkillsServiceORM(uow)


def skills_service(
        uow: AsyncSession = Depends(uow)
        ) -> SkillsService:
    return SkillsService(uow)


def params_life_cycle_orders(
    order_id: int, master_id: int
) -> ParamsLifeCycle:
    return ParamsLifeCycle(order_id=order_id, master_id=master_id)

def params_for_cancel(
    order_id: int
) -> ParamsLForCancle:
    return ParamsLForCancle(order_id=order_id)
