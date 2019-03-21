cd d:\mydocs\python\codes\pywork\Utils\patterncoding
rd /s/q dist
rd /s/q pcoding
pyinstaller --specpath spec -p . --onefile -n xlsxData.exe --console xlsxData.py
pyinstaller --specpath spec -p . --onefile -n jsonCoding.exe --console jsonTmplCoding.py
mkdir dist\tmpllib
xcopy /se /k tmpllib dist\tmpllib
copy *.docx dist
ren dist pcoding