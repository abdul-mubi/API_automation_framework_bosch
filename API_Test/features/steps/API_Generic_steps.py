import requests
import logging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import os
import time
import math
import subprocess
from subprocess import Popen
import utils.API_Requests as API_Requests
import steps.pageObjects.API_Generic_Class as API_Generic_Class
import steps.pageObjects.API_FleetManagement_Class as API_FleetManagement_Class
import socket
import json
import shutil
from xml.etree import ElementTree
import random
import datetime
import steps.constantfiles.constants_generic as constants
from zipfile import ZipFile
import steps.pageObjects.API_OTA_Updates_Class as API_OTA_Updates_Class

@step('test bench information for device "{test_device}" is gathered')
def step_impl(context, test_device):
    """ 
    
    Descirption : Gathers all the necessary global information for the device specified from the DeviceMap.json

    """ 
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    context.test_device = api_gen_obj.device_type_selection(test_device)
    if context.test_device == "virtual_device":
        test_device = api_gen_obj.check_and_start_virtual_device(test_device,context.devices_data,context)
    context.specimen_device = test_device
    context.env = context.devices_data[test_device]["device_env"]
    context.device_id = context.devices_data[test_device]["device_name"]
    if "virtual_device" not in context.specimen_device:
        context.switch_ip = context.devices_data["switch_IP"]
        context.device_ip = context.devices_data[test_device][context.test_device+"_IP"]
        if context.devices_data[test_device]["switch_port_cl15"] != "":
            context.switch_port_cl15 = int(context.devices_data[test_device]["switch_port_cl15"])
        if context.devices_data[test_device]["switch_port_cl30"] != "":
            context.switch_port_cl30 = int(context.devices_data[test_device]["switch_port_cl30"])
        # if context.device_config_data["ssh_available"]:    
        #     context.execute_steps(f'''
        #         Given customer of the device is recognized
        #     ''')
        # else:
        #     context.customer_name = context.devices_data[test_device]["device_customer"]
        context.vrs_port = context.devices_data[test_device]["vrs_port"]
        if "vrs_port_2" in context.devices_data[test_device]:
            context.vrs_port_2 = context.devices_data[test_device]["vrs_port_2"]
        if "vrs_port_3" in context.devices_data[test_device]:
            context.vrs_port_3 = context.devices_data[test_device]["vrs_port_3"]
        if "vrs_port_4" in context.devices_data[test_device]:
            context.vrs_port_4 = context.devices_data[test_device]["vrs_port_4"]
    default_vin = context.devices_data[test_device]["vin"]
    if not hasattr(context, 'default_vehicle'):
        api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
        try:
            context.default_vehicle = api_fm_obj.get_vehicle_name_by_vin(default_vin)
        except AssertionError as e:
            logging.info(f"{e}, creating vehicle with the Default VIN")
            context.default_vehicle = default_vin+"_Vehicle"
            api_fm_obj.create_new_vehicle(context.default_vehicle, context, vin = default_vin)

@then('check if return code is "{return_code}"')
def step_impl(context, return_code):
    """the function checks if the appropriate return code is returned"""
    assert context.return_code == requests.codes[return_code]

@step('reference system "{protocol}" with Identifier "{identifier}" is started for "{test_device}" device')
@step('the "{count}"nd reference system "{protocol}" with Identifier "{identifier}" is started')
@step('reference system "{protocol}" with Identifier "{identifier}" is started')
def step_impl(context, protocol, identifier, count = "1", test_device = None):
    """ Descirption : Starts the Virtual reference System

    Pre-condition : None
    
    Parameters  : 
        Protocol : Describes which ECU / VRS is used
        
        identifier : The configuration (ini file) specific to device and test
    
    Expected result : 
        proc :  Handle of procedure created. If the handle is none, test is aborted
    
    """ 
    if context.test_device !="virtual_device":
        count = int(count)
        context.protocol = protocol
        identifier = identifier.split(',')
        context.identifier = identifier
        if "Paccar_RM" in context.identifier:
            path = os.path.dirname(os.path.abspath(__file__))
            asc_zip_file_path=path + constants.ASC_ZIP_FILE_PATH
            with ZipFile(asc_zip_file_path, 'r') as zip_file:   
                zip_file.extractall(path + constants.DATA_PATH)
        api_gen_obj = API_Generic_Class.ApiGenericClass()
        for identifier in context.identifier:
            protocol_name = protocol + "_" + context.device_id + "_" + str(count)
            if(test_device is not None):
                vrs_can_port = api_gen_obj.fetch_vrs_can_port(test_device, count, context.devices_data)
            else:
                test_device = context.specimen_device
                if (count <=1):
                    vrs_can_port = context.vrs_port
                # vrsPort2's capacity is reduced to accommodate only one VRS because 'CAN enabling' VRS is always run on it
                elif (count > 1 and count <=3):
                    vrs_can_port = context.vrs_port_2
                elif (count > 3 and count <=5):
                    vrs_can_port = context.vrs_port_3
                elif (count > 5 and count <=7):
                    vrs_can_port = context.vrs_port_4
                else:
                    assert False, "More than 7 VRS trigger is requested. Not possible with current HW setup."
            proc = api_gen_obj.initiate_vrs(context, protocol_name, identifier, vrs_can_port, test_device)
            context.vrs_running = True
            context.all_vrs_proc.append(proc)
            count +=1
        separation_time = api_gen_obj.fetch_separation_time(identifier)
        if separation_time is not None:
            context.separation_time = separation_time
    else:
        logging.info("VRS start is skipped for virtual device")

@step('reference system is stopped')
@step('all "{vrs_type}" reference system is stopped')
def step_impt(context, vrs_type = None):
    """ Descirption : Stops virtual reference system

    Pre-condition : step 'reference system "{Protocol}" with Identifier "{identifier}" is started'
    
    Parameters  : None
    
    Expected result : 
        r :  Boolean, returns 'True' if the VRS is successfully stoped.
    
    """    
    
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    r = api_gen_obj.stop_all_vrs(context.protocol_names, vrs_type) if len(context.protocol_names)>0 else True

    assert r is True, "Can Not Stop VRS"
    context.protocol_names.clear()
    context.vrs_running = False

@step('reference system "{protocol}" with Identifier "{identifier}" is stopped on "{test_device}" device')
@step('reference system with protocol "{protocol}" and Identifier "{identifier}" and number "{number}" is stopped')
@step('VRS with protocol "{protocol}" and identifier "{identifier}" is stopped')
def step_impl(context, protocol, identifier, number='1', test_device = None):
    """Stops the Virtual reference system"""
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    if(test_device is not None):
        vrs_name = f'{protocol}_{context.device_id}_{number}_{test_device}_{identifier}'
    elif number == "0" :
        vrs_name = f'{protocol}_{context.device_id}_{context.specimen_device}_{identifier}'
    else:
        vrs_name = f'{protocol}_{context.device_id}_{number}_{context.specimen_device}_{identifier}'
    api_gen_obj.stop_vrs_by_name(protocol, vrs_name)

@step('command "{command}" is executed on device "{device}"')
def step_impl(context, command, device):
    """ 
    
    Descirption : To perform command on device such as - Job cleanUp, reboot device, create folders on devices etc.

    Pre-condition : NA
    
    Parameters  : 
        command   : decides the command user does on device
                    Example:
                    operation = "deleteAllJobs"
                    operation = "rebootDevice"
        
        device      : decides the device selection to perfrom operation
                    Example:
                    device = "cTPG"
                    device = "ES740"
    
    Expected result : 
        No return value. Operation should be performed on device successfully
    
    """ 
    logging.info(f"Performing command {command} on device: {device}")

    api_gen_obj = API_Generic_Class.ApiGenericClass()
    if "CCU" in device:
        device_ip = "CCU_IP"
    else:
        assert False, 'Device unrecognized'
    if context.device_config_data['ssh_available']:
        context.result = api_gen_obj.ssh_execute(context.devices_data[device][device_ip],context.device_config_data['ssh_key'],command)
        context.start_timer = time.time()
    else:
        logging.info("skipped executing ssh command on prod device")

@step('device operation "{operation}" is performed on "{device_name}" device')
@step('device operation "{operation}" is performed')
def step_impl(context, operation, device_name = None):
    """ 
    
    Descirption : To perform operations on device such as - Job cleanUp, reboot device, deleteDeviceLogs on devices.

    Pre-condition : NA
    
    Parameters  : 
        operation   : decides the operation user does on device
                    Example:
                    operation = "deleteAllJobs"
                    operation = "rebootDevice"
                    operation = "deleteDeviceLogs"
        
        device      : decides the device selection to perfrom operation
                    Example:
                    device = "CCU"
    
    Expected result : 
        No return value. Operation should be performed on device successfully
    
    """ 

    api_gen_obj = API_Generic_Class.ApiGenericClass()
    command_map = api_gen_obj.parse_json_file(context.device_config_data["command_file"])
    
    def device_operation(device_name):
        """ 
        Description : Perform device operation for the specified device

        """ 
        try:
            if context.device_config_data["ssh_available"]:
                logging.info(f"Performing operation {operation} on device: {device_name}")
                
                test_device = context.devices_data[device_name]["device_type"]
                for command in command_map[operation][test_device]:
                    context.result = api_gen_obj.ssh_execute(context.devices_data[device_name][test_device + "_IP"],context.device_config_data['ssh_key'],command)
            elif operation in ["rebootDevice", "deleteAllJobs"]:
                logging.info(f"Assigning GradeX task {operation + '.zip'} on device {device_name}")
                context.execute_steps(f'''
                    When task "{operation + '.zip'}" is executed on "{device_name}" device
                    Then verify "EXECUTED" for "Task" is available within "2" minutes
                ''')
            else:
                logging.info(f"Skipped performing operation {operation} on device {device_name} as it is Production {context.customer_type} device")
        except Exception as e:
            logging.error(f"Failed to execute {operation} on device {device_name}, error: {e}")

    if (device_name != None and device_name.upper() == "ALL"):
        device_list = list(context.devices_data.keys())[1:]
        for device in device_list:
            device_operation(device)
    else:
        device = device_name if device_name != None else context.specimen_device
        device_operation(device)
        
    if (operation == "rebootDevice"):
        logging.info("Waiting for 90 seconds to let the device to reboot")
        time.sleep(90)

@step('test data details are fetched')
def step_impl(context):
    """

    Descirption : To gather all test data needed for the test corresonding to device.

    Pre-condition : NA
    
    Parameters  : 
        
        device      : decides the device selection to perfrom operation
                    Example:
                    device = "CCU"
                    device = "virtual_device"

    Return value    : type of device
    
    Expected result : It returns the type of device that leads to fetch complete test data from DeviceMap.json        

    """
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    
    test_data = api_gen_obj.parse_json_file(constants.DEVICEMAP_JSON)
    if "virtual_device" in context.specimen_device:
        context.devices_data = test_data["virtual_devices"]
    else:
        context.devices_data = test_data[socket.gethostname()]

    context.configs_data = api_gen_obj.parse_json_file(constants.DEVICE_CONFIG_JSON)

    
@step('verify the availability of "{information}"')
def step_impl(context,information):
    output = context.result[0]
    error = context.result[1]

    logging.info(f"Error : , {error}")
    logging.info(f"output : , {output}")

    assert error == "", "Command operation returned error"

    assert output != "", "Command operation did not return any output"
    
    pos = output.find(information)
    
    assert pos != -1, "Required Information is not available in output"

    logging.info(f"Required information is available at postion : ,{pos}")


@step('verify "{key}" path in device')
def step_impl(context,key):
    '''
    
    Descirption : To verify the path of the given file(key) in the dvice

    Pre-condition : command "{command}" is executed on device "{device}"
    
    Parameters  : 
        
        key      :  to form the filepath thats need to verify from Path.json
                    Example:
                    key = "keystore"
    
    Return value    : NA
    
    Expected result : It verifies the path of the Device from given information in Path.json with Pre-condition result


    '''
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    key_data = api_gen_obj.parse_json_file(constants.GS_TEST_DATA_PATH)[context.test_device][key]
    filename = ''
    try:
        filename = eval(f"{key_data['filename']}")+f"{key_data['fileformate']}"
    except Exception:
        filename = f"{key_data['filename']}{key_data['fileformate']}"
    file_path = f"{key_data['device_path']}{filename}"

    try:
        output = context.result[0].decode("utf-8")
        error = context.result[1].decode("utf-8")
    except Exception:
        output = context.result[0]
        error = context.result[1]

    logging.error(f"Error : , {error}")
    logging.info(f"output : , {output}")

    assert error == "", "Command operation returned error"

    assert output != "", "Command operation did not return any output"
    
    pos = output.find(file_path)
    
    assert pos != -1, "Required Information is not available in output"

    logging.info(f"Required information is available at postion : ,{pos}")



@step('switch "{port}" is turned "{status}"')
@step('wago "{port}" is turned "{status}"')
@step('ignition is turned "{status}"')
def step_impl(context, status, port="CL15"):
    '''
    
    Descirption : To turn on/off CL15/CL30 using Wago/Cleware

    Pre-condition : device should be connected to Wago/Cleware to turn on/off
    
    Parameters  : 
        
        port    :  CL15/Cl30
        status  :  On / Off 
    
    Return value    : NA
    
    Expected result : Turns on/off the CL15/CL30


    '''
    if port == "CL15":
        port_no = context.switch_port_cl15
    elif port == "CL30":
        port_no = context.switch_port_cl30
    else:
        assert False, "Unkown WAGO switch type input"

    api_gen_obj = API_Generic_Class.ApiGenericClass()
    if  context.switch_ip.upper() == 'CLEWARE':
        api_gen_obj.set_cleware_state(status, port_no)
    elif 'CLEWARE_' in context.switch_ip.upper():
        cleware_pc = context.switch_ip.split('_')[1]
        ip = api_gen_obj.fetch_pc_ip(cleware_pc)
        api_gen_obj.set_cleware_state_remotely(ip, status, port_no)
    elif len(context.switch_ip) == context.switch_ip.count(' '):
        assert False, "Switch IP is not avilable for this PC"
    else:
        proc = api_gen_obj.set_wago_power_state(status, context.switch_ip, port_no)
        assert proc.stderr is None, "WAGO operation: turn "+status+" is not performed properly. It returned error."
    if(status.upper() == "OFF"):
        setattr(context,f'{port}', False)
        context.cl15_off = True
        if port == "CL15":
            context.ignition_off_time = datetime.datetime.now(datetime.timezone.utc)
    if (status.upper() == "ON"):
        setattr(context,f'{port}', True)
        context.cl15_off = False
        if port == "CL15":
            context.ignition_on_time = datetime.datetime.now(datetime.timezone.utc)
    context.start_timer = time.time()
    time.sleep(10)

@step('command "{command}" is executed on Windows')
def step_impl(context, command):
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    proc = api_gen_obj.start_process_with_command(command)
    assert proc.stderr is None, "Process couldn't be started properly. It returned error."
    logging.info(proc.stdout)

@step('command to "{command}" GSM mode of the device')
@step('command to "{command}" GSM mode for "{device_name}" the device')
def step_impl(context,command,device_name=None):
    
    if device_name is not None:
        context.execute_steps(f'''
                Given device operation "{command}" is performed on "{device_name}" device
        ''')
        if command == "stopGSMConnection" and device_name == "all":
            context.stopGSM_for_all = True        
    else:
        context.execute_steps(f'''
                Given device operation "{command}" is performed
        ''')
        # if command.find("") == 0; it means, command has 'stop' included
        # if command.find("") == -1; it means, command doesn't have 'stop' included
        if("stopGSM" in command):
            context.gsm_stop = True

@step('create file to save version details')
def step_impl(context):
    '''
    
    Descirption : To create a json file to save version information of devices connected to System 

    Pre-condition : test data details are fetched
    
    Parameters  : NA
    
    Return value    : NA
    
    Expected result : It creates a file with version infor based of device details fetched from " Pre-condition " step

    '''
    dirpath = os.path.dirname(os.path.abspath(__file__))
    file_path = dirpath + constants.VERSION_JSON_PATH
    context.customer_type = context.devices_data[context.specimen_device]["device_config"]
    context.device_config_data = context.configs_data['default_properties']
    context.device_config_data.update(context.configs_data[context.customer_type])

    if os.path.exists(file_path) == False:
        version = {}
        for element in context.devices_data:
            try:
                if "CCU" in element:
                    CCU = {}
                    CCU['Version'] = {}
                    CCU['Version']['FW-Version'] = ''
                    CCU['Device-ID'] = context.devices_data[element]["device_name"]
                    CCU['Customer'] = context.devices_data[element]["device_config"].upper()
                    CCU['Environment'] = context.devices_data[element]["device_env"]
                    CCU['Tenant'] = ''
                    CCU['Selected'] = 'False'
                    version[element] = CCU
                elif "virtual_device" in element:
                    virtual_device = {}
                    virtual_device['Version']={}
                    virtual_device['Version']['FW-Version'] = ''
                    virtual_device['Device-ID'] = context.devices_data[element]["device_name"]
                    virtual_device['Environment'] = context.devices_data[element]["device_env"]
                    virtual_device['Tenant'] = ''
                    virtual_device['Selected'] = 'False'
                    version[element] = virtual_device
            except Exception as e:
                logging.warning(f'Problem with device {context.devices_data[element]["device_name"]} -> ${str(e)}')
        logging.info(f'Device details in the machine - {version}!')
        with open(file_path, 'w') as file:
            file.write(json.dumps(version, indent=2))    

@step('enable geo tracking on the device files if already not done')
def step_impl(context):
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    database_xml_paths = ['/usr/share/bosch/configs/pea_app/database.xml', '/media/bosch/data/pea_app/STORE/database.xml']
    reboot_required = False
    dirpath = os.path.dirname(os.path.abspath(__file__))
    command_map_path = dirpath + "\\..\\..\\..\\" + context.device_config_data["command_file"]
    with open(command_map_path, 'r') as dataFile:
        command_map = json.load(dataFile)
    for path_to_xml in database_xml_paths:
        file_modified = False
        database_file_content = api_gen_obj.ssh_execute_without_encoding(context.devices_data[context.specimen_device][context.test_device+"_IP"],context.device_config_data['ssh_key'],f"cat {path_to_xml}")
        if database_file_content[1] == "":
            content = database_file_content[0]
            tree = ElementTree.ElementTree(ElementTree.fromstring(content))
            root = tree.getroot()
            ElementTree.register_namespace('config', constants.GS_CONFIG_LINK)
            name_space = {'config': constants.GS_CONFIG_LINK}
            file_modified = api_gen_obj.modify_device_file_to_enable_geo_tracking(root, name_space)
            tree.write(dirpath+'\\database.xml')
            if file_modified == True:
                reboot_required = True
                logging.info(f'{path_to_xml} needs modification')
                command = command_map['accessToModifyDeviceFiles'][context.test_device]
                api_gen_obj.ssh_execute(context.devices_data[context.specimen_device][context.test_device+"_IP"],context.device_config_data['ssh_key'],command)
                api_gen_obj.copy_to_device_with_scp(context.test_device, context.devices_data[context.specimen_device][context.test_device+"_IP"], context.device_config_data['ssh_key'], dirpath+'\\database.xml', f'{path_to_xml[:-len("/database.xml")]}')
            else: logging.info(f'{path_to_xml} in proper condition')
        else: logging.info(f'File not found at {path_to_xml}')
    if reboot_required == True:
        for command in command_map['rebootDevice'][context.test_device]:
            api_gen_obj.ssh_execute(context.devices_data[context.specimen_device][context.test_device+"_IP"],"root","",command)
        context.execute_steps('''
        Given wait for device to be "ONLINE"
        ''')
        cmd_str = f"{dirpath}\\database.xml"
        Popen(['del', '/f', cmd_str], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
    time.sleep(5)

@step('copy device specfic file "{key}" to device')
def step_impl(context,key):
    '''
    
    Descirption : To copy a file from repo to device

    Pre-condition : NA
    
    Parameters  : 
    
                key: to get the file path of source and destination
                    source : file path in the repo
                    destination : path to copy in the device (from Path.json)
                    
                    Example : keystore
    
    Return value    : NA
    
    Expected result : It copies the file of given details to device 

    '''
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    dirpath = os.path.dirname(os.path.abspath(__file__))
    key_data = api_gen_obj.parse_json_file(constants.GS_TEST_DATA_PATH)[context.test_device][key]
    filename = ''
    try:
        filename = eval(f"{key_data['filename']}")+f"{key_data['fileformate']}"
    except Exception:
        filename = f"{key_data['filename']}{key_data['fileformate']}"
    remotepath = f"{key_data['device_path']}{filename}"
    file_path = dirpath + f"{constants.ENVIRONMENT_PATH}\\{context.env}\\{context.device_id}\\{filename}"
    logging.info(f"File copied from : {file_path}  - > to : {remotepath}")
    api_gen_obj.copy_to_device_with_scp(context.test_device, context.device_ip, context.device_config_data['ssh_key'],file_path,remotepath)
    if(hasattr(context, f'replace{context.key}') and (eval(f'context.replace{context.key}') is True)):
        logging.info(f"Replacing orginal file : {context.key}")
        setattr(context,f'replace{key}', False)

  

@step('copy file "{key}" to device from "{type}" deviceType and "{space}" space')
def step_impl(context,key,type,space):
    '''
    
    Descirption : To copy a file from repo to device

    Pre-condition :


    Parameters  : key, type , space
    
                key: to get the file path of source and destination
                    source : file path in the repo
                    destination : path to copy in the device (from Path.json)
                    
                    Example : keystore

                type: type of device

                    Example : ES740
                
                space: Enviorment on which the code is executing

                    Example : "integration"
                
    
    Return value    : NA
    
    Expected result : It copies the file of given details to device 

    '''
    context.key = key
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    dirpath = os.path.dirname(os.path.abspath(__file__))
    file_path = ''
    key_data = api_gen_obj.parse_json_file(constants.GS_TEST_DATA_PATH)[context.test_device][key]
   
    for root, dirs, files in os.walk( dirpath + f"{constants.ENVIRONMENT_PATH}", topdown=False):
       for name in files:
            temp = os.path.join(root, name)
            file_path = api_gen_obj.retrieve_file_path(context, space, type, temp)
            if file_path != '':
                break

    if file_path == '':
        assert False, f"Could not find the file satisifying condition file path : {type} devicetype in {space} envireonment"
    filename = ''
    try:
        filename = eval(f"{key_data['filename']}")+f"{key_data['fileformate']}"
    except Exception:
        filename = f"{key_data['filename']}{key_data['fileformate']}"
    remotepath = f"{key_data['device_path']}{filename}"
    logging.info(f"File copied from : {file_path}  - > to : {remotepath}")
    setattr(context,f'replace{key}', True)
    api_gen_obj.copy_to_device_with_scp(context.test_device, context.device_ip, "root","",file_path,remotepath)
   


@step('copy file "{key}" from device to repo')
def step_impl(context,key):
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    dirpath = os.path.dirname(os.path.abspath(__file__))
    key_data = api_gen_obj.parse_json_file(constants.GS_TEST_DATA_PATH)[context.test_device][key]
    file_path = dirpath + f"{constants.ENVIRONMENT_PATH}\\{context.env}\\{context.device_id}\\"
    api_gen_obj.copy_to_repo_with_scp(context.test_device, context.device_ip, "root","",key_data['device_path']+key_data['filename'],file_path)
    

@step('"{mode}" the content of file "{key}" with "{data}" and copy to device')
def step_impl(context, mode, data, key):
    '''
    
    Descirption : To append or replace the content of the file and copy to device
    Pre-condition : NA
    
    Parameters  : 
    
                key: to get the file path of source and destination
                    source : file path in the repo
                    destination : path to copy in the device (from Path.json)
                    
                    Example : keystore

                mode: to modify the cotent of the file

                    Example : append
                              replace
                
                data : content to modify the file

                    Example : "^465"
                              " "
    
    Return value    : NA
    
    Expected result : It copies the file of given details to device 

    '''
    context.key = key
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    dirpath = os.path.dirname(os.path.abspath(__file__))
    key_data = api_gen_obj.parse_json_file(constants.GS_TEST_DATA_PATH)[context.test_device][key]
    filename = ''
    try:
        filename = eval(f"{key_data['filename']}")+f"{key_data['fileformate']}"
    except Exception:
        filename = f"{key_data['filename']}{key_data['fileformate']}"
    remotepath = f"{key_data['device_path']}{filename}"
    file_path = dirpath + f"{constants.ENVIRONMENT_PATH}\\{context.env}\\{context.device_id}\\{filename}"
    if file_path == '':
        assert False, f"Could not find the file satisifying condition : file with {type} device type in {context.env} environment"
    new_fp = dirpath + f"{constants.TEMP_PATH}{filename}"
    shutil.copyfile(file_path,new_fp)
    file = ' '
    if mode == "append":
        file = open(new_fp,"a+")
    if mode == "replace":
        file = open(new_fp,"w")
    file.write(data)
    logging.info(f"File copied from : {new_fp}  - > to : {remotepath}")
    setattr(context,f'replace{key}', True)
    api_gen_obj.copy_to_device_with_scp(context.test_device, context.device_ip, "root","",new_fp,remotepath)
    
@step('set device time from the windows machine')
def step_impl(context):
    """ Description     : Resets the device time to 2 hours behind the PC time to which the device is connected to.

        Pre-condition       : None

        Parameters          : None

        Expected result     : The time and date of the device is at UTC i.e., 2 hours behind the current time of the PC time to which it is connected to.
    """
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    command_map = api_gen_obj.parse_json_file(context.device_config_data["command_file"])
    #this code is prone to 'Daylight savings
    start_time = time.time()
    # start_process_with_command has 5 seconds of internal wait, which is deleted from here.
    proc = api_gen_obj.start_process_with_command("powershell [DateTime]::Now.ToUniversalTime().AddSeconds(5).ToString('yyyy-MM-dd HH:mm:ss')")
    assert proc.stderr is None, "Process couldn't be started properly. It returned error."
    device_time = proc.communicate()[0].decode('utf-8').strip()
    cmd_set_device_time = command_map['setDate'][context.test_device].format(device_time=device_time)
    api_gen_obj.ssh_execute(context.devices_data[context.specimen_device]['CCU_IP'],context.device_config_data['ssh_key'],cmd_set_device_time)
    process_time = time.time() - start_time - 5
    if process_time > 3:
        logging.info("Device time has differnce of %d seconds. Adding %d seconds to device time"%(process_time,process_time))
        api_gen_obj.set_device_time_with_difference(context,process_time)
    # logging windows time and device time
    devicetime=api_gen_obj.ssh_execute(context.devices_data[context.specimen_device]['CCU_IP'],context.device_config_data['ssh_key'],"date")
    logging.info(f'Device time = {devicetime} and windows time = {str(datetime.datetime.now())}')
    

@step('test waits for a random time period of "{}" minutes')
def step_impl(context, time_span):
    """ Description     : Halts the execution for a randomly picked number of minutes in the range

        Pre-condition       : None

        Parameters          : {time period range}

                            eg. timeSpan = "3-5"
                            exmaple step - 'test waits for a random time period of "3.5-7" minutes'

        Expected result     : Execution halts for the randomly selected time period in the given range.
    """
    upper_lower_times = time_span.split('-')
    upper_time = float(upper_lower_times[0]) * 60 
    lower_time = float(upper_lower_times[1]) * 60
    random_time = random.randint(int(upper_time), int(lower_time))
    logging.info(f'Test execution is randomly waiting for {random_time} seconds')
    time.sleep(random_time)
    

@step('switch to "{space}"')
def step_impl(context, space):
    context.env = space
    if(len(space) == space.count(' ')):
        context.env = context.provisioning_target_space

@step('test waits for "{min}" minutes')
@step('test is executed for "{min}" minutes')
@step('test is executed for "{ms}" milliseconds')
@step('test is executed for "{sec}" seconds')
@step('test waits for "{min}" minutes where wait is "{include_wait}" in recording')
@step('test waits for "{min}" minutes where wait is "{include_wait}" in recording')     
def step_impl(context,min= None, ms=None,sec=None, include_wait = "not included"):
    """ Descirption : Test execution for given time

        Pre-condition : None        

         Parameters  : 
            Min : Time for test to execution   

        Expected result : 
              Test will sleep for duration given in minute
 
    """
    if include_wait == "included":
        if not hasattr(context, "count_timer"):
            context.count_timer = 0
        context.count_timer = context.count_timer + int(float(min))

    if(min is not None):
        context.test_duration = int(float(min) * 60 * 1000) # in milisecond
        timer = int(float(min) * 60)
        time.sleep(timer)   
    elif(ms is not None):
        context.test_duration = int(ms) # in milisecond
        timer = int(ms) / 1000
        time.sleep(timer)
    else:
        context.test_duration=int(sec)*1000
        timer = int(sec)
        time.sleep(timer)


@step('test waited till device wakeup configuration time {moment} is met') 
def step_impl(context, moment):
    '''
    Descirption : test waits for particular {time}.

    Parameters  : time string
        Examples: 
            18-01-2020, 18:45 {%d-%m-%Y, %H:%M} - time should be in reference to the utc time 
            or
            000:00:10 {%d:%H:%M}
           
    Expected result : test should able to wait for particular {time}

    '''
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    api_gen_obj.test_waits_to_reach_wakeup_time(context, moment)
    
@step('logout from the application')
def step_impl(context):
    """ Description     : Logout from the application

        Pre-condition       : None

        Parameters          : None
    """
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    id_token, environment = api_gen_obj.get_token_details_for_logout()
    api_request = API_Requests.ApiRequestsClass(environment, context.log_api_details)
    api_request.logout_from_app(id_token)
    api_gen_obj.delete_token_details()
    api_gen_obj.clean_up_folder("temp")


@step('verify device status stayed in "{status}" for "{moment}"')
def step_impl(context, status, moment):
    """ Description         : verfying device stays in {status} for {time}

        Parameters          : status, time string
            Examples: 
                "ONLINE" or "OFFLINE"
                "000:00:10 {%d:%H:%M}"

         Expected result : {status} should stay for particular {time}
        
    """
    if '-' in moment:
        temp = moment.split(', ')
        temp = temp[1].split(":")
        seconds = (int(temp[0]) * 3600 + int(temp[1]) * 60)    
    else:
        temp = moment.split(':')
        seconds = (int(temp[1]) * 3600 + int(temp[2]) * 60)
   
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    api_gen_obj.update_timeout_time(seconds)
    api_gen_obj.start_timer()
    while api_gen_obj.check_timer():
        device_online_state = api_fm_obj.get_device_status(context.device_id)
        assert device_online_state == status, "Unexpected, Device didn't stay in Status: " + status + " for Duration(sec): " + str(seconds)
        time.sleep(30)

@step ('vin is erased from device "{device}"')
def step_impl(context, device):
    """ Description         : VIN is erased from device via SSH or CANalization

        Parameters          : device

        Expected result : VIN is removed from device
        
    """

    if device != context.specimen_device:
        context.execute_steps(f'''
            Given test bench information for device "{device}" is gathered
    ''')
    
    if context.device_config_data['vin_seed_and_key']:
        context.execute_steps('''
            Given performing seed and Key in device using "CANalization"
        ''')
    context.execute_steps(f'''
        Given vin "Erase" is implanted with protocol "CANalization" in device via "{context.device_config_data['implantation_method']}"
        And reference system is stopped
    ''')
    context.detected_vin = None

@step('VIN of vehicle "{vehicle}" is implanted in the device "{test_device}"')
def step_impl(context, vehicle, test_device):
    """ Description         : VIN of vehicle is implanted on device via SSH or CANalization

        Parameters          : vehicle name, device

        Expected result : VIN is set on the device using SSH or CANalization
        
    """   
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    command_map = api_gen_obj.parse_json_file(context.device_config_data["command_file"])
    command = command_map['implantDeviceVIN'][context.test_device]
    vin = api_fm_obj.get_vin_by_name(vehicle, context)
    assert len(vin) == 17, f'Length of the VIN {vin} is not 17 as expected'
    vin_hex = str.encode(vin).hex()
    vin_hex = ' '.join(a+b for a,b in zip(vin_hex[::2], vin_hex[1::2]))

    if test_device != context.specimen_device:
        context.execute_steps(f'''
            Given test bench information for device "{test_device}" is gathered
            ''')
    try:
        if context.device_config_data["RPM_VIN_impl"]:
            context.execute_steps('''
                Given reference system "CANalization" with Identifier "RPM_ON_HVB_OFF" is started
                And all "RPM_ON_HVB_OFF" reference system is stopped
            ''')

        if context.device_config_data['vin_seed_and_key']:
            context.execute_steps('''
                Given performing seed and Key in device using "CANalization"
            ''')

        context.execute_steps(f'''
            Given reference system "CANalization" with Identifier "SM_CAN_UDS_VIN" and vehicle "{vehicle}" is started for self-mapping
            And all "SM" reference system is stopped
        ''')
    except AssertionError as e:
        if 'E2E-FM' not in context.tags:
            out,err = api_gen_obj.ssh_execute(context.devices_data[context.specimen_device][context.test_device + "_IP"],context.device_config_data['ssh_key'],(command + vin_hex))
            assert "SUCCESS" in str(out),f"Device vin is not implanted properly. Error message - {str(err)} "
        else:
            assert False , f"Failed to perform seed and key operation with error - {e}"

@step('new VIN is implanted in the device "{device}"')
@step('new VIN with "{wmi_code}" is implanted in the device "{device}"')
def step_impl(context, device, wmi_code = "AUT"):
    """ Description         : ssh command for config client is run on the device to set the VIN

        Parameters          : device
                              wmi code: World Manufacturer Identifier code (3 Digit)

        Expected result : VIN is set on the device using the config client
        
    """
    current_time = datetime.datetime.now()
    vin = f"{wmi_code}{current_time.year}{'{:02d}'.format(current_time.month)}{'{:02d}'.format(current_time.day)}{'{:02d}'.format(current_time.hour)}{'{:02d}'.format(current_time.minute)}{'{:02d}'.format(current_time.second)}"
    assert len(vin) == 17, f'Length of the VIN {vin} is not 17 as expected'
    vin_hex = str.encode(vin).hex()
    vin_hex = ' '.join(a+b for a,b in zip(vin_hex[::2], vin_hex[1::2]))

    if context.device_config_data["RPM_VIN_impl"]:
        context.execute_steps('''
            Given reference system "CANalization" with Identifier "RPM_ON_HVB_OFF" is started
        ''')
        
    if context.device_config_data['vin_seed_and_key']:
        context.execute_steps('''
            Given performing seed and Key in device using "CANalization"
        ''')

    context.execute_steps(f'''
            Given reference system "CANalization" with Identifier "SM_CAN_UDS_VIN" is started for self-mapping for VIN {vin_hex}
            And reference system is stopped
        ''')
    logging.info(f'VIN {vin} is implanted on the device {device}')
    context.vin = vin
    context.vin_already_implanted = True

@step('auto creation of new vehicle is of status "{status}"')
def step_impl(context, status):
    """ Description         : New vehicle automatic creation is validated

        Parameters          : status
            Examples: 
                "True" or "False"

        Expected result : Vehicle must be auto created
        
    """
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    vehicle = None
    vehicle_found = ""
    count = 1
    while vehicle is None:
        try:
            vehicle = api_fm_obj.get_vehicle_name_by_vin(context.vin)
            logging.info(f"New vehicle : {vehicle} is autocreated by implanted VIN : {context.vin}")
            vehicle_found = "True"
            context.vehicle_name = vehicle
            context.vehicle_id = api_fm_obj.get_vehicle_id_by_name(vehicle, context)
            context.all_vehicle_id.append(context.vehicle_id)
        except AssertionError as error:
            # 30 trials each of 5 second to wait for the new vehicle to be created automatically
            if 'No vehicles exist for the VIN' in str(error) and count == 30:
                vehicle_found = "False"
                break
            count = count + 1
            time.sleep(5)           
    assert status == vehicle_found, f'VIN implantation with a non-existing vehicle for VIN' +context.vin+ 'did not create a new vehicle by itself.'        



@step('backend vehicle pairing status of the device is validated to be "{pairing_status}"')
def step_impl(context, pairing_status):
    """ Description         : ssh command is run on the device to fetch its pairing status code and validated against the expected

        Parameters          : expected pairing status code

        Expected result : Validation that the BACKEND_VEHICLE_PAIRING_STATUS on the device is the same as expected
        
    """
    # To cater to device's base pairing status during different consequences while expected to be in unmapped state
    if pairing_status == 'Unmapped':
        pairing_status_code = ['65', '16', '0']
    elif pairing_status == "Mapped":
        pairing_status_code = '64'
    elif pairing_status == "Failure":
        pairing_status_code = '80'
    elif pairing_status == "BACKEND_VIN_REPORTED":
        pairing_status_code = '32'
    elif pairing_status == "BACKEND_VIN_RECEIVED":
        pairing_status_code = '48'
    else:
        assert False, "Valid pairing status is not selected"
    
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    command_map = api_gen_obj.parse_json_file(context.device_config_data["command_file"])
    matched = False
    if context.device_config_data['ssh_available']:
        for tries in range (60):
            context.execute_steps(f'''
                Given command "{command_map['getPairingDeviceStatus'][context.test_device]}" is executed on device "{context.specimen_device}"
            ''')
            status = str(context.result[0]).split("'")[1].strip("\\n")
            logging.info(f'Pairing status from the device is {status}')
            if status in pairing_status_code:
                matched = True
                break
            else:
                logging.debug(f'Continuing to wait for pairing status to match. retry count: {tries}')
                time.sleep(0.5)
        assert matched, f'Expected pairing status code from device {pairing_status_code} but actual {status}'
    else:
        logging.warning("Skipping pairing status in the device as SSH is not available")
        time.sleep(30)

# @step('customer of the device is recognized')
# def step_impl(context):
#     """ Description         : ssh command is run on the device to fetch the customer code and the name of the
#                                 customer respective to that is set to a context variable

#         Parameters          : NA

#         Expected result : Customer name is recognized
        
#     """
#     api_gen_obj = API_Generic_Class.ApiGenericClass()
#     command_map = api_gen_obj.parse_json_file(context.device_config_data["command_file"])
    # try:
    #     context.execute_steps(f'''
    #         Given Device is "ON" with possibility of SSH connection
    #     ''')
    # except Exception:
    #         context.execute_steps(f'''
    #         Given switch "CL30" is turned "On"
    #         And switch "CL15" is turned "On"
    #         And test waits for "3" minutes
    #         when Device is "ON" with possibility of SSH connection
    #         Then check the "{context.specimen_device}" for availability of GSM connection
    #     ''')
    # context.execute_steps(f'''
    #     Given command "{command_map['readDeviceCustomer'][context.test_device]}" is executed on device "{context.specimen_device}"
    # ''')

    # output_first_line = str(context.result[0]).split("'")[1].split("\\n")[0]
    # value = output_first_line[output_first_line.index("val ")+4:].strip()

    # if value == "( 50 01 )":
    #     context.customer_name = "PACCAR"
    #     logging.info(f'{context.customer_name} is recognized as the customer')
    # elif value == "( 48 01 )":
    #     context.customer_name = "HINO"
    #     logging.info(f'{context.customer_name} is recognized as the customer')
    # elif value == "( 50 02 )":
    #     context.customer_name = "PACCAR_NON_NGD"
    #     logging.info(f'{context.customer_name} is recognized as the customer')
    # else:
    #     logging.info(f'No customer matching the value {value} is found')

@step('reference system "{protocol}" with Identifier "{identifier}" and vehicle "{vehicle}" is started for self-mapping')
def step_impl(context, protocol, identifier, vehicle=None):
    """ Description         : VRS is initiated for self-mapping considering the customer of the device

        Parameters          : protocol - VRS protocol
                                , identifier - ini file name
                                , vehicle - vehicle name of which the VIN has to be communicated from the ascii file

        Expected result : VRS is triggered.
        
    """
    API_Generic_Class.ApiGenericClass()
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    if (len(vehicle) == vehicle.count(' ')):
        vehicle = context.vehicle_name
    else:
        context.vehicle_name = vehicle
        
        # ASCII file preparation
    vin = api_fm_obj.get_vin_by_name(vehicle, context)

    assert len(vin) == 17, f'Length of the VIN {vin} is not 17 as expected'
    vin_hex = str.encode(vin).hex()
    vin_hex = ' '.join(a+b for a,b in zip(vin_hex[::2], vin_hex[1::2]))
    
    context.execute_steps(f'''
            Given reference system "CANalization" with Identifier "SM_CAN_UDS_VIN" is started for self-mapping for VIN {vin_hex}
        ''')
    
    context.detected_vin = api_fm_obj.verify_vin_changes(context.device_id, vin)
    context.vin = context.detected_vin
    logging.info(f'VIN of vehicle = {vin} and detected VIN = {context.detected_vin}')

@step('reference system "{protocol}" with Identifier "{identifier}" is started for self-mapping for VIN {vin_hex}')
def step_impl(context, protocol, identifier, vin_hex):

    api_gen_obj = API_Generic_Class.ApiGenericClass()
    
    dirpath = os.path.dirname(os.path.abspath(__file__))
    context.protocol = protocol

    common_path = dirpath + f"{constants.GC_VRS_STEPS}{protocol}\\Data\\{context.device_config_data['implantation_method']}_VIN_Self_Mapping.asc"  #2 asc files

    api_gen_obj.write_vin_to_ascii(vin_hex, common_path, context.device_config_data['implantation_method'])

    # Moving the below func to class. Will observe the existing tests and then remove it
    
    def reset_asc_data():
        cmd_str = f"{common_path}"
        Popen(['git', 'checkout', '--', cmd_str], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
        time.sleep(2)

    # Initiate VRS
    protocol_name = protocol + "_" + context.device_id
    proc = api_gen_obj.initiate_vrs(context, protocol, identifier, context.vrs_port, context.specimen_device, play=f"{context.device_config_data['implantation_method']}_VIN_Self_Mapping")
    context.protocol_names.append(protocol_name)
    reset_asc_data()
    context.vrs_running = True
    context.all_vrs_proc.append(proc)

@step('test environment is prepared')
def step_impl(context):
    """
        Description: To prepare the Test environment after performing cleanup
    """
    envlist = []
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    device_list = list(context.devices_data.keys())[1:]
    for device in device_list:
        if context.devices_data[device]["device_env"] not in envlist:
            context.env = context.devices_data[device]["device_env"]
            envlist.append(context.env)
            context.execute_steps('''
                Given set "enableSelfMapping" functionality as "ENABLED" in fleet settings
            ''')
        context.test_device = api_gen_obj.device_type_selection(device)
        context.execute_steps(f'''
            Given vin is erased from device "{device}"
            And it is validated that "{device}" is mapped to "none"
            And backend vehicle pairing status of the device is validated to be "Unmapped"
        ''')

@step('validate "{field}" as "{value}" in database.xml from "{device}"')
def step_impl(context, field, value, device):
    """ Description         : ssh command is run on the device to fetch and validate the database.xml

        Parameters          : field - RDA.LOGLEVEL and CDP.LOGLEVEL
                              value - Trace
                              device - CCU under test

        Expected result : database.xml updated as expected
        
    """
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    command_map = api_gen_obj.parse_json_file(context.device_config_data["command_file"])
    command  = command_map['peaSelfUpdateDatabase'][context.test_device]
    database_file_content = api_gen_obj.ssh_execute(context.devices_data[context.specimen_device][context.test_device+"_IP"],context.device_config_data['ssh_key'],command)
    tree = ElementTree.ElementTree(ElementTree.fromstring(database_file_content[0]))
    root = tree.getroot()
    ElementTree.register_namespace('config', constants.GS_CONFIG_LINK)
    name_space = {'config': constants.GS_CONFIG_LINK}
    node = field.split('.')
    for char in root.findall(f'.//config:key/..', name_space):
        key = char.find(f'.//config:key[1]', name_space)
        if key.text == node[0]:
            log_level = char.find(f'.//config:value//config:entry[3]//config:key', name_space)
            if log_level.text == node[1]:
                string_value = char.find(f'.//config:value//config:entry[3]//config:value//config:stringValue', name_space)
                assert value == string_value.text, f'database.xml from device {device} does not have expected value, Actual value -{string_value.text}, Expected value - {value}'
    
@step('validate "{file_name}" file in the device "{device}"')
def step_impl(context, file_name, device):
    """ Description         : ssh command is run on the device to fetch and validate the xml file

        Parameters          : file_name - file which we need to validate i.e database.xml or config.xml
                              device - CCU under test

        Expected result : xml file updated as expected
        
    """
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    if file_name == 'config.xml':
        xml_doc = api_gen_obj.ssh_execute(context.devices_data[context.specimen_device][context.test_device+"_IP"],context.device_config_data['ssh_key'],context.command)
        tree = ElementTree.ElementTree(ElementTree.fromstring(xml_doc[0]))
        root = tree.getroot()
        ElementTree.register_namespace('config', constants.GS_CONFIG_LINK)
        name_space = {'config': constants.GS_CONFIG_LINK}
        for char in root.findall(f'.//config:provisioningDefinitions/..', name_space):
            key = char.find(f'.//config:provisioningDefinitions[35]//config:origin//config:key', name_space)
            assert key.text == "APPLICATIONS.SAMPLE.LOGLEVEL", f'config.xml from device {device} does not have expected value, Actual value -{key.text}, Expected value - "APPLICATIONS.SAMPLE.LOGLEVEL"'
            logging.info(f'config:key has expected value = {key.text}')
            component = char.find(f'.//config:provisioningDefinitions[35]//config:origin//config:component', name_space)
            assert component.text == "SAMPLE_APP", f'config.xml from device {device} does not have expected value, Actual value -{component.text}, Expected value - "SAMPLE_APP"'
            logging.info(f'config:component has expected value = {component.text}')
            interface = char.find(f'.//config:provisioningDefinitions[35]//config:origin//config:interface', name_space)
            assert interface.text == "SAMPLE_INTERFACE", f'config.xml from device {device} does not have expected value, Actual value -{interface.text}, Expected value - "SAMPLE_INTERFACE"'
            logging.info(f'config:interface has expected value = {interface.text}')
            loglevel = char.find(f'.//config:provisioningDefinitions[35]//config:propertyName', name_space)
            assert loglevel.text == "SAMPLE.LOGLEVEL", f'config.xml from device {device} does not have expected value, Actual value -{loglevel.text}, Expected value - "SAMPLE.LOGLEVEL"'
            logging.info(f'Loglevel has expected value = {loglevel.text}')
            break
    elif file_name == 'database.xml':
        context.execute_steps(f'''
                Given validate "RDA.LOGLEVEL" as "TRACE" in database.xml from "{device}"
            ''')

@step('store a backup file for "{file_name}" from device "{device}"')
def step_impl(context, file_name, device):
    """ Description         : ssh command is run on the device to fetch and validate the xml file

        Parameters          : file_name - file which we need to validate i.e database.xml or config.xml
                              device - CCU under test

        Expected result : xml file updated as expected
        
    """
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    context.file_name = file_name
    command_map = api_gen_obj.parse_json_file(context.device_config_data["command_file"])
    if file_name == 'database.xml' :
        command  = command_map['peaSelfUpdateDatabase'][context.test_device]
    elif file_name == 'config.xml':
        command  = command_map['peaSelfUpdateConfig'][context.test_device]
    context.command = command
    xml_doc = api_gen_obj.ssh_execute(context.devices_data[context.specimen_device][context.test_device+"_IP"],context.device_config_data['ssh_key'],command)
    tree = ElementTree.ElementTree(ElementTree.fromstring(xml_doc[0]))
    dirpath = os.path.dirname(os.path.abspath(__file__))
    tree.write(dirpath+'\\'+file_name)
    context.pea_file_backed_up = True
    logging.info(f'BackUp for {file_name} from {device} is stored')

@step('replace updated xml file with its backup file')
def step_impl(context):
    """ Description         : ssh command is run on the device to replace the xml file

        Expected result : xml file replaced as expected
        
    """
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    dirpath = os.path.dirname(os.path.abspath(__file__))
    api_gen_obj.copy_to_device_with_scp(context.test_device, context.devices_data[context.specimen_device][context.test_device+"_IP"], 'root', '', dirpath+'\\'+context.file_name, context.command[4:-len("/"+context.file_name)])
    context.execute_steps(f'''
                Given device operation "rebootDevice" is performed
                And wait for device to be "ONLINE"
            ''')
@step('performing seed and Key in device using "{protocol}"')
def step_impl(context, protocol):
    """
        Description     : Seed and key is performed in device before vin implantation or vin unpair
        
    """
    context.execute_steps(f'''
        Given reference system "{protocol}" with Identifier "SM_TesterPresent" is started
        And reference system "{protocol}" with Identifier "SM_UDS_Extend_Session" is started
        And the "2"nd reference system "{protocol}" with Identifier "SM_record_response" is started
        And reference system "{protocol}" with Identifier "SM_UDS_RequestSeed" is started
        And reference system with protocol "{protocol}" and identifier "SM_record_response" and number "2" is stopped
        And filter seed from asc response and get key
        And start vrs after writing key to file using protocol "{protocol}" with Identifier "SM_UDS_Sendkey"
    ''')
    
@step('verify VIN Mismatch event is "{state}" by reading DTC using "{protocol}"')
def step_impl(context,protocol,state):
    """
        Description     : Getting hex values by read DTC and converting it to  binary values to check VIN Mismatch event is 'True' or 'False'

        Parameters      : state - True or False

        Expected result : VIN Mismatch event should be false for binary value '00' and should be true for binary value '11'
    """
    context.execute_steps(f'''
        Given the "2"nd reference system "{protocol}" with Identifier "record_response" is started
        And reference system "{protocol}" with Identifier "ReadDTC" is started
        And reference system with protocol "{protocol}" and identifier "record_response" and number "2" is stopped
        And filter DTC Mask from asc response for "{state}" using "{protocol}"
    ''')

@step('vin "{count}" is implanted with protocol "{protocol}" in device via "{bus}"')
@step('vin "{count}" is implanted with protocol "{protocol}" in device via "{bus}" returns "{implantation_state}"')
def step_impl(context, count, protocol, bus, implantation_state = "Success"):
    '''
        Description :  Respected VIN is implanted to the device via defined bus

        Pre-condition : VIN should be erased

        Parameters  :  count - nth VIN, bus - UDS, CAN
    '''
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    identifier = "Send_VIN"+count+"_"+bus

    if context.device_config_data["RPM_VIN_impl"]:
        if implantation_state == "Success":
            context.execute_steps('''
                Given reference system "CANalization" with Identifier "RPM_ON_HVB_OFF" is started
            ''')
        elif implantation_state == "Failure":
            context.execute_steps('''
                Given reference system "CANalization" with Identifier "RPM_OFF_HVB_OFF" is started
            ''')

    try:
        context.execute_steps(f'''
            Given reference system "{protocol}" with Identifier "{identifier}" is started
        ''')
    except AssertionError:
        logging.info("Problem with VRS start. Please check")
        assert False, f'Problem starting the VRS in {protocol} with this {identifier}. Please check'
    path = os.path.dirname(os.path.abspath(__file__))
    asc_path = path + constants.GC_VRS_STEPS + protocol+"\\Data\\"+identifier+".asc"
    context.vin_data.update({"vin"+count+"": api_gen_obj.get_vin_from_ascii(asc_path, bus)})

@step('filter seed from asc response and get key')
def step_impl(context):
    """
        Description: To filter seed from vrs resposne and calculate the key
    """
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    path = os.path.dirname(os.path.abspath(__file__))
    asc_path = path + constants.GC_VRS_RESPONSE_ASC_PATH
    seed_image = "67 03"
    time.sleep(60)
    seed = api_gen_obj.get_seed_from_vrs_response(asc_path, seed_image)
    context.key = api_gen_obj.generate_key_from_seed(seed)

@step('start vrs after writing key to file using protocol "{protocol}" with Identifier "{identifier}"')
def step_imp(context, protocol, identifier):
    """ Description         : Setting the key for asc file and start the vrs

        Parameters          : protocol, identifier and key(context)

        Expected result : Key must be properly written in asc file and vrs should be triggered
        
    """
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    path = os.path.dirname(os.path.abspath(__file__))
    key_path = path + constants.GC_VRS_UDS_SEND_KEY_ASC_PATH
    api_gen_obj.write_key_to_ascii(key_path, context.key)

    def reset_asc_data():
        cmd_str = f"{key_path}"
        Popen(['git', 'checkout', '--', cmd_str], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
        time.sleep(5)
    try:
        context.execute_steps(f'''
            Given reference system "{protocol}" with Identifier "{identifier}" is started
        ''')
    except AssertionError:
        logging.info("Problem with VRS start. Please check")
        assert False, f'Problem starting the VRS in {protocol} with this {identifier}. Please check'
    reset_asc_data()

@step('filter DTC Mask from asc response for "{state}" using "{protocol}"')
def step_impl(context,state,protocol):
    """
        Description: To filter DTC Mask from vrs resposne
    """
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    path = os.path.dirname(os.path.abspath(__file__))
    asc_path = path + constants.GC_VRS_RESPONSE_ASC_PATH
    dtc_image = "d 8 21"
    dtc = api_gen_obj.get_dtc_mask_from_vrs_response(asc_path, dtc_image)
    if dtc:
        logging.info(f'Hexadecimal value for DTC Mask from asc response : {dtc}')
        read_dtc_binary = api_gen_obj.convert_hex_to_binary(dtc)
        dtc_binary = str(read_dtc_binary[-2:])

        if (state == "false"):
            if ((dtc_binary != "00") and (context.reboot_count)):
                context.execute_steps(f'''
                    Given device operation "rebootDevice" is performed on "{context.specimen_device}" device
                    And wait for device to be "ONLINE"
                    Then the "2"nd reference system "{protocol}" with Identifier "record_response" is started
                    And reference system "{protocol}" with Identifier "ReadDTC" is started
                    And reference system with protocol "{protocol}" and Identifier "record_response" and number "2" is stopped
                ''')    
                context.reboot_count = False
                context.execute_steps(f'''
                    Given filter DTC Mask from asc response for "{state}" using "{protocol}"
                ''')
            elif(dtc_binary != "00"):
                assert False, "Masking value results values of last ignition cycle. Please check the device"
            else:
                logging.info("VIN Mismatch event is False by reading DTC before VIN implantation")

        elif(state == "true"):
            api_gen_obj.verify_vin_mismatch_event_is_true(dtc_binary)

        else:
            assert False, "Wrong state entry, State entry should be true / flase"
    else:
        logging.info("No VIN Mismatch found in ECU")


@step('validate vin "{count}" is implanted currently in device')
def step_impl(context, count):
    """
        Description: To validate the implanted vin and the detected vin in device
    """
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    expected_vin = context.vin_data.get("vin"+count)
    detected_vin = api_fm_obj.get_detected_vin(context.device_id)
    logging.info(f"ExpectedVIN - {expected_vin} DetectedVIN - {detected_vin}")
    assert expected_vin == detected_vin, f"Expected VIN is not implanted in the Device - ExpectedVIN - {expected_vin} but detectedVIN - {detected_vin}"

@step('reset VRS and delete VRS residual')
def step_impl(context):
    """ Reset VRS and delete VRS data """
    # resets the VRS if any
    path = os.path.dirname(os.path.abspath(__file__))
    cmd_str = path + constants.GC_VRS_RESET_BAT_PATH
    Popen([cmd_str], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
    time.sleep(5)
    # deletes the VRS leftover from boost_interprocess folder
    cmd_str2 = path + constants.GC_VRS_DELETE_BAT_PATH
    Popen([cmd_str2], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
    time.sleep(10)

@step('Authorization response is verified for gradex services')
def step_impl(context):
    """ Description         : create a post request with following data to get the expected access token response

        Parameters          : NA

        Expected result     : access token response must be generated
        
    """
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    context.config_data=api_gen_obj.parse_json_file(constants.TEST_CONFIG_JSON)
    gradex_token_url=context.config_data['healthcheck']['url']
    gradex_token_credentials= context.config_data['healthcheck']['credentials']
    basic_auth_header = {'Authorization': "Basic "+gradex_token_credentials
    }
    api_gen_obj.check_access_token(gradex_token_url,basic_auth_header)

@step('gradex service health check is verified with expected response')
def step_impl(context):
    """ Description         : create a get request and verify the template of the response it should contain data resembling below in expected result.

        Parameters          : NA

        Expected result     : {'percentageFree': 94.22928976323468, 'memCommitted': '790626304', 'memInit': '685768704', 'memMax': '2440560640', 'memUsed': '123426192', 'id': 'i-04919e26b1f70d2ff'}
        
    """
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    health_check_url=context.config_data['healthcheck']['health_check_url']
    api_gen_obj.services_health_check(health_check_url)
    
@step('check the "{device}" for availability of GSM connection')
def step_impl(context, device):
    """
        Checks for GSM availability and if not found, reboots the device.
    """
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    if "CCU" in device:
        device_ip = "CCU_IP"
    else:
        assert False, 'Device unrecognized'
    if context.device_config_data["ssh_available"]:
        result = api_gen_obj.ssh_execute(context.devices_data[device][device_ip],context.device_config_data['ssh_key'],"ifconfig")
        response = str(result[0])
        if context.device_config_data["network_availability"] not in response:
            logging.error("Device doesn't have network connection, rebooting the device")
            context.execute_steps(f'''
                    Given device operation "rebootDevice" is performed on "{device}" device
            ''')
        else:
            logging.info("Device has network connection")
            if context.device_config_data["network_availability"] == "ccmni0": # This if condition need to be removed completely once ota client is stable in TCU2 
                logging.error("rebooting the device to restart ota-client")
                context.execute_steps(f'''
                        Given device operation "rebootDevice" is performed on "{device}" device
                ''')
                # logging.warning("Restarting OTA client service on TCU2 as network connection is available") 
                # context.execute_steps(f'''
                #     Given device operation "stop_ota_client" is performed on "{device}" device
                #     And test is executed for "10" seconds
                #     And device operation "start_ota_client" is performed on "{device}" device
                # ''')

@step('User validates user guide page')
def step_impl(context):
    """ Description         : user login to ota environment and validating the user guide page
        Parameters          : NA
        Expected result     : user guide page should load without error
        
    """
    dict_var = {
             "Introduction":"107582",
             "Requirements and Usage":"107583",
             "Getting":"107586",
             "Fleet Management":"107591",
             "Remote Measurement":"107592",
             "Remote Diagnostics":"107764",
             "OTA Updates":"107597"
         }
    for key,value in dict_var.items():
        api_gen_obj = API_Generic_Class.ApiGenericClass()
        text_response = api_gen_obj.get_user_guide_content(value)
        assert key in text_response,f"user guide is not loading for - {key}"


@step('Device is "{status}" with no SSH connection')
@step('Device is "{status}" with possibility of SSH connection')
def step_impl(context, status):
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    api_gen_obj.device_availablity_on_system(context.device_ip,context.device_id,status)
    api_gen_obj.verify_ssh_connection_status(context.device_ip,context.device_config_data['ssh_key'], status)
        

@step('get image file from artifactory for FW "{to_version}"')
def step_impl(context, to_version):  
    api_ota_update_obj = API_OTA_Updates_Class.ApiOtaUpdatesClass(context.env, context.log_api_details)
    context.download_path = api_ota_update_obj.download_from_artifactory(context.device_config_data, to_version, package_type="USB_UPDATE")

@step('performing USB flash using powershell file')
def step_impl(context):
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    api_gen_obj.override_psfile(context.download_path + "\\flash_ubi_windows.ps1")
    logging.info("Current working directory: {0}".format(os.getcwd()))
    logging.info("Changing working directory")
    os.chdir(context.download_path)
    logging.info("Current working directory: {0}".format(os.getcwd()))
    command_map = api_gen_obj.parse_json_file(context.device_config_data["command_file"])
    command  = command_map['rebootDevice'][context.test_device][0]
    api_gen_obj.ssh_execute(context.devices_data[context.specimen_device][context.test_device+"_IP"],context.device_config_data['ssh_key'],command)
    proc = subprocess.Popen(['powershell.exe', "./flash_ubi_windows.ps1"], stdin=None, stdout=subprocess.PIPE, stderr=True)
    out,err = proc.communicate() 
    assert err is None, f"USB flashing on device - {context.device_id} is not performed properly. It returned error : {err}"
    logging.info(out.decode("utf-8").strip())
    logging.info("Waiting for 90 seconds to let the device to reboot")
    time.sleep(90)
    logging.info("Terminating USB Update Process")
    proc.terminate()
    
    
@step('perform load test for {total_executions:d} iterations with predefined steps')
def step_impl(context, total_executions):
    failure_count = 0
    exception_list = []    
    for iteration in range (1, total_executions + 1):
        logging.info(f"Load test execution number - {iteration}")
        context.start_timer = time.time()
        try:
            context.execute_steps(context.repetitive_steps)
        except AssertionError as err:
            failure_count += 1
            details = repr(err).split('Traceback')[0]
            logging.info(f"Assertion Error in Execution {details}")
            exception_list.append(f"Assertion error in Iteration {iteration}: {details}")
        except Exception as exp:
            failure_count += 1
            logging.info(f"error in Execution '{repr(exp)}")
            exception_list.append(f"Error in Load test Iteration {iteration}: {repr(exp)}")
        
        #context.distribution_package_id.clear()
        context.ota_update_assignment_details.clear()
        context.ota_status_list.clear()
        context.end_timer = time.time()
        execution_time = math.ceil(context.end_timer - context.start_timer)
        logging.info(f"Load test execution completed for - {iteration}, it took - {execution_time} seconds")
    if(failure_count > 0):
        for exception in exception_list:
            logging.error(exception)
        pass_percentage = ((total_executions -failure_count)/total_executions) * 100
        assert False, f"Total Iterations: {total_executions}, Failure count: {failure_count}, Success Rate: {pass_percentage} %"
    
@step('verify the message_id and message data in CAN bus for "{messge_type}"')
def step_impl(context, messge_type):
    """ Description      : It verifies the expected data is availble on CAN bus
        Pre-condition    : reference system <protocol> with Identifier "record_response" is started
        Parameters       : config_data - expected data from feature file , message - the message id from feature file
        Expected result  : The expected message data from feature file and actual message data from VRS_resopnse.asc is validated.    
    """
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    json_data = api_gen_obj.parse_json_file(constants.CAN_DATA_JSON_PATH)
    message_data = json_data['can_message_data'][messge_type]
    path = os.path.dirname(os.path.abspath(__file__))
    asc_path = path + constants.GC_VRS_RESPONSE_ASC_PATH
    for key, value in message_data.items():
        for i in range(0, len(value)):
            api_gen_obj.verify_message_in_can(asc_path, key, value[i])
    os.remove(asc_path) #to clean up the vrs_response.asc

@step('validate GPS data on CAN')
def step_impl(context):
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    asc_path = os.path.dirname(os.path.abspath(__file__)) + constants.GC_VRS_RESPONSE_ASC_PATH
    gps_exp_data =  context.device_config_data['gps_exp_data']

    api_gen_obj.validate_gpsdata_from_response(asc_path, gps_exp_data)
    logging.info("Successfully validated GPS data on CAN")