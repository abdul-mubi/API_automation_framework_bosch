from src.common.fileutils import FileUtil
from src.resources.proto_py.inventory import inventory_report_event_pb2
from src.common import constants
from src.common.logger import get_logger
from src.common.pb_operation import PbOperation as pb_operation_class
log = get_logger()
file_util = FileUtil()
pb_op = pb_operation_class()

class InventoryOperation:
    
    def get_inventory_data(self, device_id, assignment_id = None):
        """
            Prepares inventory report of the device, if inventory report is already available it will use the same,
            else it will create inventory report from default report. 
            And if assignment id is provided the inventory report will be updated as per assignment if required.

        Args:
            device_id (String): ID of the device
            assignment_id (ota_assignment_id, optional): Assignment ID of the ota assignment. Defaults to None.

        Returns:
            InventoryReportEvent: InventoryReportEvent object that contains updated inventory for the device
        """
        inventory_obj = inventory_report_event_pb2.InventoryReportEvent()
        if not file_util.check_file_availability(constants.DEVICE_INVENTORY_PATH.format(device_id=device_id)):
            file_util.copy_file(constants.DEFAULT_INVENTORY,constants.DEVICE_INVENTORY_PATH.format(device_id=device_id))
        if(assignment_id != None):
            self.update_inventory_data(device_id,assignment_id)
        inventory_json_data = file_util.parse_json_file(constants.DEVICE_INVENTORY_PATH.format(device_id=device_id))
        inventory_obj = pb_op.decrypt_input_message(inventory_obj, inventory_json_data, "JSON")
        return inventory_obj
    
    
    def update_inventory_data(self, device_id, assignment_id):
        """
            Updates the inventory data as per assignment ID and stores the info to the device inventory file

        Args:
            device_id (String): ID of the device
            assignment_id (ota_assignment_id): Assignment ID of the ota assignment
        """
        try:
            if file_util.check_file_availability(constants.OTA_ASSIGNMENT_JSON_PATH.format(device_id=device_id, assignment_id=assignment_id)):
                log.info("Detected inventory change after Device Update")
                log.debug("Updating Inventory file as per the update data json file")
                new_inventory_data = file_util.parse_json_file(constants.OTA_ASSIGNMENT_JSON_PATH.format(device_id=device_id, assignment_id=assignment_id))
                self.__update_inventory_json(device_id, new_inventory_data)
                file_util.delete_file(constants.OTA_ASSIGNMENT_JSON_PATH.format(device_id=device_id, assignment_id=assignment_id))
            else:
                log.info("Inventory Changes are not detected after update")
        except Exception as e:
            log.error("Failed to parse inventory JSON file")
            log.debug(e)
    
    def __update_inventory_json(self, device_id, inventory_data):
        """
            Updates inventory JSON as per assignment Data and returns latest inventory object

        Args:
            device_id (String): ID of the device
            inventory_data (JSON): Inventory change details about the assignment
        """
        
        def update_json_array(device_inventory,new_inventory_data, data_type):
            for new_data in new_inventory_data[data_type]:
                for node_data in device_inventory[data_type]:
                    if(node_data['id'] == new_data['id']):
                        node_data['version'] = new_data['version']
                        log.debug(f"Node_data Update success for node {node_data['id']}")
                        break
            return device_inventory
            
        device_inventory = file_util.parse_json_file(constants.DEVICE_INVENTORY_PATH.format(device_id=device_id))
        
        for node in inventory_data:
            log.debug(f"Updating {node} inventory")
            device_inventory = update_json_array(device_inventory, inventory_data, node)
        log.debug(f"Updated inventory: {device_inventory}")
        file_util.write_json_file(constants.DEVICE_INVENTORY_PATH.format(device_id=device_id),device_inventory)