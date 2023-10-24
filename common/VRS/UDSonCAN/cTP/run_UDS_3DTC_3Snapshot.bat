REM Start the ECU Reference System
%~dp0..\bin\UDSonCAN.exe --list-hardware-device --start --name UDSonCAN_cTP --ini "..\Data\UDS_Resp_3DTCs_3Snapshot.ini"
PAUSE

