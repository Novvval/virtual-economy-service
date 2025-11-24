FROM python:3.13-slim

RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*


WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"

COPY src/ ./src/

