ХУУУУУУУУУУУУУУУУУУУУУУУУУУУУУУУУУУУУУУУУЙЙЙЙЙЙЙЙЙЙЙ

# Сервис услуг мастеров
Сервис по заказу мастеров для различных типов внутридомовых работ. В приложении заказываешь ищешь нужный тип работ, оформляешь заказ и ищешь свободного мастера.

## Фрейморки и библиотеки
SQLite - база данных
pydantic - валидация данных
fastapi - веб-фреймворк
uvicorn - ASGI сервер

## Запуск
python -m database.init_db - запуск файла "init_db.py" для создания Базы Данных и формирования таблиц для ее работы.
python -m app.main - запуск приложения, после чего, готово к работе.

## Эндпоинты API
post | /order/new | создать заказ
post | /order/{id_order}/assinged | назначить мастера на заказ
post | /order/{id_order}/in_progress | начать выполнение работ по заказу
post | /order/{id_order}/completed | завершить выполнение заказа
post | /order/{id_order}/cancel | отменить заказ, можно только когда заказ создан, во всех других случаях нельзя.
get | /orders/{id_order} | конкретный заказ
get | /orders | список всех заказов, за все время
get | /master_list | список всех мастеров
get | /search_master | поиск свободных мастера для заказа
get | /service | список всех услуг

## Схемы БД
Таблица master_list: 
id_master INTEGER PK AUTOINCREMENT
name TEXT NOT NULL
status TEXT CHEK (status in ("FREE", "BUSY"))

Таблица master_skills:
master_id INTEGER NOT NULL
skill_id INTEGER NOT NULL
PRIMARY KEY(master_id, skill_id)
FOREIGN KEY (master_id) REFERENCES master_list (id_master) ON DELETE CASCADE,
FOREIGN KEY (skill_id) REFERENCES works(id_works) ON DELETE CASCADE

Таблица orders:
id_order INTEGER PK AUTOINCREMENT
category TEXT NOT NULL
service TEXT NOT NULL
description TEXT NOT NULL
status TEXT NOT NULL CHECK(status IN ("NEW", "ASSINGED", "IN_PROGRESS"
"COMPLETED", "CANCEL"))
created_at TEXT NOT NULL
master INTEGER
FOREIGN KEY (master) REFERENCES master_list(id_master) ON DELETE SET NULL

Таблица skills:
id_skill INTEGER PK AUTOINCREMENT
category TEXT
services TEXT
UNIQUE (category, services)

