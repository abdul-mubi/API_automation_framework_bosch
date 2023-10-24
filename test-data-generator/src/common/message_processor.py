
from src.bfb_operation import VehicleData, DeviceVehicleMapping, DeviceManagement, Inventory, SoftwareUpdate, FunctionCalls
from src.common.logger import get_logger
from src.common import constants
log = get_logger()

class MessageProcessor():
    """
        This class process all incoming messages received from Mobility cloud side. 
        And Prepares the outgoing messages to the MC side
    
    """
    def __init__(self, device_id,device_cert_path, device_key_path, vin, csv_path, proxy):
        self.vehicle_data = VehicleData(device_id, vin, csv_path,proxy)
        self.device_management = DeviceManagement(device_cert_path, csv_path)
        self.device_vehicle_mapping = DeviceVehicleMapping()
        self.inventory_report = Inventory(device_id,vin)
        self.ota_update = SoftwareUpdate(device_id, device_key_path, proxy)
        self.function_call = FunctionCalls(device_id)
    
    def process_incoming_message(self, topic_name, message):
        """
        Processes incoming message based on the topic name

        Args:
            topic_name (String): name of the topic, where the message is received
            message (serialized_message): Serialized protobuf message received from MC side

        Returns:
            dictionary: Returns the dictionary that contains topic name and the serialized message to be published to the MC side
                        In case there is no data to publish, empty dictionary is returned
        """
        
        message_data = {}
        try:
            if(topic_name=='activateMeasurement'):
                publish_message = self.vehicle_data.activate_remote_measurement(message)
                message_data[constants.MEASUREMENT_STATUS_TOPIC] = publish_message
            elif(topic_name== 'deactivateMeasurement'):
                publish_message = self.vehicle_data.deactivate_remote_measurement(message)
                message_data[constants.MEASUREMENT_STATUS_TOPIC] = publish_message
            elif(topic_name == 'setGpsStatus'):
                self.device_management.set_gps_status(message)
            elif(topic_name == 'update'):
                self.ota_update.assign_ota_update(message)
            elif(topic_name == 'updateMappingStatus'):
                self.device_vehicle_mapping.get_backend_mapping_status(message)
            elif(topic_name == 'callFunction'):
                publish_message = self.function_call.function_call_command(message)
                message_data[constants.FUNCTION_CALL_STATUS_TOPIC] = publish_message
            else: 
                log.error("Please write fn to decode the protobuf message")
        except Exception as e:
            log.error(f"Exception occurred while processing received protobuf: {e}")
        return message_data
    
    def prepare_outgoing_messages(self, message_type, **kwargs): 
        """
        Prepares the messages which should be sent to MC side from the Test data generator
         Args:
            message_type (String): Type of the message to be generated, None in case of all messages
            kwargs (known arguments):       Optional known arguments
                                            vin - for vin VIN data
                                            duration - GPS measurement duration
                                            geo_data - GEO data calculated as per requirement
        Returns:
            dictionary: Returns the dictionary that contains topic name as key and list of serialized message to be published to the MC side
                        In case there is no data to publish, empty dictionary is returned
        """
        message_data = {}
        
        try:
            if(message_type.upper() == "GPS"):
                self.__add_value_to_message_data(message_data,constants.GPS_REPORT_TOPIC,self.device_management.report_gps_position(kwargs['geo_data']))
            elif(message_type.upper() == "VIN"):
                self.__add_value_to_message_data(message_data,constants.VIN_UPDATE_TOPIC,self.device_vehicle_mapping.update_vin(kwargs['vin']))
            elif(message_type.upper() == "MEASUREMENT"):
                self.__add_value_to_message_data(message_data,constants.MEASUREMENT_RESULT_TOPIC,self.vehicle_data.generate_result(**kwargs))
            elif(message_type.upper() == "INVENTORY"):
                self.__add_value_to_message_data(message_data,constants.INVENTORY_REPORT_TOPIC,self.inventory_report.request_inventory_report())
            elif(message_type.upper() == "OTA_UPDATE"):
                result_data, completed_list = self.ota_update.prepare_update_status()
                self.__add_value_to_message_data(message_data,constants.UPDATE_STATUS_TOPIC, result_data)
                if(len(completed_list)>0):
                    for assignment_id in completed_list:
                        self.__add_value_to_message_data(message_data,constants.INVENTORY_REPORT_TOPIC,self.inventory_report.request_inventory_report(assignment_id))
            elif(message_type.upper() == "CERTIFICATE_REPORT"):
                self.__add_value_to_message_data(message_data, constants.CERTIFICATE_REPORT_TOPIC, self.device_management.report_certificate())
        except Exception as e:
            log.error(f"Exception occurred while preparing protobuf: {e}")
        return message_data
    
    def __add_value_to_message_data(self, message_data, topic, message):
        """This method will update message_data dictionary with new messages

        Args:
            message_data (dictionary): message data dictionary
            topic (string): name of the topic
            message (serialized_protobuf): Serialized protobuf message in byte format

        Returns:
            _type_: _description_
        """
        if topic not in message_data.keys():
            message_data[topic] = []
        if message != None:
            if isinstance(message, list):
                message_data[topic].extend(message)
            else:
                message_data[topic].append(message)
        return message_data