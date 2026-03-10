
def works_tabel(connect):
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS skills(  
                            id_skill INTEGER PRIMARY KEY AUTOINCREMENT
                            category TEXT,
                            services TEXT,
                            UNIQUE (category, services)
                             )""")
    
def insept_works(connect, category, service):
    cursor = connect.cursor()
    cursor.execute("""
                   INSERT INTO skills(
                   category,
                   services)
                   VALUES (?, ?)
                   ON CONFLICT (category, services)
                   DO NOTHING
                   """, (category, service))
    return cursor.lastrowid


def select_works(connect):
    cursor = connect.cursor()
    cursor.execute("""SELECT * FROM skills""")
    return cursor.fetchall()
