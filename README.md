# ML Model Serving

FastAPI-сервис инференса модели диабета с JWT-аутентификацией и RBAC.

## Запуск

### Локально

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8090
```

Переменные окружения (опционально):

```bash
export JWT_SECRET_KEY=your-secret
export JWT_ALGORITHM=HS256
export JWT_EXPIRE_MINUTES=30
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=secret123
export ADMIN_EMAIL=admin@localhost
```

### Docker

```bash
docker build -t ml-serving .
docker run -p 8090:8090 \
  -e JWT_SECRET_KEY=your-secret \
  -e ADMIN_USERNAME=admin \
  -e ADMIN_PASSWORD=secret123 \
  ml-serving
```

### Docker Compose

```bash
docker compose up --build
```

## API

| Метод | Путь | Доступ |
|---|---|---|
| GET | `/` | публичный |
| POST | `/auth/register` | публичный |
| POST | `/auth/login` | публичный |
| GET | `/me` | user, admin |
| POST | `/predict` | user, admin |
| GET | `/admin/metrics` | admin |
| DELETE | `/admin/users/{id}` | admin |

Документация: `http://localhost:8090/docs`

## Тесты

```bash
pytest
```

Запуск конкретного файла:

```bash
pytest tests/test_auth.py -v
```