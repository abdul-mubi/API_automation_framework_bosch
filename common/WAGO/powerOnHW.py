import wago
import sys
import time
import logging

IP = sys.argv[1]

wagoClient = wago.Wago(IP)
wagoClient.connect()
if ("False" in str(wagoClient.get_state(int(sys.argv[2])))):
    logging.info('WAGO switch is turned OFF. Attempting to turn it ON')
    wagoClient.power_on(int(sys.argv[2]))
    time.sleep(30)
    wagoClient.get_state(int(sys.argv[2]))
else :
    logging.info('WAGO switch is already turned ON')
wagoClient.disconnect()