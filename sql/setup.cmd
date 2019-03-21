pyinstaller -F oracleSchema.py
pyinstaller -F sqlserverSchema.py
pyinstaller -F csvDataLoader.py
pyinstaller -F sqlrunor.py
pyinstaller -F oracleDataGrapper.py
pyinstaller -F sqlserverDataGrapper.py

copy *.json dist
copy *.dbdesc dist

