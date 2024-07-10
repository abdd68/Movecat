# /bin/bash
pyinstaller -F --add-data "models/GBT.joblib;models" .\diagnosis.py 