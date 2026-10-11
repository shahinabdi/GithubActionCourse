FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1
WORKDIR /srv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY app ./app
RUN uv sync --frozen --no-dev

ARG APP_VERSION=dev
ENV APP_VERSION=$APP_VERSION \
    DB_PATH=/data/todos.db \
    PATH="/srv/.venv/bin:$PATH"

RUN useradd -r app && mkdir /data && chown app /data
USER app
VOLUME /data
EXPOSE 8000

CMD ["uvicorn", "app.asgi:app", "--host", "0.0.0.0", "--port", "8000"]
