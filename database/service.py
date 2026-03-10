from database.Repository.orders_db import add_order, specific_order, table_all_orders, assinged_order,update_master_order, in_progress_orders, complete_order, master_chek_order
from app.core.business_logic import datetime_now
from database.doman_rules import rowcount_examinator, chek_fetchone_master_order
from database.Repository.master_list_db import update_busy_status_master, updete_free_status_master, status_select_master
from database.Repository.master_skills_db import join_display_master_skills
import sqlite3


DATA_BASE = "database/DATABASE.db"
def connect_db():
    return sqlite3.connect(DATA_BASE)

def server_order_create_new(category: str, services: str,  description: str):
    with connect_db() as connect:
        add = add_order(connect=connect, category=category, services=services, description=description, status="NEW", created_at=datetime_now())
        rowcount_examinator(rowcount=add)
    return "Заказ создан и сохранен в базу данных"

def server_order_master_assinged(masterID: int, id_order: int):
    with connect_db() as connect:
        master_chek_1 = master_chek_order(connect=connect, id_master=masterID)
        chek_fetchone_master_order(master_chek_1)
        master_chek_2 = status_select_master(id_master=masterID, connect=connect)
        chek_fetchone_master_order(master_chek_2)
        assinged_order(connect=connect, id_order=id_order)
        update_master_order(connect=connect, id_order=id_order, id_master=masterID)
        master_buse = update_busy_status_master(id_master=masterID, connect=connect)
        rowcount_examinator(master_buse)

def server_order_in_progress(id_order):
    with connect_db() as connect:
        in_progress_orders(connect=connect, id_order=id_order)


def server_order_complet(masterID: int, id_order: int):
    with connect_db() as connect:
        order = complete_order(connect=connect, id_order=id_order)
        rowcount_examinator(order)
        master = updete_free_status_master(id_master=masterID, connect=connect)
        rowcount_examinator(master)




def server_display_master_skills():
    with connect_db() as connect:
        result = join_display_master_skills(connect)
    return result

def service_specific_order(id_order: int):
    with connect_db() as connect:
        result = specific_order(connect=connect, id_order=id_order)
    return result

def server_all_orders():
    with connect_db() as connect:
        result = table_all_orders(connect)
    return result







