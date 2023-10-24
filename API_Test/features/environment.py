import logging
import os
import sys
from behave.contrib.scenario_autoretry import patch_scenario_with_autoretry
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import os
import subprocess
import steps.pageObjects.API_Generic_Class as API_Generic_Class
import steps.pageObjects.API_Inventory_Class as API_Inventory_Class
from behave.model_core import Status
import steps.pageObjects.API_FleetManagement_Class as API_FleetManagement_Class
import steps.constantfiles.constants_environment as constants
from datetime import datetime
import os.path as path
from jira_operations import JiraOperations
jira_operations = JiraOperations()
api_gc_obj = API_Generic_Class.ApiGenericClass()

test_execution_id = None
tests_with_defects = {}
failed_result_uploads = []

def repeat_steps(context,steps):
    flag = True
    for x in range(context.after_hook_repeat):
        try:
            logging.info(f"Number ot tries : {x+1}")
            context.execute_steps(steps)
            flag == False
            break
        except:
            if(flag == True and x < context.after_hook_repeat):
                continue
            else:
                logging.warning(f"Exception Occurred: , {sys.exc_info()[0]}, {sys.exc_info()[1]}")
                assert False, f"{sys.exc_info()[0]}{sys.exc_info()[1]}"

def execute_step(context, steps):
    try:
        context.execute_steps(steps)
    except Exception:
        logging.warning(f"Exception Occurred: , {sys.exc_info()[0]}, {sys.exc_info()[1]}")

def dispatch_device_to_target(context):
    try:
        context.execute_steps('''
            Given switch to "device-provisioning"
            And remove paired vehicle
            When dispatch device to " " in provisioning space
            And test waits for "1" minutes
            And verify the device provisioning state "DISPATCHED" in provisioning space
            And switch to " "
            Then verify the provisioning status "REGISTERED" in target space
            And wait for device to be "OFFLINE"
            And wago "CL15" is turned "Off"
            And test waits for "1" minutes
            And wago "CL15" is turned "On"
            And wait for device to be "ONLINE"
        ''')
    except Exception:
        logging.warning(f"Exception Occurred: , {sys.exc_info()[0]}, {sys.exc_info()[1]}")

def unmap_device(context):
    if ((hasattr(context, 'deviceMapped')) and (context.device_mapped == True)):
        logging.info("Unmapping the device from vehicle's device slot")
        execute_step(context, '''
            when remove paired vehicle
            ''')
        context.device_mapped = False
        if(('E2E-RM' in context.tags or 'E2E-RD' in context.tags) and context.test_status == Status.failed):
            execute_step(context,'''
               Then remove device slot from vehicle
            ''')

def update_feature_result(context, feature_no = None):
    """Updates the feature result to Jira Test execution 

    Args:
        context (object): Behave context
        feature_no (int, optional): Feature counter number. Defaults to None(Picks the previously run feature).
    """
    global test_execution_id
    if(feature_no == None):
        feature_no = context.feature_count
    if api_gc_obj.check_file_availability(constants.CUCUMBER_RESULT_PATH) and api_gc_obj.check_file_size(constants.CUCUMBER_RESULT_PATH) > 0 and context.jira_test_execution == True:
        logging.info(f"Updating Feature result for feature count: {feature_no}")
        feature_result = api_gc_obj.get_feature_cucumber_result(constants.CUCUMBER_RESULT_PATH, feature_no)
        jira_operations.cleanup_cucumber_report_data(feature_result)
        jira_operations.mark_tests_with_defect_to_red(feature_result, tests_with_defects.keys())
        if(test_execution_id != None):
            feature_result = jira_operations.update_execution_details(feature_result, test_execution_id)
        api_gc_obj.write_json_file(constants.FEATURE_RESULT_PATH,feature_result)
        test_exec_key = jira_operations.publish_feature_report(constants.FEATURE_RESULT_PATH)
        if test_exec_key != test_execution_id:
            logging.info(f"Detected new TE ID from JIRA, Updating TE ID from: {test_execution_id} to {test_exec_key}")
            test_execution_id = test_exec_key
            jira_operations.update_test_execution_summary(test_exec_key)
        jira_operations.update_test_execution_with_defect(test_exec_key, tests_with_defects=tests_with_defects)

def self_update_get_update_status(api_ota_update_obj, device_id, check_package_app, timer, expected_status):
    assignment_response=api_ota_update_obj.package_to_device_check(device_id,check_package_app)
    assignment_id=assignment_response.json()["assignmentId"]
    device_update_status=api_ota_update_obj.get_flash_status(assignment_id,timer,expected_status)
    if expected_status in device_update_status:
        logging.info("The self update is success")  

def fetch_from_and_to_version(context, package_type):
    if  package_type == "full_update":
        context.to_version = context.config.userdata["SU_Up_version"]
    elif package_type == "downgrade_delta" or "Delta_DP_" in package_type or "CCU_DELTA" in package_type:
        context.from_version = context.config.userdata["SU_Up_version"]
        context.to_version = context.config.userdata["SU_Down_version"]
    elif package_type == "upgrade_delta":
        context.from_version = context.config.userdata["SU_Down_version"]
        context.to_version = context.config.userdata["SU_Up_version"]
    else:
        assert False, "Given package type is not correct. Expected package types are upgrade_delta and downgrade_delta"
        
#===================================================================================================================================================
#================================================================= Before Hooks =====================================================================
#===================================================================================================================================================


"""
    Description: Before hook that creates class instances and primary variable declarations
"""

def before_all(context):
    context.feature_count = 0
    global test_execution_id
    test_execution_id = context.config.userdata["TEST_EXECUTION_ID"] if ("TEST_EXECUTION_ID" in context.config.userdata) and len(context.config.userdata["TEST_EXECUTION_ID"])>2 else None
    context.jira_test_execution = True if("jira_test" in context.config.userdata and context.config.userdata["jira_test"] == "true") else False
    context.rerun_failed_test = True if ("rerun_failed_test" in context.config.userdata and context.config.userdata["rerun_failed_test"] == "true") else False
    log_file_path = "Test_Execution.log"
    jenkins_job_name = os.path.basename(path.abspath(path.join(__file__ ,"../../../")))
    try:
        if os.path.exists(log_file_path): os.remove(log_file_path)
    except OSError:
        log_file_path = "Test_Execution_{}.log".format(datetime.now().strftime("%d-%m_%H-%M"))
    if "API" in jenkins_job_name:
        logs_folder = path.abspath(path.join(__file__ ,"../../../../Logs"))
        log_file_name = jenkins_job_name+"_{}.log".format(datetime.now().strftime("%d-%m_%H-%M"))
        os.makedirs(logs_folder, exist_ok=True)
        log_file_path = os.path.join(logs_folder, log_file_name)
    with open("behave_logging.ini", "r+") as behave_ini_file:
        update_ini_file = behave_ini_file.read().replace("Test_Execution.log", log_file_path)
        behave_ini_file.seek(0)
        behave_ini_file.write(update_ini_file)
    context.config.setup_logging(configfile="behave_logging.ini", level=logging.DEBUG)

def before_feature(context, feature):
    context.log_api_details = True
    context.test_status = ""
    context.specimen_device = None
    context.after_tag = True
    context.device_mapped = False
    context.env = "azure_eu"
    context.distribution_package_id = []
    context.ota_update_assignment_details = []
    try:
        update_feature_result(context)
    except Exception:
        failed_result_uploads.append(context.feature_count)
    logging.info("="*100)
    logging.info(" "*40 + "STARTING FEATURE")
    api_inventory_obj = API_Inventory_Class.ApiInventoryClass(context.env, context.log_api_details)
    if "specimen_device" in context.config.userdata:    
        context.specimen_device = context.config.userdata["specimen_device"]
    if ("Self_Update_FW_Version" in context.config.userdata ):
        context.to_version = context.config.userdata["Self_Update_FW_Version"]
        device_id = context.config.userdata["Device_id"]
        from_version =api_inventory_obj.get_firmware_version_of_device(device_id)
        context.from_version = from_version.strip(",._DEBUG")

    if (context.jira_test_execution):
        for scenario in feature.scenarios:
            tags = scenario.tags
            defects = jira_operations.get_defects_linked_to_test(tags[0], context.specimen_device)
            if len(defects)> 0:
                tests_with_defects[tags[0]] = defects
            elif(context.rerun_failed_test):
                patch_scenario_with_autoretry(scenario, max_attempts=2)

def before_scenario(context, scenario):
    logging.info("="*100)
    logging.info(f"STARTING SCENARIO: {scenario.name}")
    logging.info("="*100 + "\n")
    if context.specimen_device is None or len(context.specimen_device) == 0:
        context.specimen_device = context.active_outline["device"].strip('\"')
        logging.info(f"Detected device for this scenario: {context.specimen_device}")
    else:
        logging.info(f"User selected the device for this scenario: {context.specimen_device}")
    context.measurement_description = 'Test job for automated system tests'
    context.cl15_off = False
    context.vin_data= {}
    context.reboot_count = True
    context.all_vehicle_id = []
    context.all_device_ids = []
    context.all_vsg_data = {}
    context.vehicle_data = {}
    context.all_vrs_proc = []
    context.trigger_capability_ep = []
    context.all_measurement_jobs = {}
    context.all_assignment_jobs  = {}
    context.campaign_vehicle_data = {}
    context.enabled_status = {}
    context.received_data = 0
    context.dtcs_count = 0
    context.separation_time = 100
    context.added_signals = []
    context.ignition_on_time = 0
    context.ignition_off_time = 0
    context.vin_already_implanted = False
    context.protocol_names = []
    context.gsm_stop = False
    context.logger = logging.getLogger("steps")
    context.update_vehicle_name = False
    context.after_hook_repeat = 5
    context.device_simulator_running =[]
    context.device_changed = False
    context.device_dispatched = True
    context.std_date_format = '%d-%m-%Y, %H:%M;%S'
    context.ota_status_list = []
    context.distribution_package_id = []
    context.ota_update_assignment_details = []
    context.rm_activation_date = ""
    context.rm_config_ids = context.measurement_configuration_ids = []
    context.device_slot_count = ""
    context.meas_config_keys = []
    context.desired_state_package =""
    context.desired_state_assignment_id =""
    
    if 'limit-log' in scenario.tags or 'limit-log' in context.config.userdata:
        logging.info('Limited logs will be printed to the console!')
        context.log_api_details = True
    context.tags = scenario.tags
    global test_execution_id
    if test_execution_id != None:
        context.test_run_id = jira_operations.get_test_run_id(test_execution_id,scenario.tags[0], create = True)
        jira_operations.update_test_run_status(context.test_run_id, "EXECUTING")

    context.execute_steps(f'''
        Given reset VRS and delete VRS residual
        And test data details are fetched
        And create file to save version details
        And test bench information for device "{context.specimen_device}" is gathered
        And read the device properties
        And perform the miscellaneous actions for the device to be ready
        
    ''')

    if ('E2E-RM' in context.tags and 'E2E-Smoke' in context.tags):  # 'E2E-Smoke' tag will be removed once implementing NON-NGD changes for regression/load/installatoin scenario
        active_outline_headings = context.active_outline.headings
        api_gc_obj.update_meas_config_name(context, active_outline_headings)

    # checking device provisioned status as Registered to Environment in-test
    context.execute_steps(f'''
        Given device "{context.specimen_device}" is "ONLINE"
    ''')
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    # if (api_fm_obj.get_device_properties(context.device_id).json()['state'].upper() != "REGISTERED"):
    #     context.device_dispatched = False
    #     logging.info("device in-test is not Registered, and so Undispatched from the Tenant in-use. Redispatching device correctly")
    #     dispatch_device_to_target(context)

    if 'E2E-ERASE_VIN' in context.tags:
        logging.info("Preparing all devices by clearing VIN, logs and pending Jobs")
        execute_step(context, '''
                Given test environment is prepared
                And device operation "deleteDeviceLogs" is performed on "ALL" device
                And device operation "deleteAllJobs" is performed on "ALL" device 
        ''')
    elif not context.device_simulator_running:
        execute_step(context, f'''
            Given device operation "deleteDeviceLogs" is performed on "{context.specimen_device}" device
            And device operation "deleteAllJobs" is performed on "{context.specimen_device}" device
        ''')

    if 'E2E-Installation' in context.tags:    
        package_type = context.active_outline["package"].strip('\"')
        fetch_from_and_to_version(context, package_type)
        if package_type != "full_update":
            logging.info("Check device FW version with expected FROM version")
            execute_step(context, f'''
                Given Check "CCU" FW version to perform "USB_Update" to "{context.from_version}" if version is not as expected
            ''')
            logging.info(f"Device has expected FROM version - '{context.from_version}'")

def before_step(context, step):
    context.step = step
    logging.info(context.step)

#===================================================================================================================================================
#================================================================= After Hooks =====================================================================
#===================================================================================================================================================

"""
    Description: After hook used to handle Deactivation of Configuration for RD and RM; and unmapping of device 
                After hook to handle Device clean Up and device reboot for scenarios that fails / Sad path scenarios  
"""
def after_scenario(context, scenario):
    
    logging.info('Entering AFTER HOOKS...')
    context.hook_failed = scenario.hook_failed
    # if ((hasattr(context, 'device_dispatched')) and (context.device_dispatched is False)):
    #     logging.info("Device is not Registered at Tenant in-use, re-registering the Device")
    #     dispatch_device_to_target(context)
    
    if ((hasattr(context, 'CL15')) and (context.CL15 is False)):
        logging.info("Turning on 'CL15'")
        repeat_steps(context,'''
                When switch "CL15" is turned "On"
                Then wait for device to be "ONLINE"
                ''')
        logging.info(f"'CL15' is Turned On  And {context.device_id} is ONLINE")
    
    if ((hasattr(context, 'CL30')) and (context.CL30 is False)):
        logging.info("Turning on 'CL30'")
        repeat_steps(context,'''
                When switch "CL30" is turned "On"
                Then wait for device to be "ONLINE"
                ''')
        logging.info(f"'CL30' is Turned On  And {context.device_id} is ONLINE")

    if ((hasattr(context, 'stopGSM_for_all')) and (context.stopGSM_for_all is True)):
        logging.info("Starting GSM mode for all the devices")
        repeat_steps(context,'''
                When command to "startGSMConnection" GSM mode for "all" the device
                And wait for device "CCU" to be "ONLINE"
                And wait for device "CCU2" to be "ONLINE"
                ''')
        logging.info(" GSM mode is ON for all the devices")

    if ((hasattr(context, 'GSMStop')) and (context.gsm_stop is True)):
        logging.info(f"Starting GSM mode the device {context.device_id}")
        repeat_steps(context,'''
                When command to "startGSMConnection" GSM mode of the device
                Then wait for device to be "ONLINE"
                ''')
        logging.info(f"{context.device_id} GSM mode is ON ")
        
    context.test_status = scenario.status
        #logging.info ("triggering Device log generation for failed test case...")
        #execute_step(context, f'''
        #    Then triggering new log file generation for device
        #''')    
    if ((hasattr(context, 'vrs_running')) and (context.vrs_running is True)):       
         execute_step(context, '''
                Given reference system is stopped
         ''')

    if(hasattr(context, 'key') and hasattr(context, f'replace{context.key}') and (eval(f'context.replace{context.key}') is True)):
        logging.info(f"Replacing original file : {context.key}")
        repeat_steps(context,f'''
                    Given copy device specific file "{context.key}" to device
                    And device operation "rebootDevice" is performed
                    And wait for device to be "ONLINE"
        ''')
        logging.info(f"Placed original file : {context.key} : to device")

    if ((hasattr(context, 'self_mapping_device')) and (context.self_mapping_device is True)):
        logging.info("Enabling automatic device mapping with mode as Create new vehicle")
        execute_step(context, '''
            Then set "enableSelfMapping" functionality as "ENABLED" with mode "CREATE"
            And set "pairOnlyTrustedVin" functionality as "DISABLED" in fleet settings
        ''')            
        logging.info("Enabled automatic device mapping with mode as Create new vehicle")
    
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    if hasattr(context, 'geo_status'):
        logging.info("Disabling Geo position on the Vehicle")
        vehicle_data = context.active_outline["vehicle"] if "vehicle" in context.active_outline.headings else context.active_outline["vehicles"]
        vehicle_list = vehicle_data.strip('\"').split(',')
        if vehicle_list == [' ']:
            vehicle_list = [context.default_vehicle]
        for vehicle in vehicle_list:
            geo_position_status = api_fm_obj.get_geopositioning_status(vehicle, context)
            if geo_position_status == "ENABLED":
                execute_step(context, f'''
                    Given geo positioning in "{vehicle}" is "DISABLED"
                ''')

    if hasattr(context, 'vin_data') and context.vin_data:
        logging.info("Erasing the VIN from the device")
        execute_step(context, f''' 
            Then vin is erased from device "{context.specimen_device}"
        ''')

    if (('E2E-RM' in context.tags)and(scenario.status == Status.passed)):
        logging.info("deleting RM steps")
        execute_step(context, '''
            Then delete the newer measurement data         
        ''')

    if (('E2E-Installation' in context.tags)and(scenario.status == Status.passed)):
        context.distribution_package_id.clear()
        context.ota_update_assignment_details.clear()
        context.ota_status_list.clear()
        execute_step(context, '''
            Then Perform PEA update
        ''')

    if hasattr(context,'pea_file_backed_up'):
        logging.info("Replacing xml file with its original content")
        execute_step(context, '''
            Then replace updated xml file with its backup file
        ''')            
        logging.info("Replaced xml file with its original content")
    
    if context.device_simulator_running:
        logging.info("Stopping device simulators for all devices")
        for pids in context.device_simulator_running:
            cmd = f"taskkill /F /PID {pids}"
            subprocess.Popen(cmd, shell = True)

    if (hasattr(context, 'test_run_id')):
        match context.test_status:
            case Status.passed:
                status = "PASS"
            case Status.failed:
                status = "FAIL"
            case Status.skipped:
                status = "FAIL"
            case _:
                status = "TODO"
        jira_operations.update_test_run_status(context.test_run_id, status)
    
    logging.info("="*100)
    logging.info(f"END OF SCENARIO: {scenario.name}")
    logging.info("="*100 + "\n")
 
def after_tag(context, tag):
    if ((('E2E-SP' in context.tags) or (context.test_status == Status.failed)) and (context.after_tag) and not (context.hook_failed)):
        logging.info("Test failed or Sadpath Scenario")

        if (('E2E-RD' in context.tags) and (hasattr(context, 'rd_campaign_activation_status')) and (context.rd_campaign_activation_status is True)):
            logging.info("De-activating diagnostics configuration for vehicles from activation RD campaign")
            execute_step(context,f'''
                Given remote diagnostic deactivated for vehicles in RD activation campaign "{context.activation_campaign_ids}" from "ACTIVE" and validate status as "INACTIVE" state and sub_status is " " for "DTC" in campaign
            ''')
        elif (('E2E-RD' in context.tags) and (hasattr(context, 'rd_activation_status')) and (context.rd_activation_status is True)):
            logging.info("De-activating diagnostics configuration")
            execute_step(context,'''
                Given deactivate ACTIVE diagnostic configuration if present
                And diagnostic configuration state is "INACTIVE"  
            ''')

        if (('E2E-RM' in context.tags) and (hasattr(context, 'campaign_rm_active')) and (context.campaign_rm_active is True)):
            execute_step(context,'''
                Given "REMOTE_MEASUREMENT" campaign is "abort"ed
                And measurement campaign status "ABORTED" is verified
            ''')
        elif (('E2E-RM' in context.tags) and (hasattr(context, 'rm_activation_status')) and (context.rm_activation_status is True)):
             logging.info("De-activating measurement configuration")
             execute_step(context,'''
                Given Remote measurement is deactivated
                And measurement status is "INACTIVE" within "10" minutes
            ''')

        if (('E2E-RM' in context.tags) and (hasattr(context, 'vsg_rm_status')) and (context.vsg_rm_status is True)):
            logging.info("Deactivating measurement for vehicle setup group")
            statistical_value=context.active_outline["deactivation_statistics"].strip('""')
            execute_step(context,f'''
                Given remote measurement deactivated for vehicle setup group
                And validate sync progress bar with "{statistical_value}"
            ''')

        if ((hasattr(context, 'vsg_remove_vehicles')) and (context.vsg_remove_vehicles is True)):
            logging.info("Removing vehicles from vehicle setup group")
            execute_step(context,f'''
                Given remove vehicles "{context.vsg_vehicles}" from vehicle setup group "{context.vsg_name}"
            ''')
        
        if 'E2E-RF' not in context.tags:
            logging.info("Clean up and Rebooting the device ...")
            execute_step(context,f'''
                    Given device operation "deleteAllJobs" is performed on "{context.specimen_device}" device
                    And device operation "rebootDevice" is performed on "{context.specimen_device}" device
                    And wait for device to be "ONLINE"
                ''')

        context.after_tag = False

def after_feature(context, feature):
    context.feature_count += 1
    logging.info("Entering AFTER FEATURE HOOKS...")
    logging.info("Logout from the application")
    execute_step(context, '''
        when logout from the application
    ''')
    
def after_all(context):
    logging.info("++++++++ calling update_feature_result method ++++++++++")
    api_gc_obj.write_json_file("temp/test_with_defects.json", tests_with_defects)
    update_feature_result(context)
    if len(failed_result_uploads) > 0:
        for feature_count in failed_result_uploads:
            update_feature_result(context, feature_count)