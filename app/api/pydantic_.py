from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated

from SQLAlchemy_work_db.enusm import StatusMasterCheck

Field_str_filter = Annotated[str, Field(min_length=1, max_length=500)]


class TableSkills(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category: str
    service: str


class UserInput(BaseModel):
    category: Field_str_filter
    services: Field_str_filter
    description: Field_str_filter


class AssingMaster(BaseModel):
    masterID: int


class TableMasterList(BaseModel):
    """
    Модель для informarion_about_craftsmen_orm
    """
    model_config = ConfigDict(from_attributes=True)

    name: str
    status: str

    master_skills: list["TableMasterSkills"]


class TableMasterSkills(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    master_id: int
    skill_id: int

    skills: TableSkills


class TableOrders(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category: str
    service: str
    description: str
    status: str
    master: int | None


class MasterSkillsRelationShema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill_id: int
    skills: TableSkills


class TableInfAboutCraftsmen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    status: StatusMasterCheck

    master_skills: list[MasterSkillsRelationShema]
