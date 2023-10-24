import logging
import glob
import os
import json
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import os
import time
from threading import Timer
from subprocess import Popen
import subprocess
import paramiko
import string
from scp import SCPClient
import datetime
from datetime import timedelta
import steps.pageObjects.API_FleetManagement_Class as API_FleetManagement_Class
import steps.pageObjects.API_Generic_Class as API_Generic_Class
import sys
import git
import shutil
import steps.constantfiles.constants_generic as constants
import jsonpath
import requests
logging.getLogger("paramiko").setLevel(logging.WARNING)
class ApiGenericClass:

    def __init__(self):
        self.timeout_time = constants.DEFAULT_TIMEOUT_TIME_SEC
    
    def get_tenant_for_space(self, be_space):
        test_config_data = self.parse_json_file(constants.TEST_CONFIG_JSON)
        return test_config_data["systemUnderTest"][be_space]["login"]["tenant"]

    # It returns the batch file name used to initialize the VRS
    def get_batch_name(self, vrs_name):
        vrs_list = {
            'UDSonCAN_ES740_2DTC':"run_UDS_2DTCs.bat",   #for es740
            "UDSonCAN_ES740_RD_SmokeTest":"CC_Sim_ES740.bat", #double correct
            "UDSonCAN_cTP":"start_cTP.bat", #correct
            "CANalization_cTP":"start_Flash.bat", #correct
            "CC_Sim_cTP":"CC_Sim_cTP.bat",
            "FOTA_Sim_Start_cTP":"FOTA_Sim_Start_cTP.bat",
            "CC_Sim_ES740":"CC_Sim_ES740.bat",
            "FOTA_Sim_Start_ES740":"FOTA_Sim_Start_ES740.bat",
            "UDSonCAN_ES740_3DTC":"run_UDS_3DTCs.bat",   #for es740
            "CANalization_ES740_CANMon":"run_UDS_CANalization_CanMon.bat",   # for es740
            "CANalization_startFlash_SmokeTest_ES740_RD_SmokeTest":"FOTA_Sim_Start_ES740.bat", #double correct
            "CANalization_ES740_J1939":"run_UDS_CANalization_J1939.bat",  # for ES740; similar 4 for cTPG

        }
        batch_file = vrs_list.get(vrs_name, "Invalid Virtual reference system name.")
        return batch_file
      
    def start_vrs(self, protocol, identifier):
        """Starts the Virtual reference System"""
        vrs_name = protocol + "_" + identifier
        vrs_batch = self.get_batch_name(vrs_name)
        logging.info(f"Starting VRS for -  {vrs_name}")
        cmd_str = "D:\\RF\\ES740\\"+vrs_batch
        proc = Popen([cmd_str], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
        time.sleep(30)
        return proc  

        # wait for 30 seconds.
        # you need to write a step if the process is exists
  
    @classmethod
    def stop_vrs_common(cls, protocol, vrs_proc):
        protocol_name = protocol
        if ("UDSONCAN" in protocol.upper()):    
            protocol = "UDSonCAN"
        elif ("CANALIZATION" in protocol.upper()):
            protocol = "CANalization"
        elif ("MONONCAN" in protocol.upper()):
            protocol = "MONonCAN"            
        logging.info("Stopping VRS %s ..."%protocol_name)

        path = os.path.dirname(os.path.abspath(__file__))
        if protocol == "MONonCAN":
            vrs_initiate = constants.GC_VRS+protocol+"\\bin\\"+protocol+".exe --stop"
            logging.info(vrs_initiate)
        if protocol == "CANalization":
            vrs_initiate = constants.GC_VRS+protocol+"\\"+protocol+".exe --name "+protocol_name+" --stop" 
        else:
            vrs_initiate = constants.GC_VRS+protocol+"\\bin\\"+protocol+".exe --name "+protocol_name+" --stop"
        cmd_str = path + vrs_initiate
        proc = subprocess.Popen(cmd_str, shell = True, stdout=None, stderr=True)
        logging.info(proc)
        if protocol == "MONonCAN":
            os.system(f"taskkill /F /IM MONonCAN.exe /T")
        time.sleep(40)
        poll = vrs_proc.poll()
        if poll == None:
            return True
        else:
            return True #It is a known issue, requires enhancement,

    def stop_all_vrs(self, all_vrs_proc, vrs_type):
        logging.info("Stopping all active VRS")
        stop_success = False
        path = os.path.dirname(os.path.abspath(__file__))
        if vrs_type is not None:
            all_vrs_proc = [vrs_name for vrs_name in all_vrs_proc if vrs_type in vrs_name]
        for each_vrs_name in all_vrs_proc:
            protocol = each_vrs_name.split("_")[0]
            proc = self.stop_vrs_by_name(protocol, each_vrs_name)
            stop_success = True
        return stop_success
    
    def stop_vrs_by_name(self, protocol, vrs_name):
        logging.info(f"Stopping VRS by process name - {vrs_name}")
        path = os.path.dirname(os.path.abspath(__file__))
        vrs_initiate = f"{constants.GC_VRS}{protocol}\\{protocol}.exe --stop --name {vrs_name}"
        cmd_str = path + vrs_initiate
        proc = subprocess.Popen(cmd_str, stdout = subprocess.PIPE, stderr = True)
        time.sleep(5) # small wait for stopping the VRS properly
        if (proc.poll() is None or isinstance(proc.poll(),int)):
            logging.info(f"+++++++++++ VRS - {vrs_name} is Stopped successfully +++++++++++")
        else:
            stdout, stderr = proc.communicate()
            vrs_execution_error, vrs_error_msg = self.check_vrs_execution_error(stdout.decode("utf-8"))
            proc.kill()
            assert vrs_execution_error == False, f"Failed stopping the VRS with stdout error message - {vrs_error_msg}"
        return proc

    @classmethod
    def start_vrs_common(cls, protocol, identifier):
        indent = identifier.split("_")
        path = os.path.dirname(os.path.abspath(__file__))
        cmd_str = path + constants.GC_VRS + "{}\\{}\\{}.bat".format(protocol,indent[0],indent[1])
        proc = Popen([cmd_str], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
        time.sleep(30)
        return proc
        
    def device_operation(self, operation, device):
        """ 
        Description: Use this method to perform operations using ssh commands on device
                    By default, this method will REBOOT the ES740 device (calling this method with no paramter)
            operation       = 'rebootDevice' or 'deleteAllJobs'
        
            device          = 'CCU'

        """
        if ("CCU" in device.upper()):
            device = "CCU"
        else:
            assert False, "Unexpected device type entered."
        
        path = os.path.dirname(os.path.abspath(__file__))
        cmd_str = path + constants.GC_DEVICECLEANUP_PS +" -action:"+operation+" -device:"+device
        proc = Popen(['powershell.exe', cmd_str], shell=True, stdin=None, stdout=None, stderr=True, close_fds=True)
        return proc
    
    def ssh_execute(self, hostname, ssh_key, command, logpath = None):
        ssh_username, ssh_password, ssh_pkey = self.__get_ssh_creds(ssh_key)
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            c.connect( hostname = hostname, username = ssh_username, password = ssh_password,  pkey = ssh_pkey)
            stdin , stdout, stderr = c.exec_command(command)
            out = stdout.read().decode('unicode_escape').encode('utf-8')
            err = stderr.read().decode('unicode_escape').encode('utf-8')
        except Exception:
            out = " "
            err = f"Error while connecting to -> {hostname}" 
            logging.error(f"{err}")
       
        c.close()
        return (out, err)
    
    def __get_ssh_creds(self, ssh_key):
        logging.debug("Preparing SSH Credentials")
        ssh_username = constants.SSH_USERNAME
        ssh_password = constants.SSH_PASSWORD
        path = os.path.dirname(os.path.abspath(__file__))
        keypath = path + constants.SSH_PKEY.format(ssh_key=ssh_key)
        ssh_pkey = paramiko.RSAKey.from_private_key_file(keypath)
        return ssh_username, ssh_password, ssh_pkey
  
    def device_type_selection(self, device_type):
        """ 
        Description: Use this method to fetch test data corresponding to machine name

        """
        if ("CCU" in device_type.upper()):
            device = "CCU"
        elif ("virtual_device" in device_type):
            device = "virtual_device"
        else:
            assert False, "Unexpected device type entered."
        return device

    def check_and_start_virtual_device(self, test_device,devices_data,context):
        """
        Description: Check if virtual device is connected to backend
                     If it is already connected use next available device, if not connected start device simulator for device 
        """
        path = os.path.dirname(os.path.abspath(__file__))
        cmd_path = path + constants.TEST_DATA_GENERATOR
        count = int(test_device.split('virtual_device').pop())
        while(count<=len(devices_data)):
            env = devices_data[test_device]["device_env"]
            api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(env,context.log_api_details)
            device_id = devices_data[test_device]["device_name"]
            device_online_state = api_fm_obj.get_device_status(device_id)
            if device_online_state =="ONLINE":
                logging.info(f"Virtual device {device_id} is already connected to backend and being used by others")
                logging.info(f"Checking next available virtual devices")
                test_device=test_device.split(str(count))[0]
                count+=1
                test_device = test_device+str(count)
                assert count <= len(devices_data), f"No virtual devices are available to connect to backend" 
                context.device_changed = True
            else:
                if not context.device_simulator_running:
                    proc_proxy=subprocess.Popen("px")
                    time.sleep(5)
                    context.device_simulator_running.append(proc_proxy.pid)
                logging.info(f"Virtual device {device_id} is not connected to backend")
                logging.info(f"starting device simulator for device {device_id}")
                print("Current working directory: {0}".format(os.getcwd()))
                os.chdir(cmd_path)
                print("Current working directory: {0}".format(os.getcwd()))
                cmd = f"python start_data_generator.py --device {device_id}"
                proc = subprocess.Popen(cmd)
                time.sleep(15)
                context.device_simulator_running.append(proc.pid)
                logging.info(f"Device {device_id} is now connected to backend")
                break
        return test_device

    def get_device_type(self, device_id, context):
        for each_key in context.devices_data.keys():
            if (type(context.devices_data[each_key]) == dict and context.devices_data[each_key]["device_name"] == device_id):
                return each_key

    def check_vrs_execution_error(self, std_out):
        vrs_execution_error = False
        vrs_error_message = ""
        for each_vrs_error in constants.VRS_ISSUE.keys():
            if each_vrs_error in std_out:
                vrs_execution_error = True
                vrs_error_message = constants.VRS_ISSUE[each_vrs_error]
                break
        if not vrs_execution_error:
            vrs_execution_error = True
            logging.info(f"VRS Error data: {std_out}")
            if re.search("0x8000", std_out):
                vrs_error_message = "NEW VRS error, please check Logs and add it to constants.VRS_ISSUE"
            else:
                vrs_error_message = f"VRS error {std_out}. \nPlease check the VRS ini file"
        return vrs_execution_error, vrs_error_message

    def initiate_vrs(self, context, protocol,identifier, vrs_port, device_type, play=None):
        protocol_name = protocol
        protocol = protocol.split("_")[0]
        protocol = protocol.rstrip(string.digits)
        logging.info(f"Trigger VRS ,{protocol}")
        path = os.path.dirname(os.path.abspath(__file__))
        ini_path = path + constants.GC_VRS+protocol+"\\Data\\"+identifier+".ini"
        if context.device_config_data["baud_rate"] != "500K":
            baudrate_value = context.device_config_data["baud_rate_ini_value"] if protocol != "UDSonCAN" else context.device_config_data["baud_rate_ini_value"].lower()
            with open(ini_path, "r+") as ini_file:
                update_ini_file = ini_file.read()
                baudrate_500k_flag = re.search(r"Baudrate.*500000", update_ini_file, flags=re.IGNORECASE)
                if baudrate_500k_flag:
                    update_ini_file = update_ini_file.replace(str(re.search('(?i)Baudrate.*500000', update_ini_file)[0]), baudrate_value)
                    ini_file.seek(0)
                    ini_file.write(update_ini_file)
                    logging.info(f"Replacing baudrate value with 250K in {identifier} ini file for NON-NGD Device")
        if protocol == "CANalization":
            vrs_initiate = f"{constants.GC_VRS}{protocol}\\{protocol}.exe --start --name {protocol_name}_{device_type}_{identifier} --hardware-device {vrs_port} --ini {ini_path} --quiet"
        else:
            vrs_initiate = f"{constants.GC_VRS}{protocol}\\{protocol}.exe --start --name {protocol_name}_{device_type}_{identifier} --hardware-device {vrs_port} --ini {ini_path}"
        if play is not None:
            asc_path = path + constants.GC_VRS+protocol+"\\Data\\"+play+".asc"
            vrs_initiate = f'{vrs_initiate} --play {asc_path}'
        logging.info(f'Starting VRS by name - {protocol_name}_{device_type}_{identifier} cmd: {vrs_initiate}')
        cmd_str = path + vrs_initiate
        proc = subprocess.Popen(cmd_str, stdout = subprocess.PIPE, stderr = True)
        time.sleep(5) # small wait for intitating the VRS properly
        logging.info(f"VRS Start response: {proc.poll()} and type : {type(proc.poll())}")
        
        if (proc.poll() is None or (isinstance(proc.poll(),int) and proc.poll() != 1)):
            logging.info("+++++++++++ VRS is started successfully +++++++++++")
            context.protocol_names.append(protocol_name+"_"+device_type+"_"+identifier)
        elif (proc.poll() is not None):
            context.protocol_names.append(protocol_name+"_"+device_type+"_"+identifier)
            stdout, stderr = proc.communicate(timeout=30)
            vrs_execution_error, vrs_error_msg = self.check_vrs_execution_error(stdout.decode("utf-8"))
            proc.kill()
            assert vrs_execution_error == False, f"Failed starting the VRS with stdout error message - {vrs_error_msg}"

        return proc
    
    def fetch_separation_time(self, identifier):
        identifier = identifier.split('_').pop()
        if ('ms' in identifier):
            separation_time = identifier.replace('ms','')
        elif ('endurance' in identifier):
            separation_time = 10
        elif ('highloadidents' in identifier):
            separation_time = 'highloadidents'
        else:
            separation_time = None
        return separation_time

    def set_wago_power_state(self, status, wago_ip, port_no):
        logging.info(f"Turn WAGO {status}")
        path = os.path.dirname(os.path.abspath(__file__)) + f"\\..\\..\\..\\..\\common\\WAGO\\power{status}HW.py"
        cmd_str = f"{path} {wago_ip} {port_no}"
        if status.casefold() in ["On".casefold(), "Off".casefold()]:
            proc = subprocess.Popen(cmd_str, shell=True, stdin=None, stdout=True, stderr=True)
            return proc
        else:
            assert False, "Unknown WAGO switch state has been input"
    
    def set_cleware_state(self, status, port_no):
        logging.info(f'Turn Cleware switch:{port_no} to {status}')
        path = os.path.dirname(os.path.abspath(__file__)) + f"{constants.CLEWARE_SWITCH}" + "\\POWER_ON-OFF_Control.py"
        cmd_str = f'python {path} {port_no} {status}'
        proc = subprocess.Popen(cmd_str, shell=True, stdin=None, stdout=subprocess.PIPE, stderr=True)
        assert proc.stderr is None, f"Cleware operation: get switch #{port_no} current status is not performed properly. It returned error : {proc.stderr}"
        out, err = proc.communicate()
        out = out.decode("utf-8")
        self.cleware_state_logging(out)    
            
    def start_process_with_command(self, command):
        logging.info('Starting windows process...')
        proc = subprocess.Popen(command, shell=True, stdin=None, stdout=subprocess.PIPE, stderr=True)
        proc.wait()
        time.sleep(5)
        return proc

    def fetch_pc_ip(self, hostname):
        proc = subprocess.Popen(f'ping {hostname}', shell=True, stdin=None, stdout=subprocess.PIPE, stderr=True, text=True)
        out, err = proc.communicate()
        assert err is None, f"Could't ping the PC {hostname}"
        first_line = out.split("\n")[1]
        m = re.search(r"\[([0-9.]+)\]", first_line)
        ip = m.group(1)
        logging.info(f'IP address of PC {hostname} is {ip}')
        return ip

    def set_cleware_state_remotely(self, ip, status, port_no):
        logging.info(f'Turn Cleware switch : {port_no} of PC {ip} to {status}')
        path = os.path.dirname(os.path.abspath(__file__)) + f"{constants.CLEWARE_SWITCH}"
        def execute_and_get_output(cmd_str):
            proc = subprocess.Popen(['powershell.exe', cmd_str], shell=True, stdin=None, stdout=subprocess.PIPE, stderr=True)
            try:
                out, err = proc.communicate(timeout=30)
            except subprocess.TimeoutExpired as e:
                assert True, f"TimeoutExpired during executing {str(e)}"
                logging.info("TimeoutExpired during executing command")
            out = out.decode("utf-8")
            assert err is None or 'Exception' in out, f"Cleware operation: get switch #{port_no} current status is not performed properly. It returned error : {err}"
            return out

        execute_and_get_output(f'robocopy {path} \\\\{ip}\\d\\ClewareAutomation')    
        script_path = f'python D:\\ClewareAutomation\\POWER_ON-OFF_Control.py {port_no} {status}'

        read_state_cmd_str = f'{path}\\WmiExec.ps1 -ComputerName {ip} -Command "{script_path}"'
        out = execute_and_get_output(read_state_cmd_str)
        self.cleware_state_logging(out)
        
    def cleware_state_logging(self, out):
        out = out.strip()
        if re.search(r'found', out):
            if re.search(r'Hence, Cleware switch', out):
                logging.info(re.search(r'Binary state of port.*', out).group())
                logging.info(re.search(r'Hence, Cleware switch.*', out).group())
            elif re.search(r'Cleware switch port:', out):
                logging.info(re.search(r'Cleware switch port:.*', out).group())
        else:
            logging.info("Output is empty")
            assert False, f"Cleware operation is not performed, it returned null output."

    def copy_to_device_with_scp(self, device_type, hostname, ssh_key, source, destination, logpath = None):
        logging.info('Starting SCP process...')
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_username, ssh_password, ssh_pkey = self.__get_ssh_creds(ssh_key)
        c.connect( hostname, 22, username=ssh_username, password=ssh_password, pkey = ssh_pkey, timeout=5 )
        scp = SCPClient(c.get_transport())
        scp.put(source, destination)

    def copy_to_repo_with_scp(self, device_type, hostname, ssh_key, source, destination):
        logging.info('Starting SCP process...')
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_username, ssh_password, ssh_pkey = self.__get_ssh_creds(ssh_key)
        c.connect( hostname, 22, username=ssh_username, password=ssh_password, pkey=ssh_pkey, timeout=5 )
        scp = SCPClient(c.get_transport())
        scp.get(source, destination)

    def parse_json_file(self, file_path):
        """  path should be from root of the repository  """
        path = os.path.dirname(os.path.abspath(__file__)) + "\\..\\..\\..\\..\\" + file_path
        with open(path, 'r') as dataFile:
            json_data = json.load(dataFile)
        return json_data
    
    def write_json_file(self, file_path, json_obj):
        """  path should be from root of the repository  """
        path = os.path.dirname(os.path.abspath(__file__)) + "\\..\\..\\..\\..\\" + file_path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as dataFile:
            dataFile.write(json.dumps(json_obj, indent=2))

    def check_file_availability(self, file_path):
        """  path should be from root of the repository  """
        path = os.path.dirname(os.path.abspath(__file__)) + "\\..\\..\\..\\..\\" + file_path
        return os.path.isfile(path)
    
    def check_file_size(self, file_path):
        """  path should be from root of the repository  """
        path = os.path.dirname(os.path.abspath(__file__)) + "\\..\\..\\..\\..\\" + file_path
        return os.path.getsize(path)
    
    def get_feature_cucumber_result(self, cucumber_rep_path, feature_count = 1):
        """  path should be from root of the repository  """
        cucumber_report_path = os.path.dirname(os.path.abspath(__file__)) + "\\..\\..\\..\\..\\" + cucumber_rep_path
        final_data = []
        with open(cucumber_report_path, "r") as file:
            datafile =file.read()
        try:
            result_data = json.loads(datafile)
        except json.JSONDecodeError:
            result_data = json.loads(datafile+ "]")
        final_data.append(result_data[feature_count-1])
        return final_data
    
    def clean_up_folder(self, dir_path_from_root):
        """  Performs cleanup of defined directory """
        folder = os.path.dirname(os.path.abspath(__file__)) + "\\..\\..\\..\\..\\" + dir_path_from_root
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    logging.error(f'Failed to delete {file_path} Reason: {e}')

    def ssh_execute_without_encoding(self, hostname, ssh_key, command, logpath = None):
        
        ssh_username, ssh_password, ssh_pkey = self.__get_ssh_creds(ssh_key)
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect( hostname = hostname, username = ssh_username, password= ssh_password, pkey = ssh_pkey)
        stdin , stdout, stderr = c.exec_command(command)
        out = stdout.read().decode('utf-8')
        err = stderr.read().decode('utf-8')
        
        c.close()
        return (out, err)

    def assert_message(self, response_detail):
        try:
            if "error" in response_detail.json():
                if "statusCode" in response_detail.json():
                    return f'Failed with Response code - {response_detail.json()["statusCode"]}, Type - {response_detail.json()["error"]}, Error message - {response_detail.json()["message"]}'
                else:
                    return f'Failed with Response code - {response_detail.json()["status"]}, Type - {response_detail.json()["error"]}, Error message - {response_detail.json()["message"]}'
            elif "detail" in response_detail.json():
                return f'Failed with Response code -{response_detail.json()["status"]}, Detail - {response_detail.json()["detail"]}'
            else:
                return f'API request failed with response code {response_detail.status_code}'
        except json.decoder.JSONDecodeError:
            return f'Response body is absent. API request failed with response code {response_detail.status_code}'

    def start_timer(self):
        logging.info(f"Timer started: Total time - , {self.timeout_time}")
        self.timer = Timer(self.timeout_time, self.timeout)
        self.timer_start_time = time.time()
        self.timer.start()

    def check_timer(self):
        logging.debug(f"Timer current value is {self.fetch_time_difference(self.timer_start_time)} and Timer remaining value is {int(self.timer.interval - (self.fetch_time_difference(self.timer_start_time)))}")
        return self.timer.isAlive() if sys.version_info.minor < 9 else self.timer.is_alive()

    def fetch_time_difference(self, start_time):
        time_diff = int((time.time() - start_time))
        return time_diff

    def stop_timer(self):
        logging.info("Timer Cancelled: Expected Job has been achieved or failed")
        self.timer.cancel()

    def timeout(self):
        logging.info("Timeout - Timer thread has ended")

    def update_timeout_time(self, timer):
        self.timeout_time = int(timer)

    def split_string(self, given_string, split_point):
        split_list = given_string.split(split_point)
        return split_list
    
    def is_approximately_equal(self, ref_val, actual_value, variation_in_percentage):
        if (ref_val-(ref_val*variation_in_percentage/100)) <= actual_value <= (ref_val+(ref_val*variation_in_percentage/100)):
            return True
        return False

    def get_token_details_for_logout(self):
        token_details = self.parse_json_file(constants.TEST_DATA_TOKEN_JSON)
        id_token = token_details["id_token"]
        environment = token_details["environment"]
        return id_token, environment

    def delete_token_details(self):
        path = os.path.dirname(os.path.abspath(__file__))
        token_path = path + constants.TEST_DATA_TOKEN
        os.remove(token_path)

    def test_waits_to_reach_wakeup_time(self, context, moment):
        if '-' in moment:
            moment_value = datetime.datetime.strptime(moment[1:-1],constants.GC_DATE_AND_TIME)
            moment_value = str(moment_value - datetime.datetime.utcnow()).split(':')
            seconds = int(moment_value[0])*3600 + int(moment_value[1]) * 60 + float(moment_value[2]) 
        else:
            time_value = moment.split(':')
            day_value = time_value[0]
            hour = time_value[1]
            minute_value = time_value[2]
            diff_utc = datetime.datetime.utcnow() + timedelta(days= int(day_value[1:]), hours=int(hour), minutes=int(minute_value[:2]), seconds=0)
            seconds = str(diff_utc - datetime.datetime.utcnow()).split(':')
            seconds = int(seconds[0])*3600 + int(seconds[1]) * 60 + float(seconds[2])
            
        if seconds > 120:
            added_utc = datetime.datetime.utcnow() + timedelta(days=0,hours=0, minutes=0,seconds=120)
            added_utc = datetime.datetime.strftime(added_utc,constants.GC_DATE_AND_TIME)
            added_utc = datetime.datetime.strptime(added_utc, constants.GC_DATE_AND_TIME).strftime('%S %M %H %d %m ? %Y')
            api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env,context.log_api_details)
            wakeup_config = api_fm_obj.vehicle_wakeup_config_present(context.vehicle_id, context.device_slot_name,"TIMER")
            if wakeup_config != None:
                time_config = {
                    "type":f"{wakeup_config['type']}",
                    "state":"ENABLED",
                    "cronExpression":added_utc,
                    "duration":context.duration,
                    "wakeUpConfigurationId":f"{wakeup_config['wakeUpConfigurationId']}"
                }   
                api_fm_obj.update_wakeup_config(context.vehicle_id, context.device_slot_name, context.wakeup_config_id, time_config)   
            else:
                time.sleep(seconds)

    def write_vin_to_ascii(self, vin_hex, path, implantation_method):
        f = open(path, 'r')
        line_list = f.readlines()
        f.close()
        fw = open(path, 'w')
        begin_index = 0
        logging.info('ASCII file -')
        for i in range(len(line_list)): #iterates based on number of lines in asc file
            line = line_list[i]
            line = line.strip()
            if i >= len(line_list)-3 and implantation_method == "CAN_HINO": # len(line_list) = 4 and 1st iteration will be skipped for 'CAN' implantation_method to igonore 1st line in asc file
                if i == len(line_list)-3: 
                    number_of_char = 8    # if i = 1 / assigning number_of_char = 8 to update last 8 values in 2nd line 
                else:
                    number_of_char = 20   # if i > 1 / assigning number_of_char = 20 to update last 20 values in 3rd and 4th line
                begin_index, line = self.create_line_data_in_ascii(vin_hex,begin_index,number_of_char,line,implantation_method,i)
            elif i >= len(line_list)-3 and implantation_method == "CAN_PACCAR": # len(line_list) = 4 and 1st iteration will be skipped for 'CAN' implantation_method to igonore 1st line in asc file
                # if i <= len(line_list)-2: 
                number_of_char = 20   # if i = 1 / assigning number_of_char = 8 to update last 8 values in 2nd line 
                # else:    
                    # if i > 1 / assigning number_of_char = 20 to update last 20 values in 3rd and 4th line
                begin_index, line = self.create_line_data_in_ascii(vin_hex,begin_index,number_of_char,line,implantation_method,i)            
            elif i >= len(line_list)-3 and implantation_method == "UDS": # len(line_list) = 3 for 'UDS' implantation_method
                if i <= len(line_list)-3:
                    number_of_char = 8    # if i = 0 / assigning number_of_char = 8 to update last 8 values in 1st line
                else:
                    number_of_char = 20   # if i > 0 / assigning number_of_char = 20 to update last 20 values in 2nd and 3rd line
                begin_index, line = self.create_line_data_in_ascii(vin_hex,begin_index,number_of_char,line,implantation_method,i)
            logging.info(f'{line}')
            fw.write(f'{line}\n')
        fw.close()

    def create_line_data_in_ascii(self, vin_hex,begin_index,number_of_char,line,implantation_method,iteration):
        first_position = number_of_char + 2
        last_index = begin_index + number_of_char
        new_character = vin_hex[begin_index:last_index]     # fetching characters from vin hex data based on begin and last index values
        if implantation_method == "CAN_PACCAR" and iteration == 3:
            line = line[:line.index('Length')-first_position] + new_character + line[line.index('Length')-14:]   # replacing the new_character in asc file based on first_position
        else:
            line = line[:line.index('Length')-first_position] + new_character + line[line.index('Length')-first_position+number_of_char:]   # replacing the new_character in asc file based on first_position
        begin_index = last_index + 1
        return begin_index, line

    def check_token_expiry(self, expiry_time):
        sys_time = time.time() + 10
        if sys_time < float(expiry_time):
            return True
        else:
            return False

    def check_token_environment(self, token_details, environment):
        token_env = token_details["environment"]
        if environment == token_env:
            return True
        else:
            return False

    def set_device_time_with_difference(self, context, process_time):
        proc = self.start_process_with_command("powershell [DateTime]::Now.ToUniversalTime().AddSeconds("+str(process_time)+").ToString('yyyy-MM-dd HH:mm:ss')")
        assert proc.stderr is None, "Process couldn't be started properly. It returned error."
        device_time = proc.communicate()[0].decode('utf-8').strip()
        cmd_set_device_time = f'date -s "{device_time}"'
        self.ssh_execute(context.devices_data['CCU']['CCU_IP'],context.device_config_data['ssh_key'],cmd_set_device_time)

    def update_version_json(self, specimen_device, device_id, customer_type, environment,fw_version):
        version_details = self.parse_json_file('version.json')
        version_details[specimen_device]['Selected'] = 'True'
        version_details[specimen_device]['Device-ID'] = device_id
        version_details[specimen_device]['Customer'] = customer_type
        version_details[specimen_device]['Environment'] = environment
        version_details[specimen_device]['Tenant'] = self.get_tenant_for_space(environment)
        if(fw_version!=''):
            version_details[specimen_device]['Version']['FW-Version'] = fw_version
        self.write_json_file('version.json', version_details)

    def get_seed_from_vrs_response(self, path, seed_image):
        with open(path) as asc:
            lines = [line.rstrip() for line in asc]
        try:
            vrs_response = [i for i, s in enumerate(lines) if seed_image in s]
            seed = lines[vrs_response.pop()].split(seed_image)[1].replace(" ", "")
        except IndexError:
            assert False, 'No Seed found in vrs_repsone. Error during VIN Pairing or unpairing'
        return seed[0:8]

    def write_key_to_ascii(self, path, key):
        with open(path) as asc:
            line_list = asc.readlines()
        line = next(iter(line_list))
        line = line[:line.index('Length') - 4] + key + line[line.index('Length') - 5:]
        with open(path, 'w') as asc:
            asc.write(line)

    def get_dtc_mask_from_vrs_response(self, path, dtc_image):
        with open(path) as asc:
            lines = [line.rstrip() for line in asc]
        vrs_response = [i for i, s in enumerate(lines) if dtc_image in s]
        if vrs_response:
            dtc = lines[vrs_response.pop()].split(dtc_image)[1].replace(" ", "")
            return dtc[0:2]
        return None

    def convert_hex_to_binary(self,hex_value):
        end_length = len(hex_value) * 4
        padded_binary = bin(int(hex_value, 16))[2:].zfill(end_length)
        logging.info(f'Converted Binary value : {padded_binary}')
        return padded_binary

    def get_vin_from_ascii(self, path, bus):
        hex_value = " "
        with open(path) as asc:
            vin_list = asc.readlines()
        line_diff = 2 if bus == "UDS" else 3
        for i in range(len(vin_list)):
            line = vin_list[i]
            if i >= (len(vin_list) - 3):
                if i >= (len(vin_list) - line_diff):
                    hex_value = hex_value + line[line.index('Length') - 22:].split(" Length")[0]
                else:
                    hex_value = hex_value + line[line.index('Length') - 10:].split(" Length")[0]
        hex_value = " ".join(hex_value.strip().split(" ", 17)[:17])
        return bytearray.fromhex(hex_value).decode()

    def fetch_vrs_can_port(self, test_device, count, devices_data):
        try:
            if (count <=2):
                vrs_can_port = devices_data[test_device]["vrs_port"]
            elif (count > 2 and count <=3):
                vrs_can_port = devices_data[test_device]["vrs_port_2"]
            elif (count > 3 and count <=5):
                vrs_can_port = devices_data[test_device]["vrs_port_3"]
            elif (count > 5 and count <=7):
                vrs_can_port = devices_data[test_device]["vrs_port_4"]
            else:
                assert False, "More than 7 VRS trigger is requested. Not possible with current HW setup."
        except KeyError as e:
            logging.warning(f"{e}")
            assert False, "VRS port details are not available for device" + test_device + " for count:" + count

        return vrs_can_port

    def modify_device_file_to_enable_geo_tracking(self, root, name_space):

        for char in root.findall(f'.//config:key/..', name_space):
            key = char.find(f'.//config:key[1]', name_space)
            if(key.text == "GPS_DATA"):
                boolean_value = char.find(f'.//config:value//config:entry[1]//config:booleanValue', name_space)
                logging.info(f"TRACKING_ENABLED |-->, {boolean_value.text}")
                if(boolean_value.text == 'false'):
                    boolean_value.text = 'true'
                    file_modified = True
                integer_value = char.find(f'.//config:value//config:entry[2]//config:integerValue', name_space)
                logging.info(f"DATA_COLLECTION_PERIOD |-->, {integer_value.text}")
                if(integer_value.text != '10'):
                    integer_value.text = '10'
                    file_modified = True

        return file_modified

    def retrieve_file_path(self, context, space, type, temp):     
        if space == "same" and type == "same" and ((context.test_device in temp) and (context.device_id not in temp) and (context.env in temp)):
            file_path = temp
        if space == "same" and type == "different" and ((context.test_device not in temp) and (context.env in temp)):
            file_path = temp
        if space == "different" and type == "same" and ((f"\\{context.env}\\" not in temp) and (context.test_device in temp)):
            file_path = temp
        if space == "different" and type == "different" and ((context.env not in temp) and (context.test_device not in temp)):
            file_path = temp

        return file_path

    def verify_vin_mismatch_event_is_true(self, dtc_binary):
        if(dtc_binary != "11"):
            assert False, "VIN Mismatch event is False by reading DTC after VIN implantation"
        else:
            logging.info("VIN Mismatch event is True by reading DTC after VIN implantation")

    def check_access_token(self,services_check_url,basic_auth_header):
        data = {
            'grant_type': "client_credentials",
            'scope': "prod/generatePackage"   
        }

        expected_access_token_template = {
            "access_token": "",
            "expires_in": "",
            "token_type": ""
        }

        r = requests.post(services_check_url , data, headers = basic_auth_header)
        assert r.status_code == requests.codes.ok, self.assert_message(r)
        
        assert expected_access_token_template.keys()==r.json().keys(),f"The expected access token template is {expected_access_token_template} is not matching with actual {r.json().keys()}"

        logging.info("The expected access token response is generated")


    def services_health_check(self,health_check_url):

        expected_template = {
                "percentageFree": "",
                "memCommitted": "",
                "memInit": "",
                "memMax": "",
                "memUsed": "",
                "id": ""   
        }

        r=requests.get(health_check_url)
        assert r.status_code == requests.codes.ok, self.assert_message(r)
        response_jsondata=r.json()

        assert expected_template.keys()== response_jsondata.keys(),f"The expected template {expected_template.keys()} is not matching with actual template {response_jsondata.keys()}"
        logging.info("The service is up and responding") 

    def parse_yaml_json(self, file_path):
        """  path should be from root of the repository  """
        path = os.path.dirname(os.path.abspath(__file__)) + "\\..\\..\\..\\..\\" + file_path
        with open(path, "r") as stream:
            try:
                yaml_data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                logging.error(exc)
        return yaml_data

    def update_meas_config_name(self, context, active_outline_headings):
        for active_outline_header in active_outline_headings:
            match_object = re.search(r"^meas.*Name$", active_outline_header, flags=re.IGNORECASE)
            config_name =  context.active_outline[active_outline_header].replace('"','')
            config_name_flag = re.search(r"^E2E_.*", config_name, flags=re.IGNORECASE) or re.search(r"^CCU_.*", config_name, flags=re.IGNORECASE)
            if match_object and config_name_flag :
                context.update_meas_config_name = context.active_outline[active_outline_header].strip('\"') + "_" + context.device_config_data["baud_rate"]
                logging.info(f"Updating measurement configuration name as {context.update_meas_config_name} for {context.customer_type} Device")
                break

    def get_user_guide_content(self,value):
        r = requests.get(constants.GC_USER_GUIDE_URL.format(value),headers={"user-agent":"Chrome"})
        assert r.status_code == requests.codes.ok, self.assert_message(r)
        return r.text
    
    def device_availablity_on_system(self,hostname,device_id, expected_status):
        actual_status=''
        proc = subprocess.Popen("ipconfig", shell=True, stdin=None, stdout=subprocess.PIPE, stderr=True)
        proc.wait()
        out,err = proc.communicate()
        assert err is None, f"unable to fetch ipconfig details in test machine: {err}"
        device_host = ''.join(hostname.rpartition('.')[:2])
        if device_host in str(out):
            actual_status = "ON"
        else:
            actual_status = "OFF"
        assert expected_status == actual_status,f"Device - {device_id} with this hostname {hostname} is is not in expected state"
        logging.info(f"Device {device_id} with hostanme {hostname} is {actual_status}")
    
    def verify_ssh_connection_status(self, hostname,ssh_key, connection_status):
        out,err = self.ssh_execute(hostname,ssh_key,"date")
        if not str(out).strip():
            actual_status = 'OFF'
        else:
            actual_status = 'ON'
        assert actual_status == connection_status,f"Expected SSH status is {connection_status} but actual SSH status is {actual_status}, which is not expected behaviour"
        logging.info(f"SSH  connection is {actual_status}")

            
    def override_psfile(self, path):
        with open(path,'r') as f:
            line_list = f.readlines()
        updated_line = ""
        lines_removed_1,lines_removed_2 = False, False
        lines_to_remove = []
        for i in range(len(line_list)):
            line = line_list[i]
            line = line.strip()
            if "$exitcode" in line and not lines_removed_1:
                lines_to_remove = self.get_index_of_lines_to_del(line_list, i+2, "$exitcode")
                lines_removed_1 = True
            elif "$Result" in line and not lines_removed_2:
                line = line[:10] + '"No"'
                lines_removed_2 = True
                lines_to_remove = self.get_index_of_lines_to_del(line_list, i+1, "$Result")
            elif "-1g.ubifs" in line:
                line = line[:10] + '"' + 'bosch-system-development-1g.ubifs' + '"' + '}'
            if i not in lines_to_remove:
                logging.info(f'>>>>{line}')
                updated_line = updated_line + f'{line}\n'
        with open(path, 'w') as fw:
            fw.write(updated_line)
                
    def get_index_of_lines_to_del(self, line_list, index, function_name):
        index_of_lines = []
        for j in range(index, len(line_list)):
            if function_name not in line_list[j]:
                index_of_lines.append(j)
            else:
                break
        return index_of_lines  

    def get_firmware_version_from_device(self, command_map, test_device, ccu_ip, ssh_key):
        command  = command_map['getCCUVersion'][test_device]
        fw_version = None
        device_data = self.ssh_execute(ccu_ip, ssh_key, command)
        if device_data[0] == " ":
            logging.error(f"Unable to fetch Device FW from Device, error:{device_data[1]}")
        else:
            fw_data = re.search(constants.DEVICE_FW_VALUE_REGEX, str(device_data[0]))
            if(fw_data!= None):
                fw_version = fw_data.group(1)
                if len(fw_version)> 3 and fw_version[2] == "_" and fw_version[:2].isalpha():
                    logging.debug(f"Removing environment from fw version: {fw_version}")
                    fw_version = fw_version[3:]
                logging.info(f"Firmware version in Device with IP {ccu_ip}: {fw_version}")
        return fw_version

    def fetch_fw_based_on_customer(self, device_type):
        fw_version = constants.INITIAL_DEFAULT_VERSION
        desired_fw_version = self.parse_json_file(constants.DESIRED_FW_FILE)
        if (device_type in desired_fw_version):
            fw_version = desired_fw_version[device_type]
        return fw_version
    
    def update_env_based_on_customer(self, desired_default_fw_versions, artifact_customer, latest_fw_value):
        updated_list_value = []
        for desired_default_fw_version in desired_default_fw_versions.split(','):
            if artifact_customer.upper() in desired_default_fw_version:
                desired_default_fw_version = desired_default_fw_version.replace(desired_default_fw_version.split(':')[1],latest_fw_value) 
            updated_list_value.append(desired_default_fw_version) 
        updated_value = ','.join(updated_list_value)
        return updated_value

    def update_yaml_file(self,desired_default_fw_versions, artifact_customer, latest_fw_value):
        updated_value = self.update_env_based_on_cutomer(desired_default_fw_versions, artifact_customer, latest_fw_value)
        logging.info("Updating test_suite_executor.yaml file")
        file_path = os.path.dirname(os.path.abspath(__file__)) + constants.GC_TEST_SUITE_EXECUTOR_YAML 
        config, ind, bsi = ruamel.yaml.util.load_yaml_guess_indent(open(file_path))
        config['jobs']['Test_Executor']['env']['DESIRED_DEFAULT_FW_VERSION'] = updated_value
        yaml = ruamel.yaml.YAML()
        yaml.indent(mapping=ind, sequence=ind, offset=bsi) 
        with open(file_path, 'w') as fp:
            yaml.dump(config, fp)
        self.push_changes_to_repo('test_suite_executor.yaml', file_path)

    def update_default_customer_fw(self, device_type, version):
        desired_fw_version = self.parse_json_file(constants.DESIRED_FW_FILE)
        desired_fw_version[device_type] = version
        self.write_json_file(constants.DESIRED_FW_FILE, desired_fw_version)
    
    def push_changes_to_repo(self, file_name, file_path):
        logging.info(f"Pushing {file_name} changes to repo")
        repo = git.Repo(os.path.dirname(os.path.abspath(__file__))+ constants.GC_GIT)
        repo.git.add(file_path)
        repo.git.commit('-m', f'Updating {file_name}')
        origin = repo.remote(name='origin')
        origin.push()
        logging.info(f"Completed pushing {file_name} changes to repo")
    
    def verify_message_in_can(self, path, message_id, expected_message_data):
        with open(path) as asc:
            lines = [line.rstrip() for line in asc]
        assert [actual_data for iterator, actual_data in enumerate(lines) if message_id in actual_data if expected_message_data in actual_data],f"The expected message id {message_id} or message data {expected_message_data} not found in CAN bus"
        logging.info(f"The Expected message id {message_id} with message data {expected_message_data} is found on CAN bus.")

    def get_similar_devices_from_device_map(self, device_type, env):
        """Gets list of devices with similar config on the particular environment

        Args:
            device_type (str): Device type, will be matched with devices in deviceMap.json
            env (str): Environment of the Devices

        Returns:
            list: Device list
        """
        device_map_data = self.parse_json_file(constants.DEVICEMAP_JSON)
        expression= f"$..[?(@.device_env=='{env}' && @.device_config=='{device_type}')].device_name"
        device_ids = jsonpath.findall(expression, device_map_data)
        logging.info(f"Following Devices are having similar device_type and env :  {device_ids}")
        return device_ids

    def generate_key_from_seed(self, hex_string):
        """Generates the Key for the given seed

        Args:
            hex_string : hex string of the seed
        Returns: 
            key_string : generated key from seed
        """
        y_factor = int(str(00), 16)
        z_factor = int(str("733007B3"), 16)
        key = []

        if len(hex_string) % 2 != 0:
            hex_string = "0" + hex_string

        hex_list = [hex_string[i:i+2] for i in range(0, len(hex_string), 2)]
        hex_list = ["0x" + value for value in hex_list]

        x_factor = hex_list[2]
        x_factor = int(x_factor, 16) << 24
        x_factor = x_factor | y_factor
        x_factor = x_factor + 0x51000000

        y_factor = hex_list[1]
        y_factor = int(y_factor, 16) << 16
        x_factor = x_factor | y_factor
        x_factor = x_factor + 0x00F90000

        y_factor = hex_list[3]
        y_factor = int(y_factor, 16) << 8
        x_factor = x_factor | y_factor
        x_factor = x_factor + 0x00008100

        y_factor = hex_list[0]
        x_factor = x_factor | int(y_factor, 16)
        x_factor = x_factor + 0x000000A8

        tester_key = x_factor^z_factor 

        key.append(tester_key & 0x000000FF)
        key.append((tester_key & 0x0000FF00) >> 8)
        key.append((tester_key & 0x00FF0000) >> 16)
        key.append((tester_key & 0xFF000000) >> 24)

        key_list = [hex(value)[2:].zfill(2).upper() for value in key]
        logging.info(f"Generated Key from Seed: {key_list}")
        return " ".join(key_list)
    

    def get_file_name(self,path, file_regex):
        """ Fetches the list of available files in the file path"""     
        files = glob.glob(os.path.join(path, "**", file_regex), recursive=True)
        return files
      
    def validate_gpsdata_from_response(self, asc_path, gps_exp_data):
        count_dict = {'expected_data' : [], 'wrong_data' : []}

        with open(asc_path) as asc:
            lines = asc.readlines()

        for can_id, exp_indexes in gps_exp_data.items():
            for line in lines:
                if can_id in line:
                    byte_list = line.split('d 8')[1].split('Length')[0].strip().split(' ') #['FF','FF','FF','FF','FF','FF','2A','5A']
                    if False not in [True if byte_list[index] != 'FF' and byte_list[index] != '00' else  False for index in exp_indexes ]:
                        count_dict['expected_data'].append(byte_list)
                    else:
                        count_dict['wrong_data'].append(byte_list)
            logging.debug(f'Expected data appeared {len(count_dict["expected_data"])} times')
            logging.debug(f'Wrong data appeared {len(count_dict["wrong_data"])} times')
            assert len(count_dict['expected_data']) > len(count_dict['wrong_data']), f'{can_id} doesnt has expected data. Expecting data every time at this index - {exp_indexes}. Expected data appeared {len(count_dict["expected_data"])} times and Wrong data appeared {len(count_dict["wrong_data"])} times'
            self.check_latitude_longitude(count_dict['expected_data'][0], can_id)
            count_dict = {'expected_data' : [], 'wrong_data' : []}
                
    def check_latitude_longitude(self,hex_list, can_id):
        if can_id == '18FEF32Bx':
            location = {}
            half_len = len(hex_list)//2
            chunck_hex_lists = [hex_list[i:i+half_len] for i in range(0, len(hex_list), half_len)]
            for index in range(len(chunck_hex_lists)):
                chunck_hex_lists[index].reverse()
                hex_string = ''.join(chunck_hex_lists[index])
                decimal_result = int(hex_string, 16)
                if 'latitude' not in location:
                    location['latitude'] = decimal_result * 0.0000001 - 210
                    assert constants.STUTTGART_LATITUDE_RANGE[0] < location['latitude'] < constants.STUTTGART_LATITUDE_RANGE[1], f'Latitude value of GPS is wrong. Actual latitude value is {location["latitude"]}, expected value is within the range of 47.7 - 49.7' 
                else:
                    location['longitude'] = decimal_result * 0.0000001 - 210
                    assert constants.STUTTGART_LONGITUDE_RANGE[0] < location['longitude'] < constants.STUTTGART_LONGITUDE_RANGE[1], f'Longitude value of GPS is wrong. Actual longitude value is {location["longitude"]}, expected value is within the range of 8.4 - 10.4' 
            logging.info(f'Latitude and Longitude valus of GPS is in expected range - {location}')







