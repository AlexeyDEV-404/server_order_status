from SQLAlchemy_work_db.enusm import StatusMasterCheck

def free_status_master_examination_0(data):
    x = data[0]
    if x == StatusMasterCheck.FREE:
        return x
    raise ValueError(f"Текущий статус: {x}")

def chek_select_fetchone(fetchone):
    if fetchone is None:
        raise ValueError("Мастера не существует")
    return fetchone
        
def chek_value_master_order_free(value: str):
    if value == StatusMasterCheck.BUSY:
        raise ValueError("Мастер занят и не может принять заказ.")
 




