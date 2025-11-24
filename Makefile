.PHONY: run migrate test-unit test-integration

run:
	docker compose up -d

migrate:
	uv run alembic upgrade head

test-unit:
	uv run pytest tests/test_use_cases.py

test-integration:
	uv run pytest tests/test_api.py
