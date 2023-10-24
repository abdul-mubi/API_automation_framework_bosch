import requests
import logging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import os
import time
import json
import utils.API_Requests as API_Requests
import steps.pageObjects.API_OTA_Function_Calls_GX_Class as API_OTA_Function_Calls_GX_Class
import pageObjects.API_FleetManagement_Class as API_FleetManagement_Class
import steps.constantfiles.constants_ota_function_calls_gx as constants
import pageObjects.API_Campaign_Class as API_Campaign_Class


@step('diagostic function details "{diag_func_name}" having capability "{capability}" are available')
def step_impl(context, diag_func_name, capability):
    context.diag_func_name = diag_func_name
    context.capability = capability
    path = os.path.dirname(os.path.abspath(__file__))
    test_data_repo = path + constants.RD_TD_CRUD_JSON

    with open(test_data_repo, 'r') as dataFile:
        test_data = json.load(dataFile)
        context.test_data = test_data


@step('diagnostic function "{diag_func_name}" with "{func_description}" having capability "{capability}" using "{file_name}" is created, if not present')
def step_impl(context, diag_func_name, func_description, capability, file_name):

    """ Description         : creates a diagnostic function using the diag_func_name and file having capability

        Pre-condition       : None

        Parameters          : diag_func_name - Name of Diagnostic Function
                              
                                eg. 'diag_func_name' = "SYS-I-RD-DConfi.01"

                              func_description - description of the diagnostic function
                                
                                eg. 'func_description' = "it reads all DTCs"
                            
                              capability - capability of the RD function
                                
                                eg. 'capability' = "READ_DTC"

                              file - file name needed for function creation

                                eg. 'file_name' = "wrongSchema.zip"

        Expected result     : new diagnostic function is created in Draft state    
    """
    logging.info(f"Checking if Diagnostic Function - {diag_func_name} already exists or not.")

    context.diag_func_name = diag_func_name
    context.capability = capability
    api_rd_obj = API_OTA_Function_Calls_GX_Class.ApiOTAFunctionCallsGXClass(context.env, context.log_api_details)
    data = api_rd_obj.get_diag_func_details_by_name(context.diag_func_name)

    if "_embedded" in data:
        logging.info(f"Diagnostic Function - {diag_func_name} already created and exists. Not creating new Diagostic Function.")
    else:
        logging.info(f"Diagnostic Function - {context.diag_func_name} doesn't exist.")
        logging.info(f"Creating a new Diagnostic Function - {context.diag_func_name}")
        
        path = os.path.dirname(os.path.abspath(__file__))
        file_path = path + constants.OTA_FUNCTION_CALL_GX + file_name
        logging.info(file_path)
        files = {'file': open(file_path, 'rb')}

        new_data = {"name":context.diag_func_name,
            "description":func_description,
            "diagnosticCapability":context.capability,
            "remotelyTriggerable":True,
            'parameterMappings':{}}

        datas = {
            'metadata':json.dumps(new_data)
        }

        api_rd_obj.create_diag_func(datas, files)        

    data = api_rd_obj.get_diag_func_details_by_name(context.diag_func_name)
    for df in data['_embedded']['diagnosticFunctions']:
        assert df['diagnosticCapability'] ==  context.capability , f"Capapbility ----- Expected : {context.capability} - > Actual : {df['diagnosticCapability']}"
        assert df['fileName'] == file_name , f"FileName ----- Expected : {file_name} - > Actual : {df['fileName']}"
        context.diag_function_id = df['diagnosticFunctionId']
        break


@step('Diagnostic function "{diag_func_name}" is available')
def step_impl(context, diag_func_name):
    context.diag_func_name = diag_func_name
    api_request = API_Requests.ApiRequestsClass(context.env, context.log_api_details)
    r1 = api_request.get_request(constants.RD_DIAG_FUNC_NAME.format(context.diag_func_name))
    assert r1.status_code == requests.codes.ok, constants.RD_FUNC_FAILURE
    res1 = r1.json()['_embedded']['diagnosticFunctions']
    for res in res1:
        if res['name'] == context.diag_func_name:
            context.diag_function_id = res['diagnosticFunctionId']
            break


@step('state of diagnostic function is "{diag_func_state}"')
def step_impl(context, diag_func_state):
    time.sleep(5)

    logging.info(f"Checking the state of Diagnostic Function - {context.diag_func_name}")
    api_request = API_Requests.ApiRequestsClass(context.env, context.log_api_details)
    r1 = api_request.get_request(constants.RD_DIAG_SEARCHNAME_FUNC_ID.format(context.diag_function_id))
    assert r1.status_code == requests.codes.ok, constants.RD_FUNC_FAILURE
    res1 = r1.json()['_embedded']['diagnosticFunctions']
    for res in res1:
        if res['diagnosticFunctionId'] == context.diag_function_id:
            context.diag_function_state = res['state']
            context.capability = res['diagnosticCapability']
            break

    assert context.diag_function_state == diag_func_state.upper(), "Unexpected. Diagnostic Function state is not expected. Actual State - "+context.diag_function_state+". Expected State - "+diag_func_state


@step('"{action}" diagnostic function attributes')
def step_impl(context, action):
    path = os.path.dirname(os.path.abspath(__file__))
    test_data_repo = path + constants.RD_TD_CRUD_JSON

    with open(test_data_repo, 'r') as dataFile:
        test_data = json.load(dataFile)
        modifying_values = test_data["DiagnosticFunction"][action.upper()]

        api_rd_obj = API_OTA_Function_Calls_GX_Class.ApiOTAFunctionCallsGXClass(context.env, context.log_api_details)
        b_edit_status = api_rd_obj.edit_diag_func(context.diag_function_id, modifying_values)
        assert b_edit_status == True, "Modifying Diagnostic Function didn't work as expected"
        context.modifying_values = modifying_values
        if "RE-EDIT" not in action:
            context.diag_func_name = modifying_values["name"]


@step('function is updated with new values')
def step_impl(context):
    # verify_diag_func_values
    api_rd_obj = API_OTA_Function_Calls_GX_Class.ApiOTAFunctionCallsGXClass(context.env, context.log_api_details)
    b_diag_func_check = api_rd_obj.verify_diag_func_values(context.diag_func_name, context.modifying_values)
    assert b_diag_func_check == True, "Unexpected. Changed Diagnostic Function values are not appearing correctly"

@step('release diagnostic function, if not in RELEASED state')
@step('diagnostic function is released')
def step_impl(context):
    """release the created diagnostic Function"""
    api_rd_obj = API_OTA_Function_Calls_GX_Class.ApiOTAFunctionCallsGXClass(context.env, context.log_api_details)
    data = api_rd_obj.get_diag_func_details_by_id(context.diag_function_id)
    logging.info(f'{context.diag_func_name} Diagnostic Function current state is {data} ')
    if data != 'RELEASED':
        logging.info(f' Releasing {context.diag_func_name} Diagnostic Function ')
        api_rd_obj.release_diag_func(context.diag_function_id)
        logging.info(f' {context.diag_func_name} Diagnostic Function is Released ')
        logging.info(f'{context.diag_func_name} Diagnostic Function current state is {data} ')


@step('editing diagnostic function is triggered')
def step_impl(context):
    """initiates the edit process of Diagnostic Function"""
    ep = constants.RD_DIAG_FUNC_ID_DRAFT.format(context.diag_function_id)
    api_request = API_Requests.ApiRequestsClass(context.env, context.log_api_details)
    ep_etag = constants.RD_DIAG_FUNC_ID.format(context.diag_function_id)
    etag = api_request.get_etag(ep = ep_etag)

    r = api_request.post_request(ep=ep, params={}, 
                                custom_header={'if-match':etag})
    assert r.status_code == requests.codes.created, "Unexpected. Re-edit of Diagnostic Function is not triggered correctly."


@step('diagnostic configuration "{diag_config_name}" with description "{config_describe}" using function "{diag_func_name}" is created, if not present')
def step_impl(context, diag_config_name, config_describe, diag_func_name):
    """new diagnostic configuration is created using diagnostic function"""
    context.diag_config_name = diag_config_name

    logging.info(f"Checking if Diagnostic Configuration - {diag_config_name} already exists or not.")

    api_rd_obj = API_OTA_Function_Calls_GX_Class.ApiOTAFunctionCallsGXClass(context.env, context.log_api_details)
    data = api_rd_obj.get_diag_config_details_by_name(diag_config_name)

    if "_embedded" in data:
        logging.info(f"Diagnostic Configuration - {diag_config_name} already created and exists. Not creating new Diagostic Function.")
    else:
        logging.info(f"Diagnostic Configuration - {diag_config_name} doesn't exist.")
        logging.info(f"Creating a new Diagnostic Configuration - {diag_config_name}")
        data = {"name":diag_config_name, "description":config_describe,
                "diagnosticFunctions":[{"diagnosticFunctionId": context.diag_function_id,
                "diagnosticCapability": context.capability
                }
                ]
        }
        logging.info(" Creating Diagnostic Configuration using Diag Function - {} ".format(diag_func_name))
        api_rd_obj.create_diag_configuration(data)

    data = api_rd_obj.get_diag_config_details_by_name(diag_config_name)
    for res in data['_embedded']['diagnosticConfigurations']:
        if res["name"] == context.diag_config_name:
            context.diag_config_id = res["diagnosticConfigurationId"]
            break



@step('Diagnostic configuration "{diag_config_name}" is available')
def step_impl(context, diag_config_name):

    context.diag_config_name = diag_config_name
    api_request = API_Requests.ApiRequestsClass(context.env, context.log_api_details)
    r1 = api_request.get_request(constants.RD_DIAG_CONFIG_SEARCH_NAME.format(context.diag_config_name))
    assert r1.status_code == requests.codes.ok, constants.RD_FUNC_FAILURE
    res1 = r1.json()['_embedded']['diagnosticConfigurations']
    for res in res1:
        if res['name'] == context.diag_config_name:
            context.diag_config_id = res['diagnosticConfigurationId']
            break


@step('state of diagnostic configuration is "{config_state}"')
def step_impl(context, config_state):
    """checks the state of created diagnostic Configuration"""
    time.sleep(5)
    logging.info(f"Checking the state of Diagnostic Configuration - {context.diag_config_name}")
    api_request = API_Requests.ApiRequestsClass(context.env, context.log_api_details)
    r1 = api_request.get_request(constants.RD_DIAG_CONFIG_SEARCH_NAME_ID.format(context.diag_config_id))
    assert r1.status_code == requests.codes.ok, "Retrieving Diagnostic Configuration information failed"
    res1 = r1.json()['_embedded']['diagnosticConfigurations']
    for res in res1:
        if res['diagnosticConfigurationId'] == context.diag_config_id:
            context.diag_config_state = res['state']
            break

    assert context.diag_config_state == config_state.upper(), "Unexpected. Diagnostic COnfiguration state is not expected. Actual State - "+context.diag_config_state+". Expected State - "+config_state


@step('"{action}" diagnostic configuration attributes')
def step_impl(context, action):
    path = os.path.dirname(os.path.abspath(__file__))
    test_data_repo = path + constants.RD_TD_CRUD_JSON

    with open(test_data_repo, 'r') as dataFile:
        test_data = json.load(dataFile)
        modifying_values = test_data["DiagnosticConfiguration"][action.upper()]

        api_rd_obj = API_OTA_Function_Calls_GX_Class.ApiOTAFunctionCallsGXClass(context.env, context.log_api_details)
        b_edit_status = api_rd_obj.edit_diag_configuration(context.diag_config_id, modifying_values)
        assert b_edit_status == True, "Modifying Diagnostic Configuration didn't work as expected"
        context.modifying_values = modifying_values
        if "RE-EDIT" not in action:
            context.diag_config_name = modifying_values["name"]


@step('configuration is updated with new values')
def step_impl(context):
    api_rd_obj = API_OTA_Function_Calls_GX_Class.ApiOTAFunctionCallsGXClass(context.env, context.log_api_details)
    b_diag_config_check = api_rd_obj.verify_diag_config_values(context.diag_config_name, context.modifying_values)
    assert b_diag_config_check == True, "Unexpected. Changed Diagnostic Configuration values are not appearing correctly"

@step('release diagnostic configuration, if not in RELEASED state')
@step('diagnostic configuration is released')
def step_impl(context):
    """release the created diagnostic Configurations"""
    api_rd_obj = API_OTA_Function_Calls_GX_Class.ApiOTAFunctionCallsGXClass(context.env, context.log_api_details)
    data = api_rd_obj.get_diag_config_details_by_id(context.diag_config_id)
    if data != "RELEASED":
        logging.info(f' Releasing {context.diag_config_name} Diagnostic Function ')
        api_rd_obj.release_diag_confih(context.diag_config_id)
        logging.info(f' {context.diag_config_name} Diagnostic Function is Released ')
        logging.info(f'{context.diag_config_name} Diagnostic Function current state is {data} ')


@step('editing diagnostic configuration is triggered')
def step_impl(context):
    """initiates the edit process of Diagnostic Configuration"""
    
    api_request = API_Requests.ApiRequestsClass(context.env, context.log_api_details)
    ep_etag = constants.RD_DIAG_CONFIG_ID.format(context.diag_config_id)
    etag = api_request.get_etag(ep = ep_etag)
    ep = constants.RD_DIAG_CONFIG_ID_DRAFT.format(context.diag_config_id)
    r = api_request.post_request(ep=ep, params={}, 
                                custom_header={'if-match':etag,'Accept':"application/hal+json;charset=UTF-8"})
    assert r.status_code == requests.codes.created, "Unexpected. Re-edit of Diagnostic Configuration is not triggered correctly."

@step('deactivate diagnostic assignment on vehicle "{vehicle_name}" from "{assignment_state}" state')
@step('deactivate ACTIVE diagnostic configuration if present')
@step('deactivate ACTIVE diagnostic configuration if present for "{vehicles}"')
@step('remote diagnostic deactivated for vehicles in RD activation campaign "{activation_campaign_id_list}" from "{assignment_state_1}" and validate status as "{assignment_state_2}" state and sub_status is "{sub_status}" for "{capability}" in campaign')
def step_impl(context, vehicle_name = None, vehicles = None, assignment_state = None, assignment_state_1 = None, assignment_state_2 = None,  activation_campaign_id_list=None, sub_status=None, capability=None):
    """ Description         : deactivates the diagnostic cofiguration assigned to a vehicle

        Pre-condition       : None

        Parameters          : Vehicle_name - Name of the Vehicle in which Diagnostic should be activated 
                                (Default Value- None, by default context.vehicle_name is selected)
                              assignment_state - This variable is used to deactivate assignment from inactive state for device slot.
                                (Default Value- None, deactivation of inactive assignment is only specific to device slot feature)

        Expected result     : method deactivates existing diagnostic Configuration assigned to a particular vehicle    
    """
    api_rd_obj = API_OTA_Function_Calls_GX_Class.ApiOTAFunctionCallsGXClass(context.env,context.log_api_details)
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env,context.log_api_details)
    api_campaign_obj = API_Campaign_Class.ApiCampaignClass(context.env, context.log_api_details)
    
    if vehicle_name is not None and assignment_state is not None:
        if(len(vehicle_name) == vehicle_name.count(' ')):
            vehicle_name = context.default_vehicle
        context.vehicle_name = vehicle_name
        context.vehicle_id =  api_fm_obj.get_vehicle_id_by_name(context.vehicle_name, context)
        context.deactivation_time = api_rd_obj.deactivate_rd_config(context.vehicle_id, vehicle_name, assignment_state)
    elif vehicles is not None:
        vehicle_list = vehicles.split(",")
        for vehicle in vehicle_list:
            vehicle_id = context.vehicle_data[vehicle]["vehicle_id"]
            context.deactivation_time =  api_rd_obj.deactivate_rd_config(vehicle_id, vehicle_name, assignment_state)
    elif activation_campaign_id_list is not None:
        for campaign_id in context.activation_campaign_ids:
            campaign_vehicles_name_list = api_campaign_obj.get_campaign_vehicles_name(campaign_id)
            for vehicle_name in campaign_vehicles_name_list:
                vehicle_id =  api_fm_obj.get_vehicle_id_by_name(vehicle_name, context)
                context.deactivation_time = api_rd_obj.deactivate_rd_config(vehicle_id, vehicle_name, assignment_state_1)
                context.rd_campaign_activation_status = api_rd_obj.verify_diag_config_state(assignment_state_2, sub_status, capability, vehicle_id)               
    else:
        context.deactivation_time = api_rd_obj.deactivate_rd_config(context.vehicle_id, context.vehicle_name, assignment_state)


@step('delete "{capability}" if present')
@step('delete DTC if present')
@step('delete existing DTCs and ECU details for "{capability}" if present')
def step_impl(context, capability="DTC"):
    """ Description         : Delete diagnostic jobs if present on vehicle

        Pre-condition       : 'context.vehicle_id' - retrieved from step - "map device <device> to the vehicle <vehicle>"

        Parameters          : None

        Expected result     : it deletes all the existing DTCs present for a particular vehicle  
    """
    logging.info(f"Deleting existing {capability}s for {context.vehicle_name} vehicle")
    api_rd_obj = API_OTA_Function_Calls_GX_Class.ApiOTAFunctionCallsGXClass(context.env, context.log_api_details)
    if("DTC" in capability):
        api_rd_obj.delete_dtc(context.vehicle_id, context.vehicle_name)
    if("ECU" in capability):
        api_rd_obj.delete_ecu(context.vehicle_id, context.vehicle_name)
    context.record_count = api_rd_obj.get_dtc_count(context.vehicle_id)


@step('diagnostic configuration "{diag_config_name}" is activated on vehicle')
@step('assign diagnostic config "{diag_config_name}" to "{device_slot_name}" of vehicle "{vehicle_name}"')
def step_impl(context, diag_config_name, device_slot_name = None, vehicle_name = None):
    """ Description         : activates the existing diagnostic configuration for a vehicle
        
        Pre-condition       : context.vehicle_name, context.vehicle_id, context.device_id - retrieved from step - "map device <device> to the vehicle <vehicle>"

        Parameters          : diag_config_name - Name of Diagnostic Configuration used for Activating to a vehicle
                              device_slot_name - name of the device slot in which diagnostic to be activated 
                                                 (Default Value: None - existing value of contex.device_slot_name will be selected)
                              vehicle_name - Name of the Vehcile in which diagnostic should be activated
                                                (Default Value: None - existing value of context.vehicle_name will be selected)
                              eg. 'diag_config_name' = "SYS-I-RD-DConfi.01", vehicle_name = "Test_Vehicle", slot_name = "CTPG"
                        
        Expected result     : {diag_config_name} is activated on particular vehicle
    """
    
    time.sleep(15)
    api_rd_obj = API_OTA_Function_Calls_GX_Class.ApiOTAFunctionCallsGXClass(context.env, context.log_api_details)
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    if(vehicle_name is not None):
        if(len(vehicle_name) == vehicle_name.count(' ')):
                vehicle_name = context.default_vehicle
        context.vehicle_name = vehicle_name
    context.vehicle_id =  api_fm_obj.get_vehicle_id_by_name(context.vehicle_name, context)
    if(device_slot_name is not None):
        context.device_slot_name = device_slot_name + "_" + context.device_slot_type
    b_rd_actice_status = api_rd_obj.activate_diag_config(diag_config_name, context.vehicle_name, context.vehicle_id, context.device_slot_name)
    if (b_rd_actice_status):
        context.rd_activation_status = True
        logging.info("RD configuration activation is triggered successfully")


@step('diagnostic configuration state is "{state}" within "{timer}" minutes')
@step('diagnostic configuration state is "{state}"')
@step('diagnostic configuration state is "{state}" for "{capability}"')
@step('diagnostic configuration state is "{state}" and sub_status is "{sub_status}"')
@step('diagnostic configuration state of "{vehicle_name}" is "{state}"')
@step('diagnostic configuration state of "{vehicle_name}" is "{state}" for "{campaign_type}" campaign')
def step_impl(context, state, timer="10",capability = "DTC", sub_status = " ", vehicle_name = None, campaign_type= None):
    """ Description         : checks the Diagnistic job state for a vehicle
    
        Pre-condition       : context.vehicle_id - retrieved from step - "map device <device> to the vehicle <vehicle>"

        Parameters          : state - State of the Diagnostic Configuration after assigning it to a particular vehicle

                              eg. 'state' = "ACTIVE" / "INACTIVE" etc.

        Expected result     : It verifies the state of Diagnostic Configuration assigned to a particular vehicle
    """

    api_rd_obj = API_OTA_Function_Calls_GX_Class.ApiOTAFunctionCallsGXClass(context.env, context.log_api_details)
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)

    if vehicle_name is not None:
        vehicles = vehicle_name.split(",")
        for vehicle_name in vehicles:
            vehicle_id =  api_fm_obj.get_vehicle_id_by_name(vehicle_name, context)
            context.rd_activation_status = api_rd_obj.verify_diag_config_state(state, sub_status, capability, vehicle_id)
    else:
        context.rd_activation_status = api_rd_obj.verify_diag_config_state(state, sub_status, capability, context.vehicle_id)

    if campaign_type == "RD activation":
        context.rd_campaign_activation_status = True
    elif campaign_type == "RD deactivation":
        context.rd_campaign_activation_status = False

@step('newer DTCs are generated')
@step('DTC is generated for "{time_period}" minutes')
@step('{newer_dtc} newer DTCs are generated')
def step_impl(context, time_period="2", newer_dtc = "yes"):
    """Duration of time required to generate the DTC for Remote Diagnostic"""
    time_for_dtc = (int(time_period))*60
    time.sleep(time_for_dtc)
    api_rd_obj = API_OTA_Function_Calls_GX_Class.ApiOTAFunctionCallsGXClass(context.env, context.log_api_details)
    dtc_count = api_rd_obj.get_dtc_count(context.vehicle_id)
    if newer_dtc.upper() == "YES":
        assert dtc_count > context.dtcs_count, "Newer DTCs are not generated"      
    elif newer_dtc.upper() == "NO":
        assert dtc_count == context.dtcs_count, "newer dtc are generated"
    context.dtcs_count = dtc_count
    context.record_count = dtc_count

@step('verify latest "{capability}" details')
@step('latest DTC status is verified')
@step('latest DTC status for "{vehicles}" is verified')
@step('latest DTC status is verified for "{ecu}"')
def step_impl(context, capability="DTC", ecu=None, vehicles = None):
    """ Description         : Verify latest DTC status
    
        Pre-condition       : context.vehicle_id - retrieved from step - "map device <device> to the vehicle <vehicle>"

        Parameters          : context.table - passed from the feature file
                              dtcs_of_ecu - Boolean value to differentiate DTC check (false) and DTC_of_ECU check (true).
                              capability - Capability name in order to validate the capability details
                              
        Expected result     : verifies the actual DTC,ECU,DTC_of_ECU with expected values passed from feature file
    """
    api_rd_obj = API_OTA_Function_Calls_GX_Class.ApiOTAFunctionCallsGXClass(context.env, context.log_api_details)
    if("DTC" in capability) and vehicles is not None:
            vehicle_list = vehicles.split(',')
            for vehicle in vehicle_list:
                vehicle_id = context.vehicle_data[vehicle]["vehicle_id"]
                status  = api_rd_obj.verify_dtc(context.table, vehicle_id,ecu, context.record_count)
                assert status[0], f"Wrong DTCs generated. Actual DTC code - {str(set(status[1])-set(status[2]))}, and Expected DTC code - {str(set(status[2])-set(status[1]))}"
    elif ("DTC" in capability) and vehicles is None:
        status  = api_rd_obj.verify_dtc(context.table, context.vehicle_id,ecu, context.record_count)
        assert status[0], f"Wrong DTCs generated. Actual DTC code - {str(set(status[1])-set(status[2]))}, and Expected DTC code - {str(set(status[2])-set(status[1]))}"

    if("ECU" in capability):
        status = api_rd_obj.verify_ecu_details(context.identifier, context.vehicle_id)
        assert status, f"Wrong ECU DTCs are generated and not matching with expected ECU IDs and DTCs."

    if (status):
        logging.info(f"Generated {capability} matches with the expected {capability} code")



@when('vehicle has "{capability}" capability available')
def step_impl(context, capability):
    """checking if the vehicle has the required capability"""
    context.diagnostic_capability_id = None
    api_rd_obj = API_OTA_Function_Calls_GX_Class.ApiOTAFunctionCallsGXClass(context.env, context.log_api_details)
    r = api_rd_obj.API_Requests.get_request(constants.RD_VEHICLES_ID_AC.format(context.vehicle_id))
    assert r.status_code == requests.codes.ok, (r.json()['message'])
    logging.info(f"device response: { r.json()}")
    if '_embedded' in r.json():
        for diag_cap in r.json()['_embedded']['diagnosticCapabilities']:
            if diag_cap['name'] == capability:
                context.diagnostic_capability_id = diag_cap['diagnosticCapabilityId']
    assert context.diagnostic_capability_id is not None
    logging.info('Device has READ_DTC capability')



@step('release diagnostic job')
def step_impl(context):
    """Releases the created diagnostic job"""
    etag = API_Requests.get_etag(constants.RD_DIAG_JOB_ID.format(context.diagnostic_job_id))
    r = API_Requests.post_request(
        constants.RD_DIAG_JOB_ID_RELEASE.format(context.diagnostic_job_id), {}, {'if-match': etag})
    if r.status_code != requests.codes.created:
        logging.info("Logref: {}, Message: {}".format(r.json()['logref'], r.json()['message']))
        assert r.status_code == requests.codes.created, r.json()['message']


@when('assign diagnostic job to vehicle')
def step_impl(context):
    """Assign the created diagnostic job to vehicle resulting in generation of capability configuration id"""
    data = {
            "diagnosticJobId": context.diagnostic_job_id,
            "deviceId": context.device_id,
            "diagnosticCapabilityId": context.diagnostic_capability_id
    }
    r = API_Requests.post_request(constants.RD_VEHICLES_ID_CC.format(context.vehicle_id), data)
    assert r.status_code == requests.codes.created, r.json()['message']


@step('trigger "{capability}" on the vehicle')
@step('trigger adhoc Read All "{capability}"')
@step('adhoc Read All DTCs is triggered')
@step('adhoc Read All DTCs is triggered for "{vehicles}"')
@step('adhoc "{capability}" is triggered')
@step('adhoc "{capability}" is triggered for ECU "{ecus_under_test}"')
def step_impl(context,capability = "DTC", vehicles = None, ecus_under_test = None):
    """triggering the adhoc for a vehicle"""
    api_rd_obj = API_OTA_Function_Calls_GX_Class.ApiOTAFunctionCallsGXClass(context.env, context.log_api_details)
    data ={}
    
    if ecus_under_test is not None : 
        ecus_under_test = ecus_under_test.split(',')
        for ecu_under_test in ecus_under_test:
            data = {
                     "ECU_ID": ecu_under_test
                    }
            #context.trigger_capability_ep is a list to store all the capability details(EP) for a single test
            context.trigger_capability_ep.append(api_rd_obj.get_trigger_location(context.vehicle_id,capability,data))
    elif vehicles is not None :
        vehicle_list = vehicles.split(',')
        for vehicle in vehicle_list:
            vehicle_id = context.vehicle_data[vehicle]["vehicle_id"]
            context.trigger_capability_ep.append(api_rd_obj.get_trigger_location(vehicle_id,capability,data))
    else:
        context.trigger_capability_ep.append(api_rd_obj.get_trigger_location(context.vehicle_id,capability,data))

@step('"{capability}" is executed within "{dtc_time}" minutes')
@step('adhoc Read All "{capability}" is generated within "{dtc_time}" minutes')
@step('adhoc Read All DTCs is generated within "{dtc_time}" minutes')
@step('adhoc Read All DTCs "{status}" in "{dtc_time}" minutes')
@step('adhoc "{capability}" is generated within "{dtc_time}" minutes')
@step('"{capability}" "{status}" within "{dtc_time}" minutes')
def step_impl(context, dtc_time, capability="DTC", status = "passes"):
    """verifies the generation of adhoc Read All DTCs for a vehicle"""
    api_rd_obj = API_OTA_Function_Calls_GX_Class.ApiOTAFunctionCallsGXClass(context.env, context.log_api_details)
    dtc_time = (int(dtc_time))*60
    timeout_time = time.time() + dtc_time
    if hasattr(context,'activation_campaign_ids'):
        for trigger in context.trigger_capability_ep:
            api_rd_obj.check_capability_status(trigger, capability, dtc_time, timeout_time, status) 
    else:
        trigger = context.trigger_capability_ep [-1]
        api_rd_obj.check_capability_status(trigger, capability, dtc_time, timeout_time, status)

@step('map device to the "{vehicle_name}" if there are no pending diagnostic jobs')
def step_impl(context, vehicle_name):
    """

    """
    context.execute_steps(f'''
            Given prepare vehicle "{vehicle_name}" by clearing all pending jobs
            And map device to the vehicle "{vehicle_name}"
     ''')

@step('Perform Remote Diagnostics {number:d} times with the data {diag_config_name}')
def step_impl(context, number, diag_config_name):
    
    context.repetitive_steps = f'''
                Given deactivate ACTIVE diagnostic configuration if present
                And delete DTC if present
                When diagnostic configuration {diag_config_name} is activated on vehicle
                And diagnostic configuration state is "ACTIVE"
                And test is executed for "30" seconds
                When adhoc Read All DTCs is triggered
                Then adhoc Read All DTCs is generated within "5" minutes
                When deactivate ACTIVE diagnostic configuration if present
                Then diagnostic configuration state is "INACTIVE"
                And latest DTC status is verified
                    | Status | Code  |
                    | AC     | A9C17 |
                    | AC     | 80522 |
                And delete DTC if present 
            '''
    context.execute_steps(f'''
                Given perform load test for {number} iterations with predefined steps           
            ''')

@step('Perform Remote Diagnostics SadPath {number:d} times with the data {diag_config_name}, {diag_protocol} and {diag_identifier_name}')
def step_impl(context, number, diag_config_name, diag_protocol, diag_identifier_name):
    
    
    context.repetitive_steps = f'''
                Given reference system {diag_protocol} with Identifier {diag_identifier_name} is started
                And deactivate ACTIVE diagnostic configuration if present
                And delete DTC if present
                When diagnostic configuration {diag_config_name} is activated on vehicle
                And diagnostic configuration state is "ACTIVE"
                And test waits for "0.5" minutes
                When adhoc Read All DTCs is triggered
                And adhoc Read All DTCs is generated within "5" minutes
                And test waits for "0.5" minutes
                And latest DTC status is verified
                    | Status | Code  |
                    | AC     | A9C17 |
                    | AC     | 80522 |
                When VRS with protocol {diag_protocol} and identifier {diag_identifier_name} is stopped
                And delete DTC if present
                And adhoc Read All DTCs is triggered
                Then adhoc Read All DTCs "fails" in "2" minutes
                Then reference system {diag_protocol} with Identifier {diag_identifier_name} is started
                And adhoc Read All DTCs is triggered
                And adhoc Read All DTCs is generated within "5" minutes
                And test waits for "1" minutes
                And latest DTC status is verified
                    | Status | Code  |
                    | AC     | A9C17 |
                    | AC     | 80522 |
                And deactivate ACTIVE diagnostic configuration if present
                And diagnostic configuration state is "INACTIVE"
                And VRS with protocol {diag_protocol} and identifier {diag_identifier_name} is stopped
            '''
            
    context.execute_steps(f'''
                Given perform load test for {number} iterations with predefined steps          
            ''')
            

@step('verify remote diagnostic configuration on vehicle "{vehicle_name}" is removed')
@step('remote diagnostic configuration state on vehicle "{vehicle_name}" is "{status}"')
def step_impl(context, vehicle_name, status = None):
    """
        Description     : Checks status of the Diagnostic asssignment on the Vehicle
        
        Pre-condition   : Diagnostic is Activated/ Deactivated from the Vehicle

        Parameters      : vehicle_name : Name of the Vehicle, 
                          status- Status of the assignment (Default None - No diagnostic config is currently assigned to Vehicle)

        Expected result : Diagnostic configuration of the vehicle is displayed as expected
    """
    api_rd_obj = API_OTA_Function_Calls_GX_Class.ApiOTAFunctionCallsGXClass(context.env, context.log_api_details) 
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details) 
    if(vehicle_name is not None):
        if(len(vehicle_name) == vehicle_name.count(' ')):
            vehicle_name = context.default_vehicle
        context.vehicle_name = vehicle_name
        context.vehicle_id =  api_fm_obj.get_vehicle_id_by_name(context.vehicle_name, context)
    api_rd_obj.check_assigned_diagostic_config_state(context.vehicle_id, status)


@step('perform device mapping and unmaping from device slot "{number:d}" times on "{vehicle_name}" for remote diagnostics')
def step_impl(context, number, vehicle_name):
    """
        Description     : Load test for device mapping and unmamping when diagnostic is assigned
        
        Pre-condition   : Diagnostic configuration is assigned to the vehicle

        Parameters      :   number : number of times load test to be performed 
                            vehicle_name : Name of the Vehicle

        Expected result : New Vehicle is created if the Vehicle was not available or
                          new vehicle is created if there is a pending diagnostic job with failed status.
    """
    context.repetitive_steps = f'''
                When map devices to device slot of "{vehicle_name}" vehicle
                    | slot_name | device	|
                    | CCU1     |  CCU 	|
                And delete DTC if present
                And remote diagnostic configuration state on vehicle "{vehicle_name}" is "ACTIVE"
                And reference system "UDSonCAN" with Identifier "UDS_Resp_2DTCs" is started
                And adhoc Read All DTCs is triggered
                And adhoc Read All DTCs is generated within "10" minutes
                Then VRS with protocol "UDSonCAN" and identifier "UDS_Resp_2DTCs" is stopped
                And latest DTC status is verified
                    | Status | Code  |
                    | AC     | A9B17 |
                    | AC     | 80511 |
                And unmap device "CCU" from vehicle
                And remote diagnostic configuration state on vehicle "{vehicle_name}" is "INACTIVE"
                And test is executed for "30" seconds
            '''
    context.execute_steps(f'''
        Given perform load test for {number} iterations with predefined steps
           ''')  


@step('verify no dtcs are generated after deactivation')
def step_impl(context):
    """
        Description     : Verify if DTCs are generated after deactivation of RD
        
        Pre-condition   : Diagnostic configuration is assigned to the vehicle and is deactivated

        Parameters      :   deactivation_time : Time of deactivation
                            vehicleId : Id of the vehicle

        Expected result : DTCs are not generated after deactivation
    """
    api_rd_obj = API_OTA_Function_Calls_GX_Class.ApiOTAFunctionCallsGXClass(context.env, context.log_api_details)
    api_rd_obj.verify_dtcs_after_deactivation(context.vehicle_id, context.deactivation_time)