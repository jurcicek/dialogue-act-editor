REM del dist\*.*
rmdir /q /s dist
c:\python24\python.exe setup.py py2exe 
rem --packages encodings,zipimport,xml.dom
set VER=dae-1.5
mkdir %VER%
copy dist\*.* %VER%
"c:\prg\WinRAR\Rar.exe" a deployment\%VER% -r %VER%\*.*
"c:\prg\WinRAR\Rar.exe" a deployment\%VER%.src *.py *.txt *.bat *.xml
rmdir /q /s build
