@echo off
REM Start the Commerce Agent API server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload
