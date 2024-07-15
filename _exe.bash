# /bin/bash
pyinstaller -F --add-data "models;models" --add-data "data;data" --collect-all customtkinter --collect-all sklearn .\diagnosis_2.py --noconsole