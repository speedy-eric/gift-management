@echo off
chcp 65001 > nul
cd /d %~dp0
echo [Speedy] 기프트 관리 서버를 시작합니다...
py -m pip install flask --quiet 2>nul || "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe" -m pip install flask --quiet
py app.py 2>nul || "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe" app.py
pause
