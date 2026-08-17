from app.models.models import Base
from sqlalchemy.exc import NoResultFound
from typing import TypeVar

T = TypeVar("T", bound=Base)


def chek_empty_request(stmt: T | None, id: int, tablename: str) -> T:
    """
    Получает на вход stmt -> принимает один объект, являющимися описаными
    моделями для создания таблицы в Базе Данных и проверяет по id что запись
    существует в указаной таблице и возвращает его.
    """
    if stmt is None:
        raise NoResultFound(
            f"Ошибка: Запрос с {id} в таблице {tablename} не найден.")
    return stmt


def chek_none_column(column):
    """
    Метод проверяет column (столбец) и выбрасывает
    TypeError если значение None.
    """
    if column is None:
        raise TypeError("Не допустимый тип данных.")
    return column
