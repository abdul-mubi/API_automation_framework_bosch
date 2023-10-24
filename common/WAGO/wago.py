import logging

from pymodbus.client.sync import ModbusTcpClient

class Wago:
    def __init__(self, ip_wago):
        self.client = ModbusTcpClient(host=ip_wago)
    def connect(self):
        self.client.connect()
    def disconnect(self):
        self.client.close()
    def read_status(self, device):
        logging.info(self.client.read_coils(device))
    def power_on(self, device):
        self.client.write_coil(device, True)
    def get_state(self, device):
        result = self.client.read_coils(device + 512, 1)
        logging.info(result.bits[0])
        return result.bits[0]
    def power_off(self, device):
        self.client.write_coil(device, False)
