import time
import logging
import steps.pageObjects.API_Generic_Class as API_Generic_Class
import steps.pageObjects.API_Inventory_Class as API_Inventory_Class
import steps.constantfiles.constants_inventory as constants

@step('fetch the firmware version of the device from inventory')
def step_impl(context):
    api_inv_obj = API_Inventory_Class.ApiInventoryClass(context.env, context.log_api_details)
    context.sw_version = api_inv_obj.get_firmware_version_of_device(context.device_id)


'''
   This step is temporarily created for ctpg device ,
    once inventory is implemented properly we can delete this method and optimize above method
'''
@step('device FW "{version}" is verified')
@step('device FW version is verified')
def step_impl(context, version=None):
    api_inv_obj = API_Inventory_Class.ApiInventoryClass(context.env, context.log_api_details)
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    if version is None:
        version = context.to_version
    api_gen_obj.start_timer()
    while (api_gen_obj.check_timer() == True) :
        device_sw_version = api_inv_obj.get_device_inventory(context.device_id)['_embedded']['inventoryItemList'][0]['swVersion']
        if(version in device_sw_version):
            api_gen_obj.stop_timer()
            break
        time.sleep(30)
    if version not in device_sw_version:
        logging.warning(f"Update executed successfully but software version in Vehicle Inventory is not updated after 600 Secs. \nExpected SW version: {version} but actual SW version: {device_sw_version}. \nChecking device version inside device")
        command_map = api_gen_obj.parse_json_file(context.device_config_data["command_file"])
        device_version = api_gen_obj.get_firmware_version_from_device(command_map, context.test_device, context.devices_data[context.specimen_device][context.test_device+"_IP"],context.device_config_data['ssh_key'])
        assert version in str(device_version), f"Device - {context.device_id} has wrong version. Expected device version is {version} but actual SW version: {device_sw_version}"
        logging.warning(f"Device - {context.device_id} has expected version - {version} but Vehicle Inventory is not updated")
    logging.info(f"Device has expected version - {version}")

@step('software version of hardware connected to vehicle is verified')
@step('software version {sw_version_change} of hardware {sw_u_id} connected to vehicle is verified')
def step_impl(context, sw_version_change=None, sw_u_id="Device SW"):
    """
        Description: verifies device(CCU/ECU) inventory and software firmware details

        Parameters : 
            sw_version : None (default)
            hardware_unit : Device SW (default) = ECU_1/ECU_2

        Expected: hardware_unit software details are verified
    """
    api_inv_obj = API_Inventory_Class.ApiInventoryClass(context.env, context.log_api_details)
    
    vehicle_inventory = api_inv_obj.get_device_inventory(context.device_id)
    for each_inventory in vehicle_inventory['_embedded']['inventoryItemList']:
        if each_inventory['swUid'] == sw_u_id:
            actual_new_sw = each_inventory['swVersion']
            '''TO DO: older version details absent from api response, has a defect'''
            break

    if (sw_version_change is None):
        new_exp_sw = context.device_new_firmware #after Self-update, save FW version value to this variable    
    else:
        new_exp_sw = sw_version_change.split("to")[1] #after Self-update, save FW version value to this variable

    assert actual_new_sw == new_exp_sw.strip(), f"Device has wrong Fw version. Actual - {actual_new_sw} and Expected - {new_exp_sw}"


@step('inventory changes for hardware are verified')
@step('inventory changes for hardware {sw_u_id} with software version change {sw_version} are verified')
def step_impl(context, sw_version_change=None, sw_u_id="Device SW"):
    """
        Description: verifies device(CCU/ECU) inventory changes and  software firmware details

        Parameters : 
            sw_version : None (default)
            hardware_unit : Device SW (default) = ECU_1/ECU_2

        Expected: Inventory changes details and hardware_unit software details are verified
    """
    api_inv_obj = API_Inventory_Class.ApiInventoryClass(context.env, context.log_api_details)

    inventory_changes = api_inv_obj.get_inventory_changes(context.device_id)
    actual_new_sw = inventory_changes[0]['inventoryChangeList'][0]['swVersion']
    '''TO DO: older version details absent from api response, has a defect'''
    '''TO DO: As Assignment and Campaign Id linkage to Inventory has defect.'''
    # actual_assignment_detail** = inventory_changes[0]['inventoryChangeList'][0]['assignment_may be']
    # actual_campaign_detail = inventory_changes[0]['inventoryChangeList'][0]['campaign_may be']
    assert len(inventory_changes) > 1, "Vehicle Inventory changes detail doesn't have more than 1 FW update entry"

    if (sw_version_change is None):
        new_exp_sw = context.device_new_firmware #after Self-update, save FW version value from device to this variable
        context.device_last_firmware #before self-update, save FW version value to this variable
    else:
        new_exp_sw = sw_version_change.split("to")[1] #after Self-update, save FW version value to this variable
        sw_version_change.split("to")[0] #before self-update, save FW version value to this variable
    
    assert actual_new_sw == new_exp_sw.strip(), f"Device has wrong Fw version. Actual - {actual_new_sw} and Expected - {new_exp_sw}"
    '''TO DO: refer above'''

    api_inv_obj.get_device_assignments(context.device_id)
    '''TO DO: As Assignment and Campaign Id linkage to Inventory has defect.'''
    # assert device_assignments[0]['assignmentId'] == actual_assignment_detail**, f"Assignment Id - {device_assignments[0]['assignmentId']} used for device firmware change is NOT linked to Inventory Change details"
    # Similar assert for Campaign Id in Assignments section to Iventory Change Campaign Id

@step('inventory history is verified')
def step_impl(context):
    api_inv_obj = API_Inventory_Class.ApiInventoryClass(context.env, context.log_api_details)
    actual_fw = context.to_version+".DEBUG" 
    expected_fw = api_inv_obj.get_inventory_timestamp(context.device_id)[0]['swVersion']
    assert actual_fw == expected_fw , f"Device has different version. Actual - {actual_fw} and Expected - {expected_fw}"


@step('vehicle inventory details are verified for "{inventory_type}"')

def step_impl(context,inventory_type):

    inventory = inventory_type.split(',')
    api_inv_obj = API_Inventory_Class.ApiInventoryClass(context.env, context.log_api_details)
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    expected_inv_data = api_gen_obj.parse_json_file(constants.VEHICLE_INVENTORY_JSON_PATH)
    expected_inv_data["inventoryDetails"]["SOFTWARE"][0]["swVersion"] = context.fw_version
    for inventory_type in inventory:
        match_status = api_inv_obj.validate_inventory_data(expected_inv_data["inventoryDetails"][inventory_type], inventory_type, context.device_id)
        assert match_status,"The above inventory details are not matching"
        logging.info(f"The inventory details are matching for type {inventory_type}")