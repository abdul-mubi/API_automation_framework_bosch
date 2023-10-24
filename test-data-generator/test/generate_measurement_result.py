from src.common.pb_operation import PbOperation
from src.measurement_operation import MeasurementOperation, RMProtoOperations
import time
import uuid

def create_rm_data():
    device_id = "E2E_OTA_DEVICE_001"
    vin = "AUT20111234569989"
    rm_operation = MeasurementOperation(device_id,vin)
    pb_operation = PbOperation()
    rm_proto_op = RMProtoOperations()
    measurement_config = {'job_id': 'c32d36f1-d49d-49a6-a680-a3ca746d8086',
                          'job_name': 'GPS_Device_Signals_10s',
                          'job_version': '1',
                          'upload_interval_sec': 60,
                          'signal_data': [
                                            {
                                                'name': 'GPSTripDistance',
                                                'sampling_rate': '10000',
                                                'id': 'CTP-GPSTripDistance',
                                                'type': 'Default',
                                                'value_type': 'DOUBLE'
                                                },
                                            {
                                                'name': 'GPSAltitude',
                                                'sampling_rate': '10000',
                                                'id': 'CTP-GPSAltitude',
                                                'type': 'Default', 
                                                'value_type': 'DOUBLE'
                                                }
                                            ], 
                          'message_data': [
                                            {
                                                'name': 'GPS',
                                                'sampling_rate': '10000',
                                                'id': 'CTP-GPS', 
                                                'type': 'Default',
                                                'value_type': 'GPSDATA'
                                                }
                                            ]
                          }
    start_time_ms = round(time.time()*1000)
    end_time_ms = start_time_ms + int(measurement_config['upload_interval_sec'] * 1000)
    test_step_data = {
                                                "uuid": str(uuid.uuid4()),
                                                "start_time": start_time_ms,
                                                "end_time" : end_time_ms,
                                                "sequence_counter": 0,
                                                "is_last": False
                                            }
    pb_name = str(start_time_ms)
    measurement_pm = rm_proto_op.get_measurement_result(measurement_config, test_step_data)
    pb_operation.create_final_protobuf(measurement_pm, pb_name)
    rm_operation.create_protobuf_zip(pb_name,measurement_config,test_step_data)

if __name__ == '__main__':
    create_rm_data()