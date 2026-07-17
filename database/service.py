from database.doman_rules import chek_value_master_order_free
from SQLAlchemy_work_db.enusm import StatusMasterCheck, StatusOrders
from app.api.pydantic_ import TableMasterSkills
from fastapi import HTTPException

from sqlalchemy.exc import (IntegrityError,
                            NoResultFound,
                            MultipleResultsFound,
                            SQLAlchemyError)

from app.api.pydantic_ import TableOrders
from app.api.deps import Repository


class Service:
    def __init__(self, repo: Repository):
        self.repo = repo

    async def server_order_create_new(
            self, category: str, service: str, description: str):
        """ Создаем новый заказ."""
        add = await self.repo.OrderRepo.add_order(
            category=category, service=service, description=description,
            status=StatusOrders.NEW
        )
        await self.repo.db.commit()
        return add

    async def server_order_master_assinged(self, masterID: int, orderID: int):
        """ Проверяем мастера, закреплен он за выполнением заказа. Проверяем,
        если статус у мастера BUSY, падаем с ошибкой. Если прошли проверки,
        меняем статус у заказа на 'ASSINGED'. Закрепляем мастера, за заказом.
        Меняем статус у мастера на 'BUSY'. Проверяем что изменение внесены,
        rowcount > 1, если нет, падаем с ошибкой."""
        master_count = await self.repo.OrderRepo.master_chek_order_count(
            master_id=masterID)
        chek_value_master_order_free(master_count)

        check_status_per_craftsman = await (
            self.repo.MastListRep.
            what_is_the_status(id=masterID)
        )
        chek_value_master_order_free(check_status_per_craftsman)

        await self.repo.OrderRepo.assinged_order(order_id=orderID)

        try:
            result = await self.repo.OrderRepo.specific_order(order_id=orderID)
        except SQLAlchemyError as e:
            raise SQLAlchemyError(
                f'Ошибка запроса на уровне SQLAlchemy. Текст ошибка - {e}.')
        else:
            if not result:
                raise ValueError(f'Заказ с ID {orderID} не найден')

        if result.status != "ASSINGED":
            await self.repo.db.rollback()
            raise ValueError((
                f"Ошибка: полученное значение {result.status}"
                "не соответствует ожидаемому ASSINGED."))

        mast_ord = await self.repo.OrderRepo.update_master_order(
            master_id=masterID, order_id=orderID)

        if mast_ord is None:
            await self.repo.db.rollback()
            raise ValueError("Ошибка: мастер не назначен за заказ.")

        update_status_in_db = await (
            self.repo.MastListRep.update_busy_status_master(id=masterID))
        if update_status_in_db != StatusMasterCheck.BUSY:
            await self.repo.db.rollback()
            raise ValueError(
                f"Ошибка: полученное значение {update_status_in_db}"
                "не соответствует ожидаемому BUSY.")

        await self.repo.db.commit()
        return TableOrders.model_validate(result)

    async def server_order_in_progress(self, orderID: int):
        """ Переводчи статус заказа с ASSINGED в IN_PROGRESS. """
        result = await self.repo.OrderRepo.in_progress_orders(order_id=orderID)
        if result is None:
            raise ValueError(
                "Ошибка, рельзутат None или неверный статус заказа.")
        await self.repo.db.commit()
        return result

    async def server_order_complet(self, orderID: int):
        """ Переводим заказ в статус "Выполнено" и освобождаем мастера,
        переводим его статус с "BUSY" на "FREE"  """
        order = await self.repo.OrderRepo.complete_order(order_id=orderID)
        if order is None:
            raise ValueError(
                "Ошибка запоса: не удалось перевести значение в статус "
                "COMPLETED. БД вернула None.")
        if order.master is None:
            raise HTTPException(
                status_code=404, detail="Ошибка: недопустимое значение None "
                "для поля master в заказе")
        master = await (
            self.repo.MastListRep
            .update_free_status_master(id=order.master)
        )
        if master != StatusMasterCheck.FREE:
            raise ValueError(f"Ошибка: поченное значение {master} не"
                             f"соответствует ожидаемому "
                             f"{StatusMasterCheck.FREE}.")
        await self.repo.db.commit()
        return order

    async def server_display_master_skills(self):
        """ Какими навыками работ обладает мастер. """
        result = await (
            self.repo.MastSkillsRep.informarion_about_craftsmen_orm())
        if result == []:
            raise ValueError("Error: response cannot be empty")
        return result

    async def server_specific_order(self, orderID: int):
        """ Поиск заказа по ID. """
        result = await (
            self.repo.OrderRepo
            .specific_order(order_id=orderID)
        )
        if result is None:
            raise ValueError(f"Заказ с ID {orderID} не найден")
        return TableOrders.model_validate(result)

    async def server_all_orders(self):
        """ Показать всю таблицу с заказами. """
        orders = await self.repo.OrderRepo.all_orders()
        x = [TableOrders.model_validate(order) for order in orders]
        if orders == []:
            raise ValueError("Error: response cannot be empty")
        return x

    async def server_search_master(self, category: str, service: str):
        """ Ищем всех мастеров, которую предостовляют услугу. """
        result = await (
            self.repo.MastSkillsRep
            .search_master(category=category, service=service))
        if result == []:
            raise ValueError("Данные отсутствуют")
        return [{"id": r.id, "name": r.name} for r in result]

    async def server_services(self):
        """ Список выполняемых работ."""
        results = await self.repo.SkillsRepo.select_works()
        if results == []:
            raise ValueError("Данные отсутствуют")
        return [{"category": r[0], "service": r[1].split(", ")}
                for r in results]

    async def server_cancel_order(self, orderID):
        """ Отмена заказа с статусом "NEW". """
        order = await self.repo.OrderRepo.specific_order(orderID)
        if order.status != "NEW":
            raise ValueError(
                "Ошибка: отменить можно только заказ с статусом 'NEW'")
        result = await self.repo.OrderRepo.cancel_order(order_id=orderID)
        await self.repo.db.commit()
        return result

    async def server_delete_order(self, orderID):
        """ Удаляем заказ по id и взвращаем str-уведомление
          про успешное удаление этого заказа."""
        order = await self.repo.OrderRepo.specific_order(orderID)
        if order:
            result = await self.repo.OrderRepo.delete_order(orderID)
            await self.repo.db.commit()
            return f"Заказ с ID {result} успешно удален."
        else:
            raise ValueError("Заказа не существует.")

    async def server_add_master_in_db(self, name, status: StatusMasterCheck):
        """ Добавляет в таблицу нового мастера. """
        try:
            result = await self.repo.MastListRep.add(name=name, status=status)
            await self.repo.db.commit()
            return result
        except NoResultFound:
            raise NoResultFound(
                "Ошика: отсутствует результат запроса. "
                "Адрес ошибки: server.py::server_add_master_in_db")
        except MultipleResultsFound:
            raise MultipleResultsFound(
                "Ошика: недопустимый результат, метод вернул больше одного "
                "значения. Адрес ошибки: server.py::server_add_master_in_db")

    async def server_master_info(self, id):
        """ Возвращает строку про мастера. id должен соответствовать
        текущему мастеру, который есть в БД."""
        result = await self.repo.MastListRep.master_info(id)
        if result is None or result == []:
            raise TypeError("Ошибка: Пустой результат")
        return result

    async def server_add_master_skills(
            self,
            master_id: int,
            skill_id: int) -> TableMasterSkills:
        """
        Серверный слой: Вставляем новый навык мастеру
        в таблицу MasterSkills
        """
        try:
            result = await (
                self.repo.MastSkillsRep
                .add_master_skills(master_id=master_id, skill_id=skill_id))
            await self.repo.db.commit()
            return TableMasterSkills.model_validate(result)
        except IntegrityError as e:
            await self.repo.db.rollback()
            if "duplicate key" in str(e.orig):
                raise ValueError("Навык уже существует")
            else:
                raise ValueError("Ошибка целостности данных")

    async def server_all_table(self):
        """ Возвращает всю таблицу навыков мастеров."""
        results = await self.repo.MastSkillsRep.all_table()
        if results is None:
            raise ValueError("Error: response cannot be empty")
        return results

    async def server_insert_skill(self, category, service):
        """ Добавляем строку в таблицу со всеми навыками """
        try:
            result = await (
                self.repo.SkillsRepo
                .insert_skill(category=category, service=service))
            await self.repo.db.commit()
            return result
        except IntegrityError as e:
            await self.repo.db.rollback()
            f"Ошибка - {e}"
            raise ValueError("Error: duplicate data")
