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
    print(id(uow), "ТУТААААААААААААААААА")
    return OrderQueryService(uow)


def order_command_service(
        uow: AsyncSession = Depends(uow)
        ) -> OrderCommandService:
    print(id(uow), "ТУТААААААААААААААААА")
    return OrderCommandService(uow)


def master_list_service(
        uow: AsyncSession = Depends(uow)
        ) -> MasterListQueryService:
    print(id(uow), "ТУТААААААААААААААААА")
    return MasterListQueryService(uow)


def master_skills_service(
        uow: AsyncSession = Depends(uow)
        ) -> MasterSkillsQueryService:
    print(id(uow), "ТУТААААААААААААААААА")
    return MasterSkillsQueryService(uow)


def skills_service_orm(
        uow: AsyncSession = Depends(uow)
        ) -> SkillsServiceORM:
    print(id(uow), "ТУТААААААААААААААААА")
    return SkillsServiceORM(uow)


def skills_service(
        uow: AsyncSession = Depends(uow)
        ) -> SkillsService:
    print(id(uow), "ТУТААААААААААААААААА")
    return SkillsService(uow)


def params_life_cycle_orders(
    order_id: int, master_id: int
) -> ParamsLifeCycle:
    print(id(uow), "ТУТААААААААААААААААА")
    return ParamsLifeCycle(order_id=order_id, master_id=master_id)

def params_for_cancel(
    order_id: int
) -> ParamsLForCancle:
    print(id(uow), "ТУТААААААААААААААААА")
    return ParamsLForCancle(order_id=order_id)
