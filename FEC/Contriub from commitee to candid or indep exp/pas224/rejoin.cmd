@echo off
cd /d "%~dp0"
echo Rejoining itpas24.txt...
copy /b "itpas24.txt.part001" + "itpas24.txt.part002" "itpas24.txt.rejoined.txt" >nul
for %%P in ("itpas24.txt.part0??" "itpas24.txt.part1??") do (
  if /I not "%%~nxP"=="itpas24.txt.part001" if /I not "%%~nxP"=="itpas24.txt.part002" (
    copy /b "itpas24.txt.rejoined.txt"+"%%~nxP" "itpas24.txt.rejoined.txt" >nul
  )
)
echo Done. Output: itpas24.txt.rejoined.txt
pause
