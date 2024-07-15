# /bin/bash
pyinstaller --noconsole --add-data "models;models" --add-data "data;data" --collect-all customtkinter --collect-all sklearn --collect-all matplotlib .\diagnosis.py