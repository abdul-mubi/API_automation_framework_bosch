import json
import os
from src.common.fileutils import FileUtil as fileutil_class
from src.common import constants
from src.common.logger import get_logger
from google.protobuf import json_format
log = get_logger()
class PbOperation():
    def __init__(self):
        self.fileutil_obj = fileutil_class()
    
    def update_protobuf_header(self, proto_obj, header):
        """
            To append bfb header object to the protobuf file.
        Args:
            proto_obj (proto_message_obj): Proto object for which header to be appended
            header (proto_message_obj): header details

        Returns:
            proto_obj (proto_message_obj):: proto_obj with header
        """
        proto_obj.header.CopyFrom(header)
        return proto_obj
    
    def create_final_protobuf(self, proto_obj, file_name, header_obj = None):
        """Creates Serialized protobuf file and writes to the file.
        Args:
            proto_obj (proto_message_obj): Protobuf message object
            file_name (_type_): Name of the file, where the serialized message to be stored
            header_obj (proto_message_obj, optional): Header data, if required. Defaults to None.
        """
        if(header_obj != None):
            proto_obj = self.update_protobuf_header(proto_obj, header_obj)
        path = self.fileutil_obj.create_protobuf_file(proto_obj, file_name)
        log.debug(f"protobuf files are created at:{path}")
    
    def generate_output_message(self, proto_obj, result_format = constants.PROTOBUF) :
        """
            Generates the proto message in the required form.
            currently Serialized Protobuf and JSON format are supported

        Args:
            proto_obj (proto_message_obj): Protobuf message object
            result_format (String, optional): Format of the Result. Defaults to constants.PROTOBUF.

        Returns:
            converted data: Formatted result data based on the requested format
        """
        if result_format == constants.PROTOBUF :
            return proto_obj.SerializeToString()
        elif result_format == constants.JSON :
            return json_format.MessageToJson(proto_obj)
        else:
            return str(proto_obj)
        
    def decrypt_input_message(self, proto_obj, input_data, input_format = constants.PROTOBUF):
        """
            This method will try to decrypt protobuf message from the different input formats to proto_object
            Currently supported formats are serialized protobuf message, JSON

        Args:
            proto_obj (proto_message_obj): Protobuf message object
            input_data (bytes/JSON): Input data based on the format.
            input_format (String, optional): Format of the input data. Defaults to constants.PROTOBUF.

        Raises:
            ValueError: Incase if the message is not processable, error will be raised

        Returns:
           proto_obj (proto_message_obj):proto_obj with data
        """
        try:
            if input_format == constants.PROTOBUF :
                return proto_obj.ParseFromString(input_data)
            elif input_format == constants.JSON :
                return  json_format.Parse(json.dumps(input_data),proto_obj)
        except TypeError as e:
            log.error(f"Invalid input message format, expected format is {input_format}")
            log.debug(f"Error Message: {e}")
            raise ValueError(f"Failed to Parse input message from {input_format}")