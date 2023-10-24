import os
import sys
import time
import logging
from logging import getLogger
from ctypes import windll

#Setting up logging configuration
logger = logging.getLogger()
formatter = logging.Formatter('%(message)s')
sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(formatter)
sh.setLevel(logging.INFO)
logger.addHandler(sh)
logger.setLevel(logging.INFO)

#Cleware USB switch control script with DLL integration
dll_name = "USBaccessX64.dll"
dllabspath = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + dll_name
mydll=windll.LoadLibrary(dllabspath) #loads dynamic-link library (DLL)
cleware=mydll.FCWInitObject() #initiating the object
device_count=mydll.FCWOpenCleware(0) #function returns the number of devices found
logger.info(f"found {device_count} devices")
serial_number=mydll.FCWGetSerialNumber(0,0) #function returns the serial number of device
device_type=mydll.FCWGetUSBType(0,0) #function returns the value depends on the specific Cleware device and its associated USB type enumeration
logger.info(f"first serial number = {serial_number}, device type = {device_type}")

if (device_type == 48):
    port_no = int(sys.argv[1]) + 16
    status = str(sys.argv[2])
    if (status == 'On') and (mydll.FCWGetSwitch(0, serial_number, port_no) != 1): #FCWGetSwitch function returns the current switch status [0=OFF / 1=ON]
        logger.info(f"Current binary switch state of port: {int(sys.argv[1])} is {mydll.FCWGetSwitch(0, serial_number, port_no)} ==> || 0=OFF / 1=ON ||")
        mydll.FCWSetSwitch(0, serial_number, port_no, 1) #FCWSetSwitch function turns an USB-Switch port on or off by passing the last parameter as 0 for OFF / 1 for ON
        logger.info(f"Binary state of port: {int(sys.argv[1])} is switched to {mydll.FCWGetSwitch(0, serial_number, port_no)} ==> || 0=OFF / 1=ON ||")
        logger.info(f"Hence, Cleware switch: {int(sys.argv[1])} is {status.upper()}")
    elif (status == 'Off') and (mydll.FCWGetSwitch(0, serial_number, port_no) != 0): #FCWGetSwitch function returns the current switch status [0=OFF / 1=ON]
        logger.info(f"Current binary switch state of port: {int(sys.argv[1])} is {mydll.FCWGetSwitch(0, serial_number, port_no)} ==> || 0=OFF / 1=ON ||")
        mydll.FCWSetSwitch(0, serial_number, port_no, 0) #FCWSetSwitch function turns an USB-Switch port on or off by passing the last parameter as 0 for OFF / 1 for ON
        logger.info(f"Binary state of port: {int(sys.argv[1])} is switched to {mydll.FCWGetSwitch(0, serial_number, port_no)} ==> || 0=OFF / 1=ON ||")
        logger.info(f"Hence, Cleware switch: {int(sys.argv[1])} is {status.upper()}")
    else:
        logger.info(f"Cleware switch port: {int(sys.argv[1])} is already turned {status.upper()}")
else :
    logger.info(f"Handling of this device type is missing")
