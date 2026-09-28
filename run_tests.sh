#!/usr/bin/env bash
set -euo pipefail

uv run mypy src/
uv run ruff check src/

uv run python -m pytest
