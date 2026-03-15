import pytest, sqlite3
from database.Repository.orders_db import add_order, specific_order, table_all_orders, assinged_order, cancel_order, complete_order, in_progress_orders
from datetime import datetime
from database.Repository.master_list_db import add_master


def test_add_order(db):
    result = add_order(connect=db,
        category="Диагностика и безопасность",
        services="Поиск утечек тока",
        description="Слишком много накручивает счетчик, при реальном потребелнии в 2 раза меньше",
        status="NEW",
        created_at=str(datetime.now()),
        master=None)
    assert result > 0
    
def test_specific_order(db):
    id = add_order(connect=db,
        category="Диагностика и безопасность",
        services="Поиск утечек тока",
        description="Слишком много накручивает счетчик, при реальном потребелнии в 2 раза меньше",
        status="NEW",
        created_at=str(datetime.now()),
        master=None)

    result = specific_order(connect=db, id_order=id)

    assert result is not None
    assert result["category"] == "Диагностика и безопасность"
    assert result["service"] == "Поиск утечек тока"

def test_table_all_orders(db):
    add_order(connect=db, category="Сантехника", services="Замена труб", description="Течёт труба под раковиной", status="NEW", created_at=str(datetime.now()), master=None)
    add_order(connect=db, category="Электрика", services="Замена розетки", description="Искрит розетка на кухне", status="NEW", created_at=str(datetime.now()), master=None)
    add_order(connect=db, category="Диагностика", services="Проверка проводки", description="Мигает свет в комнате", status="NEW", created_at=str(datetime.now()), master=None)

    result = table_all_orders(db)
    assert len(result) == 3

def test_assinged_order(db):
    id = add_order(connect=db, category="Сантехника", services="Замена труб", description="Течёт труба под раковиной", status="NEW", created_at=str(datetime.now()), master=None)
    assinged_order(id_order=id, connect=db)
    check_result = specific_order(connect=db, id_order=id)

    assert check_result is not None
    assert check_result["status"] == "ASSINGED"

def test_complete_order(db):
    add_master(Name="Сергей", connect=db)
    id = add_order(connect=db, category="Сантехника", services="Замена труб", description="Течёт труба под раковиной", status="NEW", created_at=str(datetime.now()), master=1)

    assinged_order(id_order=id, connect=db)
    in_progress_orders(connect=db, id_order=id)
    complete_order(connect=db, id_order=id)
    check_result = specific_order(connect=db, id_order=id)
    print(check_result)

    assert check_result is not None
    assert check_result["status"] == "COMPLETED"


def test_cancel_order(db):
    id = add_order(connect=db, category="Сантехника", services="Замена труб", description="Течёт труба под раковиной", status="NEW", created_at=str(datetime.now()), master=None)
    cancel_order(connect=db, id_order=id)
    check_result = specific_order(connect=db, id_order=id)

    assert check_result is not None
    assert check_result["status"] == "CANCEL"



