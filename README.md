# Server Order Status

REST API сервис для управления заказами на бытовые услуги. Клиент создаёт заказ, система подбирает свободного мастера по навыкам и сопровождает заказ через все статусы жизненного цикла.

## Стек

| Компонент | Технология |
|---|---|
| Web-фреймворк | FastAPI |
| ORM | SQLAlchemy 2.0 |
| База данных | SQLite |
| Валидация | Pydantic v2 |
| ASGI-сервер | Uvicorn |
| Тесты | Pytest |
| Контейнеризация | Docker |

## Архитектура

```
app/
├── api/
│   ├── API_routers.py     # FastAPI роутеры (HTTP-слой)
│   ├── pydantic_.py       # Request / Response модели
│   └── exc.py             # Кастомные исключения
├── main.py                # Точка входа, FastAPI app
database/
├── service.py             # Бизнес-логика (service-слой)
└── doman_rules.py         # Доменные правила и проверки
SQLAlchemy_work_db/
├── engine_and_models.py   # ORM-модели, engine, get_db
├── repository.py          # Repository-слой (SQL-запросы)
└── enusm.py               # Enum-статусы
test/
├── conftest.py            # Фикстуры, in-memory SQLite
├── test_sqlalchemy.py     # Юнит-тесты репозиториев
├── test_api.py            # API-тесты через TestClient
└── test_end_to_end.py     # E2E: полный lifecycle заказа
```

Проект следует трёхслойной архитектуре: **Router → Service → Repository**. Бизнес-логика не просачивается в роутеры, SQL не просачивается в сервисный слой.

## Жизненный цикл заказа

```
NEW ──► ASSINGED ──► IN_PROGRESS ──► COMPLETED
 │
 └──► CANCEL
```

Смена статуса строго односторонняя. Отменить можно только заказ в статусе `NEW`. Назначить мастера — только свободного (`FREE`) и без активных заказов.

## Запуск

### Через Docker

```bash
docker build -t server-order-status .
docker run -p 8000:8000 server-order-status
```

### Локально

```bash
pip install -r requirements.txt
python app/main.py
```

API будет доступно по адресу: `http://localhost:8000`  
Интерактивная документация: `http://localhost:8000/docs`

## API

### Заказы

| Метод | Эндпоинт | Описание |
|---|---|---|
| `POST` | `/user/order/new` | Создать новый заказ |
| `POST` | `/user/order/{id}/assinged` | Назначить мастера на заказ |
| `POST` | `/user/order/{id}/in_progress` | Перевести заказ в работу |
| `POST` | `/user/order/{id}/completed` | Завершить заказ |
| `POST` | `/user/order/{id}/cancel` | Отменить заказ (только статус `NEW`) |
| `POST` | `/user/order/{id}/delete` | Удалить заказ |
| `GET` | `/user/order/{id}` | Получить заказ по ID |
| `GET` | `/user/orders` | Список всех заказов |

### Мастера и навыки

| Метод | Эндпоинт | Описание |
|---|---|---|
| `POST` | `/user/add_master` | Добавить мастера |
| `POST` | `/user/add_master_skill` | Назначить навык мастеру |
| `POST` | `/user/insert_skill` | Добавить навык в справочник |
| `GET` | `/user/master_list` | Список мастеров с навыками |
| `GET` | `/user/table_skill_master` | Таблица навыков мастеров |
| `GET` | `/user/search_master` | Найти свободных мастеров по услуге |
| `GET` | `/user/service` | Список всех доступных услуг |

### Пример запроса

```bash
# Создать заказ
curl -X POST "http://localhost:8000/user/order/new" \
  -H "Content-Type: application/json" \
  -d '{"category": "Сантехника", "services": "Замена труб", "description": "Протечка под раковиной"}'

# Найти мастера
curl "http://localhost:8000/user/search_master?category=Сантехника&services=Замена+труб"
```

## Тесты

```bash
# Все тесты
pytest

# Только юнит-тесты репозиториев
pytest test/test_sqlalchemy.py -v

# Только API-тесты
pytest test/test_api.py -v

# E2E
pytest test/test_end_to_end.py -v
```
