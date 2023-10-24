from ast import arguments
import time
import uuid
import pandas
import requests
from src.common.pb_operation import PbOperation
from src.common.fileutils import FileUtil
from src.common.cloud_store import CloudStoreOperation
from src.measurement_operation import MeasurementOperation, RMProtoOperations
from src.dm_operations import DMOperation
from src.inventory_operation import InventoryOperation
from src.resources.proto_py import device_to_backend_message_meta_pb2
from src.resources.proto_py.vehicleData import activate_measurement_command_pb2, deactivate_measurement_command_pb2, measurement_result_event_pb2, measurement_status_event_pb2
from src.resources.proto_py.deviceVehicleMapping import vin_update_event_pb2, update_mapping_status_command_pb2
from src.resources.proto_py.softwareUpdate import update_status_event_pb2, ota_status_pb2, update_command_pb2
from src.resources.proto_py.deviceManagement import set_gps_status_command_pb2, gps_position_report_event_pb2, certificate_report_event_pb2
from src.resources.proto_py.inventory import inventory_report_event_pb2
from src.resources.proto_py.functionCalls import call_function_command_pb2, function_call_status_event_pb2
from src.common import constants
from src.common.logger import get_logger
log = get_logger()

pb_operation = PbOperation()
fileutil = FileUtil()
cloud_store = CloudStoreOperation()

def update_device_to_backend_meta(proto_obj, activity_id, sequence_counter = 0):
    """Generates the meta object for the device to backend message 

    Args:
        proto_obj (message_obj): Message protobuf object
        activity_id (String): Activity ID
        sequence_counter (int, optional): Device Sequence counter. Defaults to 0.

    Returns:
       proto_obj (message_obj): Message protobuf object with meta 
    """
    meta = device_to_backend_message_meta_pb2.DeviceToBackendMessageMeta()
    meta.activityId = activity_id
    meta.timestamp = round(time.time()*1000)
    meta.deviceSequenceCounter = sequence_counter
    proto_obj.meta.CopyFrom(meta)
    return proto_obj

class VehicleData:
    """
    All required functions under VehicleData (Remote Measurement) are inside this class.
    Supported Version of VehicleData - v1
    Methods in this class can process and generate serialized protobuf messages under vehicleData module
    
    """
    def __init__(self,device_id, vin, csv_path, proxy):
        self.device_sequence_counter = 1
        self.rm_op = MeasurementOperation(device_id, vin)
        self.vin = vin
        self.device_id = device_id
        self.test_step_data = {}
        self.rm_folder_path = constants.RM_FOLDER_PATH.format(device_id = device_id)
        self.zip_path = constants.RM_ZIP_PATH.format(device_id = device_id)
        self.rm_proto_op = RMProtoOperations(csv_path)
        self.measurement_completed_list = []
        self.proxy = proxy

    def activate_remote_measurement(self, input_message):
        """ Method to process the Remote measurement activation method
            Extracts and stores the measurement configuration in temp/RM_Config folder
        Args:
            input_message ([serialized protobuf/ JSON]): Payload received from activateMeasurement topic

        Returns:
            [serialized protobuf message]: Returns activation response which can then be published to measurementStatus topic
        """
        log.info("Received RM Activation command")
        rm_act_obj = activate_measurement_command_pb2.ActivateMeasurementCommand()
        pb_operation.decrypt_input_message(rm_act_obj, input_message)
        log.debug(f"RM ACTIVATION Request: {rm_act_obj}")
        encoded_config = rm_act_obj.measurementConfiguration
        try:
            fileutil.decrypt_base64_to_zip(self.zip_path,encoded_config)
            activation_response = self.prepare_rm_job_status(rm_act_obj.meta.activityId)
            self.rm_job_id = self.rm_op.process_job(self.zip_path)
            log.info(f"RM Activation Process is completed for Measurement config Id: {self.rm_job_id}")
        except Exception as e:
            log.error(f"Unable to process/decrypt measurement Job: {e}")
            activation_response = self.prepare_rm_job_status(rm_act_obj.meta.activityId, False)
        log.debug(activation_response.SerializeToString())
        return pb_operation.generate_output_message(activation_response)
    
    def deactivate_remote_measurement(self, input_message):
        """ Method to process the Remote measurement deactivation
            Deletes the RM configuration from the test data generator.
            which is located at temp/RM_Config folder
        Args:
            input_message ([serialized protobuf/ JSON]): Payload received from deactivateMeasurement topic

        Returns:
            [serialized protobuf message]: Returns deactivation response which can then be published to measurementStatus topic
        """
        log.info("Received RM Deactivation command")
        rm_deact_obj = deactivate_measurement_command_pb2.DeactivateMeasurementCommand()
        pb_operation.decrypt_input_message(rm_deact_obj, input_message)
        self.rm_op.delete_job(rm_deact_obj.measurementIdentifier)
        log.debug(f"RM DE-ACTIVATION Request: {rm_deact_obj}")
        if(rm_deact_obj.measurementIdentifier in self.measurement_completed_list):
            self.measurement_completed_list.remove(rm_deact_obj.measurementIdentifier)
        deactivation_response = self.prepare_rm_job_status(rm_deact_obj.meta.activityId)
        log.debug(deactivation_response.SerializeToString())
        log.info("RM Deactivation Processing is completed")
        return pb_operation.generate_output_message(deactivation_response)
    
    def __generate_rm_result(self,measurement_id, job_version, rm_result_encoded,device_id,zip_name):
        """Generated measurement result protobuf by using the encoded result

        Args:
            measurement_id ([string]):measurement configuration id
            job_version ([string]): version of rm configuration
            execution_start_time ([unix_time_ms]): Start time of encoded measurement result
            execution_end_time ([unix_time_ms]): End time of the encoded measurement result
            rm_result_encoded ([b64_encoded_zip]): base64 encoded measurement result
            is_last (bool_in_string_format): flag to set if the result is last value of ongoing measurement
            proxy_address: proxy_address as per user 

        Returns:
            [protobuf message]: protobuf message in the proto object format
        """
        
        rm_result = measurement_result_event_pb2.MeasurementResultEvent()
        rm_result.serialization = "base64"
        log.info(f"Generated RM result size in KBs - {len(rm_result_encoded)}")
        if len(rm_result_encoded) >= constants.MEASUREMENT_RESULT_FILE_SIZE_IN_KBS:
            content_id = cloud_store.upload_file_to_cloudstore(device_id,zip_name,self.proxy)
            rm_result.artifactUri = f"{constants.DOWNLOAD_BLOB_URL}/{content_id}"
        else:
            rm_result.measurementResult = rm_result_encoded
        rm_result.stackType = "AA" 
        rm_result.executionStart = self.rm_op.convert_unix_time(self.test_step_data[measurement_id]['start_time'])
        rm_result.executionEnd = self.rm_op.convert_unix_time(self.test_step_data[measurement_id]['end_time'])
        rm_result.measurementId = measurement_id
        rm_result.jobVersion = job_version
        rm_result.vin = self.vin
        rm_result.isLast = str(self.test_step_data[measurement_id]['is_last']).lower()
        update_device_to_backend_meta(rm_result, self.test_step_data[measurement_id]['uuid'], self.test_step_data[measurement_id]['sequence_counter'])
        return rm_result
    
    def prepare_rm_job_status(self, activity_id, success = True):
        """Prepares measurement activity status response based on the state
        
        Args:
            activity_id ([uuid]): Activity ID of the measurementActivation/ measurementDeactivation command
            success (bool, optional): [description]. Defaults to True - Activation success if false, activation is failed
            
        Returns:
            [protobuf message]: Protobuf message with measurement status
        """
        measurement_status = measurement_status_event_pb2.MeasurementStatusEvent()
        if(success):
            measurement_status.status = measurement_status_event_pb2.status__pb2.EXECUTED
        else:
            measurement_status.status = measurement_status_event_pb2.status__pb2.FAILED
            measurement_status.errorCode = "1"
            measurement_status.errorMessage = "FAILED to Parse the Job on Test Data Generator"
        update_device_to_backend_meta(measurement_status,activity_id)
        log.debug(measurement_status)
        return measurement_status


    def __prepare_rm_teststep_details(self, measurement_config, duration):
        """Generates the test step details as per input data

        Args:
            measurement_config (Dictionary): Information about measurement
            duration (int, optional): Measurement result duration. Defaults to constants.MEASUREMENT_RESULT_DURATION_SEC.
        """
        job_id = measurement_config['job_id']
        duration_ms = duration * 1000
        sequence_counter = 0
        upload_interval_ms = int(measurement_config['upload_interval_sec']) * 1000
        if  job_id not in self.test_step_data.keys():
            start_time_ms = round(time.time()*1000)
            if upload_interval_ms > duration_ms :
                end_time_ms = start_time_ms + duration_ms
            else:   
                end_time_ms = start_time_ms + upload_interval_ms
            self.test_step_data[job_id] = {
                                                "uuid": str(uuid.uuid4()),
                                                "initial_start_time": start_time_ms,
                                                "start_time": start_time_ms,
                                                "end_time" : end_time_ms,
                                                "sequence_counter": sequence_counter,
                                                "is_last": False
                                            }
        else:
            start_time_ms = self.test_step_data[job_id]['end_time']
            if(start_time_ms + upload_interval_ms) > (self.test_step_data[job_id]['initial_start_time'] + duration_ms) :
                end_time_ms = (self.test_step_data[job_id]['initial_start_time'] + duration_ms)
            else:
                end_time_ms = start_time_ms + upload_interval_ms
            sequence_counter = self.test_step_data[job_id]['sequence_counter'] + 1
            self.test_step_data[job_id].update({
                                                "start_time": start_time_ms,
                                                "end_time" : end_time_ms,
                                                "sequence_counter": sequence_counter,
                                            })
        
        if upload_interval_ms == 0 or  (sequence_counter + 1) * measurement_config['upload_interval_sec'] >= duration :
            self.test_step_data[job_id].update({"is_last": True})
            if(constants.CONTINUOUS_REPORTING == False):
                self.measurement_completed_list.append(job_id)
    
    def generate_result(self, **kwargs):
        """Generates measurement result for the measurement configurations available in the temp/RM_Config folder
        Known Args:
            duration - GPS measurement duration
            geo_data - GEO data calculated as per requirement
        
        Returns:
        Either of following params,
            1. result_protobuf: List of Serialized protobuf of measurement result that contain RM result for all configs
            2. None: in case there are no measurement configurations available in the temp/RM_Config folder
        """
        result_protobuf = []
        measurement_jobs = fileutil.fetch_sub_folders(self.rm_folder_path)
        for rm_job in measurement_jobs:
            if(rm_job not in self.measurement_completed_list):
                measurement_config = self.rm_op.get_measurement_config_details(f"{self.rm_folder_path}{rm_job}/cdpJobConfig.xml")
                if("duration" in kwargs and kwargs['duration']!=None and "gps" in measurement_config["job_name"].lower()):
                    log.debug(f"RM Job is related to GPS choosing result duration as {kwargs['duration']}")
                    self.__prepare_rm_teststep_details(measurement_config, kwargs['duration'])
                else:
                    self.__prepare_rm_teststep_details(measurement_config, kwargs['rm_duration'])
                rm_job_id = measurement_config['job_id']
                pb_name = str(self.test_step_data[rm_job_id]['start_time'])
                measurement_pm = self.rm_proto_op.get_measurement_result(measurement_config, self.test_step_data[rm_job_id], **kwargs)
                pb_operation.create_final_protobuf(measurement_pm, constants.PROTOBUF_OUT_FOLDER.format(device_id=self.device_id) + pb_name)
                zip_name = self.rm_op.create_protobuf_zip(pb_name,measurement_config, self.test_step_data[rm_job_id])
                b64_result = fileutil.encrypt_zip_to_base64(zip_name)
                rm_result = self.__generate_rm_result(measurement_config['job_id'], measurement_config['job_version'], b64_result,self.device_id,zip_name)
                if(self.test_step_data[rm_job_id]['is_last']):
                    del self.test_step_data[rm_job_id]
                result_protobuf.append(pb_operation.generate_output_message(rm_result))
        self.rm_op.cleanup_old_result(constants.RAW_RESULT_STORE_TIME_MIN)
        if len(result_protobuf)>0:
            return result_protobuf
        else:
            return None

class DeviceVehicleMapping:
    """
    All required functions under DeviceVehicleMapping (Remote Measurement) to be listed in this class.
    Supported Version of DeviceVehicleMapping - v1
    Methods in this class can process and generate serialized protobuf messages under DeviceVehicleMapping module
    
    """
    def __init__(self):
        self.device_sequence_counter = 1
        self.uuid = str(uuid.uuid4())

    def update_vin(self, vin):
        """Generates VIN Update protobuf message

        Args:
            vin ([String]): 17 Digit Alphanumeric Character/ Empty String in case of Clearing VIN

        Returns:
            [Serialized Protobuf Message]: Serialized protobuf message of VIN Update event
        """
        log.info(f"Preparing VIN Update event for VIN: {vin}")
        vin_update_event = vin_update_event_pb2.VinUpdateEvent()
        vin_update_event.vin = vin
        vin_update_event.vinIsTrusted = True
        update_device_to_backend_meta(vin_update_event, self.uuid, self.device_sequence_counter)
        self.device_sequence_counter += 1
        log.debug(vin_update_event)
        return pb_operation.generate_output_message(vin_update_event)
    
    def get_backend_mapping_status(self, input_message):
        log.info("Received update mapping status command")
        mapping_status_obj = update_mapping_status_command_pb2.UpdateMappingStatusCommand()
        pb_operation.decrypt_input_message(mapping_status_obj, input_message)
        log.debug(f"Device Mapping Status: {mapping_status_obj}")
        log.info(f"Device pairing status at backend: {update_mapping_status_command_pb2.MappingStatusEnum.Name(mapping_status_obj.mappingStatus)}")
        
class DeviceManagement:
    def __init__(self,cert_path, csv_path):
        self.gps_sequence_counter = 1
        self.gps_uuid = str(uuid.uuid4())
        self.cert_uuid = str(uuid.uuid4())
        self.gps_request_state = False
        self.use_default_data = True
        self.dm_op = DMOperation(csv_path)
        self.device_cert = fileutil.read_file_as_binary(cert_path)
    
    def set_gps_status(self, input_message):
        """
            Method to process the Geo positioning activation/ Deactivation message received at setGpsStatus topic
            And sets a local flag, which will be used by report_gps_position method
        Args:
            input_message ([serialized protobuf/ JSON]): Message received from setGpsStatus topic
        """
        gps_status = set_gps_status_command_pb2.SetGpsStatusCommand()
        pb_operation.decrypt_input_message(gps_status,input_message)
        log.debug(f"GPS request from backend after parsing:  {gps_status}")
        log.info(f"Geo positioning status change request from Backend, new state: {gps_status.gpsState}")
        self.gps_request_state = gps_status.gpsState

    def report_gps_position(self, geo_data = None):
        """
            Method generates geo position of the Device and creates a serialized protobuf message of vehicles position

        Args:
            geo_data (String, optional):GEO data which was calculated as per requirement
        Returns:
            Either of following params,
            1. gps_position_report: Serialized protobuf message that can be published to backend in case gps_state is true
            2. None: None will be returned if backend has not requested the geo positioning of the Vehicle linked to device
        """
        if(isinstance(geo_data, pandas.DataFrame) and self.use_default_data):
            log.info("GEO position in Fleet Management will be updated as per defined city data")
            self.dm_op.update_geo_data(geo_data)
            self.use_default_data = False
        gps_position_report = gps_position_report_event_pb2.GpsPositionReportEvent()
        if(self.gps_request_state):
            log.debug("Generating GPS Data for the Device")
            gps_position_report.longitude = self.dm_op.get_geo_details_for_signal("GPSLongitude",self.gps_sequence_counter)
            gps_position_report.latitude = self.dm_op.get_geo_details_for_signal("GPSLatitude",self.gps_sequence_counter)
            gps_position_report.altitude = self.dm_op.get_geo_details_for_signal("GPSAltitude",self.gps_sequence_counter)
            gps_position_report.heading = self.dm_op.get_geo_details_for_signal("GPSHeading",self.gps_sequence_counter,int)
            gps_position_report.speed = self.dm_op.get_geo_details_for_signal("GPSSpeed",self.gps_sequence_counter)
            gps_position_report.accuracy = 5
            gps_position_report.timestamp = round(time.time()*1000)
            update_device_to_backend_meta(gps_position_report,self.gps_uuid,self.gps_sequence_counter)
            log.debug(gps_position_report)
            self.gps_sequence_counter += 1
            return pb_operation.generate_output_message(gps_position_report)
        else:
            return None
    
    def report_certificate(self):
        log.info("Preparing certificate report to backend")
        cert_obj = certificate_report_event_pb2.CertificateReportEvent()
        cert_data = certificate_report_event_pb2.CertificateEntry()
        cert_data.purpose = certificate_report_event_pb2.ARTIFACT_ENCRYPTION
        cert_data.certificate = fileutil.encrypt_base64(self.device_cert)
        cert_obj.certificates.append(cert_data)
        update_device_to_backend_meta(cert_obj,self.cert_uuid)
        log.debug(f"Certificate protobuf: {cert_obj}")
        return pb_operation.generate_output_message(cert_obj)
    

class Inventory:
    def __init__(self, device_id, vin):
        self.uuid = str(uuid.uuid4())
        self.device_sequence_counter = 1
        self.device_id = device_id
        self.vin = vin
        self.inventory_op = InventoryOperation()


    def request_inventory_report(self, ota_assignment_id = None):
        """Generates Inventory Report protobuf message

        Args:
            ota_assignment_id : Incase inventory update required as part of OTA Update. Default: None
        Returns:
            [Serialized Protobuf Message]: Serialized protobuf message of InventoryReport event
        """
        inventory_obj = self.inventory_op.get_inventory_data(self.device_id, ota_assignment_id)
        self.__update_vehicle_info(inventory_obj)
        if ota_assignment_id == None:
            update_device_to_backend_meta(inventory_obj,self.uuid, self.device_sequence_counter)
        else:
             update_device_to_backend_meta(inventory_obj, ota_assignment_id, 1)
        log.debug(f"Inventory report message: {inventory_obj}")
        log.info("Sending updated Inventory Report")
        self.device_sequence_counter += 1
        return pb_operation.generate_output_message(inventory_obj)
    
    def __update_vehicle_info(self, inventory_obj):
        """
            Updates the vehicle information and BFB capabilities as per requirement.
            This will be sent to backend as part of inventory report

        Args:
            inventory_obj (InventoryReportEvent): Inventory report object

        Returns:
            inventory_obj (InventoryReportEvent): Inventory report object along with vehicle and bfb data
        """
        
        vehicle_data = inventory_report_event_pb2.VehicleData()
        vehicle_data.id = self.vin
        vehicle_data.version = "3"
        for bfb_service, version in constants.BFB_SUPPORT.items():
            bfb_data = inventory_report_event_pb2.Tuple()
            bfb_data.key = "BfB."+ bfb_service
            bfb_data.value = version
            vehicle_data.parameters.append(bfb_data)
        inventory_obj.vehicle.CopyFrom(vehicle_data)
        return inventory_obj
class SoftwareUpdate:
    def __init__(self,device_id, key_path, proxy):
        self.device_key = fileutil.read_file_as_binary(key_path)
        self.device_id = device_id
        self.update_statuses = [ota_status_pb2.DOWNLOADING,ota_status_pb2.DOWNLOAD_SUCCESS,ota_status_pb2.WAITING_FOR_UPDATE_CONDITION,ota_status_pb2.UPDATING,ota_status_pb2.UPDATE_SUCCESS]
        self.update_data = {1:"DOWNLOADING", 3:"DOWNLOADED",4:"PENDING UPDATE CONDITION", 7: "UPDATING", 9: "SUCCESSFUL"}
        self.assignment_data = {}
        self.proxy = proxy
        

    def assign_ota_update(self, input_message):
        """
            Gets ota assignment protobuf from backend and stores assignment details

        Args:
            input_message (serialized protobuf): Protobuf message for ota Update
        """
        ota_assignment_obj = update_command_pb2.UpdateCommand()
        pb_operation.decrypt_input_message(ota_assignment_obj, input_message)
        log.info(f"Received OTA ASSIGNMENT Request: {ota_assignment_obj.meta.activityId}")
        log.debug(f"OTA Assignment message: {ota_assignment_obj}")
        self.__store_update_package(ota_assignment_obj.meta.activityId, ota_assignment_obj.artifactUri)
        self.assignment_data[ota_assignment_obj.meta.activityId]=0
        
    def __store_update_package(self, assignment_id, uri):
        """Downloads and stores update package. In OTA directory

        Args:
            assignment_id (uuid): assignment ID
            uri (URL): BLOB URL
        """
        try:
            proxies = {
                        'http': self.proxy,
                        'https': self.proxy,
                }
            response = requests.get(uri, proxies=proxies)
            if(response.status_code == 200):
                fileutil.write_to_file_binary(constants.OTA_FOLDER_PATH.format(device_id=self.device_id), assignment_id + ".json", response.content)
                log.debug(f"JSON Content of the Update File: {fileutil.parse_json_file(constants.OTA_ASSIGNMENT_JSON_PATH.format(device_id=self.device_id, assignment_id=assignment_id))}")
            else:
                log.error(f"Failed to download the Update package from Cloud store response code {response.status_code}")
        except Exception as e:
            log.debug(f"Unable to parse the received file for as JSON, assignment ID {assignment_id}, error {e}")
            fileutil.delete_file(constants.OTA_ASSIGNMENT_JSON_PATH.format(device_id=self.device_id, assignment_id=assignment_id))

    def prepare_update_status(self):
        """Prepares update status for all available assignments

        Returns:
            proto_result_data: protobuf message that contains status of the assignments
            completed_list: list that contains details about completed assignments
        """
        proto_result_data = []
        completed_list = []
        for activity_id, sequence in self.assignment_data.items():
            rf_update_status_obj = update_status_event_pb2.UpdateStatusEvent()
            if sequence < len(self.update_statuses):    
                rf_update_status_obj.status = self.update_statuses[sequence]
                log.info(f"Status of activity Id: {activity_id} is updated to {self.update_data[rf_update_status_obj.status]}")
                update_device_to_backend_meta(rf_update_status_obj,activity_id,sequence)
                log.debug(f"OTA Status Message: {rf_update_status_obj}")
                if(rf_update_status_obj.status == 9): 
                    completed_list.append(activity_id)
            proto_result_data.append(pb_operation.generate_output_message(rf_update_status_obj))
            self.assignment_data[activity_id] = sequence+1

        for assignment_id in completed_list:
            del self.assignment_data[assignment_id]
            
        return proto_result_data, completed_list
class FunctionCalls:
    def __init__(self, device_id):
        self.device_sequence_counter = 1
        self.function_call_path = constants.FUNCTION_CALL_FILE

    def update_property_status(self, namespace, arg):
        function_call_json = fileutil.parse_json_file(self.function_call_path)
        function_call_json[self.namespace] = arg
        fileutil.write_json_file(self.function_call_path, function_call_json)
        fileutil.parse_json_file(self.function_call_path)
        log.debug(f"{namespace} property is updated and current value is {function_call_json[self.namespace]}")

    def function_call_command(self, input_message):
        functioncall_cmd = call_function_command_pb2.CallFunctionCommand()
        pb_operation.decrypt_input_message(functioncall_cmd, input_message)
        log.debug(f"Function call command from backend after parsing:  {functioncall_cmd}")
        log.info(f"Function call command to this property: {functioncall_cmd.name}")
        self.namespace = functioncall_cmd.name.rsplit('.',1)[-2]
        self.arguments = functioncall_cmd.inArguments
        self.method = functioncall_cmd.name.rsplit('.',1)[-1]
        if self.method == 'set_enabled':
            self.update_property_status(self.namespace,self.arguments)
        return self.prepare_property_status(functioncall_cmd.meta.activityId)

    def prepare_property_status(self, activity_id):
        function_call_json = fileutil.parse_json_file(self.function_call_path)
        function_call_status = function_call_status_event_pb2.FunctionCallStatusEvent()
        function_call_status.status = 2
        if self.method == 'get_enabled':
            function_call_status.outArguments = function_call_json[self.namespace]
        status_obj = update_device_to_backend_meta(function_call_status,activity_id,self.device_sequence_counter)
        log.info("Function call: Publishing message to backend")
        return pb_operation.generate_output_message(status_obj)
