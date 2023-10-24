import serial
import serial.tools.list_ports as serial_list
from serial.serialwin32 import Serial
import logging

class TesterAction:
    release_button = "FBT-00"  # Corresponding CodeName in Arduino
    click_button = "FBT-01"
    get_led_status = "LED-??"


def serial_ports():
    """ Lists all serial port names and filter supported RemoteHW device

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A serial port object of corresponding RemoteHW device
    """
    ports = serial_list.comports()
    for port_no, description, address in ports:
        try:
            logging.info("Checking Port : {}".format(port_no))
            ser = Serial(port_no, 115200, timeout=3)
            line = str(ser.readline())
            if "RHS-" in line:
                logging.info("Fount RemoteHW {} in port {}".format(description, port_no))
                return ser
            ser.close()
        except (OSError, serial.SerialException):
            pass
    return -1


testerAction = TesterAction()


def control_flashbutton(state=TesterAction.release_button):
    """Controls the flash button by sending the commands as in class 'TesterAction' """
    global arduino_port
    if arduino_port == -1:
        assert False, "Unable to find arduino port! \n Please check arduino board is connected properly"
    try:
        temp = arduino_port.readlines()
        logging.info(temp)
        arduino_port.write('{}\n'.format(state).encode())
    except (OSError, serial.SerialException):
        pass


def status_flashled():
    """get the status of Flash led """
    global arduino_port
    if arduino_port == -1:
        assert False, "Unable to find arduino port! \n Please check arduino board is connected properly"
    try:
        temp = arduino_port.readlines()
        logging.info(temp)
        arduino_port.write('LED-??\n'.encode())
        line = arduino_port.readline().decode('utf-8')
        logging.info(line)
        return line
    except (OSError, serial.SerialException):
        pass
