from datetime import datetime

from app.models.models import MasterList, MasterSkills, Skills
from app.models.enum_model import StatusMasterCheck, StatusOrders
from app.shemas.shemas import MasterListAllValid, OrderValid, SkillsValidNoID
import pytest


class TestAddMethodRepo:
    """
    Тестируемые методы вставки (insert) новых строк в БД.
    """
    @pytest.mark.asyncio
    async def test_add_master(self, asession, repo):
        """ Метод add_master для таблицы MasterList """
        async with asession.begin_nested():
            print(f'ID SESSION {id(asession)}')
            req = repo.master_list.add_master(name="Test_name", status=StatusMasterCheck.FREE)
        assert req.name == "Test_name"
        assert req.id is not None
        assert req.status == StatusMasterCheck.FREE


    @pytest.mark.asyncio
    async def test_add_skill(self, asession, repo):
        """ Метод add для таблицы Skills """
        async with asession.begin_nested():
            res = repo.skills_rep_orm.add(category="Test_categ", service="Test_serv")

        assert res.id is not None
        assert res.category == "Test_categ"
        assert res.service == "Test_serv"


    @pytest.mark.asyncio
    async def test_add_skills_master(self, asession, repo, one_master, one_skill):
        """ Метод add_skills для таблицы MasterSkills """
        async with asession.begin_nested():
            res = repo.master_skills_orm.add_skills(master_id=one_master.id, skill_id=one_skill.id)

        assert res.master_id > 0
        assert res.skill_id > 0

    @pytest.mark.asyncio
    async def test_order_create(self, asession, repo, one_skill):
        async with asession.begin_nested():
            res = repo.order_repo_orm.create(skill_id=one_skill.id, description="Some task for master")

        assert res.id is not None
        assert isinstance(res.skill_id, int)
        assert res.description == "Some task for master"

class TestOtherMerhodRepo:
# ================================ MASTER LIST REPOSITORY ====================================
    @pytest.mark.asyncio
    @pytest.mark.parametrize("block_select", [True, False])
    async def test_get_inform(self, asession, repo, one_master, add_skills_master, block_select):
        async with asession.begin_nested():
            query = await repo.master_list.get_inform(master_id=one_master.id, block_select=block_select)
            await asession.refresh(query, attribute_names=["master_skills"]) # подгружаем реляционную связь, что бы orm-сессия выполнила запрос.
            res = MasterListAllValid.model_validate(query)
        
        assert res.name == "Test_name"
        assert res.status == StatusMasterCheck.FREE
        assert isinstance(res.master_skills, list)
        assert isinstance(res.master_skills[0].master_id, int)

    @pytest.mark.asyncio
    async def test_search(self, asession, repo, one_master):
        async with asession.begin_nested():
            res = await repo.master_list_core.search(status=StatusMasterCheck.FREE)

        assert isinstance(res[0], MasterList)
        assert res[0].status in StatusMasterCheck

    @pytest.mark.asyncio
    async def test_all_info(self, asession, repo, one_master, add_skills_master):
        async with asession.begin_nested():
            res = await repo.master_list_core.all_info()

        result = res[0]
        assert result.status in StatusMasterCheck
        assert isinstance(result, MasterList)
        assert isinstance(result.master_skills[0], MasterSkills)
        assert isinstance(result.master_skills[0].skills.category, str)

# ================================ SKILLS REPOSITORY ====================================

    @pytest.mark.asyncio
    async def test_exists_or_not(self, asession, repo, one_skill):
        async with asession.begin_nested():
            res = await repo.skills_rep.exists_or_not(category="Test_categ", service="Test_serv")

        assert isinstance(res, bool)
        assert res is True

    @pytest.mark.asyncio
    async def test_get_skill_from_db(self, asession, repo, one_skill):
        async with asession.begin_nested():
            res = await repo.skills_rep.get_skill_from_db(category="Test_categ", service="Test_serv")

        assert res is not None
        assert isinstance(res, Skills)

    @pytest.mark.asyncio
    async def test_all_table(self, asession, repo, one_skill):
        async with asession.begin_nested():
            res = await repo.skills_rep.all_table()

        assert res is not None
        assert isinstance(res, list)
        assert isinstance(res[0], Skills)
        assert res[0].category == "Test_categ"

# ================================ MASTER SKILL REPOSITORY ====================================

    @pytest.mark.asyncio
    async def test_quick_check_existence(self, asession, repo, one_skill, one_master, add_skills_master):
        async with asession.begin_nested():
            res = await repo.master_skills.quick_check_existence(master_id=one_master.id, skill_id=one_skill.id)

        assert isinstance(res, bool)
        assert res is True

# ================================ ORDERS REPOSITORY ====================================

    @pytest.mark.asyncio
    @pytest.mark.parametrize("block_select", [True, False])
    async def test_order_get_inform(self, asession, repo, one_order, block_select):
        async with asession.begin_nested():
            query = await repo.order_repo_orm.get_inform(order_id=one_order.id, block_select=block_select)
            await asession.refresh(query, attribute_names=["orders_skills"]) # подгружаем реляционную связь, что бы orm-сессия выполнила запрос.
            res = OrderValid.model_validate(query)
        
        assert isinstance(res.orders_skills, SkillsValidNoID)
        assert isinstance(res.orders_skills.category, str)
        assert isinstance(res.created_at, datetime)
        assert res.status in StatusOrders

    @pytest.mark.asyncio
    async def test_fast_fast_chek(self, asession, repo, one_order):
        async with asession.begin_nested():
            query = await repo.order_repo.fast_chek(order_id=one_order.id)

        assert query is not None
        assert isinstance(query, bool)

    @pytest.mark.asyncio
    async def test_fast_chek_new_order(self, asession, repo, one_order, one_skill):
        async with asession.begin_nested():
            query = await repo.order_repo.fast_chek_new_order(skill_id=one_skill.id, description="Some string")

        assert query is not None
        assert isinstance(query, bool)
        assert query is True
