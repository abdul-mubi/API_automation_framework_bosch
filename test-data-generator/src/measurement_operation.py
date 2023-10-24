import pandas
from src.common.fileutils import FileUtil
from src.common.pb_operation import PbOperation
from src.resources.proto_py import Measurement_v3_pb2
import datetime
import uuid
import time
from src.common import constants
from src.common.logger import get_logger
log = get_logger()
file_util = FileUtil()
class MeasurementOperation:
    """
    
        Measurement related operations are handled in MeasurementOperation class file
        
    """
    def __init__(self, device_id, vin):
        self.pb_operation = PbOperation()
        self.measurement_res = Measurement_v3_pb2.Measurement()
        self.application_session_id = str(uuid.uuid4())
        self.boot_cycle_id = str(uuid.uuid4())
        self.device_id = device_id
        self.vin = vin
        self.rm_folder_path = constants.RM_FOLDER_PATH.format(device_id = device_id)
        self.zip_extract_path = constants.ZIP_EXTRACT_PATH.format(device_id = device_id)

    def get_measurement_config_details(self, file_path):
        """Measurement configuration details are fetched from the particular path and processed

        Args:
            file_path ([path]): Path of the CDPJob.xml file

        Returns:
            measurement_config [list]: Returns a list that contains information related to measurement configuration
        """
        measurement_config = {}
        signal_data = []
        message_data = []
        job_details = file_util.get_json_from_xml(file_path)
        log.debug("======================== JOB DETAILS ========================")
        measurement_config['job_id'] = job_details['config']['content']['@jobId']
        measurement_config['job_name'] = job_details['config']['content']['name']
        measurement_config['job_version'] = job_details['config']['content']['@jobVersion']
        if job_details['config']['content']['reportingConfig']['reportingSettings']['@xsi:type'] == "SingleShotReporting":
            measurement_config['upload_interval_sec'] = 0
        else:
            measurement_config['upload_interval_sec'] = int(job_details['config']['content']['reportingConfig']['reportingSettings']['uploadPeriodSeconds'])
        log.debug(f"JOB Name: {measurement_config['job_name']}, JOB Id: {measurement_config['job_id']}, Job Version: {measurement_config['job_version']}")
        signal_details = job_details['config']['content']['measurementConfig']['daq']
        if isinstance(signal_details, dict):
            message_info, signal_info_list = self._get_message_signal_data(signal_details)
            if(len(message_info)>0):
                message_data.append(message_info)
            signal_data.extend(signal_info_list)
        else:
            for signal in signal_details:
                message_info, signal_info_list = self._get_message_signal_data(signal)
                if(len(message_info)>0):
                    message_data.append(message_info)
                signal_data.extend(signal_info_list)
        log.debug(signal_data)
        measurement_config['signal_data'] = signal_data
        measurement_config['message_data'] = message_data
        return measurement_config
    
    
    def _get_message_signal_data(self, signal_daq):
        """Returns signal details of individual signal by iterating through the signal_daq contents

        Args:
            signal_daq ([json]): Signal daq details from the CDPJob.xml file

        Returns:
            Signal Details [Dictionary]: dictionary object that contain signal_name, id, sampling_rate
        """
        signal_data = []
        message_data = {}
        daq_type = signal_daq["@xsi:type"]
        if daq_type == "CANRawDAQ" or daq_type =="J1939PgnDAQ":
            if signal_daq["reportResults"] == "true":
                message_data = {"name": signal_daq["name"],
                                "sampling_rate":signal_daq["samplingRateMs"],
                                "id":signal_daq["uid"],
                                "type": "Default",
                                "value_type": "BYTES"
                                }
            signal_data = self.__prepare_individual_signal_data(signal_daq)
        elif daq_type == "GPSDAQ":
            message_data = {"name": signal_daq["name"],
                                "sampling_rate":signal_daq["samplingRateMs"],
                                "id":signal_daq["uid"],
                                "type": "Default",
                                "value_type": "GPSDATA"
                                }
        elif daq_type == "DeviceSignalsDAQ":
            signal_data = self.__prepare_individual_signal_data(signal_daq, "DOUBLE")
        else:
            log.error(f"DAQ type {daq_type} is unknown to the Data generator")
        return message_data, signal_data
        
    def __prepare_individual_signal_data(self, signal_daq, value_type = None):
        """fetches individual signal data for each signal and returns list

        Args:
            signal_daq (dictionary): signal daq info
            value_type (String, optional): Type of the signal value, Example "DOUBLE", "GPS_DATA". Defaults to None.
        
        returns list: that contains signal data for individual signal in the daq
        """
        def fetch_signal_details(signal, value_type):
            if "@xsi:type" in signal.keys():
                signal_type = signal['@xsi:type']
            else:
                signal_type = "Default"
            if "valueConverter" in signal.keys() and value_type == None:
                value_type = signal['valueConverter']['type']
            data = {    "name": signal['name'],
                        "sampling_rate":signal['samplingRateMs'],
                        "id":signal['uid'],
                        "type": signal_type,
                        "value_type": value_type
                    }
            return data
        signal_data = []
        if('signal' in signal_daq):
            if isinstance(signal_daq['signal'], list):
                for signal in signal_daq['signal']:
                    signal_data.append(fetch_signal_details(signal, value_type))
            else:
                signal_data.append(fetch_signal_details(signal_daq['signal'], value_type))
        return signal_data
    
    def create_protobuf_zip(self, pb_name, measurement_config, test_step_data):
        """Creates final protobuf zip file which can be processed by measurement upload method

        Args:
            pb_name ([String]): Name of the Protobuf file
            measurement_config (dictionary): Measurement configuration related details
            test_step_data (dictionary): Contents of the teststep

        Returns:
            zip_name[String]: Name  of the final zip file which is created
        """
        
         
        zip_name = constants.PROTOBUF_OUT_FOLDER.format(device_id=self.device_id) + pb_name + ".zip"
        file_util.copy_file(constants.RESULT_TEMPLATE_FOLDER + "result.info", constants.PROTOBUF_OUT_FOLDER.format(device_id=self.device_id) + pb_name + "/" + pb_name + ".info")
        self.create_index_xml(pb_name)
        self.create_metadata_xml(pb_name,measurement_config['job_name'],measurement_config['job_id'],test_step_data['start_time'], test_step_data['end_time'])
        self.create_job_result_xml(pb_name, measurement_config, test_step_data)
        file_util.make_zip_file(constants.PROTOBUF_OUT_FOLDER.format(device_id=self.device_id) + pb_name, zip_name)
        return zip_name
    
    def create_index_xml(self, pb_name):
        """Creates index.xml file for the measurement result and places it the same folder where protobuf file is created

        Args:
            pb_name ([string]): result protobuf file name
        """
        var_dict = {"JOB_RESULT_XML": "jobResult.xml","PROTOBUF_DATA":pb_name+".pb","PROTOBUF_INFO":pb_name+".info","METADATA_XML": "MetaData.xml"}
        index_json = file_util.get_json_from_xml(constants.RESULT_TEMPLATE_FOLDER + "index.xml")
        config_data = index_json["config:config"]["config:content"]["config:taskIndexEntry"]
        for item in config_data:
            data_val = item["config:file"]
            if(data_val in var_dict.keys()):
                item["config:file"] = var_dict[data_val]
        index_json["config:config"]["config:content"]["config:taskIndexEntry"] = config_data
        file_util.convert_json_to_xml(constants.PROTOBUF_OUT_FOLDER.format(device_id=self.device_id) + pb_name + "/index.xml", index_json)
        
    def create_metadata_xml(self,pb_name, job_name, job_id, config_start_time_ms,config_end_time_ms, status = "RUNNING"):
        """Creates metadata.xml for the protobuf and places it in the same folder where in protobuf result is located

        Args:
            pb_name ([String]): Name of the protobuf result
            job_name ([String]): Measurement Job Name
            job_id ([uuid]): Measurement Job Id
            config_start_time_ms ([int]): Start time of particular measurement result protobuf
            config_end_time_ms ([int]): End time of the particular measurement result protobuf
            status (str, optional): [description]. Defaults to "RUNNING". - For ongoing measurement
        """
        metadata_json = file_util.get_json_from_xml(constants.RESULT_TEMPLATE_FOLDER + "MetaData.xml")
        metadata_json[constants.CONFIG][constants.CONTENT]['config:deviceId'] = self.device_id
        metadata_json[constants.CONFIG][constants.CONTENT]['config:vin']=self.vin
        result_meta =  metadata_json[constants.CONFIG][constants.CONTENT]['config:resultMetaData']
        result_meta['config:jobId'] = job_id
        result_meta['config:jobName'] = job_name
        result_meta[constants.CONFIG_ENTRIES]['config:startTime'] = self.convert_unix_time(config_start_time_ms)
        result_meta[constants.CONFIG_ENTRIES]['config:endTime'] = self.convert_unix_time(config_end_time_ms)
        result_meta[constants.CONFIG_ENTRIES]['config:executionStatus'] = status
        metadata_json[constants.CONFIG][constants.CONTENT]['config:resultMetaData'] = result_meta
        file_util.convert_json_to_xml(constants.PROTOBUF_OUT_FOLDER.format(device_id=self.device_id) + pb_name + "/MetaData.xml", metadata_json)
        
    
    def create_job_result_xml(self, pb_name, measurement_config, test_step_data):
        """Creates job_result.xml file for the measurement

        Args:
            pb_name ([String]): Name of the protobuf result
            measurement_config (dictionary): Measurement configuration related details
            test_step_data (dictionary): Contents of the teststep
        """
        
        job_result_json = file_util.get_json_from_xml(constants.RESULT_TEMPLATE_FOLDER + "jobResult.xml")
        job_result_json[constants.CONFIG][constants.CONTENT]['@measurementId'] = measurement_config['job_id']
        job_result_json[constants.CONFIG][constants.CONTENT]['@measurementInstanceId'] = test_step_data['uuid']
        job_result_json[constants.CONFIG][constants.CONTENT]['@jobVersion'] = measurement_config['job_version']
        job_result_json[constants.CONFIG][constants.CONTENT]['@packageIndex'] = test_step_data['sequence_counter']
        job_result_json[constants.CONFIG][constants.CONTENT]['@lastPackage'] = str(test_step_data['is_last']).lower()
        job_result_json[constants.CONFIG][constants.CONTENT]['@applicationSessionId'] = self.application_session_id
        job_result_json[constants.CONFIG][constants.CONTENT]['@bootCycleId'] = self.boot_cycle_id
        job_result_json[constants.CONFIG][constants.CONTENT]['config:errorInfo']['config:timestamp'] = self.convert_unix_time(test_step_data['end_time'] + 50)
        job_result_json[constants.CONFIG][constants.CONTENT]['config:executionStart'] = self.convert_unix_time( test_step_data['start_time'])
        job_result_json[constants.CONFIG][constants.CONTENT]['config:executionEnd'] = self.convert_unix_time(test_step_data['end_time'])
        file_util.convert_json_to_xml(constants.PROTOBUF_OUT_FOLDER.format(device_id=self.device_id) + pb_name + "/JobResult.xml", job_result_json)
            
    def convert_unix_time(self, time_ms):
        """Converts unix epoch time into human readable format 

        Args:
            time_ms ([int]): Epoch time

        Returns:
            Date time[String]: Time in human readable format
        """
        utc_time = datetime.datetime.utcfromtimestamp(time_ms/1000.0).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        return str(utc_time)
    
    def process_job(self, zip_path):
        """
            Process the measurement zip file and extract the file and place in a folder. 
            measurement config Id will be the name of the folder

        Args:
            zip_path ([String]): Path to the zip file

        Returns:
            measurement id[String]: Measurement config id, received from backend as part of zip (Returns name of the folder)
        """
        file_util.extract_zip_file(zip_path, self.zip_extract_path)
        measurement_config = self.get_measurement_config_details(constants.CDP_JOB_INITIAL_PATH.format(device_id = self.device_id))
        measurement_config['job_id'] 
        file_util.copy_dir(self.zip_extract_path, self.rm_folder_path  + measurement_config['job_id'])
        file_util.delete_dir(self.zip_extract_path)
        file_util.delete_file(zip_path)
        return measurement_config['job_id']
    
    def delete_job(self, measurement_config_id):
        """
        This method delete the measurement job located in the Temp/RM_Config path

        Args:
            measurement_config_id ([String]): UUIDof the measurement  Configuration
        """
        log.info(f"Deleting remote measurement Job from Data generator with Id: {measurement_config_id}")
        file_util.delete_dir(self.rm_folder_path  + measurement_config_id)
    
    def cleanup_old_result(self, time_in_min: int):
        """Cleans up old measurement results from the Remote measurement result directory

        Args:
            time_in_min (int): Time in mins where the result should be saved, in case time is 0 no measurement result will be stored
            If time is 5 mins, measurement results will be cleared except measurement results created in last 5 mins
        """
        current_unix_time = time.time()
        cleanup_time = current_unix_time - time_in_min * 60
        try:
            file_util.cleanup_folder_content_by_time(constants.PROTOBUF_OUT_FOLDER.format(device_id=self.device_id), cleanup_time)
        except OSError:
            pass
    
class RMProtoOperations():
    
    def __init__(self, csv_path):
        self.measurement_csv_path = csv_path
        self.csv_data = file_util.read_csv(csv_path)
        self.gps_data = pandas.DataFrame()
    
    def __generate_marker_data(self, reason_type, unix_time):
        """Generate marker data for the measurement result

        Args:
            reason_type (String): Start or stop reason.
            unix_time (epoch time- float): timestamp for the reason

        Returns:
            Measurement_v3_pb2.Marker: marker data object
        """
        marker_obj = Measurement_v3_pb2.Marker()
        if reason_type == "START":
            marker_obj.label = "Test Data generator - Test Step Start"
            marker_obj.timestamp = unix_time
            marker_obj.type = Measurement_v3_pb2.MarkerType.DRIVE_CYCLE_START
        elif reason_type == "STOP":
            marker_obj.label = "Test Data generator - Test Step End"
            marker_obj.timestamp = unix_time
            marker_obj.type = Measurement_v3_pb2.MarkerType.DRIVE_CYCLE_END
        else:
            marker_obj.label = "Generic Event"
            marker_obj.timestamp = unix_time
            marker_obj.type = Measurement_v3_pb2.MarkerType.GENERIC_EVENT
        return marker_obj
    
    def _generate_series_group_info(self, signal_details, upload_interval, start_time, result_index, series_key = 0):
        """Generates series group info for a measurement

        Args:
            signal_details (dictionary): signal details contains signal details for the individual signal
            upload_interval (float): upload interval of the measurement result in seconds
            start_time (epoch time): Start time of the measurement result for the particular signal
            result_index (int): result index of the upload cycle for the measurement
            series_key (int, optional): Series key for the measurement result. Defaults to 0.

        Returns:
            Measurement_v3_pb2.SeriesGroup: Series group object for the signal
        """
        
        series_group_info = Measurement_v3_pb2.SeriesGroup()
        series_group_info.series.append(self._generate_series_details(signal_details, series_key))
        if(int(signal_details['sampling_rate']) == 0):
            signal_details['sampling_rate'] = 100
        
        downsampling_rate = int(signal_details['sampling_rate'])
        if(upload_interval != 0):
            total_values = int( (upload_interval*1000) / downsampling_rate )
        else:
            total_values = 1
        log.debug(f"Total values for signal {signal_details['name']} at result index {result_index} is {total_values}")
        for row in range(0, total_values):
            data_row = (result_index * total_values) + row
            result_time = start_time + (downsampling_rate*row)
            result_data = self._generate_time_point_data(signal_details, series_key, result_time, data_row)
            if(result_data != None):
                series_group_info.time_point.append(result_data)
        return series_group_info
    
    def _generate_series_details(self,signal_details, series_key):
        """Generates series details for the individual signal

        Args:
            signal_details (dictionary): signal details contains signal details for the individual signal
            series_key (int, optional): Series key for the measurement result. Defaults to 0.
            
        Returns:
            Measurement_v3_pb2.Series: returns series info 
        """
        series = Measurement_v3_pb2.Series()
        series.key= series_key
        series.name= signal_details['name']
        if signal_details['type']== "SPNSignal":
            series.value_type = Measurement_v3_pb2.ValueType.LIST
        elif signal_details['value_type']== "GPSDATA":
             series.value_type = Measurement_v3_pb2.ValueType.GPSDATA
        elif signal_details['value_type']== "BYTES":
            series.value_type = Measurement_v3_pb2.ValueType.BYTES
        elif signal_details['value_type']== "STRING":
            series.value_type = Measurement_v3_pb2.ValueType.STRING
        else:
            series.value_type = Measurement_v3_pb2.ValueType.DOUBLE
        series.uid= signal_details['id']
        return series
    
    def _generate_time_point_data(self,signal_details, series_key, unix_time, result_key):
        """Generates timepoint data for the signal, used to create individual signal data point

        Args:
            signal_details (dictionary): signal details contains signal details for the individual signal
            unix_time (float): timestamp of the particular data point
            result_key (int): Index of the signal value to be fetched from csv
            series_key (int, optional): Series key for the measurement result. Defaults to 0.

        Returns:
            Measurement_v3_pb2.TimePoint: timepoint object contains information about individual data point at given time
        """
        try:
            time_point_obj = Measurement_v3_pb2.TimePoint()
            time_point_obj.timestamp = unix_time
            time_point_obj.data_point.append(self._generate_data_point(signal_details,series_key,result_key, unix_time))
            return time_point_obj
        except (TypeError, IndexError, ValueError) as e:
            log.error(f"Invalid signal/message data for {signal_details['name']} at index {result_key}, error: {e}")
            return None
            

    def _generate_data_point(self, signal_details, series_key, result_key, unix_time):
        """Generates the data for the particular time based on the signal

        Args:
            signal_details (dictionary): signal details contains signal details for the individual signal
            result_key (int): Index of the signal value to be fetched from csv
            series_key (int, optional): Series key for the measurement result. Defaults to 0.
            unix_time (float): timestamp of the particular data point

        Returns:
            Measurement_v3_pb2.DataPoint: Returns the data required for particular timepoint
        """
        
        data_point_obj = Measurement_v3_pb2.DataPoint()
        data_point_obj.series_ref = series_key
        if signal_details["type"] == "SPNSignal":
            data_point_obj.value.list_value.CopyFrom(self.__get_list_data(signal_details, result_key))
        elif signal_details["value_type"] == "DOUBLE":
            data_point_obj.value.scalar_value.number_value.double_value = self.__get_double_data(signal_details['name'],result_key,signal_details['sampling_rate'] )
        elif signal_details["value_type"] == "GPSDATA":
            data_point_obj.value.gpsdata_value.CopyFrom(self.__get_gps_data(result_key, unix_time, signal_details['sampling_rate']))
        elif signal_details["value_type"] == "BYTES":
            data_point_obj.value.scalar_value.bytes_value = self.__get_byte_data(signal_details['name'],result_key)
        elif signal_details["value_type"] == "STRING":
            data_point_obj.value.scalar_value.string_value = str(self._get_data_for_signal(signal_details['name'],result_key))
        else:
            raise KeyError(f"Measurement result type {signal_details['value_type']}  is not defined in data generator")
        return data_point_obj
    
    def __get_double_data(self, signal_name, result_key, down_sampling_rate):
        """
            Creates double data for the specified signal
        Args:
            signal_name (String): Name of the signal, which should be fetched from csv
            result_key (int): Result index

        Returns:
            result data: DOUBLE result data
        """
        data = float(self._get_data_for_signal(signal_name,result_key, down_sampling_rate))
        return data
    
    
    def __get_byte_data(self, signal_name, result_key):
        """Creates Byte data for the signal and returns same

       Args:
            signal_name (String): Name of the signal, which should be fetched from csv
            result_key (int): Result index

        Returns:
            result data: BYTE result data
        """
        data = self._get_data_for_signal(signal_name,result_key)
        hex_data = data.split("0x")[1]
        return bytes.fromhex(hex_data)
    
    def __get_gps_data(self, result_key, unix_time, down_sampling_rate):
        """Creates GPS data for the GPSDATA message. by fetching different signal values.
        Args:
            result_key (int): Result index
            unix_time (float): timestamp of the particular data point
        
        Returns:
             Measurement_v3_pb2.GPSData: GPS data object
        """
        
        gps_obj = Measurement_v3_pb2.GPSData()
        gps_obj.longitude= self.__get_double_data("GPSLongitude",result_key, down_sampling_rate)
        gps_obj.latitude= self.__get_double_data("GPSLatitude",result_key, down_sampling_rate)
        gps_obj.elevation= self.__get_double_data("GPSAltitude",result_key, down_sampling_rate)
        gps_obj.gps_time= unix_time
        gps_obj.direction= self.__get_double_data("GPSHeading",result_key, down_sampling_rate)
        gps_obj.gps_speed= self.__get_double_data("GPSSpeed",result_key, down_sampling_rate)
        return gps_obj
    
    def __get_list_data(self,signal_details, result_key):
        """
            Prepares list data for the specified message.
            Currently only SPN Signals use this type of data with data type as DOUBLE

        Args:
            signal_details (String): Details of the signal
            result_key (int): Result index

        Returns:
            Measurement_v3_pb2.ScalarList: Scalar list that contains list of data
        """
        scalar_list = Measurement_v3_pb2.ScalarList()
        result_data = self._get_data_for_signal(signal_details['name'],result_key)
        result_data_list = result_data.strip('][').split(', ')
        scalar_value = Measurement_v3_pb2.ScalarValue()
        for each_data in result_data_list:
            if signal_details["value_type"] == "DOUBLE":
                scalar_value.number_value.double_value = float(each_data)
                scalar_list.value.append(scalar_value)
        return scalar_list
        
    def get_measurement_result(self, measurement_config, test_step_data, **kwargs):
        """Prepares measurement result for the measurement config based on input details

        Args:
            measurement_config (dictionary): Details related to measurement config
            test_step_data (dictionary): Details related to test step

        Returns:
            Measurement_v3_pb2.Measurement: Measurement proto file, which can be used for further process
        """
        rm_proto = Measurement_v3_pb2.Measurement()
        rm_proto.marker.append(self.__generate_marker_data("START", test_step_data['start_time']))
        if(self.gps_data.empty and "geo_data" in kwargs.keys() and isinstance(kwargs["geo_data"], pandas.DataFrame)):
            self.gps_data = kwargs["geo_data"]

        for signal in measurement_config["signal_data"]:
            try:
                rm_proto.series_group.append(self._generate_series_group_info(signal, measurement_config['upload_interval_sec'],test_step_data['start_time'], test_step_data['sequence_counter']))
            except KeyError as e:
                log.info(f"{e}")
        for message in measurement_config["message_data"]:
            try:
                rm_proto.series_group.append(self._generate_series_group_info(message, measurement_config['upload_interval_sec'],test_step_data['start_time'], test_step_data['sequence_counter']))
            except KeyError as e:
                log.info(f"{e}")
        if(test_step_data['is_last']):
            rm_proto.marker.append(self.__generate_marker_data("STOP",test_step_data['end_time']))
        return rm_proto
    
    def _get_data_for_signal(self, signal_name, row_num: int, down_sampling = None):
        """
            Fetches the signal/ Message data from the CSV object and returns the same
            Incase key is not found, it will log a error
            If the row num exceeds available data, replay of the data will be performed
        Args:
            signal_name (String): Name of the signal/Message
            row_num (int): _description_
        Raises:
            ValueError: Incase signal details are not available.
        Returns:
            String: Content of the signal at the specified row
        """
        
        try:
            if("GPS" in signal_name and (not self.gps_data.empty) and signal_name in self.gps_data.columns):
                row_val = int(row_num * (int(down_sampling)/(constants.GPS_SAMPLE_SEC * 1000))) 
                if row_val >= len(self.gps_data[signal_name]):
                    row_val = len(self.gps_data[signal_name]) - 1
                return self.gps_data[signal_name][row_val]
            else:
                row = row_num % len(self.csv_data[signal_name].dropna())
                return self.csv_data[signal_name][row]
        except KeyError as e:
            log.error(f"{e} details are not found in {self.measurement_csv_path} please update signal/message data")
            raise KeyError(f"Details are missing for signal {signal_name}")