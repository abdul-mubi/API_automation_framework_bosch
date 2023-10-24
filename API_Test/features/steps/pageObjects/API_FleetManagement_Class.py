import requests
import logging
import time
import os

import steps.utils.API_Requests as API_Request
import steps.pageObjects.API_Generic_Class as API_Generic_Class
from io import BytesIO
from zipfile import ZipFile
import json
import pynmea2
import datetime
import logging
import shutil
import steps.constantfiles.constants_fleetmanagement as constants

class ApiFleetManagementClass():
    
    path = os.path.dirname(os.path.abspath(__file__))
    fleet_management_data_path = path + constants.TEST_DATA_FM
    speed = {
            "halt": "halt",
            "average": "average",
            "fast": "fast",
            "slow": "slow"
        }

    def __init__(self, enviroment, log_api_details):
        self.api_requests = API_Request.ApiRequestsClass(enviroment, log_api_details)
        self.api_gen_obj = API_Generic_Class.ApiGenericClass()

    def get_model_id(self, manufacturer_name, model_name):
        """Get the model id for given manufacturer and model"""
        #https://ui-plcs-integration.s-apps.de1.bosch-iot-cloud.com/api/applications/fleet-management/manufacturers?search=name=="Ford"
        r = self.api_requests.get_request(constants.FM_MANUFACTURERS_SEARCH_NAME.format(manufacturer_name))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        manufacturer_id = r.json()['_embedded']['manufacturers'][0]['manufacturerId']
        r_model = self.api_requests.get_request(constants.FM_MANUFACTURERS_ID_MODELS_SEARCH_NAME.format(manufacturer_id,model_name))
        assert r_model.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r_model)
        model_id = r_model.json()['_embedded']['models'][0]['modelId']
        return model_id


    def get_manufacturer_detail(self, manufacturer):
        r = self.api_requests.get_request(constants.FM_MANUFACTURERS_SEARCH_NAME.format(manufacturer))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r


    def create_manufacturer_model(self, manufacturer, model):
        logging.info(f"Creating a Manufacturer - {manufacturer}")
        manufacturer_data = {"name" : manufacturer}
        r = self.api_requests.post_request(constants.FM_MANUFACTURERS, manufacturer_data)
        assert r.status_code == requests.codes.created, self.api_gen_obj.assert_message(r)
        r = self.get_manufacturer_detail(manufacturer)
        manufacturer_id = r.json()['_embedded']['manufacturers'][0]['manufacturerId']

        logging.info(f"Creating Model -{model} for Manufacturer - {manufacturer}")
        model_data = {"name" : model}
        r_model = self.api_requests.post_request(constants.FM_MANUFACTURERS_ID_MODELS.format(manufacturer_id), model_data)
        assert r_model.status_code == requests.codes.created, self.api_gen_obj.assert_message(r_model)

    def create_new_vehicle(self, vehicle_name, context, manufacturer_name = "Ford", model_name = "Mustang", vin = None):
        """Creates vehicle with name"""
        r = self.get_manufacturer_detail(manufacturer_name)
        if "_embedded" not in r.json():
            logging.info(f"Manufacturer - {manufacturer_name} doesn't exist. Creating a new one ...")
            self.create_manufacturer_model(manufacturer_name, model_name)

        model_id = self.get_model_id(manufacturer_name, model_name)
        if vin == 'smart_vin':
            if vehicle_name.startswith('ZE2E_'):
                vin = f'AUT{vehicle_name[-14:]}'
            else:
                current_time = datetime.datetime.now()
                vin = f"AUT{current_time.year}{'{:02d}'.format(current_time.month)}{'{:02d}'.format(current_time.day)}{'{:02d}'.format(current_time.hour)}{'{:02d}'.format(current_time.minute)}{'{:02d}'.format(current_time.second)}"
            assert len(vin) == 17, f'Length of the VIN {vin} is not 17 as expected'    
        data = {
            'name': vehicle_name,
            'modelId': model_id,
            'VIN': vin       
        }

        r = self.api_requests.post_request(constants.FM_VEHICLES, data)
        assert r.status_code == requests.codes.created, self.api_gen_obj.assert_message(r)
        
        return self.get_vehicle_id_by_name(vehicle_name, context)

    def get_vehicle_by_name(self, vehicle_name, context):
        """Returns the single vehicle JSON object specified by the name"""
        r = self.api_requests.get_request(constants.FM_VEHICLES_SEARCH_NAME.format(vehicle_name))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        if r.json()['page']['totalElements'] == 0:
            r = self.create_new_vehicle(vehicle_name, context, vin = 'smart_vin')
            logging.info(r)
            r = self.api_requests.get_request(constants.FM_VEHICLES_SEARCH_NAME.format(vehicle_name))
            assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)

        res = r.json()['_embedded']['vehicles']
        for v in res:
            if v['name'] == vehicle_name:
                return v

    def get_vehicle_id_by_name(self, vehicle_name, context):
        """Search for the specified vehicle name and the corresponding
        vehicle id is extracted for further use"""
        if vehicle_name not in context.vehicle_data:
            vehicle = self.get_vehicle_by_name(vehicle_name, context)
            vehicle_id = vehicle['vehicleId']
            context.vehicle_data[vehicle_name] = {"vehicle_id":vehicle_id, "device_data":{}, "remote_measurement":{}}
        return context.vehicle_data[vehicle_name]["vehicle_id"]

    def get_vin_by_name(self, vehicle_name, context):
        """Search for the specified vehicle name and the corresponding
        VIN is extracted for further use"""
        vehicle = self.get_vehicle_by_name(vehicle_name, context)
        return vehicle['VIN']
    
    def get_model_id_by_vehicle_name(self, vehicle_name, context):
        """Search for the specified vehicle name and the corresponding
        model id is extracted for further use"""
        vehicle = self.get_vehicle_by_name(vehicle_name, context)
        return vehicle['_embedded']['model']['modelId']
        
    def get_vehicle_name_by_vin(self, vin):
        r = self.api_requests.get_request(constants.FM_VEHICLES_SEARCH_VIN.format(vin))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        if '_embedded' in r.json():
            res = r.json()['_embedded']['vehicles']
            for v in res:
                if v['VIN'] == vin:
                    return v['name']
        else:
            assert False, f'No vehicles exist for the VIN {vin}'

    def get_device_properties(self, device_id):
        """Check if the device is online"""
        r = self.api_requests.get_request(constants.FM_DEVICES_ID.format(device_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r

    def get_device_status(self, device_id):
        """Check if the device is online"""
        r = self.get_device_properties(device_id)
        return r.json()['onlineState']

    def unmap_device_from_vehicle(self, device_id):
        vehicle_id = self.get_paired_vehicle(device_id)
        if (vehicle_id is not None):
            logging.info("Unmapping device from Vehicle")
            r = self.api_requests.get_request(constants.FM_VEHICLES_ID.format(vehicle_id))
            assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
            if "deviceSlots" in r.json()['_embedded']:
                for slot in r.json()['_embedded']["deviceSlots"] :
                    if "deviceId" in slot and slot["deviceId"] == device_id:
                        logging.info("Unmapping device from Vehicle")
                        etag = self.api_requests.get_etag(constants.FM_VEHICLES_ID.format(vehicle_id))
                        r = self.api_requests.delete_request(constants.FM_VEHICLES_DEVICE_SLOT_NAME_ID.format(vehicle_id,slot["name"],device_id),{'if-match': etag})
                        assert r.status_code == requests.codes.no_content, "Unable to Unmap device from Device slot of previous vehicle"
                        time.sleep(3)
                        logging.info("Device is unmapped from the Vehicle")
            else:
                assert False, f"Device slots details are not displayed in the response for vehicle with id: {vehicle_id}"
        else:
            logging.info(f"Device {device_id} is not mapped to any Vehicle")

    def get_detected_vin(self,device_id):
        """fetches detected vin of the device"""
        r = self.api_requests.get_request(constants.SM_DEVICE_ID.format(device_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r.json()['detectedVin']

    def get_vehicle_position(self, vehicle_id):
        r = self.api_requests.get_request(constants.FM_VEHICLES_ID_LATEST_POSITION.format(vehicle_id))
        return r
    

    def del_vehicle_position(self, vehicle_id):
        etag = self.api_requests.get_etag(constants.FM_VEHICLES_ID.format(vehicle_id))
        r = self.api_requests.delete_request(constants.FM_VEHICLES_ID_POSITIONS
                                            .format(vehicle_id),{'if-match': etag})
        return r

    def modify_geo_position_for_vehicle(self,vehicle_id, vehicle_name, model_id, vin, gps_status):
        data = {
            "VIN" : vin,
            "assignedVehicleCustomAttributes" : [],
            "geoPositioning" : gps_status,
            "name" : vehicle_name,
            "modelId" : model_id
        }

        etag = self.api_requests.get_etag(constants.FM_VEHICLES_ID.format(vehicle_id))
        r = self.api_requests.put_request(constants.FM_VEHICLES_ID.format(vehicle_id), params=data, custom_header = {'if-match': etag})
        assert r.status_code == requests.codes.no_content, self.api_gen_obj.assert_message(r)
    
    def del_geo_positions(self):
        r = self.api_requests.delete_request(constants.FM_VEHICLES_POSITIONS)
        return r
    
    def get_vehicle_maps_status(self):
        r = self.api_requests.get_request(constants.FM_VEHICLES_POSITIONS)
        return r
    
    def set_geo_position(self,state):
        if state.upper() == "ENABLED":
            set_val = True
        else:
            set_val = False
        data = {
            "enabled" : set_val
        }        
        r = self.api_requests.put_request(constants.FM_VEHICLES_GPSCONFIG,params=data, custom_header = {})
        return r

    def undispatch_device(self,device_id):
        etag = self.api_requests.get_etag(constants.FM_DEVICES_ID.format(device_id))
        r = self.api_requests.put_request(constants.FM_UNDISPATCH.format(device_id),params="", custom_header = {'if-match': etag})
        assert r.status_code == requests.codes.no_content, self.api_gen_obj.assert_message(r)

    def trigger_log_generation(self, device_id, data={}):
        """
        Description   : It triggers the device log generation for a particular device
        Parameter     : device_id
                        data -> Payload to trigger container app log(container name) and empty for device logs
        """
        ep = constants.FM_LOG_TRIGGERS.format(device_id)
        logging.info(f"Triggering device new log file generation on device - {device_id}")
        r = self.api_requests.post_request(ep=ep, params=data)
        assert r.status_code == requests.codes.created, self.api_gen_obj.assert_message(r)
        location = r.headers.get('Location')
        log_trigger_id = location.split('/').pop()
        return log_trigger_id
        
    def get_log_trigger_details(self, log_trigger_id, device_id):
        ep = constants.FM_LOG_TRIGGERS_ID.format(device_id, log_trigger_id)
        logging.info(f"Fetching log trigger details for this trigger id - {log_trigger_id}")
        r = self.api_requests.get_request(ep = ep)
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r.json()

    def get_device_log_entries(self, device_id):
        """
            Description         : It fetches the generated device log entry count

            Parameter           : device_id = "ES740-4100072"
        """
        ep = constants.FM_LOG_ENTRIES.format(device_id)
        logging.info("Fetching device log entries details...")
        r = self.api_requests.get_request(ep = ep)
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r

    def download_device_logs(self,device_id, log_entry_id, log_download_path = None):
        """
            Description         : It fetches the generated device log entry count

            Parameter           : device_id = "ES740-4100072"
        """    
        ep = constants.FM_LOG_ENTRIES_ID_FILE.format(device_id,log_entry_id)
        logging.info("Triggering downloading of the generated log entries for the device...")
        r = self.api_requests.get_request(ep = ep)
        time.sleep(15)  # wait is needed to get all log files detail as response
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)

        if log_download_path is None:
            log_zip_file = ZipFile(BytesIO(r.content))
            log_file_names = log_zip_file.namelist()
            return log_file_names
        else:
            log_zip_file = ZipFile(BytesIO(r.content))
            log_zip_file.extractall(log_download_path)
            
    def delete_device_logs(self, device_id, log_entry_ids):
        for index in log_entry_ids:
        # for index in range(0,len(log_entry_ids)):
            logging.info(f"Delete log files for Log Entry Id - {index}")
            ep = constants.FM_LOG_ENTRIES_INDEX.format(device_id,index)
            r = self.api_requests.delete_request(ep = ep)
            assert r.status_code == requests.codes.no_content, self.api_gen_obj.assert_message(r)

    def vehicle_wakeup_config_present(self, vehicle_id, slot_name, wakeup_type):
        r = self.api_requests.get_request(constants.FM_DEVICE_SLOT_NAME_WAKEUPCONFIG.format(vehicle_id,slot_name))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        if "_embedded" in r.json():
            count =0
            for wake_up_configuration in r.json()['_embedded']['wakeUpConfigurations']:
                if wake_up_configuration["type"]== wakeup_type:
                    return r.json()['_embedded']['wakeUpConfigurations'][count]
                count+=1
                   
    def enable_remote_wakeup_sms(self, vehicle_id, slot_name):
        etag = self.api_requests.get_etag(constants.FM_VEHICLES_ID.format(vehicle_id))
        data = {'message': 'trigger remote wakeup'}
        r = self.api_requests.post_request(constants.FM_VEHICLES_DEVICE_SLOT_NAME_SMS.format(vehicle_id,slot_name), params=data, custom_header = {'if-match': etag})
        assert r.status_code == requests.codes.accepted, self.api_gen_obj.assert_message(r)

    def update_self_mapping_state(self,enable_self_mapping,vehicle_creation_strategy,device_mapping):
        if(vehicle_creation_strategy is not None):
            request_body = {
                device_mapping : enable_self_mapping,
                "vehicleCreationStrategy" : vehicle_creation_strategy
            }
        else:
            request_body = {
                device_mapping : enable_self_mapping
            }
        r = self.api_requests.put_request(constants.SM_CONFIG,params=request_body)
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
    
    def self_mapping_state(self,device_mapping):
        r = self.api_requests.get_request(constants.SM_CONFIG)
        mode = None
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        if r.json()[device_mapping] == True:
            state = "ENABLED"
            mode = r.json()["vehicleCreationStrategy"]
        else:
            state = "DISABLED"
        return state,mode
                
    def create_wakeup_config(self, vehicle_id, slot_name, time_config):
        etag = self.api_requests.get_etag(constants.FM_VEHICLES_ID.format(vehicle_id))
        r=self.api_requests.post_request(constants.FM_DEVICE_SLOT_NAME_WAKEUPCONFIG.format(vehicle_id,slot_name), time_config, custom_header = {'if-match': etag})
        assert r.status_code == requests.codes.created, self.api_gen_obj.assert_message(r)
    
    def update_wakeup_config(self, vehicle_id, slot_name, wakeup_config_id, time_config):
        etag = self.api_requests.get_etag(constants.FM_VEHICLES_ID.format(vehicle_id))
        r=self.api_requests.put_request(constants.FM_DEVICE_SLOT_NAME_WAKEUPCONFIG_ID.format(vehicle_id,slot_name,wakeup_config_id), time_config, custom_header = {'if-match': etag})
        assert r.status_code == requests.codes.no_content, self.api_gen_obj.assert_message(r)

    def check_interim_device_status(self, device_id, interim_status, update_timer=None):
        device_online_state = self.get_device_status(device_id)
        if device_online_state != interim_status:
            logging.info(f"Device {device_id} is not {interim_status}")
            if update_timer is not None:
                self.api_gen_obj.update_timeout_time(update_timer)
            self.api_gen_obj.start_timer()
            while (self.api_gen_obj.check_timer() == True):
                logging.debug(f"Checking device - {device_id} status")
                device_online_state = self.get_device_status(device_id)
                if device_online_state == interim_status:
                    logging.info(f"Device is back after intermettent behavior {interim_status}")
                    self.api_gen_obj.stop_timer()
                    break
                time.sleep(30)

            if (self.api_gen_obj.check_timer() == False):
                assert device_online_state == interim_status, "Please check the device, Device is not "+interim_status+" after waiting for 10 minutes."

        else:
            logging.info(f"Device has the expected status {interim_status}")


    def fetch_specific_slot_from_vehicle(self,vehicle_id,slot_name, device_type, create_new_slot = True):
        """Checks for device slot availablity and creates new slot on request, if required slot is not available"""
        r = self.api_requests.get_request(constants.FM_VEHICLES_ID.format(vehicle_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        device_slot_available = False
        status = False
        if "deviceSlots" in r.json()['_embedded']:
            for slot in r.json()['_embedded']["deviceSlots"] :
                if(slot["name"]==slot_name and device_type == slot["deviceType"]) :
                    logging.info("Device Slot Already Exists")
                    device_slot_available = True
                elif (slot["name"]==slot_name and device_type != slot["deviceType"]) :
                    logging.info(f"Device slot type mismatch, Deleting the Device slot of type: {slot['deviceType']}")  
                    self.delete_device_slot_from_vehicle(vehicle_id, slot_name)
        if create_new_slot and not device_slot_available:
            self.create_device_slot_for_vehicle(vehicle_id, slot_name, device_type)
            status = True
        elif device_slot_available:
            logging.info("New slot is not created")
            status = True
        else :
            logging.info("Device slot is not available, User has not requested to create new slot")
        return status
    
    def map_device_to_vehicle_device_slot(self, vehicle_id, slot_name, device_id):
        """Maps the Device to the Specified device slot and Returns the status of mapping"""
        device_mapped_to_slot = False
        r = self.api_requests.get_request(constants.FM_VEHICLES_ID.format(vehicle_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        if "deviceSlots" in r.json()['_embedded']:
            for slot in r.json()['_embedded']["deviceSlots"] :
                if slot["name"] == slot_name :
                    if("deviceId" in slot and slot["deviceId"] == device_id):
                        logging.info("Device is rightly mapped to Slot")
                        device_mapped_to_slot = True
                        break
                    elif("deviceId" in slot and slot["deviceId"] != device_id):
                        logging.info("A different Device is mapped to the Slot, Unmaping fromt the slot")
                        etag = self.api_requests.get_etag(constants.FM_VEHICLES_ID.format(vehicle_id))
                        r = self.api_requests.delete_request(constants.FM_VEHICLES_DEVICE_SLOT_NAME_ID.format(vehicle_id,slot_name,slot["deviceId"] ),{'if-match': etag})
                        assert r.status_code == requests.codes.no_content, "Unable to Unmap Different Mapped device from Device slot of requested vehicle"
                    etag = self.api_requests.get_etag(constants.FM_VEHICLES_ID.format(vehicle_id))
                    data = {'deviceId': device_id}
                    r = self.api_requests.put_request(ep=constants.FM_VEHICLES_DEVICE_SLOT_NAME.format(vehicle_id,slot_name),params=data,
                            custom_header={'if-match': etag})
                    assert r.status_code == requests.codes.no_content,self.api_gen_obj.assert_message(r)
                    device_mapped_to_slot = True
                    logging.info(f"Device {device_id} is mapped to vehicle with id: {vehicle_id}")
                    break
        assert device_mapped_to_slot == True, "Failed to Map device to Vehicles device slot, check Device slot or Device availablity for Vehicle"

    def delete_device_slot_from_vehicle(self, vehicle_id, slot_name):
        r = self.api_requests.get_request(constants.FM_VEHICLES_ID.format(vehicle_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        if "deviceSlots" in r.json()['_embedded']:
            for slot in r.json()['_embedded']["deviceSlots"] :
                if slot["name"] == slot_name and "deviceId" in slot:
                    logging.info("Device is mapped Slot, unmapping it before deleting the slot")
                    etag = self.api_requests.get_etag(constants.FM_VEHICLES_ID.format(vehicle_id))
                    r = self.api_requests.delete_request(constants.FM_VEHICLES_DEVICE_SLOT_NAME_ID.format(vehicle_id,slot_name,slot["deviceId"] ),{'if-match': etag})
                    assert r.status_code == requests.codes.no_content, "Unable to Unmap Different Mapped device from Device slot of requested vehicle"
        etag = self.api_requests.get_etag(constants.FM_VEHICLES_ID.format(vehicle_id))
        r = self.api_requests.delete_request(constants.FM_VEHICLES_DEVICE_SLOT_NAME.format(vehicle_id,slot_name),{'if-match': etag})
        assert r.status_code == requests.codes.no_content, self.api_gen_obj.assert_message(r)

    def create_device_slot_for_vehicle(self, vehicle_id, slot_name, device_type):
        etag = self.api_requests.get_etag(constants.FM_VEHICLES_ID.format(vehicle_id))
        data = {
            'deviceType': device_type,
            'name': slot_name   
        }
        r = self.api_requests.post_request(constants.FM_VEHICLES_DEVICE_SLOT.format(vehicle_id), data, {'if-match': etag})
        assert r.status_code == requests.codes.created, "Unable to Create Device slot for vehicle with ID: " +vehicle_id + " and Slot Name: " + slot_name + " and Type: " + device_type
       
    def check_device_mapping_status(self, device_id, vehicle_id):
        unmapped_from_slot = None
        slot_name = None
        assigned_vehicle_id = self.get_paired_vehicle(device_id)
        if assigned_vehicle_id not in (None,vehicle_id):
            self.unmap_device_from_vehicle(device_id)
            unmapped_from_slot = True
        elif assigned_vehicle_id is None:
            logging.info("Device is not paired to any Vehicle")
            unmapped_from_slot = True
        else:
            r = self.api_requests.get_request(constants.FM_VEHICLES_ID.format(vehicle_id))
            assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
            if "deviceSlots" in r.json()['_embedded']:
                for slot in r.json()['_embedded']["deviceSlots"] :
                    if "deviceId" in slot and slot["deviceId"] == device_id: 
                        slot_name = slot['name']
                        logging.info(f"Device is mapped to expected Vehicle on Device Slot: {slot_name}")
                        unmapped_from_slot = False
                        break
        return unmapped_from_slot, slot_name

    def map_already_mapped_device_to_vehicle(self, vehicle_id, slot_name, device_id):
        """Maps the Device to the Specified device slot and Returns the status of mapping"""
        etag = self.api_requests.get_etag(constants.FM_VEHICLES_ID.format(vehicle_id))
        data = {'deviceId': device_id}
        r = self.api_requests.put_request(ep=constants.FM_VEHICLES_DEVICE_SLOT_NAME.format(vehicle_id,slot_name),params=data,
                    custom_header={'if-match': etag})
        assert r.status_code == requests.codes.precondition_failed ,self.api_gen_obj.assert_message(r)
        
    def calculate_gsm_duration(self, gsm_timer, count_timer):
        gsm_timer_off = gsm_timer.get("OFFLINE")
        gsm_timer_on  = gsm_timer.get("ONLINE")
        gsm_timer_duration = abs(gsm_timer_off - gsm_timer_on) 
        count_timer = count_timer*60
        total_duration_gsm = (gsm_timer_duration + count_timer)*1000 
        return total_duration_gsm

    def create_vsg(self, vsg_name):
        data = {
                    'name': vsg_name,
                    'description': 'automated-test group'          
                }
        r = self.api_requests.post_request(ep=constants.FM_VSG, params=data)
        assert r.status_code == requests.codes.created ,self.api_gen_obj.assert_message(r)

    def edit_vsg(self, vsg_name):
        data = {
                    'name': vsg_name,
                    'description': 'automated-test group- edited'          
                }
        vsg_id = self.get_vsg_id_from_vsg_name(vsg_name)
        r = self.api_requests.put_request(ep=constants.FM_VSG_ID.format(vsg_id), params=data)
        assert r.status_code == requests.codes.no_content ,self.api_gen_obj.assert_message(r)

    def delete_vsg(self, vsg_id):
        etag = self.api_requests.get_etag(constants.FM_VSG_ID.format(vsg_id))
        r = self.api_requests.delete_request(ep=constants.FM_VSG_ID.format(vsg_id),
                                                     custom_header = {'if-match': etag})
        assert r.status_code == requests.codes.no_content ,self.api_gen_obj.assert_message(r)

    def get_slot_for_vsg(self, vsg_id, slot_name, device_type, create_slot = True):
        slot_available = False
        r = self.api_requests.get_request(constants.FM_VSG_ID.format(vsg_id))
        assert r.status_code == requests.codes.ok ,self.api_gen_obj.assert_message(r)
        if '_embedded' in r.json()and "deviceSlots" in r.json()['_embedded']:
            for slot in r.json()['_embedded']["deviceSlots"] :
                if slot["name"] == slot_name:
                    if(slot["deviceType"]!=device_type):
                        self.delete_device_slot_from_vsg(vsg_id, slot_name)
                    else:
                        slot_available = True
        if(create_slot == True and slot_available == False):
            logging.info("Device Slot is not Available for VSG, creating new Device slot")
            self.create_device_slot_for_vsg(vsg_id,slot_name, device_type)
            slot_available = True
        return slot_available

    def add_vehicle_to_vsg(self, vehicle_id, vsg_id):
        etag = self.api_requests.get_etag(constants.FM_VSG_ID.format(vsg_id))
        data = {
            'vehicleId': vehicle_id
        }
        r = self.api_requests.post_request(constants.FM_VSG_ID_ASSIGNEDVEHICLE.format(vsg_id), data, {'if-match': etag})
        assert r.status_code == requests.codes.created, "Unable to Add Vehicle to Vehicle Setup Group"

    def remove_vehicle_from_vsg(self, vsg_id, vehicle_id):
        vehicle_ids = []
        if(vehicle_id.upper() == "ALL"):
            vehicle_ids = self.get_vehicles_from_vsg(vsg_id)
        else:
            vehicle_ids.append(vehicle_id)
        
        for vehicle in vehicle_ids:
            etag = self.api_requests.get_etag(constants.FM_VSG_ID.format(vsg_id))
            r = self.api_requests.delete_request(constants.FM_VSG_ID_ASSIGNEDVEHICLE_NAME.format(vsg_id,vehicle), {'if-match': etag})

            assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
    
    def get_vehicles_from_vsg(self, vsg_id):
        vehicle_ids = []
        r = self.api_requests.get_request(constants.FM_VSG_ID_ASSIGNEDVEHICLE.format(vsg_id))
        if "_embedded" in r.json() and ("vehicles" in r.json()["_embedded"]):
           for vehicle in r.json()["_embedded"]["vehicles"]:
                vehicle_ids.append(vehicle['vehicleId'])
        else:
            logging.info(f"No Vehicles are to on Vehicle setup group with ID: , {vsg_id}")
        return vehicle_ids

    def get_vsg_by_name(self, vsg_name):
        """Returns the single vehicle JSON object specified by the name"""
        r = self.api_requests.get_request(constants.FM_VSG_SEARCH_NAME.format(vsg_name))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        if r.json()['page']['totalElements'] == 0:
            self.create_vsg(vsg_name)
            r = self.api_requests.get_request(constants.FM_VSG_SEARCH_NAME.format(vsg_name))
            assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        res = r.json()['_embedded']['vehicleSetupGroups']
        for v in res:
            if v['name'] == vsg_name:
                logging.info(f"vsg id ={v['vehicleSetupGroupId']}")
                return v
        assert False, "Unable to Find the Vehicle Setup-group"

    def get_vsg_id_from_vsg_name(self, vehicle_name):
        vsg_data = self.get_vsg_by_name(vehicle_name)
        return vsg_data['vehicleSetupGroupId']


    def delete_device_slot_from_vsg(self, vsg_id, slot_name):
        etag = self.api_requests.get_etag(constants.FM_VSG_ID.format(vsg_id))
        r = self.api_requests.delete_request(constants.FM_VSG_ID_DEVICE_SLOT_NAME.format(vsg_id,slot_name), {'if-match': etag})
        assert r.status_code == requests.codes.no_content, self.api_gen_obj.assert_message(r)

    def create_device_slot_for_vsg(self, vsg_id, slot_name, device_type):
        etag = self.api_requests.get_etag(constants.FM_VSG_ID.format(vsg_id))
        data = {
            'deviceType': device_type,
            'name': slot_name   
        }
        r = self.api_requests.post_request(constants.FM_VSG_ID_DEVICE_SLOT.format(vsg_id), data, {'if-match': etag})
        assert r.status_code == requests.codes.created, "Unable to Create Device slot for vehicle setup group with ID: " +vsg_id + " and Slot Name: " + slot_name + " and Type: " + device_type

    def verify_vsg_prop_on_vehicle(self, vehicle_id, vsg_id, property_name):
        if(property_name.upper() == "DEVICE_SLOTS"):
            res = self.api_requests.get_request(constants.FM_VSG_ID.format(vsg_id))
            if "_embedded" in res.json():
                for deviceslot in res.json()["_embedded"]["deviceSlots"]:
                    slot_available = self.fetch_specific_slot_from_vehicle(vehicle_id,deviceslot["name"],deviceslot['deviceType'], False)
                    assert slot_available == True, "Verification of vsg property in Vehicle is Failed, unable to find Device slot with name:" + deviceslot["name"] + "on vehicle" + vehicle_id
            else:
                 assert False, "Device slots are not available in vsg with ID:" + vsg_id
        else:
            assert False, "Invalid property to verify in VSG, property name: " + property_name
    
    def get_paired_vehicle(self, device_id):
        paired_vehicle_id = None
        r = self.get_device_properties(device_id)
        if(r.json()['paired'] == True):
             paired_vehicle_id = r.json()['vehicleId']
        return paired_vehicle_id
    
    def get_device_slot_by_type(self,vehicle_id, default_slot_name, device_type):
        new_slot_name = None
        r = self.api_requests.get_request(constants.FM_VEHICLES_ID.format(vehicle_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        if "deviceSlots" in r.json()['_embedded']:
            for slot in r.json()['_embedded']["deviceSlots"] :
                if(device_type == slot["deviceType"]) :
                    logging.info(f"Slot is already available on Vehicle with type: {device_type}")
                    new_slot_name = slot["name"]
                    break
        if new_slot_name is None:
            self.fetch_specific_slot_from_vehicle(vehicle_id, default_slot_name, device_type)
            new_slot_name = default_slot_name
        return new_slot_name
    
    def verify_vin_changes(self, device_id, expected_vin):
        for count in range (1, 20):
            # TODO: remove for loop,when VIN changes reflected in the backend immediately without any delay.
            detected_vin = self.get_detected_vin(device_id)
            if(expected_vin == detected_vin):
                logging.debug(f'Implanted VIN is reflected in the backend as expected')
                break
            else:
                time.sleep(3)
                logging.debug(f'VIN of device is not reflected in backend, retrying after 3 seconds. Retry count = {count}')
        time.sleep(3) #Additional 3 seconds are added as backend takes 1-3 seconds to create vehicle and map it to the device.
        return detected_vin

    def remove_unwanted_vehicles_from_vsg(self, vsg_id, vehicles, actual_vehicle_id_list, context):
        expected_vehicle_id_list = []
        updated_vehicle_id_list = []
        for vehicle_name in vehicles:
            expected_vehicle_id_list.append(self.get_vehicle_id_by_name(vehicle_name, context))
        for vehicle_id in actual_vehicle_id_list:
            if vehicle_id in expected_vehicle_id_list:
                updated_vehicle_id_list.append(vehicle_id)
            else:
                self.remove_vehicle_from_vsg(vsg_id, vehicle_id)
        return updated_vehicle_id_list

    def get_geopositioning_status(self, vehicle_name, context):
        vehicle_id = self.get_vehicle_id_by_name(vehicle_name, context)
        r = self.api_requests.get_request(constants.FM_VEHICLES_ID.format(vehicle_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r.json()["geoPositioning"]

    def verify_ids_log(self,log_download_path):
        result = False
        result_string = ""

        files = self.api_gen_obj.get_file_name(log_download_path,  "IDSReport.dat")

        for file_path in files:
            with open(file_path, "r") as fp:
                result_string = fp.read()
                if constants.FM_IDS_REPORT_RESULT in result_string:
                    result = True
        
        shutil.rmtree(log_download_path)

        return result, result_string
    
    def validate_log_with_count(self, log_count, log_entry_ids, device_id, device_log_old_count, api_gen_obj):
        time.sleep(180*int(log_count))
        api_gen_obj.start_timer()
        while (api_gen_obj.check_timer() == True):
            device_log_new_details = self.get_device_log_entries(device_id)
            device_log_new_count = device_log_new_details.json()["page"]["totalElements"]
            diff_count = int(device_log_new_count - device_log_old_count)
            if (int(diff_count) >= int(log_count)):
                for index in range(0, int(diff_count)):
                    log_entry_id = device_log_new_details.json()["_embedded"]["logEntries"][index]["logEntryId"]
                    logging.info(f"logEntryId - {log_entry_id}")
                    log_file_size = device_log_new_details.json()["_embedded"]["logEntries"][index]["fileSize"]
                    log_entry_ids[log_entry_id] = log_file_size
                assert int(len(log_entry_ids)) == int(log_count), "Log entries generated and log count mismatch. Exp count - %s, Actual Count - %s"%(int(log_count),int(diff_count))
                # context.log_time_stamp=device_log_new_details.json()["_embedded"]["logEntries"][0]["timestamp"].replace('T',',')
                api_gen_obj.stop_timer()
                break
            time.sleep(30)
        return log_entry_ids
