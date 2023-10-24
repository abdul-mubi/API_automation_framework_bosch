
import logging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import os
import re
from subprocess import Popen
import time
import logging
import steps.pageObjects.API_OTA_Updates_Class as Api_Ota_Updates_Class
import pageObjects.API_Generic_Class as API_Generic_Class
import steps.pageObjects.API_Campaign_Class as API_Campaign_Class
import steps.pageObjects.API_Inventory_Class as API_Inventory_Class
import steps.constantfiles.constants_ota_updates as constants

@step('check ECU flashing DP "{package_type}" is available')
@step('check OTA update DP "{package_type}" is available')
def step_impl(context, package_type):
    
    distribution_package = package_type.split(',')
    api_ota_update_obj = Api_Ota_Updates_Class.ApiOtaUpdatesClass(context.env, context.log_api_details)

    for package in distribution_package:
        package_id = api_ota_update_obj.search_distribution_package(package)
        if package_id == None:
            assert False, f"Distribution package - {package} name is not present "
        if package_id not in context.distribution_package_id:
            context.distribution_package_id.append(package_id)

@step('check CCU Self update distribution package from "{from_version}" to "{to_version}" available, create if not present')
@step('check CCU Self update "{package_type}" distribution package from "{from_version}" to "{to_version}" available, create if not present')
@step('check CCU Self update for "{security_option}" distribution package from "{from_version}" to "{to_version}" available, create if not present')
@step('check CCU Full update "{package_type}" distribution package to "{to_version}" available, create if not present')
@step('check CCU Full update for "{security_option}" distribution package to "{to_version}" available, create if not present')
def step_impl(context, to_version, from_version=None, package_type=None,security_option=None):
    if(security_option == None):
        security_option = context.device_config_data['su_security_option']
    api_ota_update_obj = Api_Ota_Updates_Class.ApiOtaUpdatesClass(context.env, context.log_api_details)
    fw_type = context.device_config_data['firmware_type'].upper()
    if package_type is not None:
        if from_version != None:
            package_name = constants.DELTA_UPDATE_DP_FORMAT.format(context.from_version,context.to_version,security_option, fw_type)
        else:
            context.from_version = None 
            package_name = constants.FULL_UPDATE_DP_FORMAT.format(context.to_version,security_option,fw_type)
    elif from_version == None:
        context.from_version = None
        package_name = constants.FULL_UPDATE_DP_FORMAT.format(context.to_version,security_option, fw_type)
    elif re.match("\D", from_version):
        from_version = context.from_version
        to_version = context.to_version
        package_name = constants.DELTA_UPDATE_DP_FORMAT.format(from_version,to_version,security_option,fw_type)
    else:
        package_name = constants.DELTA_UPDATE_DP_FORMAT.format(from_version,to_version,security_option, fw_type)

    distribution_package_id = api_ota_update_obj.search_distribution_package(package_name)
    if distribution_package_id is None:
        logging.info(f"Distribution package doesn't exist. So, creating Distribution package - {package_name}")
        gz_file=api_ota_update_obj.download_from_artifactory(context.device_config_data, context.to_version,context.from_version)
        if(context.device_config_data['artifactory']=='TCU_artifactory'):
            
            gz_file_strip=gz_file.strip(",_(unzip_me_before_install).zip")
            gz_file_name=constants.TCU_GZ_FILE.format(file_name=gz_file_strip)
        else:
            gz_file_name = constants.TCU2_GZ_FILE
        logging.info(f"Update package gz name = {gz_file_name}")
        update_package_id = api_ota_update_obj.create_update_package(gz_file_name)
        distribution_package_id = api_ota_update_obj.create_dist_package(package_name, security_option, update_package_id)
        api_ota_update_obj.create_and_check_container_status(distribution_package_id)
    
    context.distribution_package_id.append(distribution_package_id)


@step('{pea} OTA package is assigned to device with status "{status}"')
@step('{distribution_number:d} OTA package is assigned to device "{device}" with status "{status}"')
@step('OTA package is assigned to device "{device}" with status "{status}"')
def step_impl(context, status,device=None, distribution_number=None, pea=None):
    """Triggers package Self Update of device for upgrade / downgrade"""
    
    ota_status_list = []
    api_ota_update_obj = Api_Ota_Updates_Class.ApiOtaUpdatesClass(context.env, context.log_api_details)

    if pea is not None:
        api_ota_update_obj.get_assignment_ids_and_status(status, ota_status_list, context.distribution_package_id[-1], context)
    else:
        if(distribution_number is None):
            for distribution_package in context.distribution_package_id:
                api_ota_update_obj.get_assignment_ids_and_status(status, ota_status_list, distribution_package, context)
        else:
            api_ota_update_obj.get_assignment_ids_and_status(status, ota_status_list, context.distribution_package_id[distribution_number-1], context)

@step('verify assignment creation is "{dp_device_compatible}" for device "{device}" with incompatible distribution package')
@step('verify assignment creation is "{dp_device_compatible}" for device "{device}" with compatible distribution package')
def step_impl(context, device, dp_device_compatible):
    """ 
        Description         : Verifying the status of Assignment based upon whether the Distribution Package is Compatible with Device Firmware Version or not

        Pre-condition       : None

        Parameters          : dp_device_compatible, device

        Expected result     : Checks and Verifies the Compatibility of the Distribution Package with the Device Firmware
    """

    api_ota_update_obj = Api_Ota_Updates_Class.ApiOtaUpdatesClass(context.env, context.log_api_details) 

    for distribution_package in context.distribution_package_id:
        api_ota_update_obj.check_dp_device_compatibility(distribution_package, dp_device_compatible,context.device_id)

@step('flashing status of {assignment_number:d} OTA assignment is changed to "{exp_status}" within "{timer}" seconds')
@step('flashing status of OTA package is changed to "{exp_status}" within "{timer}" seconds')
@step('Self update of assignment "{count}" status "{exp_status}" is verified in "{timer}" seconds')
@step('Self update assignment status "{exp_status}" is verified in "{timer}" seconds')
@step('full update assignment status "{exp_status}" is verified in "{timer}" seconds')
def step_impl(context, exp_status, timer, assignment_number = None, count="1"):
    exception_status_list = []
    exception_dict = {}
    api_ota_update_obj = Api_Ota_Updates_Class.ApiOtaUpdatesClass(context.env, context.log_api_details)

    if(assignment_number is None):
        for assignments in context.ota_update_assignment_details:
            exception_status_list = api_ota_update_obj.verify_ota_status(assignments, timer, exp_status, exception_status_list, exception_dict, context)
            if len(exception_status_list) > 0 and "_FAILURE" not in exception_status_list:
                logging.info(f'Expected assignment status - {exp_status} is not appeared. Started checking in status history')
                exception_status_list = api_ota_update_obj.verify_ota_status_history(assignments, exp_status, exception_status_list)
    else:
        exception_status_list = api_ota_update_obj.verify_ota_status(context.ota_update_assignment_details[assignment_number-1], timer, exp_status, exception_status_list, exception_dict, context)
        if len(exception_status_list) > 0 and "_FAILURE" not in exception_status_list:
            logging.info(f'Expected assignment status - {exp_status} is not appeared. Started checking in status history')
            exception_status_list = api_ota_update_obj.verify_ota_status_history(context.ota_update_assignment_details[assignment_number-1], exp_status, exception_status_list)   
    
    if len(exception_status_list) > 0 :
        assert False, "Unexpected OTA assignment status appears. For Assignment[actual status,expected status] - {}".format(exception_dict)


@step('trigger the driver approval for device update if required')
def step_impl(context):
    if(context.device_config_data["su_driver_approval"]):
        api_ota_update_obj = Api_Ota_Updates_Class.ApiOtaUpdatesClass(context.env, context.log_api_details)
        status_list = api_ota_update_obj.get_flash_status(context.ota_update_assignment_details[-1], 900, "WAITING_FOR_UPDATE_CONDITION")
        if "UPDATING" in status_list:
            logging.error("Updating is already started without driver approval")
            #assert False, f"Assignment ID: {context.ota_update_assignment_details[-1]} already reached Updating without driver approval"
        elif("WAITING_FOR_UPDATE_CONDITION" in status_list):
            logging.info("Driver approval is required for this Update, performing Driver approval")
            context.execute_steps('''
                When trigger flashing using protocol "CANalization" Identifier "DriverApp_Break_True"
            ''')
        else:
            logging.error("Assignment did not reach to waiting for update condition state")
            assert False, f"OTA Assignment: {context.ota_update_assignment_details[-1]} didn't reach WAITING FOR UPDATE CONDITION state actual status: {status_list}"
    else:
        logging.info("Driver approval is not required for this update")

@step('wait for self update of device "{devices}" to complete in {timeout} seconds')
@step('wait for self update of device "{devices}" to complete')
def step_impl(context, devices, timeout=1800):
    """ 
    Description : Wait until the self-update of the device software is complete or till the timeout of 30 minutes
    
    """ 
    device_list = devices.split(",")
    update_status = {}
    update_status.update(dict.fromkeys(device_list, "Not_Completed"))
    start_time = time.time()
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    api_ota_update_obj = Api_Ota_Updates_Class.ApiOtaUpdatesClass(context.env, context.log_api_details)
    
    command = api_gen_obj.parse_json_file(context.device_config_data["command_file"])["getSelfUpdateStatus"][context.test_device]
    while (int(time.time() - start_time) < timeout ) and "Not_Completed" in update_status.values():
        for test_device in device_list:
            if(update_status[test_device]=="Not_Completed") and context.device_config_data['ssh_available']:
                api_ota_update_obj.check_update_status(test_device, update_status, command, start_time, context)
        time.sleep(30)
    logging.info(f"Self Update status for devices: {update_status}")
    incomplete_data = {key: value for (key, value) in update_status.items() if value != "Success"}
    if (len(incomplete_data) > 0) :
        logging.warning(f"Unable to verify self update status for all devices, following devices didn't reached success state: {incomplete_data}")

@step('full update device status "{exp_status}" is verified within "{timeout}" seconds')
def step_impl(context, exp_status, timeout=180):
    """ 
        Description         : verifying the full-update status of the device using device command

        Pre-condition       : None

        Parameters          : exp_status, timeout

        Expected result     : Wait until the full-update status of the device software is verified within given time
    """
    context.start_timer = time.time()
    api_gen_obj = API_Generic_Class.ApiGenericClass()

    command = api_gen_obj.parse_json_file(context.device_config_data["command_file"])["getFullUpdateStatus"][context.test_device]
    act_status = ""
    api_gen_obj.update_timeout_time(timeout)
    api_gen_obj.start_timer()
    while (api_gen_obj.check_timer()):
        if context.device_config_data['ssh_available']:
            result = api_gen_obj.ssh_execute(context.devices_data[context.specimen_device][context.test_device+"_IP"],context.device_config_data['ssh_key'],command)
            act_status = str(result[0]).replace("'","").strip(",.b\/n")

            if (exp_status == act_status):
                logging.info(f"Full update status {exp_status} is verified for {context.test_device}, took {int(time.time() - context.start_timer)} seconds")
                api_gen_obj.stop_timer()
                break
            elif (("FAILED" or "NOT_POSSIBLE" or "NOT_AVAILABLE") in act_status):
                api_gen_obj.stop_timer()
                break
        time.sleep(10)
    if act_status !="":
        assert (exp_status == act_status), f"Device has different full update status. Actual - {act_status} and Expected - {exp_status}"
    else:
        logging.info("skipped status check on prod device")

@step('all the flashing status "{ota_assignment_status}" is verified')
def step_impl(context, ota_assignment_status):
    """ Description     : it verifies the complete list of RF job status with the expected status list

        Pre-condition       : None

        Parameters          : ota_assignment_status  (Assignment separated by comma

                            eg: "DOWNLOADING,DOWNLOAD_SUCCESS"

        Expected result     : verifying complete flashing status
    """
    actual_ota_status_list = []

    logging.info(" Comparing actual RF job status list with the expected list ")
    expected_ota_status_list = ota_assignment_status.split(",")
    api_ota_update_obj = Api_Ota_Updates_Class.ApiOtaUpdatesClass(context.env, context.log_api_details)
    for created_assignment_id in context.ota_update_assignment_details:
        actual_ota_status_list = api_ota_update_obj.get_ota_status_history(created_assignment_id) 
    
    logging.info(f"Actual RF status list - {actual_ota_status_list}")
    logging.info(f"Expected RF status list - {expected_ota_status_list}")
    
    diff_ota_status = set(expected_ota_status_list) - set(actual_ota_status_list)
    extra_status = set(actual_ota_status_list) - set(expected_ota_status_list)
    assert len(diff_ota_status) == 0, f"Following OTA Status {diff_ota_status} didn't appear"
    logging.warning(f"Additional info in actual are: {extra_status}")

@step('perform remote flashing {number:d} times with the data {vehicle}, {device}, {distribution_package}, {protocol}, {identifier}, {identifier1}, {fota}, {fota_identifier}')
def step_impl(context, number, vehicle, device, distribution_package, protocol, identifier, identifier1, fota, fota_identifier):
    """ Description     : it completes the RF assignment data for flashing for multiple number of times

        Pre-condition       : None

        Parameters          : number, vehicle, device, distribution_package, protocol, identifier, identifier1, fota, fota_identifier

                            eg. number = 100, vehicle_new = "E2E_SYS_ES740_14", device = "ES740_46100072",
                            distribution_package = "E2E_RF_Standard_Job_encrypted", protocol = "UDSonCAN",
                            identifier = "DemoFlashSim", identifier1 = "DemoFlashSim_1", fota = "CANalization", fota_identifier = "DriverApp_Break_True"

        Expected result     : completes Remote Flashing multiple number of times over and over again on the same device
    """
    context.execute_steps(f'''
        Given device {device} is "ONLINE"
        And map device to the vehicle {vehicle}
        And check ECU flashing DP {distribution_package} is available
        And reference system {protocol} with identifier {identifier} is started
        And reference system {protocol} with identifier {identifier1} is started
        
    ''')
    
    context.repetitive_steps = f'''
        Given device {device} is "ONLINE"
        And OTA package is assigned to device {device} with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "80" seconds
        And trigger flashing using protocol {fota} identifier {fota_identifier}
        Then flashing status of OTA package is changed to "UPDATE_SUCCESS" within "120" seconds
        And reference system with protocol {fota} and identifier {fota_identifier} and number "0" is stopped
    '''
    
    context.execute_steps(f'''
        Given perform load test for {number} iterations with predefined steps
        Then reference system is stopped
    ''')

@step('perform remote flashing while RM is in progress for {number:d} times with the data {vehicle}, {device}, {distribution_package}, {protocol}, {identifier}, {identifier1}')
def step_impl(context, number, vehicle, device, distribution_package, protocol, identifier, identifier1):
    """ Description     : it completes the RF assignment data for flashing for multiple number of times

        Pre-condition       : None

        Parameters          : number, vehicle, device, distribution_package, protocol, identifier, identifier1

                            eg. number = 100, vehicle_new = "AUT_VSG_TEST_Vehicle_001", device = "CCU_2740003534",
                            distribution_package = "VECU_Slow_runImmediately_InstallRdaJob", protocol = "UDSonCAN",
                            identifier = "DemoFlashSim", identifier1 = "DemoFlashSim_1"

        Expected result     : completes Remote Flashing multiple number of times over and over again on the same device
    """
    context.execute_steps(f'''
        Given device {device} is "ONLINE"
        And map device to the vehicle {vehicle}
        And check ECU flashing DP {distribution_package} is available
        And reference system {protocol} with identifier {identifier} is started
        And reference system {protocol} with identifier {identifier1} is started
    ''')
    
    context.repetitive_steps = f'''
        Given device {device} is "ONLINE"
        And OTA package is assigned to device {device} with status "UPDATE_ASSIGNED"
        Then flashing status of OTA package is changed to "UPDATE_SUCCESS" within "200" seconds
    '''
    
    context.execute_steps(f'''
        Given perform load test for {number} iterations with predefined steps
        Then reference system is stopped
    ''')

@step('perform remote flashing with CAN disconnection {number:d} times with the data {vehicle}, {device}, {distribution_package}, {protocol}, {identifier}, {identifier1}, {fota}, {fota_identifier}')
def step_impl(context, number, vehicle, device, distribution_package, protocol, identifier, identifier1, fota, fota_identifier):
    """ Description     : it fails the RF assignment data for flashing for multiple number of times due to CAN disconnection in the middle

        Pre-condition       : None

        Parameters          : number, vehicle, device, distribution_package, protocol, identifier,identifier1, fota,fota_identifier

                            eg. number = 100, vehicle_new = "E2E_SYS_ES740_14", device = "ES740_46100072",
                            distribution_package = "E2E_RF_Standard_Job_encrypted", protocol = "UDSonCAN",
                            identifier = "DemoFlashSim", identifier1 = "DemoFlashSim_1", fota = "CANalization", fota_identifier = "DriverApp_Break_True"

        Expected result     : fails the Remote Flashing multiple number of times over and over again on the same device
    """
    context.execute_steps(f'''
        Given device {device} is "ONLINE"
        And map device to the vehicle {vehicle}
        And check ECU flashing DP {distribution_package} is available
        And reference system {protocol} with identifier {identifier} is started
        And reference system {protocol} with identifier {identifier1} is started
    ''')
    context.repetitive_steps = f'''
                Given device {device} is "ONLINE"
                And OTA package is assigned to device {device} with status "UPDATE_ASSIGNED"
                And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "80" seconds
                And trigger flashing using protocol {fota} identifier {fota_identifier}
                And test waits for a random time period of "0.5-1.5" minutes
                And reference system is stopped
                Then flashing status of OTA package is changed to "UPDATE_FAILURE" within "120" seconds
            '''
    context.execute_steps(f'''
        Given perform load test for {number} iterations with predefined steps
    ''')

@step('trigger flashing using protocol "{fota}" Identifier "{fota_identifier}" for "{process_name}" process')
@step('trigger flashing using protocol "{fota}" Identifier "{fota_identifier}"')
def step_impl(context, fota, fota_identifier, process_name=None):
    """ Description     : starts the flashing batch to trigger flash Job

        Pre-condition   : None

        Parameters      : startFlash, fota, identifier

                          eg. startFlash = "startFlash" (Used for batch file call)
                          
                          fota = "CANalization_startFlash"

                          identifier = "ES740_RD_SmokeTest"

        Expected result : starts the flashing process
    """
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    
    if context.test_device != "virtual_device":
        identifiers = "DriverApp_Break_True"
        context.fota = fota
        fota = fota + "_" + context.device_id
        
        if (process_name != None):
            for each_device in context.device_for_fota:
                context.specimen_device = each_device
                test_device = api_gen_obj.get_device_type(each_device,context)
                context.test_device = test_device
                context.vrs_port_2 = context.devices_data[test_device.upper()]["vrs_port_2"]
                fota_identifier = identifiers
                proc = api_gen_obj.initiate_vrs(context, fota, fota_identifier, context.vrs_port_2, context.specimen_device)
                context.protocol_names.append(fota)
        else:
            context.fota_identifier = fota_identifier
            proc = api_gen_obj.initiate_vrs(context, fota, fota_identifier, context.vrs_port_2, context.specimen_device)
            context.protocol_names.append(fota)
        
        context.vrs_running = True
        context.all_vrs_proc.append(proc)
    else:
        logging.info("Skipping VRS trigger on virtual device")


@step('verify the hex content for "{identifier}"')
def step_impl(context, identifier):
    """ Description     : Verify the hex content of file created after Remote Flashing

        Pre-condition   : None

        Parameters      : identifier

                          eg. 'identifier' = "ES740_RFSmokeTest"
                          
        Expected result : verify generated hex file content with the expected hex file content   
    """
    
    
    path = os.path.dirname(os.path.abspath(__file__))
    file_path = path + constants.GC_UDS_DATA_PATH
    
    if context.test_device != "virtual_device":
        if ("CCU" in identifier.upper()):
            ref_file = file_path+"WR_cTP_Ref.hex"
            actual_file = file_path+"WR_cTP.hex"
            proc = Popen(['FC',ref_file, actual_file], stdout=None,stderr=None)
            returncode = proc.wait()
        else:
            ref_file = file_path+"DemoFlash_Master_Ref.hex"
            actual_file = file_path+"DemoFlash_Master.hex"
            proc = Popen(['FC', ref_file, actual_file], stdout=None,stderr=None)
            returncode = proc.wait()
        assert returncode == 0
    else:
        logging.info("")


@step('"{process}" OTA assignment is revoked')
@step('revoke the OTA assignment')
@step('revoke {assignment_number:d} OTA assignment')
def step_impl(context, assignment_number = None, process=None):
    """
    Description: To revoke the OTA Assignment.
    Parameters: 
            assignment_number : Sl No  of Assignment, To check the Specific assignment Details 
                                Default Value: None
                                Eg: 1 (In case of First Assignment)
    Expected Result: Assignment is revoked successfully
    """
    api_ota_update_obj = Api_Ota_Updates_Class.ApiOtaUpdatesClass(context.env, context.log_api_details)

    # for Campaign Process, fetching assignment IDs created from a Campaign - for performing revocation
    if (process is not None and process.upper() == "CAMPAIGN"):
        api_campaign_obj = API_Campaign_Class.ApiCampaignClass(context.env, context.log_api_details)
        for campaign_id in context.campaign_ids:
            vehicles_list = api_campaign_obj.get_campaign_vehicles_details(campaign_id)
            campaign_assignments = api_campaign_obj.get_assignment_id_in_campaign(campaign_id,vehicles_list)
            context.campaign_assignments = campaign_assignments
    
    if("campaign_assignments" in context):
        flash_assignments = context.campaign_assignments
    else:
        flash_assignments = context.ota_update_assignment_details
        
    if (assignment_number is None):
        for created_assignment in flash_assignments:
            api_ota_update_obj.revoke_assignment(created_assignment)
    else:
        api_ota_update_obj.revoke_assignment(flash_assignments[assignment_number-1])

@step('retry revoked Ota assignment using retry mechanism')
def step_impl(context):
        """
        Description: To retry the Revoked OTA Assignment.
    
        Expected Result: Revoked Assignment is retried successfully
        """
        api_ota_update_obj = Api_Ota_Updates_Class.ApiOtaUpdatesClass(context.env, context.log_api_details)
        for assignment in context.ota_update_assignment_details:
            api_ota_update_obj.retry_assignment(assignment)

@step('verify that assignment revocation is failed')
def step_impl(context):
    """
    Description: To verify that OTA Assignment revocation is failed.
    Parameters: None
    Expected Result: Assignment is revocation is Failed
    """
    
    api_ota_update_obj = Api_Ota_Updates_Class.ApiOtaUpdatesClass(context.env, context.log_api_details)
    for created_assignment_id in context.ota_update_assignment_details:
        api_ota_update_obj.revocation_failure_check(created_assignment_id)

@step('verify logs for "{assignment_type}" OTA assignments within "{timer}" seconds')
def step_impl(context, assignment_type, timer):

    api_ota_update_obj = Api_Ota_Updates_Class.ApiOtaUpdatesClass(context.env, context.log_api_details)

    for assignments in context.ota_update_assignment_details:
        api_ota_update_obj.verify_ota_logs(assignments, timer, assignment_type)


@step('perform ECU update with log generation {number:d} times with the data {vehicle}, {device}, {distribution_package}, {protocol}, {identifier}, {identifier1}, {fota}, {fota_identifier}')
def step_impl(context, number, vehicle, device, distribution_package, protocol, identifier, identifier1, fota, fota_identifier):
    """ Description     : it completes the ECU Flashing with Log generation for multiple number of times

        Pre-condition       : None

        Parameters          : number, vehicle, device, distribution_package, protocol, identifier, identifier1, fota, fota_identifier

        Expected result     : completes Remote Flashing with log generation multiple number of times over and over again on the same device
    """
    context.execute_steps(f'''
        Given device {device} is "ONLINE"
        And map device to the vehicle {vehicle}
        And check ECU flashing DP {distribution_package} is available
        And reference system {protocol} with identifier {identifier} is started
        And reference system {protocol} with identifier {identifier1} is started
    ''')
    context.repetitive_steps = f'''
                    Given device {device} is "ONLINE"
                    When OTA package is assigned to device {device} with status "UPDATE_ASSIGNED"
                    And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "80" seconds
                    And trigger flashing using protocol {fota} identifier {fota_identifier}
                    Then flashing status of OTA package is changed to "UPDATE_SUCCESS" within "120" seconds
                    And reference system with protocol {fota} and identifier {fota_identifier} and number "0" is stopped
                    And verify logs for "SUCCESSFUL" OTA assignments within "180" seconds
                '''
    context.execute_steps(f'''
        Given perform load test for {number} iterations with predefined steps
        Then reference system is stopped
    ''')
    
    
@step('perform ECU update failure with log generation {number:d} times with the data {vehicle}, {device}, {distribution_package}, {protocol}, {identifier}, {identifier1}, {fota}, {fota_identifier}')
def step_impl(context, number, vehicle, device, distribution_package, protocol, identifier, identifier1, fota, fota_identifier):
    """ Description     : it completes the ECU Flashing using wrong binaries with Log generation for multiple number of times

        Pre-condition       : None

        Parameters          : number, vehicle, device, distribution_package, protocol, identifier, identifier1, fota, fota_identifier

                            eg. number = 100, vehicle_new = "E2E_SYS_ES740_14", device = "ES740_46100072",
                            distribution_package = "E2E_RF_Standard_Job_encrypted", protocol = "UDSonCAN",
                            identifier = "DemoFlashSim", identifier1 = "DemoFlashSim_1", fota = "CANalization", fota_identifier = "DriverApp_Break_True"

        Expected result     : completes Remote Flashing using wrong binaries with log generation multiple number of times over and over again on the same device
    """
    
    context.execute_steps(f'''
        Given device {device} is "ONLINE"
        And map device to the vehicle {vehicle}
        And check ECU flashing DP {distribution_package} is available
        And reference system {protocol} with identifier {identifier} is started
        And reference system {protocol} with identifier {identifier1} is started
    ''')
    
    context.repetitive_steps = f'''
        Given device {device} is "ONLINE"
        When OTA package is assigned to device {device} with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "80" seconds
        And trigger flashing using protocol {fota} identifier {fota_identifier}
        Then flashing status of OTA package is changed to "UPDATE_FAILURE" within "120" seconds
        And reference system with protocol {fota} and identifier {fota_identifier} and number "0" is stopped
        And verify logs for "FAILED" OTA assignments within "180" seconds
    '''
            
    context.execute_steps(f'''
        Given perform load test for {number} iterations with predefined steps
        Then reference system is stopped
    ''')
@step('Perform PEA update')
def step_impl(context):
    logging.info("Performing PEA Update for device")
    context.execute_steps(f'''
        When check ECU flashing DP "{constants.PEA_UPDATE_PACKAGE}" is available
        And "pea" OTA package is assigned to device with status "UPDATE_ASSIGNED"
        Then Self update assignment status "UPDATE_SUCCESS" is verified in "100" seconds
    ''')
    context.distribution_package_id.clear()
    context.ota_update_assignment_details.clear()
    context.ota_status_list.clear()

@step('Perform Delta update for device "{specimen_device}" from "{device_version}" to "{to_version}"')
def step_impl(context, specimen_device, device_version, to_version):
    logging.info(f'Device FW version is not matching, performing delta update from: {device_version} to: {to_version}')
    context.execute_steps(f'''
        Given device "{specimen_device}" is "ONLINE"
        And check CCU Self update distribution package from "{device_version}" to "{to_version}" available, create if not present
        When OTA package is assigned to device "{specimen_device}" with status "UPDATE_ASSIGNED"
        And trigger the driver approval for device update if required
        Then Self update assignment status "UPDATING" is verified in "300" seconds
        And wait for self update of device "{specimen_device}" to complete
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And Self update assignment status "UPDATE_SUCCESS" is verified in "300" seconds
        And device FW "{to_version}" is verified
        ''')

@step('Perform Full update of CCU-M device "{specimen_device}" to "{to_version}"')
def step_impl(context, specimen_device, to_version):
    logging.info(f'Device FW version is not matching, performing Full update to: {to_version}')
    context.execute_steps(f'''
        Given device "{specimen_device}" is "ONLINE"
        And check CCU Full update "full_update" distribution package to "{to_version}" available, create if not present
        When OTA package is assigned to device "{specimen_device}" with status "UPDATE_ASSIGNED"
        And trigger the driver approval for device update if required
        Then full update assignment status "UPDATING" is verified in "600" seconds
        And full update device status "Activated" is verified within "1800" seconds
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And switch "CL15" is turned "On"
        And full update device status "UpdateComplete" is verified within "600" seconds
        And wait for device to be "ONLINE"
        Then full update assignment status "UPDATE_SUCCESS" is verified in "60" seconds
        And device FW version is verified 
    ''')

@step('Perform Full update of CCU device "{specimen_device}" to "{to_version}"')
def step_impl(context, specimen_device, to_version):
    logging.info(f'Device FW version is not matching, performing Full update to: {to_version}')
    context.execute_steps(f'''
        Given device "{specimen_device}" is "ONLINE"
        And check CCU Full update "full_update" distribution package to "{to_version}" available, create if not present
        When OTA package is assigned to device "{specimen_device}" with status "UPDATE_ASSIGNED"
        And trigger the driver approval for device update if required
        Then full update assignment status "UPDATING" is verified in "600" seconds
        And full update device status "VERIFY_SUCCESSFUL" is verified within "300" seconds
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And switch "CL15" is turned "On"
        And full update device status "UPDATE_SUCCESSFUL" is verified within "600" seconds
        And wait for device to be "ONLINE"
        Then full update assignment status "UPDATE_SUCCESS" is verified in "60" seconds
        And device FW version is verified 
    ''')

@step('Perform USB update for device "{specimen_device}" to "{to_version}"')
def step_impl(context, specimen_device, to_version):
    logging.info(f'Device FW version is not matching, performing USB update to: {context.to_version}')
    context.execute_steps(f'''
        Given device "{specimen_device}" is "ONLINE"
        And get image file from artifactory for FW "{to_version}"
        When performing USB flash using powershell file
        And device operation "rebootDevice" is performed
        Then device "{specimen_device}" is "ONLINE"
        And device FW "{to_version}" is verified
    ''')

@step('Check "{device}" FW version to update device if version is not as expected')
@step('Check "{device}" FW version to perform "{type_of_update}" to "{exp_device_version}" if version is not as expected')
def step_impl(context,device,type_of_update=None,exp_device_version=None):
    api_inventory_obj = API_Inventory_Class.ApiInventoryClass(context.env, context.log_api_details)
    api_ota_update_obj = Api_Ota_Updates_Class.ApiOtaUpdatesClass(context.env, context.log_api_details)
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    device_list = [key for key in context.devices_data.keys() if type(context.devices_data[key]) == dict and context.devices_data[key]['device_env'] == context.env]
    exception_list = []
    for specimen_device in device_list:
        try:
            device_id = context.devices_data[specimen_device]["device_name"]
            actual_device_version = api_inventory_obj.get_firmware_version_of_device(device_id).strip(",._DEBUG").strip(",._PRODUCTION")
            command_map = api_gen_obj.parse_json_file(context.device_config_data["command_file"])
            if context.device_config_data["ssh_available"]:
                logging.info(f"Checking firmware in the device via SSH for Device: {specimen_device}")
                device_version = api_gen_obj.get_firmware_version_from_device(command_map, context.test_device, context.devices_data[specimen_device][device+"_IP"],context.device_config_data['ssh_key'])
            else:
                device_version = actual_device_version
            if ( device_version != None) and (actual_device_version != device_version) :
                logging.warning("Device version in inventory is not matching with device version. Continuing the test with FW version inside device")
                actual_device_version = device_version
            if type_of_update == None and exp_device_version == None and "Type_of_update" in context.config.userdata:
                exp_device_version = api_ota_update_obj.fetch_expected_device_version(actual_device_version,context.config.userdata)
                type_of_update = context.config.userdata["Type_of_update"]
            if not hasattr(context, 'from_version'): 
                context.from_version = actual_device_version
                context.to_version = exp_device_version
            logging.info(f"type_of_update {type_of_update}, actual_device_version: {actual_device_version}, specimen_device: {specimen_device} exp_device_version: {exp_device_version}")
            api_ota_update_obj.perform_device_update(context,type_of_update,actual_device_version,specimen_device,exp_device_version)
        except Exception as e:
            logging.error(f"Unable to Update {specimen_device} due to error {e}")
            exception_list.append(f"Unable to Update {specimen_device} due to error {e}")
            
    assert len(exception_list) == 0, f"Failed to Update the devices, error {exception_list}"

@step('check desired state package "{desired_state_package}" is available, create if not present')
def step_impl(context, desired_state_package):
    """Checks desired state package, if not available create it using Desired_states.json

    Args:
        desired_state_package (string): package name
    """
    api_ota_update_obj = Api_Ota_Updates_Class.ApiOtaUpdatesClass(context.env, context.log_api_details)
    package_created = api_ota_update_obj.check_desired_state_package(desired_state_package)    
    if not package_created:
        api_ota_update_obj.create_desired_state_package(desired_state_package)
    context.desired_state_package = desired_state_package

@step('desired package is assigned to vehicle "{vehicle}"')
def step_impl(context, vehicle):
    """Assigns desired state assignment to current vehicle

    Args:
        vehicle (string): vehicle
    """
    api_ota_update_obj = Api_Ota_Updates_Class.ApiOtaUpdatesClass(context.env, context.log_api_details)
    context.desired_state_assignment_id = api_ota_update_obj.assign_desired_state_package(context.vehicle_id,context.desired_state_package)
    logging.info(f"Desired state assignment created for vehicle {context.vehicle_id} with id {context.desired_state_assignment_id}")
    
@step('desired state package assignment is changed to {exp_status} with sub status {exp_sub_status} within "{timer}" seconds')
def step_impl(context, exp_status, exp_sub_status, timer):
    """checks desired state assignment status and sub status with expected 

    Args:
        exp_status (string): expected desired state status 
        exp_sub_status (json): expected desired state sub status
        timer (string): time to wait until expected status and sub status
    """
    api_ota_update_obj = Api_Ota_Updates_Class.ApiOtaUpdatesClass(context.env, context.log_api_details)
    desired_state_assignment_id = context.desired_state_assignment_id
    if(desired_state_assignment_id != ""):
        api_ota_update_obj.check_desired_state_assignment_status(desired_state_assignment_id,exp_status,exp_sub_status,timer)
    
@step('desired state assignment message changed to "{message}"')
def step_impl(context, message):
    """Checks desired state assignment message with expected message

    Args:    
        message (string): desired state assignment message
    """
    api_ota_update_obj = Api_Ota_Updates_Class.ApiOtaUpdatesClass(context.env, context.log_api_details)
    desired_state_assignment_id = context.desired_state_assignment_id
    desired_state_message = api_ota_update_obj.check_desired_state_assignment_message(desired_state_assignment_id)
    assert desired_state_message == message, f"Desired state assignment message is {desired_state_message} expected is {message}"
