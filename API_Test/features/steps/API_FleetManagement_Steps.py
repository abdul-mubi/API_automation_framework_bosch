import requests
import logging
import sys
import os
import time
from subprocess import Popen
import datetime
from pageObjects import API_OTA_Function_Calls_GX_Class
from pageObjects import API_OTA_Vehicle_Data_Class
import utils.API_Requests as API_Request
import steps.pageObjects.API_FleetManagement_Class as API_FleetManagement_Class
import steps.pageObjects.API_Generic_Class as API_Generic_Class
import steps.pageObjects.API_Inventory_Class as API_Inventory_Class
import steps.constantfiles.constants_fleetmanagement as constants
import subprocess
from subprocess import Popen

@step('use a vehicle with name "{vehicle_name}"')
def step_impl(context, vehicle_name):
    """Search for the specified vehicle name and the corresponding
    vehicle id is extracted for further use"""
    context.vehicle_name = vehicle_name
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    context.vehicle_id = api_fm_obj.get_vehicle_id_by_name(vehicle_name, context)
    assert context.vehicle_id is not None, constants.FM_UNABLE_TO_FIND_VEHICLE_NAME.format(vehicle_name)

@given('define a device with id "{device_id}"')
def step_impl(context, device_id):
    """Define the device with new specified id"""
    logging.info(device_id)
    context.device_id = device_id


@step('device "{test_device}" is "{status}"')
def step_impl(context, test_device, status):
    """Check if the device is online"""

    if test_device != context.specimen_device and "device2" in context.active_outline.headings :
        context.execute_steps(f'''
            Given test bench information for device "{test_device}" is gathered
            And read the device properties
            And perform the miscellaneous actions for the device to be ready
        ''')

    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    context.provisioning_target_space = context.env #storing device provisioned tenant information
    device_online_state = api_fm_obj.get_device_status(context.device_id)    
    if( device_online_state != status) :
        api_fm_obj.check_interim_device_status(context.device_id,status)
    logging.info(f"Device {context.device_id} is {status}")
    context.device_online_state = status

@step('read the device properties')
def step_impl(context):
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    r = api_fm_obj.get_device_properties(context.device_id)
    context.device_slot_type = r.json()['deviceType']
    context.default_slot_name = context.test_device + "_" + context.device_slot_type
    context.detected_vin = None
    if'detectedVin' in r.json():
        context.detected_vin = r.json()['detectedVin']
    logging.info(f'Device Detected VIN: {context.detected_vin}')
    device_online_state = r.json()['onlineState']
    if device_online_state != "ONLINE" and context.test_device != "virtual_device":
        context.execute_steps(f'''
                Given switch "CL30" is turned "On"
                And switch "CL15" is turned "On"
                And check the "{context.specimen_device}" for availability of GSM connection
            ''')
        # checking device provisioned status as Registered to Environment in-test
        # if r.json()["state"] != "REGISTERED":
        #     context.device_dispatched = False
        #     logging.info("device in-test is not Registered, and so Undispatched from the Tenant in-use. Redispatching device correctly")
        #     try:
        #         context.execute_steps('''
        #             Given switch to "device-provisioning"
        #             And remove paired vehicle
        #             When dispatch device to " " in provisioning space
        #             And test waits for "1" minutes
        #             And verify the device provisioning state "DISPATCHED" in provisioning space
        #             And switch to " "
        #             Then verify the provisioning status "REGISTERED" in target space
        #             And wait for device to be "OFFLINE"
        #             And switch "CL15" is turned "Off"
        #             And test waits for "1" minutes
        #             And switch "CL15" is turned "On"
        #             And wait for device to be "ONLINE"
        #         ''')
        #     except Exception:
        #         logging.warning(f"Exception Occured: , {sys.exc_info()[0]}, {sys.exc_info()[1]}")
    

@step('perform the miscellaneous actions for the device to be ready')
def step_impl(context):
    if context.device_config_data["ssh_available"]:
        context.execute_steps(f'''
            #TO-DO: Delete the below line once the defect of CCU device time is fixed
            Given set device time from the windows machine
        ''')
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    api_inv_obj = API_Inventory_Class.ApiInventoryClass(context.env, context.log_api_details)
    context.fw_version = ''
    try:
        context.fw_version = api_inv_obj.get_firmware_version_of_device(context.device_id)
    except KeyError as e:
        logging.warning(f"{e}")
    api_gen_obj.update_version_json(context.specimen_device, context.device_id, context.customer_type, context.env, context.fw_version)

@step('wait for device to be "{device_status}"')
@step('wait for device "{test_device}" to be "{device_status}"')
@step('wait for device to be "{device_status}" within "{minutes:d}" minutes')
def step_impl(context, device_status, minutes = 15, test_device = None):
    if test_device is not None:
        device_id = context.devices_data[test_device]["device_name"]
    else:
        device_id = context.device_id
    context.start_timer = time.time()
    actual_status = ""
    timeout_in_sec = minutes * 60
    if not hasattr(context, "gsm_timer"):
        context.gsm_timer = {}

    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    api_gen_obj = API_Generic_Class.ApiGenericClass()

    logging.info(f"Checking device - {device_id} status")

    api_gen_obj.update_timeout_time(timeout_in_sec)
    api_gen_obj.start_timer()
    while (api_gen_obj.check_timer() == True):
        actual_status = api_fm_obj.get_device_status(device_id)    
        if actual_status == device_status:
            context.end_timer = time.time()
            logging.info("Device is back {} after {} seconds".format(device_status,(context.end_timer - context.start_timer)))
            time.sleep(1)
            context.gsm_timer[device_status] = time.time()
            api_gen_obj.stop_timer()
            break
        time.sleep(30)

    assert actual_status == device_status, "Please check the device, Device is not "+device_status+" after waiting for" + str(timeout_in_sec) + " seconds"
    setattr(context,f'device_{device_status.lower()}_moment', datetime.datetime.now(datetime.timezone.utc))
    #TO-DO: Delete the below lines once the defect of CCU device time is fixed
    if device_status == "ONLINE" and context.test_device == "CCU" and context.device_config_data['ssh_available']:
        context.execute_steps('''
            Given set device time from the windows machine
        ''')


@step('map "{phase}" created vehicle "{vehicle_name}" to the device')
@step('device is mapped to vehicle "{vehicle_name}"')
@step('map device to the vehicle "{vehicle_name}"')
def step_impl(context, vehicle_name, phase=None):
    """Map the specified device to selected vehicle"""
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    if(len(vehicle_name) == vehicle_name.count(' ')):
            vehicle_name = context.default_vehicle
    context.vehicle_name = vehicle_name
    vehicle_id = api_fm_obj.get_vehicle_id_by_name(vehicle_name, context)
    context.vehicle_id = vehicle_id
    if(api_fm_obj.get_vin_by_name(vehicle_name, context)!= context.detected_vin and not context.vin_already_implanted):
        context.execute_steps(f'''
                Given VIN of vehicle "{context.vehicle_name}" is implanted in the device "{context.specimen_device}"
        ''')
    if (phase is None):
        context.all_vehicle_id.append(context.vehicle_id)
    assert vehicle_id is not None, constants.FM_UNABLE_TO_FIND_VEHICLE_NAME.format(vehicle_name)
    unmapped_status, slot_name = api_fm_obj.check_device_mapping_status(context.device_id, context.vehicle_id)
    if(unmapped_status == False): 
        context.device_slot_name = slot_name
    else: 
        context.device_slot_name = api_fm_obj.get_device_slot_by_type(context.vehicle_id, context.default_slot_name, context.device_slot_type)
        api_fm_obj.map_device_to_vehicle_device_slot(context.vehicle_id, context.device_slot_name, context.device_id)
    context.device_mapped = True
    context.all_device_ids.append(context.device_id)
    context.vehicle_vin = api_fm_obj.get_vin_by_name(vehicle_name, context)

@step('it is validated that "{test_device}" is mapped to vin "{count}" vehicle')      
@step('it is validated that "{test_device}" is mapped to "{vehicle}"')
def step_impl(context, test_device, vehicle=None, count=None):
    """ Description         : The validation if the specimen device is mapped to the specimen vehicle is done.
                                Note - The vehicle can take the values
                                <Vehicle Name>,
                                "none" - to validate that the device is mapped to no vehicle,
                                <array of spaces> - to consider vehicle name which was automatically created in earlier steps

        Parameters          : device, vehicle

        Expected result : Validation of the device to vehicle mapping is done.
        
    """
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    if count is None:
        r = api_fm_obj.get_device_properties(context.devices_data[test_device]['device_name'])
        mapping_status = r.json()['paired']
        detected_vin = r.json()['detectedVin'] if 'detectedVin' in r.json() else None
        logging.info(f'Detected vin on the device is {detected_vin}')
        if (len(vehicle) == vehicle.count(' ')):
            vehicle = context.vehicle_name
        if (vehicle == 'none'):
            assert mapping_status is False, 'Device is mapped to a vehicle but expected to be not mapped to any vehicle'
            logging.info('Device is not mapped to any vehicle as expected')
            assigned_vehicle_id = None
        else:
            assert mapping_status is True, 'Device is not mapped to any vehicle'
            assigned_vehicle_id = r.json()['vehicleId']
            vehicle_id = api_fm_obj.get_vehicle_id_by_name(vehicle, context)
            assigned_vehicle_name = api_fm_obj.get_vehicle_by_name(vehicle, context)
            logging.info(f'Assigned vehicle on the device is {assigned_vehicle_name["name"]}')
            vin = api_fm_obj.get_vin_by_name(vehicle, context)
            assert vehicle_id == assigned_vehicle_id, f'Device {test_device} is mapped to {assigned_vehicle_name["name"]} while expected to be mapped to {vehicle}'
            assert detected_vin == vin, f'Detected VIN by the device is {detected_vin} but expected {vin}'
            context.detected_vin = detected_vin
            logging.info(f'Device {test_device} is rightly mapped to {vehicle}')
    else:
        vehicle_name = context.vin_data.get("vin"+count) + "_Vehicle".strip()
        expected_vehicle_id = api_fm_obj.get_vehicle_id_by_name(vehicle_name, context)
        device_properties = api_fm_obj.get_device_properties(context.device_id)
        assert device_properties.json()['paired'] == True, 'Device is not mapped to any vehicle'
        actual_vehicle_id = device_properties.json()['vehicleId']
        assert expected_vehicle_id == actual_vehicle_id, "Device is not mapped to vin {count} vehicle"

@step('a vehicle "{vehicle}" using Manufacturer "{manufacturer}" and Model "{model}" is created with VIN "{vin}"')
@step('a vehicle "{vehicle}" using Manufacturer "{manufacturer}" and Model "{model}" is created')
def step_impl(context, vehicle, manufacturer, model, vin = 'smart_vin'):
    """ Description         : A new vehicle with a desired vehicle name, manufacturer, model and VIN is done.

        Parameters          : vehicle - vehicle name
                                manufacturer - manufacturer name
                                model - model name
                                vin(optional) - Vehicle Identification Number
                                    Note - Values of vin can be 
                                    <VIN>,
                                    "None" - New vehicle shall not have a VIN,
                                    <array of spaces> - Automatically created vehicle, so the VIN is derived from the vehicle name

        Expected result : New vehicle with desired attributes is created.
        
    """
    if (len(vehicle) == vehicle.count(' ')):
        new_vehicle_name = f"ZE2E_{context.device_id}_{datetime.datetime.now().year}{'{:02d}'.format(datetime.datetime.now().month)}{'{:02d}'.format(datetime.datetime.now().day)}{'{:02d}'.format(datetime.datetime.now().hour)}{'{:02d}'.format(datetime.datetime.now().minute)}{'{:02d}'.format(datetime.datetime.now().second)}"
    else:
        new_vehicle_name = vehicle
    vehicle_id = ""
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)

    api_request = API_Request.ApiRequestsClass(context.env, context.log_api_details)
    r = api_request.get_request(constants.FM_VEHICLES_SEARCH_NAME.format(new_vehicle_name))
    assert r.status_code == requests.codes.ok, "Fetching vehicle details failed - {}"%r.status_code
    if vin is not None and len(vin) == vin.count(' '):
            vin = context.vin
    if "_embedded" in r.json():
        if r.json()["_embedded"]["vehicles"][0]["_embedded"]["model"]["name"] == model:
            logging.info(f"Vehicle with desired model {model} already present. New vehicle will not be created")
            vehicle_id = r.json()["_embedded"]["vehicles"][0]["vehicleId"]
        else:
            logging.info(f'Vehicle with name {new_vehicle_name} already present but the model is different from expected')
            logging.info(f'Continuing to create a new vehicle with name {new_vehicle_name} ')
            vehicle_id = api_fm_obj.create_new_vehicle(new_vehicle_name, context, manufacturer, model, vin)
    else:
        vehicle_id = api_fm_obj.create_new_vehicle(new_vehicle_name, context, manufacturer, model, vin)
        logging.info(f'A new vehicle with name {new_vehicle_name} is created')
    context.vehicle_name = new_vehicle_name
    context.vehicle_id = vehicle_id
    context.all_vehicle_id.append(context.vehicle_id)

@step('remove paired vehicle')
def step_impl(context):
    """Unmap all the paired devices from device slot if mapped in automation earlier in the script.
        device = None, default - it unmaps device id stored in context.all_device_ids and unmaps from device slot
    """

    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    for device_id in context.all_device_ids:
        api_fm_obj.unmap_device_from_vehicle(device_id)

@step('remove device slot from vehicle')
def step_impl(context):
    """
        removes device slot from the vehicle
    """

    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    api_fm_obj.delete_device_slot_from_vehicle(context.vehicle_id, context.device_slot_name)

@step('unmap vehicle from the device')
@step('unmap device from the vehicle')
def step_impl(context):
    """Unmap the device from any vehicle if paired
        Unmaps device id stored in context.device_id from vehicle
    """
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    api_fm_obj.unmap_device_from_vehicle(context.device_id)
    context.vin = None

@step('geo position data of "{vehicle_name}" is deleted if available')
def step_impl(context, vehicle_name):
    """Geo position data of the vehicle is deleted if present"""

    if(len(vehicle_name) == vehicle_name.count(' ')):
        vehicle_name = context.vehicle_name

    context.vehicle_name = vehicle_name
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    vehicle_id = api_fm_obj.get_vehicle_id_by_name(vehicle_name, context)
    context.vehicle_id = vehicle_id
    assert vehicle_id is not None, f'Unable to find vehicle with name {vehicle_name}'
    r = api_fm_obj.get_vehicle_position(context.vehicle_id)
    if r.status_code == requests.codes.ok:
        r = api_fm_obj.del_vehicle_position(context.vehicle_id)
        assert r.status_code == requests.codes.no_content, "Geo Position of the vehicle is not deleted"
        logging.info(f'Geo positions of the vehicle {vehicle_name} is deleted')
    elif r.status_code == requests.codes.not_found:
        logging.info(f'No geo position history to the vehicle {vehicle_name}')
    else:
        assert False, api_gen_obj.assert_message(r)

@step('geo positioning in "{vehicle_list}" is enabled')
@step('geo positioning in "{vehicle_list}" is "{gps_status}"')
def step_impl(context, vehicle_list, gps_status = "ENABLED"):
    """
        Descirption : Changes geo positioning status for the Vehicle

        Pre-condition : Device is mapped to vehicle and it has Matching VIN to the vehicle
    
        Parameters  : 
            vehicle_name- Name of the Vehicle
            gps_status = Status of the geo position for the vehicle; Enabled by default
        Expected result : 
            Vehicle geo position status is updated as expected.
    """
    if("geo_status" not in context):
        context.geo_status = {}
    if(len(vehicle_list) == vehicle_list.count(' ')):
        vehicle_list = context.vehicle_name

    vehicles = vehicle_list.split(',')
    for vehicle_name in vehicles:
        api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
        vehicle_id = api_fm_obj.get_vehicle_id_by_name(vehicle_name, context)
        model_id = api_fm_obj.get_model_id_by_vehicle_name(vehicle_name, context)
        vin = api_fm_obj.get_vin_by_name(vehicle_name, context)
        api_fm_obj.modify_geo_position_for_vehicle(vehicle_id, vehicle_name, model_id, vin, gps_status.upper())
        logging.info(f"Gps of the Vehicle is  {gps_status} at: {str(datetime.datetime.utcnow().isoformat())}")
        context.geo_status[datetime.datetime.utcnow().isoformat()] = gps_status.upper()

@step('geo positioning data is verified')
@step('positioning data is verified within "{timeout:d}" seconds')
def step_impl(context, timeout = 600):
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    logging.info(f"Checking GPS Status for Vehicle -  {context.vehicle_name}")
    location_displayed = False
    api_gen_obj.update_timeout_time(timeout)
    api_gen_obj.start_timer()
    while (api_gen_obj.check_timer() == True):
        r = api_fm_obj.get_vehicle_position(context.vehicle_id)
        if r.status_code == requests.codes.ok:
            logging.info(f"Current Location LAT: {r.json()['latitude']} and LONG: {r.json()['longitude']} at:{r.json()['date']}")
            location_displayed = True
            api_gen_obj.stop_timer()
            break
        time.sleep(30)
    assert location_displayed == True, "Location for the Vehicle" + context.vehicle_name + " is not displayed after waiting for "+ str(timeout) + " seconds"

@step('geo positioning data of "{vehicle_name}" is deleted')
def step_impl(context, vehicle_name):
    """Geo position data of the vehicle is deleted if present"""
    if(len(vehicle_name) == vehicle_name.count(' ')):
        vehicle_name = context.vehicle_name
    context.vehicle_name = vehicle_name
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    vehicle_id = api_fm_obj.get_vehicle_id_by_name(vehicle_name, context)
    context.vehicle_id = vehicle_id
    assert vehicle_id is not None, constants.FM_UNABLE_TO_FIND_VEHICLE_NAME.format(vehicle_name)
    r = api_fm_obj.del_vehicle_position(context.vehicle_id)
    assert r.status_code == requests.codes.no_content, "Geo Position data deletion is not possible"

@step('geo position data of all vehicles are deleted')
def step_impl(context):
    """Geo position of all the vehicles are deleted"""
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    r = api_fm_obj.del_geo_positions()
    assert r.status_code == requests.codes.no_content, "Geo Position data deletion is not possible"

@step('verify that vehicle map is "{status}"')
def step_impl(context, status):
    """Status of vehicle map is verified"""
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    r = api_fm_obj.get_vehicle_maps_status()
    if status == "empty":
        assert '_embedded' not in r.json(), "Vehicle map is not empty"
    else:
        assert '_embedded' in r.json(), "Vehicle map is empty"

@step('geo position of all vehicles is "{state}"') 
def step_impl(context, state):
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    r = api_fm_obj.set_geo_position(state)
    assert r.status_code == requests.codes.no_content, api_gen_obj.assert_message(r)

@step('verify geo positioning in "{vehicle}" is "{status}"')
def step_impl(context, vehicle, status):
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    vehicle_data = api_fm_obj.get_vehicle_by_name(vehicle, context)
    assert vehicle_data['geoPositioning'] == status.upper(), constants.FM_UNABLE_TO_FIND_VEHICLE_NAME.format(vehicle)


@step('perform CL15 On and Off operation {number:d} times on device {device} with a time limit of {max_time:d} minutes for each iteration')
def step_impl(context,device,number,max_time):
    """
    Description: 
                Perform "number" times CL15 ON and OFF and validate if the time taken for device to come online/offline is within "max_time"
    Parameters: 
                number   - Number of CL15 ON/OFF iterations
                max_time - Max time for device to go offline/online
    Expected result: 
                Time taken by the device to come to expected state is within the max_time for each of the iterations and report at the end
    """
    
    context.execute_steps(f'''
        Given device {device} is "ONLINE"
    ''')
    
    context.repetitive_steps = f'''
            When switch "CL15" is turned "Off" 
            Then wait for device to be "OFFLINE" within "5" minutes
            When switch "CL15" is turned "On"
            Then wait for device to be "ONLINE" within "5" minutes
        '''

    context.execute_steps(f'''
        Given perform load test for {number} iterations with predefined steps
           ''')


@step('perform CL30 On and Off operation {number:d} times on device {device} with a time limit of {max_time:d} minutes for each iteration')
def step_impl(context,device,number,max_time):
    """
    Description: 
                Perform "number" times CL15 ON and OFF and validate if the time taken for device to come online/offline is within "max_time"
    Parameters: 
                number   - Number of CL15 ON/OFF iterations
                max_time - Max time for device to go offline/online
    Expected result: 
                Time taken by the device to come to expected state is within the max_time for each of the iterations and report at the end
    """
    
    context.execute_steps(f'''
        Given device {device} is "ONLINE"
    ''')
    
    context.repetitive_steps = f'''
            When switch "CL30" is turned "Off" 
            Then wait for device to be "OFFLINE" within "5" minutes
            When switch "CL30" is turned "On"
            Then wait for device to be "ONLINE" within "5" minutes
        '''

    context.execute_steps(f'''
        Given perform load test for {number} iterations with predefined steps
           ''')


@step('perform {number:d} times GSM connection on and off for device {device}')
def step_impl(context, number, device):
    """
    """

    context.device = device
    context.execute_steps(f'''
        Given device {device} is "ONLINE"
        And test waits for "1" minutes
        Then wait for device to be "ONLINE"
    ''')
    context.repetitive_steps = f'''
                Given command to "stopGSMConnection" GSM mode of the device
                And wait for device to be "OFFLINE"
                When command to "startGSMConnection" GSM mode of the device
		        Then wait for device to be "ONLINE"
            '''
    context.execute_steps(f'''
        Given perform load test for {number} iterations with predefined steps
           ''')

@step('device log count is fetched')
def step_impl(context):
    """Stores the device log existing count to context value"""
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    
    device_log_details = api_fm_obj.get_device_log_entries(context.device_id)
    device_log_old_count = device_log_details.json()["page"]["totalElements"]
    context.device_log_old_count = device_log_old_count

@step('triggering "{trigger_count:d}" new log file generation for device')
@step('triggering new log file generation for device')
@step('triggering new log file generation for "{device_status}" device under test')
@step('triggering new log file generation for container "{container_id}"')
@step('triggering new log file generation for container "{container_id}" when device is "{device_status}"')
@step('triggering new log file generation for device "{device}" and container "{container_id}"')
def step_impl(context, device='', trigger_count = 1, device_status = "ONLINE", container_id = ''):
    """
        Description : It triggers the log file generation for a particular device.

        Pre-condition : None
    
        Parameters  : 
            device = "ES740"
            triggerCount = '1' (optional)
            deviceStatus = "ONLINE" (optional)
   
        Expected result : 
            Triggering is successful
    
    """
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)    
    context.log_trigger_ids = []
    container_trigger_count = 0
    if container_id != '':
        container_ids = container_id.split(',')
        container_trigger_count = len(container_ids)
        trigger_count = container_trigger_count
        if device != '':
            trigger_count += 1

    while trigger_count >= 1:
        api_fm_obj.check_interim_device_status(context.device_id, device_status, 120)
        if container_trigger_count > 0:
            data = {"containerId" : container_ids[container_trigger_count-1]}
            context.log_trigger_ids.append(api_fm_obj.trigger_log_generation(context.device_id, data))
            container_trigger_count -= 1
        else:
            context.log_trigger_ids.append(api_fm_obj.trigger_log_generation(context.device_id))
            time.sleep(30) #Adding this hard wait as 'logEntries' for device log takes time (May be due to file size) even after logTriggers status is executed
        trigger_count -= 1

@step('"{log_count:d}" new log entries are generated for the device')
@step('"{log_count:d}" new log entries are generated for the container')
@step('"{log_count:d}" new log entries are generated for the device and container')
@step('new log entry is generated for the device')
def step_impl(context,log_count=1):
    """
        Description : Verifies the generation of device log entries.

        Pre-condition : NA
    
        Parameters  : 
            logCount = '1' (optional)
   
        Expected result : 
            returns generated device log entries ID
    """
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    log_entry_ids = {}
    if hasattr(context, 'log_trigger_ids'):
        log_trigger_count = len(context.log_trigger_ids)
        for index in range(log_trigger_count):
            logging.info(f'Checking log status for trigger id - {context.log_trigger_ids[index]}')
            api_gen_obj.start_timer()
            while api_gen_obj.check_timer():
                log_trigger_details = api_fm_obj.get_log_trigger_details(context.log_trigger_ids[index], context.device_id)
                trigger_status = log_trigger_details['state']
                if trigger_status == 'EXECUTED':
                    device_log_new_details = api_fm_obj.get_device_log_entries(context.device_id)
                    log_entry_id = device_log_new_details.json()["_embedded"]["logEntries"][index]["logEntryId"]
                    log_file_size = device_log_new_details.json()["_embedded"]["logEntries"][index]["fileSize"]
                    log_entry_ids[log_entry_id] = log_file_size
                    logging.info(f'Log trigger status is Executed as expected for {context.log_trigger_ids[index]}')
                    api_gen_obj.stop_timer()
                    break
                #this trigger_status needs to be changed to 'UNKNOWN' OR 'FAILED' once this bug - ARTMC-32643 is closed
                elif trigger_status == 'PENDING' and (True if 'containerId' in log_trigger_details else False) and log_trigger_details['containerId'] not in ["atos","trimble"]:
                    api_gen_obj.stop_timer()
                    break
                time.sleep(30)
    else:
        log_entry_ids = api_fm_obj.validate_log_with_count(log_count, log_entry_ids, context.device_id, context.device_log_old_count, api_gen_obj)
    
    context.log_entry_ids = log_entry_ids
    if not api_gen_obj.check_timer():
        assert len(log_entry_ids) >= log_count, f"Wrong device log entries count generated. Exp count - {log_count}, Actual Count - {len(log_entry_ids)}"
        
@step('device logs are downloaded and stored')
@step('containers logs are downloaded and stored')  
@step('device and container logs are downloaded and stored')  
@step('device logs can be downloaded containing file {files}')
def step_impl(context, files = None):
    """
        Descirption : verifies downloading of device logs and checks for log file presence.

        Pre-condition : step: new log entry is generated for the device
    
        Parameters  : 
            files = ['MetaData.xml,syslog.txt]
   
        Expected result : 
            validates correct log files are generated and downloaded or not
    """
    
    # for index in range(0,len(context.log_entry_ids)):
    for key, value in context.log_entry_ids.items():
        # logging.info("Trigger downloading of log files for Log Entry Id - %s"%context.log_entry_ids[index])
        logging.info(f"Trigger downloading of log files for Log Entry Id - {key} with file size - {value/1000000} MB")
        api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
        assert value > 0, f'File is empty, file size - {value}'
        if files is not None:
            exp_file_list = files.split(',')
            downloaded_device_logs = api_fm_obj.download_device_logs(context.device_id, key)
            for exp_file in exp_file_list:
                logging.info(f"Checking existence of file - {exp_file} in generated device logs")
                assert exp_file in downloaded_device_logs, "Downloaded device logs doesn't have expected file content, %s file not present"%exp_file
                logging.info(f"File - {exp_file} exists.")
            logging.info (" Generated and downloaded log files contain the expected files. ")
        else:
            path = os.path.dirname(os.path.abspath(__file__))
            context.log_download_path=path+constants.DEVICE_LOG_PATH
            api_fm_obj.download_device_logs(context.device_id, key, context.log_download_path)


@step('delete generated log files from device log entries')
def step_impl(context):
    """
       Description : Deletes the log files from log entries 

       Expected Result : Deleted log files must not present in log entries

    """
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    device_log_details = api_fm_obj.get_device_log_entries(context.device_id)
    device_log_old_count = device_log_details.json()["page"]["totalElements"]
    deleted_log_expected_count = (device_log_old_count - len(context.log_entry_ids))

    # api_fm_obj.delete_device_logs(context.device_id, context.log_entry_ids)
    api_fm_obj.delete_device_logs(context.device_id, context.log_entry_ids.keys())

    device_log_details = api_fm_obj.get_device_log_entries(context.device_id)
    deleted_log_actual_count = device_log_details.json()["page"]["totalElements"]

    assert deleted_log_expected_count == deleted_log_actual_count, "Device logs doesn't have the expected log entries Exp del count - %s, Actual del Count - %s"%(int(deleted_log_expected_count),int(deleted_log_actual_count))

@step('time "{moment}" for device wake up is set')
@step('time "{moment}" for device wake up is set and device should be online for "{duration}"')
@step('time mode and duration for device wake up is set "{moment}" "{mode}" "{duration}"')
@step('set "{mode}" wakeup configuration for device')
def step_impl(context, moment="000:00:10", duration="000:00:05", mode="once"):
    '''
        Descirption : Setting Timer wakeup for a device with {time}.

        Pre-condition : device must be mapped to vehicle

        Parameters  : time string and {duration}
            Examples: 
                12-03-2020, 16:45 {%d-%m-%Y, %H:%M} - time should be in reference to the utc time 
                or
                000:00:10 {%d:%H:%M} 
                duration=200 {in seconds}
           
        Expected result : 
            should able to set a wakeup time for device.

    '''

    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    temp = duration.split(':')
    duration = (int(temp[1]) * 3600 + int(temp[2]) * 60)
    if '-' not in moment:
        moment = moment.split(':')
        day    = int(moment[0])
        hour   = int(moment[1])
        minute = int(moment[2])
        added_utc = datetime.datetime.utcnow() + datetime.timedelta(days= day,hours=hour, minutes=minute,seconds=0)
        moment = datetime.datetime.strftime(added_utc,constants.FM_DATE_AND_TIME)

    get_utc = datetime.datetime.strptime(str(datetime.datetime.utcnow()), '%Y-%m-%d %H:%M:%S.%f').strftime(constants.FM_DATE_AND_TIME)  
    date_time_obj_param = datetime.datetime.strptime(moment, constants.FM_DATE_AND_TIME)
    date_time_obj_utc = datetime.datetime.strptime(get_utc, constants.FM_DATE_AND_TIME)

    if mode == "daily":
        date_format=datetime.datetime.strptime(moment, constants.FM_DATE_AND_TIME).strftime('%S %M %H ? * *')
        logging.info(f'{mode}->{date_format}')
        
    elif mode == "every_second_day":
        date_format=datetime.datetime.strptime(moment, constants.FM_DATE_AND_TIME).strftime('%S %M %H 1/2 * ?')
        logging.info(f'{mode}->{date_format}')

    elif mode == "weekly":
        date_format=datetime.datetime.strptime(moment, constants.FM_DATE_AND_TIME).strftime('%S %M %H ? * %a *')
        logging.info(f'{mode}->{date_format}')
     
    elif mode == "monthly":
        date_format=datetime.datetime.strptime(moment, constants.FM_DATE_AND_TIME).strftime('%S %M %H %d * ? *')
        logging.info(f'{mode}->{date_format}')
     
    elif mode == "yearly":
        date_format=datetime.datetime.strptime(moment, constants.FM_DATE_AND_TIME).strftime("%S %M %H %d %b ? *")
        logging.info(f'{mode}->{date_format}')

    elif mode == "once":
        date_format = datetime.datetime.strptime(moment, constants.FM_DATE_AND_TIME).strftime('%S %M %H %d %m ? %Y')
        logging.info(f'{mode}->{date_format}')

    else:
        assert False, "Pass the correct mode name"


    if date_time_obj_param < date_time_obj_utc:
        assert False, f"date {date_format} should not  preceed {get_utc}"
    wakeup_config = api_fm_obj.vehicle_wakeup_config_present(context.vehicle_id, context.device_slot_name,"TIMER")
    if wakeup_config == None:
        time_config = {
            "type":"TIMER",
            "state":"ENABLED",
            "cronExpression":f"{date_format}",
            "duration":f"{duration}"
        }
        context.duration = duration
        api_fm_obj.create_wakeup_config(context.vehicle_id, context.device_slot_name, time_config)
        context.wakeup_config_id = api_fm_obj.vehicle_wakeup_config_present(context.vehicle_id, context.device_slot_name,"TIMER")['wakeUpConfigurationId']
        
    else:
        time_config = {
            "type":f"{wakeup_config['type']}",
            "state":"ENABLED",
            "cronExpression":f"{date_format}",
            "duration":f"{duration}",
            "wakeUpConfigurationId":f"{wakeup_config['wakeUpConfigurationId']}"
        }   
        context.duration = duration 
        context.wakeup_config_id = time_config['wakeUpConfigurationId']
        if moment == time_config['cronExpression']:
            logging.info(f"existing time {time_config['cronExpression']} is similar to the proposed time {time}")
        else:
            api_fm_obj.update_wakeup_config(context.vehicle_id, context.device_slot_name, time_config['wakeUpConfigurationId'], time_config)

@step('set remote wakeup SMS state as "{state}" for duration "{sms_duration}" is configured')
@step('remote wakeup SMS state as "{state}" is configured')
def step_impl(context, state, sms_duration = "00:15:00"):

    '''
        Descirption : Set remote wakeup state as "{state}" for "{sms_duration}".

        Pre-condition : device should be online

        Parameters  : sate as string and duration be in {sms_duration}
            Examples: 
                "ENABLED"
                "DISABLED"
                "duration" : "00:00:00" {%H:%M:%S}
           
        Expected result : 
            should able to change the remote wakeup status to {state}.

    '''
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    wakeup_sms_config = api_fm_obj.vehicle_wakeup_config_present(context.vehicle_id, context.device_slot_name,"REMOTE")
    h,m,s = sms_duration.split(":")
    context.total_sms_seconds = int(h) * 3600 + int(m) * 60 + int(s)
    wakeup_sms_config_duration = context.total_sms_seconds
    if wakeup_sms_config == None:
        time_config ={
            "duration": wakeup_sms_config_duration, 
            "state": "ENABLED",
            "type": "REMOTE"
        }
        api_fm_obj.create_wakeup_config(context.vehicle_id, context.device_slot_name, time_config)
    elif wakeup_sms_config['state'] == state and wakeup_sms_config['duration']== sms_duration:
        logging.info('Remote wakeup on SMS configuration is as expected')
    else:
        wakeup_sms_config['state'] = f"{state.upper()}"
        time_config ={
            "duration": wakeup_sms_config_duration,
            "state": f"{wakeup_sms_config['state']}",
            "type": "REMOTE",
            "wakeUpConfigurationId": f"{wakeup_sms_config['wakeUpConfigurationId']}"
        }
        api_fm_obj.update_wakeup_config(context.vehicle_id, context.device_slot_name, wakeup_sms_config['wakeUpConfigurationId'], time_config)

@step('test waited till device remote wakeup configuration "{sms_duration}" is met')
def step_impl(context, sms_duration):
    '''
        Descirption : test waits for particular {sms_duration}

        Pre-condition : device should be online

        Parameters  : duration as string
            Examples: 
                "00:00:05" {%H:%M:%S}

        Expected result : test should able to wait for particular {duration}
            
    ''' 
    final_duration = (datetime.datetime.utcnow() - context.final_sms_duration).total_seconds()
    logging.info(f"test waited for the duration, {final_duration}")
    logging.info(context.total_sms_seconds)
    if final_duration >= context.total_sms_seconds:
        logging.info("remote wakeup SMS configuration duration has been exceeded")
    else:
        time.sleep(final_duration)

@step('device wake-up with SMS is triggered')
def step_impl(context):
    '''
        Descirption :  SMS is triggered to the device to wakeup

        Pre-condition : device should be online and wakeup on SMS must be configured with duration 

        Parameters  : message as string
            Examples: 
                "trigger remote wakeup"
    
        Expected result : test should able to wait for particular {duration}
            
    ''' 
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    api_fm_obj.enable_remote_wakeup_sms(context.vehicle_id, context.device_slot_name)
    context.final_sms_duration = datetime.datetime.utcnow()
    logging.info(f'wakeup has triggered on:, {context.final_sms_duration}')

@step('set wakeup timer state as "{state}"')
def step_impl(context, state):
    '''
        Descirption : Set wakeup timer state as "{state}.

        Pre-condition : device should have the wakeup time configuration present 

        Parameters  : sate as string
            Examples: 
                "ENABLED"
                "DISABLED"
           
        Expected result : 
            should able to change the wakeup timer status to {state}.

    '''
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    wakeup_config = api_fm_obj.vehicle_wakeup_config_present(context.vehicle_id, context.device_slot_name,"TIMER")
    if wakeup_config['state'] == state:
        logging.info(f'wakeup config state is as expected {state}')
    else:
        wakeup_config['state'] = f"{state.upper()}"
        api_fm_obj.update_wakeup_config(context.vehicle_id, context.device_slot_name, wakeup_config['wakeUpConfigurationId'], wakeup_config)
        wakeup_config = api_fm_obj.vehicle_wakeup_config_present(context.vehicle_id, context.device_slot_name,"TIMER")
        assert wakeup_config['state'] == state,f"failed to change the wakeup config state to {state}"

@step('perform {number:d} times self mapping of {device} with vehicles {vehicle1} and {vehicle2}')
def step_impl(context, number, device, vehicle1, vehicle2):
    """ Description     : Perfoms the functionalities of 
                            {
                                Unmap the device from any vehicle
                                Map it to Vehicle 1
                                Validate
                                Map it to Vehicle 2
                                Validate
                                Map it to Vehicle 1
                                Validate
                                Map it to Vehicle 2
                                Validate
                            }
                            for 'n' times

        Pre-condition       : None

        Parameters          : number, device, vehicle1, vehicle2

        Expected result     : Load test succeeds for the number of iterations mentioned
    """

    context.repetitive_steps  = f'''
        Given device {device} is "ONLINE"
        And unmap device from the vehicle
        And vin is erased from device {device}
        And backend vehicle pairing status of the device is validated to be "Unmapped"
        And it is validated that {device} is mapped to "none"
        And a vehicle {vehicle1} using Manufacturer "BMW" and Model "X5" is created with VIN "smart_vin"
        When VIN of vehicle {vehicle1} is implanted in the device {device}
        And backend vehicle pairing status of the device is validated to be "Mapped"
        Then it is validated that {device} is mapped to {vehicle1}
        When a vehicle {vehicle2} using Manufacturer "BMW" and Model "X5" is created with VIN "smart_vin"
        And VIN of vehicle {vehicle2} is implanted in the device {device}
        And backend vehicle pairing status of the device is validated to be "Mapped"
        Then it is validated that {device} is mapped to {vehicle2}
        #============================================================================
    '''
    context.execute_steps(f'''
        Given perform load test for {number} iterations with predefined steps
    ''')
        
@step('Perform timer wakeup {number:d} times with the data {vehicle}, {device}, {duration}, {moment}')
def step_impl(context, number, device, moment, duration, vehicle):
    """
    Description     : Performs timer wakeup for 20 iterations
                        {
                            set time/moment and duration for timer wakeup
                            switch off CL15
                            wait for device to go "OFFLINE"
                            when wakeup time is met
                            wait for device to come "ONLINE" (due to timer wakeup)
                            After duration of timer wakeup  
                            wait for device to go "OFFLINE"       
                        }
                            for 'n' times

        Pre-condition       : None

        Parameters          : number, device, vehicle, duration and moment 

        Expected result     : Load test succeeds for the number of iterations mentioned
    """

    context.device = device
    context.execute_steps(f'''
        Given device {device} is "ONLINE"  
        And map device to the vehicle {vehicle}
    ''')
    context.repetitive_steps = f'''
        
                When time {moment} for device wake up is set and device should be online for {duration}
                And switch "CL15" is turned "Off"
                And wait for device to be "OFFLINE"
                And test waited till device wakeup configuration time {moment} is met 
                And wait for device to be "ONLINE"
                And test waited till device wakeup configuration time {duration} is met 
                And wait for device to be "OFFLINE"
                And switch "CL15" is turned "On"
                And wait for device to be "ONLINE"
            
            '''
    context.execute_steps(f'''
        Given perform load test for {number} iterations with predefined steps
           ''')
           
@step('create "{vehicle_list}" if it is not available')
def step_impl(context, vehicle_list):
    """
        Description     : Creates a Vehicle if the Vehicle is not available in the Environment.
        
        Pre-condition   : None

        Parameters      : vehicle_name : Name of the Vehicle

        Expected result : New Vehicle is created if the Vehicle was not available.
    """
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    vehicles = vehicle_list.split(",")
    for vehicle_name in vehicles:
        if(len(vehicle_name) == vehicle_name.count(' ')):
                if(vehicles.count(' ') == 1) :
                    vehicle_name = context.default_vehicle
                else:
                    assert False, "Unable to add more than one vehicle from devicemap data, please enter valid vehicle names"
        context.vehicle_name = vehicle_name
        context.vehicle_id = api_fm_obj.get_vehicle_id_by_name(context.vehicle_name, context)
        context.all_vehicle_id.append(context.vehicle_id)


@step('create device slot "{device_slot_list}" for "{vehicle_name}" vehicle')
@step('create device slot "{device_slot_list}" with "{slot_type}" for "{vehicle_name}" vehicle ')
def step_impl(context, device_slot_list, vehicle_name, slot_type = None):
    """
        Description     : Creates device slots of the given type on the Vehicle
        
        Pre-condition   : Vehilce is created and available

        Parameters      : device_slot_list , vehicle , slot_type (Default type: CCU_6430)
        Example         :device_slot_list = CCU1,CCU2

        Expected result : Device slots are created on the Vehicle with the Expected type
    """
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    if slot_type!= None:
        context.device_slot_type = slot_type
    slot_list = device_slot_list.split(",")
    if(len(vehicle_name) == vehicle_name.count(' ')):
            vehicle_name = context.default_vehicle
    context.vehicle_name = vehicle_name
    context.vehicle_id =  api_fm_obj.get_vehicle_id_by_name(context.vehicle_name, context)
    for slot_name in slot_list:
        slot_available = api_fm_obj.fetch_specific_slot_from_vehicle(context.vehicle_id, slot_name + "_" + context.device_slot_type, context.device_slot_type)
        assert slot_available == True, "Unable to create device slot with name" + slot_name + "For vehicle " + vehicle_name


@step('map devices to device slot of "{vehicle_name}" vehicle')
def step_impl(context, vehicle_name):
    """
        Description     : Maps devices to the Device slot of Vehicle
        
        Pre-condition   : Vehilce is created and available
                        Device Slots are avaialble for Vehicle
                        Device is available in the Environment

        Parameters      : vehicle , data table which contains device and slot_name parameters in heading and data for both

        Expected result : Devices are mapped to the expected device slot of the vehicle
    """
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    if(len(vehicle_name) == vehicle_name.count(' ')):
            vehicle_name = context.default_vehicle
    context.vehicle_name = vehicle_name
    context.vehicle_id =  api_fm_obj.get_vehicle_id_by_name(context.vehicle_name, context)
    for row in context.table:
        device_id =context.devices_data[row["device"]]["device_name"]
        api_fm_obj.unmap_device_from_vehicle(device_id)
        api_fm_obj.map_device_to_vehicle_device_slot(context.vehicle_id, row["slot_name"] + "_" + context.device_slot_type, device_id)
        context.all_device_ids.append(device_id)
        if(api_fm_obj.get_vin_by_name(context.vehicle_name, context)!= api_fm_obj.get_detected_vin(device_id)):
            context.execute_steps(f'''
                When VIN of vehicle "{context.vehicle_name}" is implanted in the device "{row["device"]}"
        ''')
    context.device_mapped = True


@step('unmap device "{device_list}" from vehicle')
def step_impl(context, device_list):
    """
        Description     : UnMaps devices from the Device slot of Vehicle

        Pre-condition   : Device is attached to Device slot of Vehicle

        Parameters      : vehicle , data table which contains device and slot_name parameters in heading and data for both

        Expected result : Devices are unmapped to the expected device slot of the vehicle
    """
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    devices = device_list.split(",")
    for device in devices:
        api_fm_obj.unmap_device_from_vehicle(context.devices_data[device]["device_name"])

@step('device not being mapped to vehicle "{vehicle_name}" is verified')
def step_impl(context, vehicle_name):
    """
        Description     : Method tries to Map devices to the Device slot of Vehicle which are already mapped to a different slot
        
        Pre-condition   : Vehilce is created and available
                        Device Slots are avaialble for Vehicle
                        Device is already mapped to another slot
        Parameters      : vehicle , data table which contains device and slot_name parameters in heading and data for both

        Expected result : Devices is not mapped to the requested device slot of the vehicle
    """
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    if(len(vehicle_name) == vehicle_name.count(' ')):
            vehicle_name = context.default_vehicle
    context.vehicle_name = vehicle_name
    context.vehicle_id =  api_fm_obj.get_vehicle_id_by_name(context.vehicle_name, context)
    for row in context.table:
        api_fm_obj.map_already_mapped_device_to_vehicle(context.vehicle_id, row["slot_name"] + "_" + context.device_slot_type, context.devices_data[row["device"]]["device_name"])

@step('prepare vehicle "{vehicle_name}" by clearing all pending jobs')
def step_impl(context, vehicle_name):
    """
        Description     :
        
        Pre-condition   :
        Parameters      : 
        Expected result : 
    """
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    api_rd_obj = API_OTA_Function_Calls_GX_Class.ApiOTAFunctionCallsGXClass(context.env, context.log_api_details)
    slotlist = []
    if(len(vehicle_name) == vehicle_name.count(' ')):
            vehicle_name = context.default_vehicle
    context.vehicle_name = vehicle_name
    context.vehicle_id = api_fm_obj.get_vehicle_id_by_name(context.vehicle_name, context)
    slotlist = api_rm_obj.get_slot_with_pending_rm_assignment(context.vehicle_id)
    rd_slot_name = api_rd_obj.get_slot_with_pending_rd_assignment(context.vehicle_id)
    if(rd_slot_name is not None) and (rd_slot_name not in slotlist):
        slotlist.append(rd_slot_name)
    for slot in slotlist:
        api_fm_obj.delete_device_slot_from_vehicle(context.vehicle_id, slot)
        time.sleep(2)

@step('set "{device_mapping}" functionality as "{state}" with mode "{vehicle_creation_strategy}"')
@step('set "{device_mapping}" functionality as "{state}" in fleet settings')
def step_impl(context, state, device_mapping, vehicle_creation_strategy = None):
    '''
        Description : Set "{device_mapping}" functionality state as "{state}" with "{mode}".

        Pre-condition : Device should be online 

        Parameters  : device_mapping, state and mode as string
            Examples: 
                device_mapping  -  "enableSelfMapping"
                                    "pairOnlyTrustedVin"
                Mode            -   "Create new vehicle"
                                    "Wait for new vehicle"
                                    "Ignore"
                State -         -   "ENABLED","DISABLED"
           
        Expected result : Automatic "{device_mapping}" status to {state} with {mode} is changed.

    '''
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    current_mapping_status = api_fm_obj.self_mapping_state(device_mapping)
    if(current_mapping_status[0] == state and vehicle_creation_strategy is None):
        logging.info(f'automatic device mapping state is as expected :  {state}')
    elif current_mapping_status[0] == state and current_mapping_status[1] == vehicle_creation_strategy:
        logging.info(f'automatic device mapping state is as expected :  {state}')
    else:
        if state == "ENABLED":
            enable_self_mapping = True
        else:
            enable_self_mapping = False
        api_fm_obj.update_self_mapping_state(enable_self_mapping,vehicle_creation_strategy,device_mapping)
    context.self_mapping_device = True
    


@step('create a vehicle setup group "{vsg_name}"')
def step_impl(context, vsg_name):
    '''
        Description :  Step will create a new Vehicle setup group, in case its not available 
                       and vehicle setup group ID will be stored in context

        Pre-condition : NIL

        Parameters  :  vsg_name: Name of Vehicle Setup group

        Expected result : Vehicle setup group is available for use
    '''
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    context.vsg_id = api_fm_obj.get_vsg_id_from_vsg_name(vsg_name)
    context.all_vsg_data[vsg_name] = { 'vsg_id': context.vsg_id, 'vehicles': [], 'device_slot': [], 'remote_measurements': {}, 'remote_diagnostics': []}

@step('create device slots "{slot_list}" to vehicle setup group "{vsg_name}"')
def step_impl(context, slot_list, vsg_name, slot_type = None):
    '''
        Description : Creates Device slots for the Vehicle setup group

        Pre-condition : Vehicle setu-p group is created and available for use

        Parameters  : slot_list - Slot names to be created; seperated with comma
                      vsg_name - Name of Vehicle setup group
                      slot_type - Device slot type - Default type: CCU-6430
            Examples: slot_list: CTPG,CTPG2
               
           
        Expected result : Slots are created on VSG

    '''
    if slot_type is not None:
        context.device_slot_type = slot_type
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    vsg_id = context.all_vsg_data[vsg_name]['vsg_id']
    slots = slot_list.split(",")
    for slot_name in slots:
        slot_available = api_fm_obj.get_slot_for_vsg(vsg_id, slot_name + "_" + context.device_slot_type, context.device_slot_type)
        assert slot_available == True, "Unable to create Device slot with name: " + slot_name + " for VSG: " + vsg_name
        context.all_vsg_data[vsg_name]["device_slot"].append(slot_name + "_" + context.device_slot_type)

@step('add vehicles "{vehicle_list}" to vehicle setup group "{vsg_name}"')
def step_impl(context, vehicle_list, vsg_name):
    '''
        Description : Used to Add Vehicles to the Vehicle setup group. if Vehicle is not available in VSG

        Pre-condition : Vehicle setup group is available

        Parameters  : vehicle_list- Name of Vehicles; seperated by Comma
                      vsg_name - Name of Vehicle setup group

            Examples: vehicle_list - TestVehicle1,TestVehicle2
               
           
        Expected result : Vehicles are added to VSG

    '''
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    vsg_id = context.all_vsg_data[vsg_name]['vsg_id']
    context.vsg_vehicles = vehicle_list
    context.vsg_name = vsg_name
    vehicles = vehicle_list.split(",")
    context.vehicle_count = len(vehicles)
    vehicleslist = api_fm_obj.get_vehicles_from_vsg(vsg_id)
    if vehicleslist is not None:
        vehicleslist = api_fm_obj.remove_unwanted_vehicles_from_vsg(vsg_id, vehicles, vehicleslist, context)
    for vehicle_name in vehicles:
        vehicle_id = api_fm_obj.get_vehicle_id_by_name(vehicle_name, context)
        if(vehicle_id not in vehicleslist):
            api_fm_obj.add_vehicle_to_vsg(vehicle_id, vsg_id)
        else: 
            logging.info(f"Vehicle ,{vehicle_name},  is already part of VSG")
        context.all_vsg_data[vsg_name]["vehicles"].append(vehicle_name)
        context.vsg_remove_vehicles = True

@step('delete the vsg "{vsg_name}"')
@step('delete the vehicle setup group')
def step_impl(context, vsg_name = None):
    '''
        Description : VSG with the provided name will be deleted

        Pre-condition : Vehicle setup group is available

        Parameters  : vsg_name - Name of Vehicle setup group
               
           
        Expected result : VSG or list of VSGs are deleted successfully

    '''
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    if(vsg_name is not None):
        api_fm_obj.delete_vsg(context.all_vsg_data[vsg_name]['vsg_id'])
    else:
        for vsgs in context.all_vsg_data:
            api_fm_obj.delete_vsg(context.all_vsg_data[vsgs]['vsg_id'])

@step('remove vehicles "{vehicle_list}" from vehicle setup group "{vsg_name}"')
def step_impl(context, vehicle_list, vsg_name):
    '''
        Description : Remove Vehicles which are part of the Vehicle setup group.

        Pre-condition : Vehicle setup group is available, Vehicle is available in vsg

        Parameters  : vehicle_list- Name of Vehicles; seperated by Comma
                      vsg_name - Name of Vehicle setup group

            Examples: vehicle_list - TestVehicle1,TestVehicle2
               
           
        Expected result : Vehicles are removed from VSG

    '''
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    vsg_id = context.all_vsg_data[vsg_name]['vsg_id']
    vehicles = vehicle_list.split(",")
    vehicleslist = api_fm_obj.get_vehicles_from_vsg(vsg_id)
    for vehicle_name in vehicles:
        vehicle_id = api_fm_obj.get_vehicle_id_by_name(vehicle_name, context)
        if(vehicle_id in vehicleslist):
            api_fm_obj.remove_vehicle_from_vsg(vsg_id, vehicle_id)
            context.all_vsg_data[vsg_name]["vehicles"].remove(vehicle_name)
            context.vsg_remove_vehicles = False
        else: 
            logging.info(f"Vehicle ,{vehicle_name},  is not part of VSG")

@step('delete device slots "{slot_list}" from vehicle setup group "{vsg_name}"')
def step_impl(context, slot_list, vsg_name):
    '''
        Description : Deletes Device slots for the Vehicle setup group by clearing all attached Vehicles

        Pre-condition : Vehicle setup group is created and slots are added to it

        Parameters  : slot_list - Slot names to be created; seperated with comma
                      vsg_name - Name of Vehicle setup group
            Examples: slot_list: CTPG,CTPG2
               
        Expected result : Slots are Deleted from VSG

    '''
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    vsg_id = context.all_vsg_data[vsg_name]['vsg_id']
    slots = slot_list.split(",")
    for slot_name in slots:
       api_fm_obj.delete_device_slot_from_vsg(vsg_id, slot_name + "_" + context.device_slot_type)
       context.all_vsg_data[vsg_name]["device_slot"].remove(slot_name + "_" + context.device_slot_type)

@step('verify vehicles "{vehicle_list}" have same "{property_name}" as vehicle setup group "{vsg_name}"')
def step_impl(context, vehicle_list, property_name, vsg_name):
    '''
        Description : To verify Vehicles in the Vehicle setup group are having same property as VSG

        Pre-condition : Vehicle setup group is available

        Parameters  : vehicle_list- Name of Vehicles; seperated by Comma
                      vsg_name - Name of Vehicle setup group
                      property - name of property

            Examples: vehicle_list - TestVehicle1,TestVehicle2
                      property - DEVICE_SLOT, REMOTE_MEASUREMENT, REMOTE_DIAGNOSITC (Currently only DEVICE_SLOT is implemented)
           
        Expected result : Vehicles have same property as VSG

    '''
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    vsg_id = context.all_vsg_data[vsg_name]['vsg_id']
    vehicles = vehicle_list.split(",")
    vehicleslist = api_fm_obj.get_vehicles_from_vsg(vsg_id)
    for vehicle_name in vehicles:
        vehicle_id = api_fm_obj.get_vehicle_id_by_name(vehicle_name, context)
        if(vehicle_id not in vehicleslist):
            assert False, "Vehile with name: " + vehicle_name+ " is not available in to VSG: " + vsg_name
        else: 
            api_fm_obj.verify_vsg_prop_on_vehicle(vehicle_id, vsg_id, property_name)
        

@step('map device to "{device_slot}" slot of vehicles')
def step_impl(context, device_slot):
    """
        Description     : Maps devices to the Device slot of Vehicle in th VSG
        
        Pre-condition   : Vehilce is created and available
                          Vehicle is mapped to vsg
                          Device is available in the Environment

        Parameters      : device_slot, data table which contains vehicle and device parameters in heading and data for both

        Expected result : Devices are mapped to the expected device slot of the vehicle
    """
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    for row in context.table:
        vehicle_id =  api_fm_obj.get_vehicle_id_by_name(row["vehicle_name"], context)
        api_fm_obj.unmap_device_from_vehicle(context.devices_data[row["device"]]["device_name"])
        api_fm_obj.map_device_to_vehicle_device_slot(vehicle_id, device_slot + "_" + context.device_slot_type, context.devices_data[row["device"]]["device_name"])
        context.all_device_ids.append(context.devices_data[row["device"]]["device_name"])
        context.vehicle_data[row["vehicle_name"]]["device_data"].update({"slot_name": device_slot + "_" + context.device_slot_type, "device": context.devices_data[row["device"]]["device_name"]})
        context.execute_steps(f'''
            When VIN of vehicle "{row["vehicle_name"]}" is implanted in the device "{row["device"]}"
     ''')
    context.device_mapped = True

@step('check device "{specimen_device}" IP connection')
def step_impl(context, specimen_device):
    CCU_IP = context.devices_data[specimen_device][context.test_device+"_IP"]
    proc = subprocess.Popen("ipconfig", shell=True, stdin=None, stdout=subprocess.PIPE, stderr=True)
    proc.wait()
    time.sleep(5)
    out,err = proc.communicate()
    assert err is None, f"Device ip - {CCU_IP} is not proper, Please check the same. It returned error : {err}"
    device_host = ''.join(CCU_IP.rpartition('.')[:2])
    assert device_host in str(out), f"Device - {context.device_id} with this hostname {CCU_IP} is not ONLINE"
    logging.info(f"Device with this ip - {CCU_IP} is ONLINE")

@step('verify the IDS report log file')
def step_impl(context):
    '''
    Description : Verify latest IDS report log file in fleet management device section
    Expected result : able to download log file 
    '''
    
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    report,result = api_fm_obj.verify_ids_log(context.log_download_path)
    assert report == True ,f"IDS Report is not as expected, actual_result-{result}"
