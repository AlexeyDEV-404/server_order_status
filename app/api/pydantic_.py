from pydantic import BaseModel, Field
from typing import Annotated



Field_str_filter = Annotated[str, Field(min_length=1, max_length=500)]

class UserInput(BaseModel):
    category: Field_str_filter
    services: Field_str_filter
    description: Field_str_filter

class AssingMaster(BaseModel):
    masterID: int

    
