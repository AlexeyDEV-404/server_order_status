# flake8: noqa
import pytest
from app.core.unit_of_work import UnitOfWork
from app.models.enum_model import StatusMasterCheck, StatusOrders
from app.services.master_list_case import MasterListQueryService
from app.services.master_skills_case import MasterSkillsQueryService
from app.services.orders_case import OrderCommandService, OrderQueryService
from app.core.exception import (
    MasterStatusError,
    OrderStatusError,
    MasterNoFoundError,
    SkillsError)
from sqlalchemy.exc import NoResultFound, IntegrityError

from app.services.skills_case import SkillsService, SkillsServiceORM
from app.shemas.shemas import MastListValid, MasterListOut, OrderValid, SkillsValid


class TestOrderLifeCycle:
    async def test_assign_and_error(
        self, init_uow: UnitOfWork, create_skills, create_master, one_order
    ):
        logic = OrderCommandService(uow=init_uow)
        ord_id = one_order.id
        master_id = create_master.id

        with pytest.raises(MasterNoFoundError):
            test_func = await logic.order_lifecycle(
                new_status=StatusOrders.ASSIGNED,
                order_id=ord_id,
                master_id=999)

        with pytest.raises(NoResultFound):
            test_func = await logic.order_lifecycle(
                new_status=StatusOrders.ASSIGNED,
                order_id=999,
                master_id=master_id)

        with pytest.raises(OrderStatusError):
            test_func = await logic.order_lifecycle(
                new_status=StatusOrders.COMPLETED,
                order_id=ord_id,
                master_id=master_id)

        test_func = await logic.order_lifecycle(
            new_status=StatusOrders.ASSIGNED,
            order_id=ord_id,
            master_id=master_id)
        
        async with init_uow as uow:
            res = await uow.repo.master_list.get_inform(
                master_id=create_master.id, block_select=True)

        assert res.status == StatusMasterCheck.BUSY  # type: ignore
        assert test_func.status == StatusOrders.ASSIGNED
        assert test_func.master_id == master_id

    async def test_assign_for_master_error(
        self, init_uow: UnitOfWork, create_skills, create_master_busy,
        one_order
    ):
        logic = OrderCommandService(uow=init_uow)
        ord_id = one_order.id
        master_id = create_master_busy.id

        with pytest.raises(MasterStatusError):
            await logic.order_lifecycle(
                new_status=StatusOrders.ASSIGNED,
                order_id=ord_id,
                master_id=master_id)

    async def test_in_progress(
        self, init_uow: UnitOfWork, one_order_assign
    ):
        logic = OrderCommandService(uow=init_uow)
        ord_id = one_order_assign.id
        master_id = one_order_assign.master_id

        test_func = await logic.order_lifecycle(
            new_status=StatusOrders.IN_PROGRESS,
            order_id=ord_id,
            master_id=master_id)

        assert test_func.status == StatusOrders.IN_PROGRESS

    async def test_in_progress_exc_ord_status(
        self, init_uow: UnitOfWork, one_order, create_master
    ):
        logic = OrderCommandService(uow=init_uow)
        ord_id = one_order.id
        master_id = create_master.id
        with pytest.raises(OrderStatusError):
            await logic.order_lifecycle(
                new_status=StatusOrders.IN_PROGRESS,
                order_id=ord_id,
                master_id=master_id)

    async def test_complete(
        self, init_uow: UnitOfWork, one_order_in_progress
    ):
        logic = OrderCommandService(uow=init_uow)
        ord_id = one_order_in_progress.id
        master_id = one_order_in_progress.master_id

        test_func = await logic.order_lifecycle(
            new_status=StatusOrders.COMPLETED,
            order_id=ord_id,
            master_id=master_id)

        async with init_uow as uow:
            master = await uow.repo.master_list.get_inform(
                master_id=master_id, block_select=True)

        assert master.status == StatusMasterCheck.FREE  # type: ignore
        assert test_func.status == StatusOrders.COMPLETED
        assert test_func.master_id == master_id
        assert test_func.description == "desriptor order."

    async def test_complete_error(
        self, init_uow: UnitOfWork, one_order_in_progress
    ):
        logic = OrderCommandService(uow=init_uow)
        ord_id = one_order_in_progress.id
        master_id = one_order_in_progress.master_id

        async with init_uow as uow:
            master = await uow.repo.master_list.get_inform(
                master_id=master_id,
                block_select=True)
            master.status = StatusMasterCheck.FREE  #type: ignore
            
        with pytest.raises(MasterStatusError):
            await logic.order_lifecycle(
                new_status=StatusOrders.COMPLETED,
                order_id=ord_id,
                master_id=master_id)

    async def test_cancel(
        self, init_uow: UnitOfWork, create_skills, create_master, one_order
    ):
        logic = OrderCommandService(uow=init_uow)
        ord_id = one_order.id
        master_id = create_master.id
        result = await logic.order_lifecycle(
            new_status=StatusOrders.CANCEL,
            order_id=ord_id,
            master_id=master_id)

        assert result.status == StatusOrders.CANCEL

    async def test_delete(self, init_uow: UnitOfWork, one_order):
        assert isinstance(one_order.id, int)
        assert one_order.status == StatusOrders.NEW

        logic = OrderCommandService(uow=init_uow)
        ord_id = one_order.id

        await logic.delete(order_id=ord_id)

        async with init_uow as uow:
            result = await uow.repo.order_repo.fast_chek(order_id=ord_id)

        assert isinstance(result, bool)
        assert result is False
  

class TestOrderQuery:
    async def test_get_inf_order(self, init_uow: UnitOfWork, one_order):
        logic = OrderQueryService(uow=init_uow)
        ord_id = one_order.id
        result = await logic.get_inf_order(order_id=ord_id)

        assert isinstance(result, OrderValid)
        assert isinstance(result.status, StatusOrders)
        assert result.orders_skills.category == "Plumbing"
        assert result.orders_skills.service == "replacement of internal building pipes"
        assert result.description == "desriptor order."

    async def test_post_in_db(self, init_uow: UnitOfWork, create_skills):
        logic = OrderQueryService(uow=init_uow)
        skill_id = create_skills.id
        result = await logic.post_in_db(skill_id=skill_id, description="Test description")
        
        assert isinstance(result, bool)


class TestSkill:
    async def test_add_raise(self, init_uow: UnitOfWork, create_skills):
        logic = SkillsServiceORM(uow=init_uow)
        with pytest.raises(SkillsError):
            async with init_uow as uow:
                await logic.add(
                    category=create_skills.category,
                    service=create_skills.service)

    async def test_add(self, init_uow: UnitOfWork):
        logic = SkillsServiceORM(uow=init_uow)
        categ = "Plumbing"
        serv = "replacement of internal building pipes"
        result = await logic.add(
            category=categ, service=serv)

        assert isinstance(result.id, int)
        assert result.category == "Plumbing"

    async def test_get_all_table(self, init_uow: UnitOfWork):
        async with init_uow as conn:
            conn.repo.skills_rep_orm.add(
                category="Категория 1",
                service="Услуга 1")
            conn.repo.skills_rep_orm.add(
                            category="Категория 2",
                            service="Услуга 2")
            conn.repo.skills_rep_orm.add(
                category="Категория 3",
                service="Услуга 3")
    
        logic = SkillsService(uow=init_uow)
        result = await logic.get_all_table()

        assert isinstance(result, list)
        assert isinstance(result[0], SkillsValid)
        assert isinstance(result[-1], SkillsValid)
        assert result[0].category == "Категория 1"
        assert result[0].service == "Услуга 1"
        assert result[-1].category == "Категория 3"
        assert result[-1].service == "Услуга 3"


class TestMasterSkills:
    async def test_add(self, init_uow: UnitOfWork, create_master, create_skills):
        logic = MasterSkillsQueryService(uow=init_uow)
        result = await logic.add(
            master_id=create_master.id, skill_id=create_skills.id)

        with pytest.raises(ValueError, match="Такая связь мастер-навык уже существует"):
            await logic.add(
                master_id=create_master.id, skill_id=create_skills.id)

        assert result is True


class TestMasterList:
    async def test_add(self, init_uow: UnitOfWork):
        logic = MasterListQueryService(uow= init_uow)
        result = await logic.create(
            name="Иван", status=StatusMasterCheck.FREE)

        assert isinstance(result, MastListValid)
        assert isinstance(result.name, str)
        assert result.status == StatusMasterCheck.FREE

    async def all_free_master(self, init_uow: UnitOfWork, create_master):
        logic = MasterListQueryService(uow= init_uow)
        result = await logic.all_free_master(status=StatusMasterCheck.FREE)
        
        assert isinstance(result, list)
        assert isinstance(result[0], MastListValid)

    async def test_all_table(self, init_uow: UnitOfWork, create_master):
        logic = MasterListQueryService(uow= init_uow)
        result = await logic.all_table()

        assert isinstance(result, list)
        assert isinstance(result[0], MasterListOut)





