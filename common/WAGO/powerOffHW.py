import wago
import sys
import time
import logging

IP = sys.argv[1]

wagoClient = wago.Wago(IP)
wagoClient.connect()
if ("True" in str(wagoClient.get_state(int(sys.argv[2])))):
    logging.info('WAGO switch is turned ON. Attempting to turn it OFF')
    wagoClient.power_off(int(sys.argv[2]))
    time.sleep(5)
    wagoClient.get_state(int(sys.argv[2]))
else :
    logging.info('WAGO switch is already turned OFF')
wagoClient.disconnect()