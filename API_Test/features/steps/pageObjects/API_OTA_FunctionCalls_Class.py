import logging
import requests
import time
from asyncio import constants
import steps.utils.API_Requests as api_requests
import steps.pageObjects.API_Generic_Class as API_Generic_Class
import steps.constantfiles.constants_ota_functioncalls as constants
import os
import yaml

class APIOtaFunctionCalls:
    def __init__(self, environment, log_api_details):
        self.api_requests = api_requests.ApiRequestsClass(environment, log_api_details)
        self.env = environment
        self.log_details = log_api_details
        self.api_gen_obj = API_Generic_Class.ApiGenericClass()

    def check_vsc_definition(self, property_name):
        r = self.api_requests.get_request(constants.VSC_DEF)
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)

        yaml_response = yaml.load_all(r.text,Loader=yaml.FullLoader)

        check_property_exist = False
        for service in yaml_response:
            dict_service = dict(service.items())
            if property_name.strip('"') in dict_service.values():
                check_property_exist = True
        
        if check_property_exist == False:
            property_file = property_name.strip('"')
            file_path = constants.OTA_FUNCTION_CALL_FILES_PATH +f"\\{property_file}.yaml"
            full_path = os.path.dirname(os.path.abspath(__file__)) + "\\..\\..\\..\\..\\" + file_path
            property_file_content = None
            with open(full_path, "r") as stream:
                property_file_content = stream.read()

            raw_update_content = r.text +'\n'+ property_file_content

            #If Match is default 0
            custom_header  = {'accept': '*/*',
                        'content-type': 'text/plain',
                        'if-match': '0', 'X-Requested-With': 'XMLHttpRequest'}

            pr = self.api_requests.put_request_file(constants.VSC_DEF, dbc_file=raw_update_content,custom_header=custom_header)
            assert pr.status_code == requests.codes.ok, self.api_gen_obj.assert_message(pr)

    def create_vsc_definition(self, property_name):
        data = self.api_gen_obj.parse_yaml_file(constants.OTA_FUNCTION_CALL_FILES_PATH+f"\\{property_name}.yaml")
        r = self.api_requests.put_request(constants.VSC_DEF, params=data)
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)

    def call_function(self, data):
        """ Description     : Triggers a function call on a specific device or vehicle or vin .

        Parameters          : data = the request body data for function call.

        Expected result : The 'callId' value returned in the response can be used as the 'callId'

    """

        r = self.api_requests.post_request(constants.CALL_FUNCTION, data)
        assert r.status_code == requests.codes.created, self.api_gen_obj.assert_message(r)
       
        location = r.headers['location']
        return location.rsplit('/',1)[-1]
    
    def prepare_function_call_request_body(self, action, property,target_value, in_arg_value = None):
        """ Description     : It parses the property json and prepares the OFC request data based on the given property

        Parameters          : action - ids_csg_logs,preconditioning, property = property name,
                              in_arg_value = in arguments config value for preconditioning feature

        Expected result : It should return the request body data for function call.

    """
        json_data = self.api_gen_obj.parse_json_file(constants.PROPERTY_JSON_PATH)
        data = json_data[property][action]
        data['target'] = target_value    
        if in_arg_value is not None:
            config_key = in_arg_value.split(":")[0]
            config_value = in_arg_value.split(":")[1]
            data['inArguments'][config_key] = config_value
        return data
        

    def verify_status_for_function_call(self, call_id, status):
        status_list = status.upper().split('/')
        self.api_gen_obj.update_timeout_time(180)
        self.api_gen_obj.start_timer()
        while (self.api_gen_obj.check_timer() == True):
            r = self.api_requests.get_request(constants.GET_STATUS_FUNCTION_CALL.format(call_id))
            assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
            actual_status = r.json()["status"]
            if actual_status.upper() in status_list:
                logging.info(f"Expected {'/'.join(status_list)} Actual {actual_status} for callId - {call_id}")
                self.api_gen_obj.stop_timer()
                break
            time.sleep(10)
        if self.api_gen_obj.check_timer() == False:
            assert actual_status in status_list, f'Status mismatch in function call. Expected {"/".join(status_list)} Actual {actual_status} for callId - {call_id}'
        return r.json()
