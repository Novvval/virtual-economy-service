### Как развернуть приложение

1. Заходим в директорию с проектом `cd <папка с проектом>`
2. Создаем .env файл по примеру .env.example: `cp .env.example .env`, вставив необходимые значения
3. Устанавливаем uv, если его нет: `pip install uv` или `pipx install uv`
4. Устанавливаем зависимости командой `uv sync`
5. Поднимаем docker сервисы `make run`
6. Устанавливаем миграции и дефолтные данные `make migrate`
7. Юнит-тесты запускать командой `make test-unit`
8. Интеграционные тесты запускать командой `make test-integration`
9. Приложение должно быть доступно по localhost:8000

Использованные технологии: FastAPI, Celery, Redis, Postgresql, Sqlalchemy


### Тестовые запросы

Купить товар

```shell
curl -X 'POST' \
  'http://127.0.0.1:8000/products/1/purchase' \
  -H 'accept: application/json' \
  -H 'Idempotency-Key: 9aa239dd-9cdb-4db3-8a49-933080575989' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MX0.h_AWxlL7rBnQj-Zx_LiBUW7JrzePH4sZBbHPti_20KE' \
  -H 'Content-Type: application/json' \
  -d '{
  "amount": 1
}'
```

Использовать товар

```shell
curl -X 'POST' \
  'http://127.0.0.1:8000/products/1/use' \
  -H 'accept: application/json' \
  -H 'Idempotency-Key: 002ef035-c161-4f27-9266-f7674d930896' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MX0.h_AWxlL7rBnQj-Zx_LiBUW7JrzePH4sZBbHPti_20KE' \
  -H 'Content-Type: application/json' \
  -d '{
  "amount": 1
}'
```

Пополнить баланс

```shell
curl -X 'POST' \
  'http://127.0.0.1:8000/users/1/add-funds' \
  -H 'accept: application/json' \
  -H 'Idempotency-Key: 23e594b9-2727-466e-b9e7-7dcf8b929bdc' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MX0.h_AWxlL7rBnQj-Zx_LiBUW7JrzePH4sZBbHPti_20KE' \
  -H 'Content-Type: application/json' \
  -d '{
  "amount": 300
}'
```

Посмотреть инвентарь

```shell
curl -X 'GET' \
  'http://127.0.0.1:8000/users/1/inventory' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MX0.h_AWxlL7rBnQj-Zx_LiBUW7JrzePH4sZBbHPti_20KE'
```

Посмотреть популярные товары

```shell
curl -X 'GET' \
  'http://127.0.0.1:8000/analytics/popular-products?limit=5' \
  -H 'accept: application/json'
```
