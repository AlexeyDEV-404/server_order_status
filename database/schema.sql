PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS master_list(
        id_master INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        status TEXT CHECK(status in ("FREE", "BUSY"))
        );

CREATE TABLE IF NOT EXISTS masters_skills(
        master_id INTEGER NOT NULL,
        skill_id INTEGER NOT NULL,
        PRIMARY KEY(master_id, skill_id),
        FOREIGN KEY (master_id) REFERENCES master_list (id_master) ON DELETE CASCADE,
        FOREIGN KEY (skill_id) REFERENCES skills(id_skill) ON DELETE CASCADE);

CREATE TABLE IF NOT EXISTS orders(
        id_order INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        service TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ("NEW", "ASSINGED", "IN_PROGRESS", "COMPLETED", "CANCEL")),
        created_at TEXT NOT NULL,
        master INTEGER,
        FOREIGN KEY (master) REFERENCES master_list(id_master) ON DELETE SET NULL);

CREATE TABLE IF NOT EXISTS skills(  
        id_skill INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        services TEXT,
        UNIQUE (category, services)
            )   
    