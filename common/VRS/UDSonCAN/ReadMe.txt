1. Start the local Loopback Server (Note the default Data\UDSonCAN.ini file is configured to run with Data\VirtualOCD.xml)
2. Start the VRS by running run_UDSonCAN.bat
3. Open INCA and import the Export File  .\INCA\Export\UDSonCAN.exp
4. Under INCA 
    4.1. Initialize hardware 
    4.2  Download from File to Working Page
    4.3. Copy from Working Page to Reference Page
5. Open Experiment and start measurement.    


Changelog
---------
- update Prof-Configuration UDSonCAN_FD_StdID_ExtAddr_1MBaud 1.1.4 -> 1.1.5  change CAN-IDs for UDSonCANFD