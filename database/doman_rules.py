from SQLAlchemy_work_db.enusm import StatusMasterCheck

def rowcount_examinator(rowcount):
    if rowcount >= 1:
        return "Обновление успешно"
    raise ValueError("Ошибка: rowcount равен 0.")

def free_status_master_examination_0(data):
    x = data[0]
    if x == StatusMasterCheck.FREE:
        return x
    raise ValueError(f"Текущий статус: {x}")

def chek_select_fetchone(fetchone):
    if fetchone is None:
        raise ValueError("Мастера не существует")
    return fetchone
    
def chek_fetchone_master_order_count(fetchone : int): # работает с master_chek_order в файле orders_db.py возвращает число из-за COUNT(*) в условии запроса
    """ Проверка, назначен ли мастер. """
    if fetchone != 0:
        raise ValueError("Ошибка: Мастере занят и не может быть назначен на заказ.")  
    
def chek_fetchone_master_order_free(fetchone: str):
    if fetchone == StatusMasterCheck.BUSY:
        raise ValueError("Мастер занят и не может принять заказ.")
 




