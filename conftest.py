import pytest, sqlite3
from app.main import app
from fastapi.testclient import TestClient
from database import service
from database.Repository import master_skills_db, skills_db, master_list_db, orders_db
from datetime import datetime
from sqlalchemy import create_engine
from SQLAlchemy_work_db.engine_and_models import Base, sessionmaker


@pytest.fixture
def db():
    connect = sqlite3.connect(":memory:", check_same_thread=False)
    connect.row_factory = sqlite3.Row
    with open("database/schema.sql", "r") as f:
        connect.executescript(f.read())
    yield connect
    connect.close()

@pytest.fixture
def SQLALchemy_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def client_app():
    return TestClient(app)


@pytest.fixture
def order_one(db):
    return orders_db.add_order(status="NEW", created_at=str(datetime.now()), connect=db, category="Сантехника", services="замена труб", description="Протечка")

@pytest.fixture
def add_master_and_order_assinged(monkeypatch, db, order_one):
    monkeypatch.setattr("database.service.connect_db", lambda: db)
    id_master = master_list_db.add_master(connect=db, name="Андрей")
    service.server_order_master_assinged(masterID=id_master, id_order=order_one)
    return {"order" : order_one,  "id_master": id_master}

@pytest.fixture
def order_in_progress(add_master_and_order_assinged):
    order_assinged = add_master_and_order_assinged["order"]
    service.server_order_in_progress(id_order=order_assinged)
    return add_master_and_order_assinged

@pytest.fixture
def master(db):
    return master_list_db.add_master(connect=db, name="Андрей")


