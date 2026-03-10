from datetime import datetime


def datetime_now(): # Устанавливает текущее время. Остается в файле без изменений
    return datetime.now().strftime("%Y-%m-%d %H:%M")
