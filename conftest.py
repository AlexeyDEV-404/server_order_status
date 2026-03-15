import pytest, sqlite3

@pytest.fixture
def db():
    connect = sqlite3.connect(":memory:")
    connect.row_factory = sqlite3.Row
    with open("database/schema.sql", "r") as f:
        connect.executescript(f.read())
    yield connect
    connect.close()
