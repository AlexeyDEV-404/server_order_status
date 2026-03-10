import sqlite3

DATA_BASE = "database/DATABASE.db"

def create_table_order(connect):
    cursor = connect.cursor()
    cursor.execute("""
       CREATE TABLE IF NOT EXISTS orders(
                   id_order INTEGER PRIMARY KEY AUTOINCREMENT,
                   category TEXT NOT NULL,
                   service TEXT NOT NULL,
                   description TEXT NOT NULL,
                   status TEXT NOT NULL CHECK(status IN ("NEW", "ASSINGED", "IN_PROGRESS", "DONE", "CANCELLED")),
                   created_at TEXT NOT NULL,
                   master INTEGER) 
    """)

def add_order(connect, category: str, services: str, description: str, status: str, created_at: str, master=None):
    cursor = connect.cursor()
    cursor.execute("""INSERT INTO orders(
        category,
        service,
        description,
        status,
        created_at, 
        master
        )
        VALUES(?, ?, ?, ?, ?, ?)
        """, (
            category,
            services,
            description,
            status,
            created_at,
            master
            ))
    result = cursor.lastrowid
    return result

def table_all_orders(connect): # Вся таблица
    connect.row_factory = sqlite3.Row
    cursor = connect.cursor()
    cursor.execute("""SELECT * FROM orders""")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

def specific_order(connect, id_order: int): # конкретная строка таблицы
    connect.row_factory = sqlite3.Row
    cursor = connect.cursor()
    cursor.execute("""SELECT * FROM orders WHERE id_order = ?""", (id_order,))
    result = cursor.fetchone()
    return dict(result) if result else None

def master_chek_order(connect, id_master):
    cursor = connect.cursor()
    cursor.execute("""SELECT COUNT(*) 
                   FROM orders 
                   WHERE master = ?
                   AND status = 'IN_PROGRESS'""", (id_master))
    return cursor.fetchone()[0]
    
def update_master_order(connect, id_master: int, id_order): #Обновление поля мастера
    cursor = connect.cursor()
    cursor.execute("""UPDATE orders 
                   SET master = ?  
                   WHERE id_order = ?
                   """, (id_master, id_order))
    return cursor.rowcount
    
def delete_order(connect, id_delete: int): # Удаление данных заказа.
    cursor = connect.cursor()
    cursor.execute("""DELETE FROM orders WHERE id_order = ?""", (id_delete,))
    return cursor.rowcount
    
def assinged_order(connect, id_order: int): # ASSINGED - мастер для заказа найден
    cursor = connect.cursor()
    cursor.execute("""UPDATE orders
                   SET status = 'ASSINGED'
                   WHERE status = 'NEW'
                   AND id_order = ?""", (id_order,))
    return cursor.rowcount

def in_progress_orders(connect, id_order: int):
    cursor = connect.cursor()
    cursor.execute("""UPDATE orders
                   SET status = 'IN_PROGRESS'
                   WHERE status = 'ASSINGED'
                   AND id_order = ?
                   AND master > 0""", (id_order,))
    return cursor.rowcount

def complete_order(connect, id_order: int):
    cursor = connect.cursor()
    cursor.execute("""UPDATE orders
                   SET status = 'COMPLETED', master = 0
                   WHERE status = 'IN_PROGRESS'
                   AND id_order = ?
                   """, (id_order,))
    return cursor.rowcount

def cancel_order(connect, id_order: int):
    cursor = connect.cursor()
    cursor.execute("""UPDATE orders
                   SET status = 'CANCEL'
                   WHERE  status = 'NEW'
                   AND id_order = ?""", (id_order,))
    return cursor.rowcount


