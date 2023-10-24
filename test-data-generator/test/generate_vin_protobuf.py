from src.resources.proto_py import vin_update_event_pb2
from src.common.fileutils import FileUtil as fileutil_class
from src.common.pb_operation import PbOperation as pb_operation_class
from src.common.logger import get_logger

log = get_logger()

def create_vin_protobuf_from_static_values():
    pb_op = pb_operation_class()
    header = vin_update_event_pb2.bfb__header__pb2.BfbHeader()
    header.device_sequence_counter = 1
    header.timestamp = 1641193467
    header.serialization = 'protobuf'
    header.version = 1
    header.api_section = "deviceVehicleMapping"
    header.message_type = "vinUpdateEvent"
    
    vin_data = vin_update_event_pb2.VinUpdateEvent()
    vin_data.vin = "AUT2020101010101010"
    vin_data.vin_is_trusted = True
    vin_data.header.CopyFrom(header)
    log.info("====================VIN Created with Static Data====================")
    log.info(f"proto_data: {vin_data}")
    log.info(f"Serialized proto data: {vin_data.SerializeToString()}")
    pb_op.create_final_protobuf(vin_data,"VIN_FILE_STATIC")


def create_vin_protobuf_from_json():
    pb_op = pb_operation_class()
    file_util = fileutil_class()
    vin_proto = vin_update_event_pb2.VinUpdateEvent()
    vin_json_data = file_util.parse_json_file("test/data/user_data/device_vin.json")
    vin_proto = pb_op.decrypt_input_message(vin_proto, vin_json_data, "JSON")
    header_proto = vin_update_event_pb2.bfb__header__pb2.BfbHeader()
    header_json_data = file_util.parse_json_file("test/data/user_data/vin_header.json")
    header_proto = pb_op.create_protobuf_from_json(header_proto, header_json_data,  "JSON")
    pb_op.create_final_protobuf(vin_proto, "VIN_FROM_JSON",header_proto)
    
if __name__ == '__main__':
    create_vin_protobuf_from_static_values()
    create_vin_protobuf_from_json()