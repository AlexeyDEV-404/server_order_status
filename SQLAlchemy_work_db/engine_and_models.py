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
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()

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

    def to_dict(self):
        return {
            "name" : MasterList.name,
            "status" : MasterList.status
        }

class MasterSkills(Base):
    __tablename__ = "MasterSkills"
    __table_args__ = (ForeignKeyConstraint((["master_id"]), ["MasterList.id"], ondelete="CASCADE"),
                      ForeignKeyConstraint(["skill_id"], ["Skills.id"], ondelete="CASCADE"),
                      PrimaryKeyConstraint("skill_id", "master_id"))
    
    master_id : Mapped[int] = mapped_column(nullable=False)
    skill_id : Mapped[int] = mapped_column(nullable=False)

    def to_dict(self):
        return{
            "master_id" : self.master_id,
            "skill_id" : self.skill_id
        }

class Skills(BaseClass):
    __tablename__ = "Skills"
    __table_args__ = (UniqueConstraint("category", "service"), )

    category : Mapped[BaseClass.string]
    service : Mapped[BaseClass.string]

    def to_dict(self):
        return{
            "category" : Skills.category,
            "service" : Skills.service
        }


class Orders(BaseClass):
    __tablename__ = "Orders"

    category : Mapped[BaseClass.string]
    service : Mapped[BaseClass.string]
    description : Mapped[BaseClass.string]
    status : Mapped[str] = mapped_column(Enum(StatusOrders))
    master : Mapped[int|None]
    created_at : Mapped[datetime] = mapped_column(server_default=func.now())
    update_at : Mapped[datetime] = mapped_column(onupdate=func.now(), nullable=True)

    def to_dict(self):
        """
        id": <...>, 
        "category": <...>,
        "service": <...>,
        "description": <...>,
        "status": <...>,
        "master": <...>,
        "created_at": <...>,
        "update_at: <...>
        """
        return {
            "id": self.id,
            "category": self.category,
            "service": self.service,
            "description": self.description,
            "status": self.status,
            "master": self.master,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "update_at": self.update_at.isoformat() if self.update_at else None
    }
