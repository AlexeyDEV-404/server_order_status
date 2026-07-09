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


def chek_value_master_order_free(value: str | int):
    isinstance(value, str)
    if isinstance(value, str):
        if value == "BUSY":
            raise ValueError(
                "Статус мастера BUSY (занят) и не может принять заказ."
            )
    elif isinstance(value, int):
        if value > 0:
            raise ValueError(
                "Мастер выполняет заказ и не может быть назначен на другой."
            )
