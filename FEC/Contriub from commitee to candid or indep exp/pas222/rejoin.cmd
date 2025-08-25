@echo off
cd /d "%~dp0"
echo Rejoining itpas22.txt...
copy /b "itpas22.txt.part001" + "itpas22.txt.part002" "itpas22.txt.rejoined.txt" >nul
for %%P in ("itpas22.txt.part0??" "itpas22.txt.part1??") do (
  if /I not "%%~nxP"=="itpas22.txt.part001" if /I not "%%~nxP"=="itpas22.txt.part002" (
    copy /b "itpas22.txt.rejoined.txt"+"%%~nxP" "itpas22.txt.rejoined.txt" >nul
  )
)
echo Done. Output: itpas22.txt.rejoined.txt
pause
