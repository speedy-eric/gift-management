@echo off
cd /d %~dp0
echo 기프트 관리 서버를 시작합니다...
"C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe" -m pip install flask --quiet
"C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe" app.py
pause
