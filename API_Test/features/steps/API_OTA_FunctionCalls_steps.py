import steps.pageObjects.API_OTA_FunctionCalls_Class as API_OTA_FunctionCalls_Class
import logging
import re
import steps.constantfiles.constants_ota_functioncalls as constants

@step('check VSC is available for tenant with {property_name}')
def step_impl(context, property_name):
    """Check VSC definition is available for tenant"""
    api_fc_obj = API_OTA_FunctionCalls_Class.APIOtaFunctionCalls(context.env, context.log_api_details)
    api_fc_obj.check_vsc_definition(property_name)
    
@step('check function call status as "{status}"')
def step_impl(context, status):
    """Check function call status with callId as input to backend"""
    api_fc_obj = API_OTA_FunctionCalls_Class.APIOtaFunctionCalls(context.env, context.log_api_details)
    context.response = api_fc_obj.verify_status_for_function_call(context.call_id, status)

@step('invoke function call to "{target_type}" for "{action}" on "{property_name}"')
@step('invoke function call to "{target_type}" "{action}" on "{property_name}" for "{in_arg_value}"')
def step_impl(context, action, property_name,target_type, in_arg_value = None):
    """ Description         : It invokes a function call to actions for property in vehicle
                            For RDL : It invokes a function call to set boolean actions for property in device 
                            
        Parameters          : action - ids_csg_logs,preconditioning , property = property name,
                              in_arg_value = in arguments config value for preconditioning feature
                              For RDL : action = enable or disable
        Expected result : function call response should be created and callID should be generated
                         
    """
    api_fc_obj = API_OTA_FunctionCalls_Class.APIOtaFunctionCalls(context.env, context.log_api_details)
    match target_type.lower():
        case "device":
            target = {"deviceId" : context.device_id}
        case "vehicle":
            target = {"vehicleId": context.vehicle_id}
        case "vin":
            target = {"vin": context.vehicle_vin}

    function_call_body = api_fc_obj.prepare_function_call_request_body(action, property_name,target,in_arg_value)
    context.call_id = api_fc_obj.call_function(function_call_body)
        
    
@step('verify artifactUrl for IDS Report function call')
def step_impl(context):
    """ Description         : verify artifactUrl from function call response
        Parameters          : None
        Expected result : artifactUrl should be available with blobID
    """
    actual_url = context.response['outArguments']['artifactUrl'] 
    expected_pattern = re.compile(constants.ARTIFACT_URL_PATTERN)
    matched_pattern = expected_pattern.match( actual_url )
    if matched_pattern == None:
        logging.debug(f'artifact URL in function call - {actual_url}')
        assert False,f"Valid URL mismatch actual_url-{actual_url}"

@step('verify Remote Tacho download status to be "{status}"')
def step_impl(context, status):
    """
    Description         : Function call to get current status from device and validates for remote_tacho_download property                       
    Parameters          : status = enabled/disabled
    Expected result     : it validates last modified status and the current status to be same

    """
    context.execute_steps(f'''
            When invoke function call to "device" for "get_status" on "remote_tacho_download"
            Then check function call status as "SUCCESS"
    ''')
    actual_status = context.response['outArguments']['enabled']
    expected_status = "True" if status == "enabled" else "False"
    assert str(actual_status) == str(expected_status), f'Current status {actual_status} is not same as expected {expected_status}. callId is {context.call_id}'
    logging.info(f'Function call has proper status post validation,actual_status-{actual_status} and expected-{actual_status}')
