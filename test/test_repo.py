import pytest
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.core.unit_of_work import UnitOfWork
from app.models.enum_model import StatusMasterCheck
from app.models.models import MasterList, Orders, Skills


class TestOrderRep:
    """
    Класс для тестирования репозитория: order_rep.py
    """
    @pytest.mark.parametrize(
            'description', [
                ("description abaot service"),
                pytest.param(None, marks=pytest.mark.xfail(raises=IntegrityError)), # noqa
                pytest.param(1, marks=pytest.mark.xfail(raises=DBAPIError)),
                ]
            )
    async def test_create_order(
            self, create_skills, init_uow: UnitOfWork, description,
            ):
        """
        Тестируемые методы: create, fast_chek_new_order.
        Описание:
            create -> создание заказа происходит верно, передача неверных
                типов данных в поля вызывает ожидаемую ошибку
            fast_chek_new_order -> проверка существования заказа в БД
                (аналогичен SELECT 1 ...)
        """
        async with init_uow as uow:
            skills_id = create_skills.id
            ord = uow.repo.order_repo_orm.create(
                skill_id=skills_id, description=description)

        with pytest.raises(DBAPIError):
            async with init_uow as uow:
                uow.repo.order_repo_orm.create(
                    skill_id="skills_id", description=description) # Намеренно передан тип данных str # noqa # type: ignore

        async with init_uow as uow:
            result = await uow.repo.order_repo.fast_chek_new_order(
                skill_id=skills_id, description=description)
        assert result is True
        assert ord.description == "description abaot service"
        assert isinstance(ord.id, int)
        assert ord.skill_id == skills_id

    async def test_get_indorm_order(self, one_order, init_uow: UnitOfWork):
        """
        Тестируемый метод: get_inform.
        Описание: Проверка что метод возвращает информацию о заказе,
        а также тип данных соответствует ожидаемому.
        """
        async with init_uow as uow:
            await uow.session.flush()
            id = one_order.id
            get_order = await uow.repo.order_repo_orm.get_inform(
                order_id=id, block_select=False)

        assert isinstance(get_order, Orders)
        assert get_order.id == id
        assert get_order.description == "desriptor order."
        assert get_order.orders_skills.category == "Plumbing"
        assert get_order.orders_skills.service == "replacement of internal building pipes" # noqa

    async def test_fast_check(self, one_order, init_uow: UnitOfWork):
        """
        Тестируемый метод: fast_check.
        Описание: проверяем работоспособность самого метода, что он возвращает
        ожидаемое bool-значение
        """
        async with init_uow as uow:
            await uow.session.flush()
            id = one_order.id
            result = await uow.repo.order_repo.fast_chek(id)

        assert isinstance(result, bool)
        assert result is True


class TestSkillRep:
    """
    Класс для тестирования репозитория: skills_rep.py
    """
    @pytest.mark.parametrize("category, service", [
        ("Electrics", "rewiring in the kitchen"),
        pytest.param(
            "Electrics", 1, marks=pytest.mark.xfail(raises=DBAPIError)),
        pytest.param(
            1,  "rewiring in the kitchen",
            marks=pytest.mark.xfail(raises=DBAPIError)),
        pytest.param(
            "Electrics", None, marks=pytest.mark.xfail(raises=DBAPIError)),
        pytest.param(
            None,  "rewiring in the kitchen",
            marks=pytest.mark.xfail(raises=DBAPIError)),
    ])
    async def test_add(self, category, service, init_uow: UnitOfWork):
        async with init_uow as uow:
            result = uow.repo.skills_rep_orm.add(
                category=category, service=service)

        assert isinstance(result, Skills)
        assert result.category == "Electrics"
        assert result.service == "rewiring in the kitchen"

    async def test_add_unique(self, init_uow: UnitOfWork):
        """
        Тестируем нарушение правила уникальности (UNIQUE)
        """
        with pytest.raises(DBAPIError):
            async with init_uow as uow:
                uow.repo.skills_rep_orm.add(
                    category="Electrics", service="rewiring in the kitchen")
                uow.repo.skills_rep_orm.add(
                    category="Electrics", service="rewiring in the kitchen")

    async def test_exists_or_not_True(
        self, create_skills, init_uow: UnitOfWork
            ):

        async with init_uow as uow:
            result = await uow.repo.skills_rep.exists_or_not(
                category=create_skills.category,
                service=create_skills.service)

        assert isinstance(result, bool)
        assert result is True

    async def test_exists_or_not_False(
        self, init_uow: UnitOfWork
            ):

        async with init_uow as uow:
            result = await uow.repo.skills_rep.exists_or_not(
                category="Test",
                service="Test")

        assert isinstance(result, bool)
        assert result is False

    async def test_all_table(
        self, create_some_skills, init_uow: UnitOfWork
    ):
        async with init_uow as uow:
            result = await uow.repo.skills_rep.all_table()

        assert isinstance(result, list)
        assert isinstance(result[0], Skills)
        assert result[0].category == "Plumbing"
        assert result[0].service == "replacement of internal building pipes."
        assert result[-1].category == "Painting"
        assert result[-1].service == "wall painting"

    async def test_get_skill_from_db(
        self, create_skills, init_uow: UnitOfWork
    ):
        async with init_uow as uow:
            result = await uow.repo.skills_rep.get_skill_from_db(
                category=create_skills.category,
                service=create_skills.service
            )

        assert isinstance(result, Skills)
        assert result.category == create_skills.category


class TestMasterListRep:
    """
    Класс для тестирования репозитория: master_list_rep.py
    """
    async def test_add_master(
        self, init_uow: UnitOfWork
    ):
        async with init_uow as uow:
            result = uow.repo.master_list.add_master(
                name="Иван", status=StatusMasterCheck.FREE)

        with pytest.raises(DBAPIError):
            async with init_uow as uow:
                uow.repo.master_list.add_master(
                    name="Иван", status="test string")  # type: ignore

        assert isinstance(result, MasterList)
        assert result.name == "Иван"
        assert result.status == StatusMasterCheck.FREE

    async def test_get_inform(
        self, init_uow: UnitOfWork, create_master
    ):
        async with init_uow as uow:
            result = await uow.repo.master_list.get_inform(
                master_id=create_master.id, block_select=False
            )

        assert isinstance(result, MasterList)
        assert result.name == "Иван"

    async def test_search(
        self, init_uow: UnitOfWork, create_master
    ):
        async with init_uow as uow:
            result = await uow.repo.master_list_core.search(
                status=StatusMasterCheck.FREE)

        assert isinstance(result[0], MasterList)
        assert result[0].name == "Иван"

    async def test_all_info(
        self, init_uow: UnitOfWork, create_master, create_skills
    ):
        async with init_uow as uow:
            uow.repo.master_skills_orm.add_skills(
                master_id=create_master.id,
                skill_id=create_skills.id
            )
        async with init_uow as uow:
            result = await uow.repo.master_list_core.all_info()

        assert isinstance(result[0], MasterList)
        assert result[0].master_skills[0].skills.category == "Plumbing"
        assert result[0].master_skills[0].skills.service == "replacement of internal building pipes"  # noqa
        assert result[0].name == "Иван"
        assert result[0].status == StatusMasterCheck.FREE


class TestMasterSkillRep:
    """
    Класс для тестирования репозитория: master_skills.py
    """

    async def test_add_skills(
        self, init_uow: UnitOfWork, create_master, create_skills
    ):
        """
        Тестируемые методы: add_skills, quick_check_existence
        Описание: Проверка корректности работы этих методов.
        """
        async with init_uow as uow:
            result = uow.repo.master_skills_orm.add_skills(
                master_id=create_master.id,
                skill_id=create_skills.id
            )
        assert result.master_id == create_master.id
        assert result.skill_id == create_skills.id

        with pytest.raises(IntegrityError):
            async with init_uow as uow:
                uow.repo.master_skills_orm.add_skills(
                    master_id=999,
                    skill_id=999
                )
