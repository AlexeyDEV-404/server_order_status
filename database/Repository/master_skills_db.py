
def insert_master_skill(connect, master_id, skill_id):
    cursor = connect.cursor()
    cursor.execute("""INSERT INTO masters_skills(
                   master_id,
                   skill_id
                   ) VALUES (?, ?)""", (master_id, skill_id))
    
    return cursor.lastrowid

def select_table_masters_skills(connect):
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM masters_skills")
    return cursor.fetchall()

def select_masters_skills(connect, master_id):
    cursor = connect.cursor()
    cursor.execute("""SELECT * FROM masters_skills WHERE master_id = ?""", (master_id,))
    result = cursor.fetchall()
    return result

def join_search_master(connect, category, service): # Поиск мастера по необходимой услуге
    cursor = connect.cursor()
    cursor.execute("""
        SELECT m.id_master, m.name
        FROM master_list AS m
        JOIN masters_skills ms ON m.id_master = ms.master_id
        JOIN skills s ON ms.skill_id = s.id_skill
        WHERE s.category = ? 
        AND s.services = ?
        AND m.status = "FREE"
        """, (category, service))
    rows = cursor.fetchall()
    return rows
    
def join_display_master_skills(connect): # Отображение всех мастеров
    cursor = connect.cursor()
    cursor.execute("""
        SELECT m.name, s.category, s.service, m.status
        FROM master_list AS m
        JOIN master_skills AS ms ON ms.master_id = m.id_master
        JOIN skills AS s ON ms.skill_id = s.id_skill
                  """)
    rows = cursor.fetchall()
    return rows