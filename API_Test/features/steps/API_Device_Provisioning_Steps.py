import requests
import logging
import steps.pageObjects.API_Device_Provisioning_Class as API_Device_Provisioning_Class
import steps.pageObjects.API_FleetManagement_Class as API_FleetManagement_Class
import steps.pageObjects.API_Generic_Class as API_Generic_Class



@step('fetch Device Provisioning details in provisioning space')
def step_impl(context):
    api_dp_obj = API_Device_Provisioning_Class.ApiDeviceProvisioningClass(context.env, context.log_api_details)
    details = api_dp_obj.get_device_details(context.device_id).json()
    context.target_backend_name = details['targetBackendName']
    context.dispatch_status = details['state']
    

@step('undispatch device in targetspace')
def step_impl(context):
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    logging.info(f" Undispatching device {context.device_id} from {context.env} ")
    api_fm_obj.undispatch_device(context.device_id)
    logging.info(f" Device {context.device_id} Undispatched from {context.env} ")
    

@step('verify the provisioning status "{state}" in target space')
def step_impl(context, state):
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    r = api_fm_obj.get_device_properties(context.device_id)
    assert r.status_code == requests.codes.ok, r.json()['message']
    assert state.upper() ==  r.json()['state'].upper(),"Device state didnt match"
    if (state.upper() == "REGISTERED"):
        context.device_dispatched = True
    elif (state.upper() == "UNDISPATCHED"):
        context.device_dispatched = False


@step('verify the device provisioning state "{state}" in provisioning space')
def step_impl(context, state):
    api_dp_obj = API_Device_Provisioning_Class.ApiDeviceProvisioningClass(context.env, context.log_api_details)
    details = api_dp_obj.get_device_details(context.device_id).json()
    assert details['state'] == state, "Device state is not matching"

@step('dispatch device to "{targetspace}" in provisioning space')
def step_impl(context, targetspace):
    api_dp_obj = API_Device_Provisioning_Class.ApiDeviceProvisioningClass(context.env, context.log_api_details)
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    targets = api_dp_obj.target_backends()
    found = False
    if(len(targetspace) == targetspace.count(' ')):
        targetspace = api_gen_obj.get_tenant_for_space(context.provisioning_target_space)
        logging.info(f"target space detected via code is - {targetspace}")
    for target in targets:
        if targetspace.upper() == target['name'].upper():
            targetspace = target['name']
            found = True
            break
    
    if found == False:
        assert False, f" {targetspace} not found in TargerBackend List {targets}"

    logging.info(f" Dispatching device {context.device_id} to '{targetspace}' tenant in '{context.env}' environment")
    api_dp_obj.dispatch_device(context.device_id, targetspace)
    logging.info(f" Device {context.device_id} Dispatched to '{targetspace}' tenant in '{context.env}' environmen ")


@step('undispatch device from "{targetspace}" in provisioning space')
def step_impl(context, targetspace):
    api_dp_obj = API_Device_Provisioning_Class.ApiDeviceProvisioningClass(context.env, context.log_api_details)
    details = api_dp_obj.get_device_details(context.device_id).json()
    assert details['targetBackendName'].upper() == targetspace.upper(), f"Tenant name is not matching : Actual =  {details['targetBackendName'].upper()} -> Expected :{details['targetBackendName'].upper()} "
    logging.info(f" Undispatching device {context.device_id} from {context.env} ")
    api_dp_obj.undispatch_device(context.device_id, targetspace)
    logging.info(f" Device {context.device_id} Undispatched from {context.env} ")


