@echo off
color 8f
MODE 90,50
cd ..
if NOT "%~x1" == ".feature" (
color cf
echo -------------------------------WARNING !-----------------------------------------
echo Please drag and drop *.feature file on this batch file to test particular feature
echo You drag and dropped the file %~n1%~x1
pause>nul | echo Press any key to exit
exit
)

set BUILD_NUMBER=%DATE:~7,2%%DATE:~4,2%%TIME:~3,2%%TIME:~6,2%
echo setting BUILD_NUMBER as %BUILD_NUMBER%
set usernameUI=automated-test@bosch.com
set passwordUI=kaiSerschmarrn+19
set PYTHONWARNINGS=ignore:Unverified HTTPS request
echo Running Python Behave...
echo Testing %~n1 .feature
echo log output will be stored in output_log_%BUILD_NUMBER%.txt

behave -i %~n1 -f pretty -o offline_tests\logs\output_log_%BUILD_NUMBER%.txt --tags=offline
pause>nul | echo Testing complete.. Press any key to exit
