from dataclasses import dataclass
from datetime import datetime


@dataclass
class OrdersDTO:
    category: str
    service: str
    description: str
    status: str
    master: int | None
    created_at: datetime
    update_at: datetime


@dataclass
class MasterSkillsDTO:
    master_id: int
    skill_id: int
