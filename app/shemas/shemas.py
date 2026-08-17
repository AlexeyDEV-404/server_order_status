from pydantic import (BaseModel,
                      Field,
                      ConfigDict)
from typing import Annotated
from app.models.enum_model import StatusMasterCheck, StatusOrders
from app.models.models import MasterList


Field_str_filter = Annotated[str, Field(min_length=1, max_length=200)]


class MasterSkillValid(BaseModel):
    """
    master_id: int, skill_id: int
    """
    model_config = ConfigDict(from_attributes=True)

    master_id: int
    skill_id: int


class SkillsValid(BaseModel):
    """
    id: int, category: Field_str_filter, service: Field_str_filter
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: Field_str_filter
    service: Field_str_filter


class SkillsValidNoID(BaseModel):
    """
    category: Field_str_filter, service: Field_str_filter
    """
    model_config = ConfigDict(from_attributes=True)

    category: Field_str_filter
    service: Field_str_filter


class OrderValid(BaseModel):
    """
    orders_skills: SkillsValid, description: Field_str_filter,
    status: StatusOrders, master_id: int | None
    """
    model_config = ConfigDict(from_attributes=True)

    orders_skills: SkillsValid
    description: Field_str_filter
    status: StatusOrders
    master_id: int | None


class ParamsLifeCycle(BaseModel):
    """
    order_id: int, master_id: int
    """
    model_config = ConfigDict(from_attributes=True)

    order_id: int
    master_id: int


class MastListValid(BaseModel):
    """
    id: int, name: str, status: StatusMasterCheck
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    status: StatusMasterCheck


class MastListValidNoID(BaseModel):
    """
    name: str, status: StatusMasterCheck
    """
    model_config = ConfigDict(from_attributes=True)

    name: str
    status: StatusMasterCheck


class MasterListOut(BaseModel):
    """
    id: int, name: str, status: StatusMasterCheck, skills: list[SkillsValid]
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    status: StatusMasterCheck
    skills: list[SkillsValid]

    @classmethod
    def from_orm_master(cls, master: MasterList):
        return cls(
            id=master.id,
            name=master.name,
            status=master.status,
            skills=[SkillsValid.model_validate(ms.skills)
                    for ms in master.master_skills])
