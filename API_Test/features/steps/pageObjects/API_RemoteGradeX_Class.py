import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import os
import zipfile
import io
import re
import shutil
import steps.utils.API_Requests as API_Request
import steps.pageObjects.API_Generic_Class as API_Generic_Class
import steps.constantfiles.constants_remotegradex as constants

class ApiRemoteGradeXClass:
    def __init__ (self, enviroment, log_api_details):
        self.api_requests = API_Request.ApiRequestsClass(enviroment, log_api_details)
        self.api_gen_obj = API_Generic_Class.ApiGenericClass()
    
    def create_rda_task(self, data, file_data, device_id):
        """Assigned flash job template to a vehicle"""
        # equest to create RDA task execution with a device
        r = self.api_requests.post_request_file(constants.RGX_RDA_TASK_EXE, data, file_data)
        assert r.status_code == requests.codes.created, self.api_gen_obj.assert_message(r)
        r = self.api_requests.get_request(constants.RGX_RDA_TASK_EXE_DEVICE_ID.format(device_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        task_id = r.json()['_embedded']['rdaTaskExecutions'][0]['taskId']
        return task_id

    def get_rda_task_status(self, device_id):
        r = self.api_requests.get_request(constants.RGX_RDA_TASK_EXE_DEVICE_ID.format(device_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r

    def get_rda_task_details(self, task_id):
        """Returns RDA Task details by ID

        Args:
            task_id (str ): UUID

        Returns:
            dict: Details related to the task
        """
        r = self.api_requests.get_request(constants.GRADEX_TASK_ID.format(task_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r.json()
    
    def get_rda_job_result(self, device_id):
        r = self.api_requests.get_request(constants.RGX_RDA_JOB_RESULT_DEVICE_ID.format(device_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r

    def del_rda_job_result(self, job_result_id):
        r = self.api_requests.delete_request(constants.RGX_RDA_JOB_RESULT_ID.format(job_result_id))
        assert r.status_code == requests.codes.no_content, self.api_gen_obj.assert_message(r)
        return r

    def ver_rda_job_result(self, job_result_id):
        r = self.api_requests.get_request(constants.RGX_RDA_JOB_RESULT_ZIP_ID.format(job_result_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        data = zipfile.ZipFile(io.BytesIO(r.content))
        path = os.path.dirname(os.path.abspath(os.curdir)) + "\\ZipContent"
        data.extractall(path)
        result = False
        pb_txt_files =self.api_gen_obj.get_file_name(path,"*.pb_txt")
        for file in pb_txt_files:                  
                    with open(file,"r") as fp:
                        lines = fp.readlines()
                        value_1 = re.findall('[0-9]*$', lines[323])
                        value_2 = re.findall('[0-9]*$', lines[537])      
                        if ( (85000 < int(value_1[0]) < 95000) and (85000 < int(value_2[0]) < 95000)  ):
                             result = True                
                        
        shutil.rmtree(path)
        return result

    def verify_gx_rd_job_result(self, job_result_id, dtc_code_result):
        r = self.api_requests.get_request(constants.RGX_RDA_JOB_RESULT_ZIP_ID.format(job_result_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        data = zipfile.ZipFile(io.BytesIO(r.content))
        path = os.path.dirname(os.path.abspath(os.curdir)) + "\\ZipContent"
        data.extractall(path)
        result = False
        log_files =self.api_gen_obj.get_file_name(path,"log_stdout.txt")
        for log_file_path in log_files:
            with open(log_file_path, "r") as fp:
                 data = fp.read()
                 if dtc_code_result in data:
                      result = True
                      break        
        shutil.rmtree(path)
        return result