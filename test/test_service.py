# pytest test/test_service.py::test_server_display_master_skills -v -s
# pytest test\test_service.py -v -s
 
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy import Row
from SQLAlchemy_work_db.engine_and_models import MasterList
from SQLAlchemy_work_db.enusm import StatusMasterCheck, StatusOrders
from sqlalchemy.exc import IntegrityError, MultipleResultsFound, NoResultFound, SQLAlchemyError

import pytest

from app.api.pydantic_ import TableInfAboutCraftsmen
from database.service import Service

@pytest.mark.asyncio
async def test_server_order_create_new():
    mok_repo = AsyncMock()
    mok_repo.OrderRepo = AsyncMock()
    mok_repo.OrderRepo.add_order.return_value = 123

    result = await Service(repo=mok_repo).server_order_create_new(category='Test' , service='Test' , description='Test')

    assert result == 123

    mok_repo.OrderRepo.add_order.assert_called_once()
    mok_repo.db.commit.assert_called_once()

class TestAssignMaster:
    """Все тесты для метода server_order_master_assinged."""

    @pytest.fixture(autouse=True)
    def setup(self, create_order_for_mocktest):
        """Общая настройка для всех тестов в классе."""
        self.mock_order = create_order_for_mocktest
        self.mock_order_repo = AsyncMock()
        self.mock_master_repo = AsyncMock()
        
        # Настройка базовых (успешных) return_value
        self.mock_order_repo.master_chek_order_count.return_value = None
        self.mock_order_repo.assinged_order.return_value = None
        self.mock_order_repo.update_master_order.return_value = 1
        self.mock_order_repo.specific_order.return_value = self.mock_order
        
        self.mock_master_repo.what_is_the_status.return_value = "FREE"
        self.mock_master_repo.update_busy_status_master.return_value = "BUSY"
        
        self.service = Service(
            repo=MagicMock(
                OrderRepo=self.mock_order_repo,
                MastListRep=self.mock_master_repo,
                db=AsyncMock()
            )
        )
    
    async def test_success(self):
        """Успешное назначение мастера на заказ."""
        self.mock_master_repo.update_busy_status_master.return_value = StatusMasterCheck.BUSY
        result = await self.service.server_order_master_assinged(masterID=2, orderID=1)
        assert result.status == 'ASSINGED'
        self.mock_order_repo.assinged_order.assert_called_once_with(order_id=1)
        self.mock_master_repo.update_busy_status_master.assert_called_once_with(id=2)

    async def test_master_has_active_order(self):
        """Мастер уже выполняет другой заказ (ошибка)."""
        self.mock_order_repo.master_chek_order_count.return_value = 1
        with pytest.raises(ValueError, match="Мастер выполняет заказ и не может быть назначен на другой."):
            await self.service.server_order_master_assinged(masterID=2, orderID=1)

    async def test_master_busy(self):
        """Статус мастера BUSY (ошибка)."""
        self.mock_master_repo.what_is_the_status.return_value = "BUSY"
        self.mock_order_repo.master_chek_order_count.return_value = None
        with pytest.raises(ValueError, match=r"Статус мастера BUSY \(занят\) и не может принять заказ\."):
            await self.service.server_order_master_assinged(masterID=2, orderID=1)

    async def test_order_not_found(self):
        """Заказ не найден (ошибка)."""
        self.mock_order_repo.specific_order.return_value = None
        with pytest.raises(ValueError, match='Заказ с ID 1 не найден'):
            await self.service.server_order_master_assinged(masterID=2, orderID=1)

    async def test_sqlalchemy_error(self):
        """Ошибка на уровне SQLAlchemy."""
        self.mock_order_repo.specific_order.side_effect = SQLAlchemyError("Алхим выдал ошибку.")
        with pytest.raises(SQLAlchemyError, match="Ошибка запроса на уровне SQLAlchemy. Текст ошибка - Алхим выдал ошибку."):
            await self.service.server_order_master_assinged(masterID=2, orderID=1)

    async def test_update_master_order_failed(self):
        """Не удалось назначить мастера (update вернул None)."""
        self.mock_order_repo.update_master_order.return_value = None
        with pytest.raises(ValueError, match="Ошибка: мастер не назначен за заказ."):
            await self.service.server_order_master_assinged(masterID=2, orderID=1)

    async def test_update_status_master_failed(self):
        """Не удалось обновить статус мастера (BUSY не был установлен)."""
        self.mock_master_repo.update_busy_status_master.return_value = "FREE"
        self.mock_master_repo.specific_order.return_value = "ASSINGED"
        with pytest.raises(ValueError, match="Ошибка: полученное значение FREE не соответствует ожидаемому BUSY."):
            await self.service.server_order_master_assinged(masterID=2, orderID=1)

@pytest.mark.asyncio
async def test_server_order_in_progress(create_order_for_mocktest):
    mock_order = AsyncMock()
    order = create_order_for_mocktest
    mock_order.in_progress_orders.return_value = order

    service = await Service(
        repo=MagicMock(OrderRepo=mock_order,
            db=AsyncMock())).server_order_in_progress(1)
    
    assert service.status == "ASSINGED"
    
@pytest.mark.asyncio
async def test_server_order_complet(create_order_for_mocktest):
    mock_MasterList = AsyncMock()
    mock_Order = AsyncMock()


    mock_tabel_order = create_order_for_mocktest
    mock_Order.complete_order.return_value = mock_tabel_order
    mock_MasterList.update_free_status_master.return_value = StatusMasterCheck.FREE

    result = await Service(repo=MagicMock(OrderRepo=mock_Order, MastListRep = mock_MasterList, db = AsyncMock())).server_order_complet(1)

    assert result.category == "Test_cat"
    assert result.status == "ASSINGED"

@pytest.mark.asyncio
async def test_server_display_master_skills():
    mock_masterskill = AsyncMock()

    mock_masterskill.informarion_about_craftsmen.return_value = [TableInfAboutCraftsmen(name="name", category="category", service="service", status="ASSINGED")]

    result = await Service(repo=AsyncMock(MastSkillsRep = mock_masterskill, db = AsyncMock())).server_display_master_skills()
    print(result, "====", result[0])
    assert result[0].status == "ASSINGED"

@pytest.mark.asyncio
async def test_server_specific_order_tru(create_order_for_mocktest):
    mock_order = AsyncMock()
    order = create_order_for_mocktest
    mock_order.specific_order.return_value = order

    result = await Service(repo=MagicMock(OrderRepo=mock_order, db = AsyncMock())).server_specific_order(order.id)
    assert result.status == "ASSINGED"
    assert result.category == "Test_cat"
    assert result.service == "Test_serv"

@pytest.mark.asyncio
async def test_server_specific_order_false():
    mock_order = AsyncMock()
    mock_order.specific_order.return_value = None

    with pytest.raises(ValueError, match="Заказ с ID 1 не найден"):
        await Service(repo=MagicMock(OrderRepo=mock_order, db = AsyncMock())).server_specific_order(1)
     
@pytest.mark.asyncio
async def test_server_all_orders_tru(create_order_for_mocktest):
    mock_order = AsyncMock()

    order = create_order_for_mocktest   
    mock_order.server_all_orders.return_value = order

    result = await Service(repo=MagicMock(OrderRepo=mock_order, db = AsyncMock())).server_all_orders()
    assert isinstance(result, list)
    
@pytest.mark.asyncio
async def test_server_all_orders_false():
    mock_order = AsyncMock()
    mock_order.all_orders.return_value = []

    with pytest.raises(ValueError, match="Error: response cannot be empty"):
        await Service(repo=MagicMock(OrderRepo=mock_order, db = AsyncMock())).server_all_orders()

@pytest.mark.asyncio
async def test_server_search_master_try():
    mock_masterskillsrepo = AsyncMock()
    mock_masterskillsrepo.search_master.return_value = [
    SimpleNamespace(id=1, name="name")
]
    result = await Service(repo=MagicMock(MastSkillsRep=mock_masterskillsrepo, db = AsyncMock())).server_search_master(category="Test_cat", service="Test_serv")

    assert result == [{"id": 1, "name": "name"}]

@pytest.mark.asyncio
async def test_server_search_master_false():
    mock_masterskillsrepo = AsyncMock()
    mock_masterskillsrepo.search_master.return_value = []
    
    with pytest.raises(ValueError, match="Данные отсутствуют"):
        await Service(repo=MagicMock(MastSkillsRep=mock_masterskillsrepo, db = AsyncMock())).server_search_master(category="Test_cat", service="Test_serv")

@pytest.mark.asyncio
async def test_server_services_try():
    mock_rep = AsyncMock()
    mock_rep.select_works.return_value = [("Test_cat", "Test_serv1, Test_serv2")]

    result = await Service(repo=MagicMock(SkillsRepo=mock_rep, db = AsyncMock())).server_services()

    assert result[0]["category"] == "Test_cat"
    assert result[0]["service"] == ['Test_serv1', 'Test_serv2']

@pytest.mark.asyncio
async def test_server_services_false():
    mock_rep = AsyncMock()
    mock_rep.select_works.return_value = []

    with pytest.raises(ValueError, match="Данные отсутствуют"):
        await Service(repo=MagicMock(SkillsRepo=mock_rep, db = AsyncMock())).server_services()

@pytest.mark.asyncio
async def test_server_cancel_order_try(create_order_for_mocktest):
    mock_rep = AsyncMock()
    order = create_order_for_mocktest
    order.status = "NEW"
    mock_rep.specific_order.return_value = order
    mock_rep.cancel_order.return_value = StatusOrders.CANCEL

    result = await Service(repo=MagicMock(OrderRepo=mock_rep, db=AsyncMock())).server_cancel_order(order.id)

    assert result == StatusOrders.CANCEL

@pytest.mark.asyncio
async def test_server_cancel_order_false(create_order_for_mocktest):
    mock_rep = AsyncMock()
    order = create_order_for_mocktest
    order.status = "RANDOM_STATUS"
    mock_rep.specific_order.return_value = order

    with pytest.raises(ValueError, match="Ошибка: отменить можно только заказ с статусом 'NEW'"):
        await Service(repo=MagicMock(OrderRepo=mock_rep, db=AsyncMock())).server_cancel_order(order.id)

@pytest.mark.asyncio
async def test_server_delete_order_order_try(create_order_for_mocktest):
    mock_rep = AsyncMock()
    order = create_order_for_mocktest
    mock_rep.specific_order.return_value = order
    mock_rep.delete_order.return_value = order.id


    result = await Service(repo=MagicMock(OrderRepo=mock_rep, db=AsyncMock())).server_delete_order(order.id)

    assert result == f"Заказ с ID {order.id} успешно удален."

@pytest.mark.asyncio
async def test_server_delete_order_order_false():
    mock_rep = AsyncMock()
    mock_rep.specific_order.return_value = None

    with pytest.raises(ValueError, match="Заказа не существует."):
        await Service(repo=MagicMock(OrderRepo=mock_rep, db=AsyncMock())).server_delete_order(1)

@pytest.mark.asyncio
async def test_server_add_master_in_db_try():
    mock_repo = AsyncMock()
    mock_repo.add.return_value = 1

    result = await Service(repo=MagicMock(MastListRep=mock_repo, db=AsyncMock())).server_add_master_in_db(name="Test_name", status=StatusMasterCheck.FREE)

    assert result == 1

@pytest.mark.asyncio
async def test_server_add_master_in_db_false_1():
    mock_repo = AsyncMock()
    mock_repo.add.side_effect = NoResultFound

    with pytest.raises(NoResultFound, match="Ошика: отсутствует результат запроса. Адрес ошибки: server.py::server_add_master_in_db"):
        await Service(repo=MagicMock(MastListRep=mock_repo, db=AsyncMock())).server_add_master_in_db(name="Test_name", status=StatusMasterCheck.FREE)

@pytest.mark.asyncio
async def test_server_add_master_in_db_false_2():
    mock_repo = AsyncMock()
    mock_repo.add.side_effect = MultipleResultsFound

    with pytest.raises(MultipleResultsFound, match="Ошика: недопустимый результат, метод вернул больше одного значения. Адрес ошибки: server.py::server_add_master_in_db"):
        await Service(repo=MagicMock(MastListRep=mock_repo, db=AsyncMock())).server_add_master_in_db(name="Test_name", status=StatusMasterCheck.FREE)

@pytest.mark.asyncio
async def test_server_master_info_try():
    mock_repo = AsyncMock()
    mock_repo.master_info.return_value = MasterList(name = "Nick", status = StatusMasterCheck.FREE)

    result = await Service(repo=MagicMock(MastListRep=mock_repo, db=AsyncMock())).server_master_info(1)
    assert result.name == "Nick"
    assert result.status == StatusMasterCheck.FREE

@pytest.mark.asyncio
async def test_server_master_info_false():
    mock_repo = AsyncMock()
    mock_repo.master_info.return_value = None

    with pytest.raises(TypeError, match="Ошибка: Пустой результат"):
        await Service(repo=MagicMock(MastListRep=mock_repo, db=AsyncMock())).server_master_info(1)

@pytest.mark.asyncio
async def test_server_add_master_skills_tru():
    mock_repo = AsyncMock()
    mock_repo.add_master_skills.return_value = {"master_id": 1, "skill_id": 1}
    result = await Service(repo=MagicMock(MastSkillsRep=mock_repo, db=AsyncMock())).server_add_master_skills(1, 1)

    assert result.master_id == 1
    assert result.skill_id == 1
  
@pytest.mark.asyncio
async def test_server_add_master_skills_false_1():
    mock_repo = AsyncMock()
    mock_repo.add_master_skills.side_effect = IntegrityError(statement="test", params={}, orig=Exception("duplicate key"))

    with pytest.raises(ValueError, match="Навык уже существует"):
        await Service(repo=MagicMock(MastSkillsRep=mock_repo, db=AsyncMock())).server_add_master_skills(1, 1)
    
@pytest.mark.asyncio
async def test_server_add_master_skills_false_2():
    mock_repo = AsyncMock()
    mock_repo.add_master_skills.side_effect = IntegrityError(statement="test", params={}, orig=Exception("some error"))

    with pytest.raises(ValueError, match="Ошибка целостности данных"):
        await Service(repo=MagicMock(MastSkillsRep=mock_repo, db=AsyncMock())).server_add_master_skills(1, 1)

@pytest.mark.asyncio
async def test_server_all_table_tru():
    mock_repo = AsyncMock()
    mock_repo.all_table.return_value = [(1, 1), (2, 1)]

    result = await Service(repo=MagicMock(MastSkillsRep=mock_repo, db=AsyncMock())).server_all_table()

    assert result == [(1, 1), (2, 1)]

@pytest.mark.asyncio
async def test_server_all_table_false():
    mock_repo = AsyncMock()
    mock_repo.all_table.return_value = None

    with pytest.raises(ValueError, match="Error: response cannot be empty"):
        await Service(repo=MagicMock(MastSkillsRep=mock_repo, db=AsyncMock())).server_all_table()

async def test_server_insert_skill_try():
    mock_repo = AsyncMock()
    mock_repo.insert_skill.return_value = 1

    result = await Service(repo=MagicMock(SkillsRepo=mock_repo, db=AsyncMock())).server_insert_skill(category="test_cat", service="test_service")

    assert result == 1

async def test_server_insert_skill_false():
    mock_repo = AsyncMock()
    mock_repo.insert_skill.side_effect = IntegrityError(statement="test", params={}, orig=Exception("some error"))

    with pytest.raises(ValueError, match="Error: duplicate data"):
        await Service(repo=MagicMock(SkillsRepo=mock_repo, db=AsyncMock())).server_insert_skill(category="test_cat", service="test_service")
    