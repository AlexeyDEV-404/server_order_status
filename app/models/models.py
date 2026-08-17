from sqlalchemy import (ForeignKey,
                        String,
                        UniqueConstraint,
                        PrimaryKeyConstraint,
                        func,
                        Enum)
from sqlalchemy.orm import (DeclarativeBase,
                            mapped_column,
                            Mapped,
                            relationship)

from typing import (Annotated,
                    List)
from app.models.enum_model import (
    StatusMasterCheck, StatusOrders)
from datetime import datetime


class Base(DeclarativeBase):
    pass


class BaseClass(Base):
    __abstract__ = True

    string_nullableF = Annotated[str, mapped_column(
        String(length=255), nullable=False)]
    string = Annotated[str, mapped_column(String(length=200))]

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class MasterList(BaseClass):
    __tablename__ = "MasterList"

    name: Mapped[BaseClass.string_nullableF]
    status: Mapped[StatusMasterCheck] = mapped_column(Enum(StatusMasterCheck))

    master_skills: Mapped[List["MasterSkills"]] = relationship(
        back_populates="master_list", cascade="all, delete-orphan")


class MasterSkills(Base):
    __tablename__ = "MasterSkills"
    __table_args__ = (PrimaryKeyConstraint("master_id", "skill_id"),)

    master_id: Mapped[int] = mapped_column(
        ForeignKey("MasterList.id"), nullable=False)
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("Skills.id"), nullable=False)

    master_list: Mapped["MasterList"] = relationship(
        back_populates="master_skills")
    skills: Mapped["Skills"] = relationship(
        back_populates="master_skills")


class Skills(BaseClass):
    __tablename__ = "Skills"
    __table_args__ = (UniqueConstraint("category", "service"),)

    category: Mapped[BaseClass.string]
    service: Mapped[BaseClass.string]

    master_skills: Mapped[List["MasterSkills"]] = relationship(
        back_populates="skills", cascade="all, delete-orphan")
    skills_orders: Mapped[List["Orders"]] = relationship(
        back_populates="orders_skills", cascade="all, delete-orphan")


class Orders(BaseClass):
    __tablename__ = "Orders"

    skill_id: Mapped[int] = mapped_column(ForeignKey("Skills.id"))
    orders_skills: Mapped["Skills"] = relationship(
        back_populates="skills_orders")
    description: Mapped[BaseClass.string]
    status: Mapped[StatusOrders] = mapped_column(Enum(StatusOrders))
    master_id: Mapped[int | None] = mapped_column(
        ForeignKey("MasterList.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(
        onupdate=func.now(), nullable=True)
