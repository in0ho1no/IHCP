@echo off
call .\.venv\Scripts\activate.bat
streamlit run "src\main_gui.py" --server.address=127.0.0.1
pause