#!/usr/bin/env sh
set -eu
python -m uvicorn ai_agent.api.server:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}"
