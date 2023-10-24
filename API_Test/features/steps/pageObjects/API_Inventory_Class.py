import requests
import logging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from prettytable import PrettyTable
import steps.utils.API_Requests as API_Request
import steps.pageObjects.API_Generic_Class as API_Generic_Class
import steps.constantfiles.constants_inventory as constants


class ApiInventoryClass:

    def __init__(self, enviroment, log_api_details):
        self.api_request = API_Request.ApiRequestsClass(enviroment, log_api_details)
        self.api_gen_obj = API_Generic_Class.ApiGenericClass()

    def get_firmware_version_of_device(self, device_id):
        r = self.api_request.get_request(constants.INV_DEVICES_ID.format(device_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        inventory_list = r.json()['_embedded']['inventoryItemList']
        for entries in inventory_list:
            if entries['nodeId']=='Device SW' and entries['type']=='SOFTWARE':
                version = entries['swVersion']
        logging.info(f'Firmware version of the device is {version} in inventory')
        return version

    def get_device_raw_inventory(self, device_id):
        r = self.api_request.get_request(constants.INV_DEVICES_ID_RAW.format(device_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r.json()
    
    def get_device_inventory(self, device_id):
        r = self.api_request.get_request(constants.INV_DEVICES_ID.format(device_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r.json()

    def get_inventory_changes(self, device_id):
        r = self.api_request.get_request(constants.INV_DEVICES_ID_CHANGES.format(device_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r.json()['_embedded']['inventoryChangeTimestampList']

    def get_device_assignments(self, device_id):
        r = self.api_request.get_request(constants.INV_DEVICES_ID_ASSIGNMENTS.format(device_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r.json()['_embedded']['assignments']
        
    def get_inventory_timestamp(self, device_id):
        r = self.api_request.get_request(constants.INV_DEVICES_ID_TIMESTAMPS.format(device_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        timestamp = r.json()['_embedded']['inventoryTimestampList'][0]['timestamp']
        res = self.api_request.get_request(constants.INV_DEVICES_ID_SNAPSHOT.format(device_id,timestamp))
        assert res.status_code == requests.codes.ok, self.api_gen_obj.assert_message(res)
        return  res.json()['_embedded']['inventoryItemList']

    def get_vehicle_inventory(self, device_id ,invt_type):
        r = self.api_request.get_request(constants.INV_DEVICES_ID_TYPE.format(device_id,invt_type))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r.json()['_embedded']['inventoryItemList']

    def validate_inventory_data(self, expected_inv_data, inv_type, device_id):
        id_dict  = {"SOFTWARE":"swUid", "HARDWARE": "hwUid"}
        unmatched_table = PrettyTable()
        unmatched_table.field_names = ["Entries","key","Expected_Value","Actual_Value"]
        match_status = True
        actual_inv_data = self.get_vehicle_inventory(device_id, inv_type)
        for each_exp_element in expected_inv_data:
            for each_key in each_exp_element.keys():
                for each_act_element in actual_inv_data:
                    if (each_exp_element[id_dict[inv_type]] == each_act_element[id_dict[inv_type]]) and each_act_element[each_key] != each_exp_element[each_key]:
                            match_status = False
                            unmatched_table.add_row([each_exp_element[id_dict[inv_type]],each_key,each_exp_element[each_key], each_act_element[each_key]])
        if match_status == False:
            logging.info("unmatched values found while performing inventory validation")
            logging.info(unmatched_table)
        return match_status

    def compare_devices_with_matching_version(self, device_list, fw_version, version_to_skip = None):
        """Compares the the device list and splits into two list, 
        if devices has matching version as fw_version it would be added to matched_devices list
        else devices will be added to unmatched_devices list

        Args:
            device_list (list): all device ids
            fw_version (str): FW version for segregation of devices
            version_to_skip (str, optional): In case if devices on specific version need to be skipped from check. Defaults to None.

        Returns:
            list, list: devices with matched version and unmatched version
        """

        matched_devices = []
        unmatched_devices = []
    
        for device in device_list:
            version = self.get_firmware_version_of_device(device)
            logging.info(f"Current version of {device} is {version}")
            if version_to_skip != None and version_to_skip in version:
                logging.info(f"Skipping device  {device} with version {version} from list")
            elif version == fw_version:
                matched_devices.append(device)
            else:
                unmatched_devices.append(device)
        
        return matched_devices, unmatched_devices