from enum import Enum


class StatusMasterCheck(Enum):
    FREE = "FREE"
    BUSY = "BUSY"


class StatusOrders(Enum):
    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCEL = "CANCEL"
