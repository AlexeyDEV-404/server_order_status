from fastapi import Depends
from app.core.database import AsyncSessionFactory
from app.core.unit_of_work import UnitOfWork
from app.services.master_skills_case import MasterSkillsQueryService
from app.services.orders_case import (
    OrderQueryService,
    OrderCommandService)
from app.services.master_list_case import MasterListQueryService
from app.services.skills_case import SkillsService, SkillsServiceORM
from app.shemas.shemas import ParamsLifeCycle


def uow() -> UnitOfWork:
    return UnitOfWork(AsyncSessionFactory)


def order_query_service(
        uow: UnitOfWork = Depends(uow)
        ) -> OrderQueryService:
    return OrderQueryService(uow)


def order_command_service(
        uow: UnitOfWork = Depends(uow)
        ) -> OrderCommandService:
    return OrderCommandService(uow)


def master_list_service(
        uow: UnitOfWork = Depends(uow)
        ) -> MasterListQueryService:
    return MasterListQueryService(uow)


def master_skills_service(
        uow: UnitOfWork = Depends(uow)
        ) -> MasterSkillsQueryService:
    return MasterSkillsQueryService(uow)


def skills_service_orm(
        uow: UnitOfWork = Depends(uow)
        ) -> SkillsServiceORM:
    return SkillsServiceORM(uow)


def skills_service(
        uow: UnitOfWork = Depends(uow)
        ) -> SkillsService:
    return SkillsService(uow)


def params_life_cycle(order_id: int, master_id: int,) -> ParamsLifeCycle:
    return ParamsLifeCycle(order_id=order_id, master_id=master_id)
