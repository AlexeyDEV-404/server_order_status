from sqlalchemy import create_engine, String, Enum, ForeignKeyConstraint, UniqueConstraint, PrimaryKeyConstraint, func
from sqlalchemy.orm import DeclarativeBase, sessionmaker, mapped_column, Mapped
from pathlib import Path
from typing import Annotated
from SQLAlchemy_work_db.enusm import StatusMasterCheck, StatusOrders
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parents[0]
ROOT_DIRECTORY = BASE_DIR.parent
DB = BASE_DIR / "DATABASE.db"

driver = "pysqlite"
database_url = "sqlite"
url = f"{database_url}+{driver}:///{DB}"

engine = create_engine(url, echo=True)
SessionFactory = sessionmaker(bind=engine)


def get_db():
    with SessionFactory() as session:
        yield session
    


    
class Base(DeclarativeBase): pass
class BaseClass(Base):
    __abstract__ = True
    string_nullableF = Annotated[str, mapped_column(String(length=255), nullable=False)]
    string = Annotated[str, mapped_column(String(length=255))]

    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class MasterList(BaseClass):
    __tablename__ = "MasterList"

    name : Mapped[BaseClass.string_nullableF]
    status : Mapped[str] = mapped_column(Enum(StatusMasterCheck))


class MasterSkills(Base):
    __tablename__ = "MasterSkills"
    __table_args__ = (ForeignKeyConstraint((["master_id"]), ["MasterList.id"], ondelete="CASCADE"),
                      ForeignKeyConstraint(["skill_id"], ["Skills.id"], ondelete="CASCADE"),
                      PrimaryKeyConstraint("skill_id", "master_id"))
    
    master_id : Mapped[int] = mapped_column(nullable=False)
    skill_id : Mapped[int] = mapped_column(nullable=False)

class Skills(BaseClass):
    __tablename__ = "Skills"
    __table_args__ = (UniqueConstraint("category", "service"), )

    category : Mapped[BaseClass.string]
    service : Mapped[BaseClass.string]


class Orders(BaseClass):
    __tablename__ = "Orders"

    category : Mapped[BaseClass.string]
    service : Mapped[BaseClass.string]
    description : Mapped[BaseClass.string]
    status : Mapped[str] = mapped_column(Enum(StatusOrders))
    master : Mapped[int|None]
    created_at : Mapped[datetime] = mapped_column(server_default=func.now())
    update_at : Mapped[datetime] = mapped_column(onupdate=func.now(), nullable=True)
