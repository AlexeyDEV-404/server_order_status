from database.Repository.orders_db import add_order, specific_order, table_all_orders, assinged_order,update_master_order, in_progress_orders, complete_order, master_chek_order_count, cancel_order
from app.core.business_logic import datetime_now
from database.doman_rules import rowcount_examinator, chek_fetchone_master_order_count, chek_fetchone_master_order_free
from database.Repository.master_list_db import update_busy_status_master, updete_free_status_master, status_select_master
from database.Repository.master_skills_db import join_display_master_skills, join_search_master
from database.Repository.skills_db import select_works
import sqlite3


DATA_BASE = "database/DATABASE.db"
def connect_db():
    return sqlite3.connect(DATA_BASE)
# Тест написан
def server_order_create_new(category: str, services: str,  description: str):
    with connect_db() as connect:
        add = add_order(connect=connect, category=category, services=services, description=description, status="NEW", created_at=datetime_now())
        rowcount_examinator(rowcount=add)
    return "Заказ создан и сохранен в базу данных"
# Тест написан
def server_order_master_assinged(masterID: int, id_order: int): # Назначаем мастера на заказ, меняем статус 
    with connect_db() as connect:
        master_chek_1 = master_chek_order_count(connect=connect, id_master=masterID) # Выводим инф., назначен ли мастер
        chek_fetchone_master_order_count(master_chek_1) # Проверка, назначен ли мастер.
        master_chek_2 = status_select_master(id_master=masterID, connect=connect) # Смотрим статус мастера
        chek_fetchone_master_order_free(master_chek_2) # Проверяем статус мастера
        result = assinged_order(connect=connect, id_order=id_order) # Переводи заказ в статус assigned (назначенный)
        update_master_order(connect=connect, id_order=id_order, id_master=masterID) # Обновляем поле master в таблице orders (заказы)
        master_buse = update_busy_status_master(id_master=masterID, connect=connect) # переводим статус мастера (табл. master_list - список всех мастеров) в BUSY-занятый и проверяем что он FREE (свободный)
        rowcount_examinator(master_buse) # Проверка, что "master_buse = update_busy_status_master" прошел успешно.
    return result
# Тест написан
def server_order_in_progress(id_order): # Заказ в процессе выполнения
    with connect_db() as connect:
        in_progress_orders(connect=connect, id_order=id_order)
# Тест написан
def server_order_complet(masterID: int, id_order: int): # Перевести заказ в статус "выполнен" (complet)
    with connect_db() as connect:
        order = complete_order(connect=connect, id_order=id_order)
        rowcount_examinator(order)
        master = updete_free_status_master(id_master=masterID, connect=connect)
        rowcount_examinator(master)
# Тест написан
def server_display_master_skills(): # Какими навыками работ обладает мастер
    with connect_db() as connect:
        result = join_display_master_skills(connect)
    return result
# тест написан
def server_specific_order(id_order: int): # Найти указанный заказ № id_order
    with connect_db() as connect:
        result = specific_order(connect=connect, id_order=id_order)
    return result
# Тест написан
def server_all_orders(): # Таблица всех заказов что есть в базе данных
    with connect_db() as connect:
        result = table_all_orders(connect)
    return result
# Тест написан
def server_search_master(category, service): # Поиск мастера, по нужному типу работы.
    with connect_db() as connect:
        result = join_search_master(connect=connect, category=category, service=service)
    return result
# Тест написан
def server_services(): #Список выполняемых работ
    with connect_db() as connect:
        result = select_works(connect)
    return result
# Тест написан
def server_cancel(id_order): # Отмена заказа
    with connect_db() as connect:
        result = cancel_order(connect=connect, id_order=id_order)
    return result
