from database.service import server_specific_order
from sqlalchemy.orm import Session
from fastapi import HTTPException



def NotFoundErrorOrderID(order_id:int, db: Session) -> None:
    try:
        server_specific_order(orderID=order_id, db=db)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Order with this ID not found")