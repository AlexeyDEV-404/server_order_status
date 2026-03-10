from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent 
DATABASE = BASE_DIR.parent / "database"  / "DATABASE.db"
SCHEMA_PATH = BASE_DIR/ "schema.sql"

def init_db():
    with sqlite3.connect(DATABASE) as connect:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = f.read()
        
        connect.executescript(schema)
    return "Database initialized"

if __name__ == "__main__":
    init_db()
  