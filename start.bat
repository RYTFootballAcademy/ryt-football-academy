@echo off
setlocal
python -m uvicorn ai_agent.api.server:app --host 127.0.0.1 --port 8000 --reload
