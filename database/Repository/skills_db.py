
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
    cursor.execute("""SELECT category, GROUP_CONCAT(services, ', ') 
                    FROM skills
                   GROUP BY category
                   """)
    return cursor.fetchall()
