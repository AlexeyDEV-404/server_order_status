
def creat_master_skills(connetc):
    cursor = connetc.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS masters_skills(
        master_id INTEGER NOT NULL,
        skill_id INTEGER NOT NULL,
        PRIMARY KEY(master_id, skill_id),
        FOREIGN KEY (master_id) REFERENCES master_list (id_master) ON DELETE CASCADE,
        FOREIGN KEY (skill_id) REFERENCES works(id_works) ON DELETE CASCADE)""")
    
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

def join_search_master(connect, category, service):
    cursor = connect.cursor()
    cursor.execute("""
        SELECT m.id_master, m.name
        FROM master_list AS m
        JOIN master_skills ms ON m.id_master = ms.id_master
        JOIN skills s ON ms.skill_id = s.id_skill
        WHERE s.category = ? 
        AND s.service = ?
        AND m.status = "FREE"
        """, (category, service))
    rows = cursor.fetchall()
    return rows
    
def join_display_master_skills(connect):
    cursor = connect.cursor()
    cursor.execute("""
                  SELECT m.name, s.category, s.service, m.status
                  FROM master_list AS m
                  JOIN master_skills AS ms ON ms.master_id = m.id_master
                  JOIN skills AS s ON ms.skill_id = s.id_skill
                  """)
    rows = cursor.fetchall()
    return rows