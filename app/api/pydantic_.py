from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated



Field_str_filter = Annotated[str, Field(min_length=1, max_length=500)]

class UserInput(BaseModel):
    category: Field_str_filter
    services: Field_str_filter
    description: Field_str_filter

class AssingMaster(BaseModel):
    masterID: int

class TableMasterList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    status: str

class TableMasterSkills(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    master_id : int
    skill_id : int

class TableSkills(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category: str
    service: str
    
class TableOrders(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category: str
    service: str
    description: str
    status: str
    master: int | None

class TableInfAboutCraftsmen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name : str
    category : str
    service : str
    status : str
