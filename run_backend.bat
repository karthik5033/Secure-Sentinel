@echo off
cd /d "%~dp0"
echo Starting Backend Server...
"C:\Users\Karthik k P\AppData\Local\Programs\Python\Python314\python.exe" -m uvicorn backend.main:app --host 0.0.0.0 --port 8002 --reload
pause
