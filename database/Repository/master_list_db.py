

def create_master(connect):
    cursor = connect.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS master_list(
        id_master INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        status TEXT CHECK(status in ("FREE", "BUSY"))
        )        
        """)
    
def add_master(connect, Name: str):
    cursor = connect.cursor()
    cursor.execute("""
        INSERT INTO master_list(
                   name,
                   status
                   )
        VALUES(?, ?)
        """, (
            Name, "FREE"
        ))
    return {"msg" : "Добавлен в таблицу мастеров"}

def status_select_master(connect, id_master):
    cursor = connect.cursor()
    cursor.execute("""
                   SELECT status FROM master_list WHERE id_master = ?
                   """, (id_master,))
    return cursor.fetchone()[0]

def select_master(connect, id_master):
    cursor = connect.cursor()
    cursor.execute("""
                   SELECT * FROM master_list WHERE id_master = ?
                   """, (id_master,))
    return cursor.fetchone()

def update_busy_status_master(connect, id_master):
    cursor = connect.cursor()
    cursor.execute("""
                   UPDATE master_list SET status = "BUSY" WHERE status = "FREE" AND id_master = ?
                   """, (id_master,))
    result = cursor.rowcount
    return result
    
def updete_free_status_master(connect, id_master):
    cursor = connect.cursor()
    cursor.execute("""UPDATE master_list SET status = "FREE" WHERE status = "BUSY" AND id_master = ?""", (id_master,))
    return cursor.rowcount