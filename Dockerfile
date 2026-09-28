FROM python:3.9-slim-bookworm

RUN pip install --no-cache-dir uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

COPY pyproject.toml uv.lock README.md run_tests.sh ./
RUN uv sync --locked --no-install-project

COPY src ./src
RUN uv sync --locked
RUN ./run_tests.sh

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
