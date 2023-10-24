REM Start the ECU Reference System
%~dp0..\bin\UDSonCAN.exe --list-hardware-device --start --name UDSonCAN_cTP --ini "..\Data\UDS_Resp_2DTCs_RD.ini"
PAUSE