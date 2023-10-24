import requests
import logging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import os
import time
import json
import re
from io import BytesIO
from zipfile import ZipFile
from bs4 import BeautifulSoup
import urllib.parse
import re
from packaging import version
import steps.utils.API_Requests as api_requests
import steps.pageObjects.API_Generic_Class as API_Generic_Class
import steps.constantfiles.constants_ota_updates as constants
import steps.pageObjects.API_FleetManagement_Class as API_FleetManagement_Class

class ApiOtaUpdatesClass:

    def __init__ (self, environment, log_api_details):
        self.api_requests = api_requests.ApiRequestsClass(environment, log_api_details)
        self.api_fleetmgt_obj = API_FleetManagement_Class.ApiFleetManagementClass(environment, log_api_details)
        self.api_gen_obj = API_Generic_Class.ApiGenericClass()
        self.env = environment
        self.log_details = log_api_details
    
    def get_ota_status_history(self,assignment_id):        
        r = self.api_requests.get_request(constants.OTA_CORE_ASSIGNMENT + assignment_id + constants.STATUS_HISTORY)
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return [flash_status['status'] for flash_status in r.json()['_embedded']['assignmentStatusHistoryItems']]
        
    def search_distribution_package(self, package_name):
        distribution_package_id = ""
        ep = constants.OTA_PACKAGE_NAME.format(package_name)
        r = self.api_requests.get_request(ep=ep)
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        
        if "_embedded" in r.json():
            
            logging.info("Distribution Package %s already exists. So, uploading and creating new package will not be done."%package_name)
            
            for p in r.json()["_embedded"]["distributionPackages"]:
                if p["name"] == package_name:
                    distribution_package_id = p["distributionPackageId"]
                    break
        else:
            distribution_package_id = None
        return distribution_package_id

    def create_update_package(self, update_package_name):
        path = os.path.dirname(os.path.abspath(__file__))
        file_path = path + constants.ARTIFACTORY_DOWNLOAD_FILE_PATH + "/" + update_package_name
        logging.info(f"Update package path: {file_path}")
        files = {'file': open(file_path, 'rb')}
        data = {
            "name": update_package_name,
            "contentType": "application/octet-stream",
            "updateAgent": "SUA",
            "properties": {}
        }

        r = self.api_requests.post_request_file(ep= constants.OTA_CREATE_UPDATE_PACKAGE, params=data, dbc_file=files)
        assert r.status_code == requests.codes.created, self.api_gen_obj.assert_message(r)
        return r.json()['updatePackageId']
        
    def create_dist_package(self, dist_package_name, security_option, update_package_id):
        data = {
            "name": dist_package_name,
            "packageProcessor": "CTP_OBUA",
            "securityOption": security_option, 
            "parts":[
                {"updatePackageId": update_package_id}
            ]
        }
        r = self.api_requests.post_request(ep= constants.OTA_CREATE_DISTRIBUTION_PACKAGE, params=data)
        assert r.status_code == requests.codes.created, self.api_gen_obj.assert_message(r)
        return r.json()['distributionPackageId']

    def create_and_check_container_status(self,distribution_pkg_id):       
        r = self.api_requests.post_request(ep= constants.OTA_CREATE_CONTAINER.format(distribution_pkg_id),params={})
        assert r.status_code == requests.codes.accepted, self.api_gen_obj.assert_message(r)
        
        container_status=False
        self.api_gen_obj.start_timer()
        while (self.api_gen_obj.check_timer() == True):
            r = self.api_requests.get_request(ep=constants.OTA_CREATE_CONTAINER.format(distribution_pkg_id))
            if(r.json()['containerState'] == "CREATED"):
                container_status=True
                self.api_gen_obj.stop_timer()
                break
        assert container_status == True,f'Container is not created in the distribution package with id {distribution_pkg_id}'       

    def package_to_device_check(self, device, distribution_package_id):
        """Checks the delta package is distributed to test device"""
        data = {
        "distributionPackageId":distribution_package_id, #context.distribution_package_id,
        "cuId": device#context.device
        }
        r = self.api_requests.post_request(ep= constants.OTA_DISTRIBUTION_ASSIGNMENT, params=data)
        logging.info(f"Response details: {r} ")
        assert r.status_code == requests.codes.created, self.api_gen_obj.assert_message(r)
        return r


    def get_flash_status(self, flash_assignment_id, timer, exp_status):
        """it gathers the Self Update assignment status and returns it"""
        all_status = []
        ep = constants.OTA_DISTRIBUTION_ASSIGNMENT_ID+flash_assignment_id
        time_out_time = time.time() + (int(timer))*2
        while ((time.time() < time_out_time) and ("UPDATE_FAILURE" not in all_status) and ("UPDATE_SUCCESS" not in all_status) and ("DOWNLOAD_FAILURE" not in all_status)):
            r = self.api_requests.get_request(ep=ep)
            assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
            self_update_status = r.json()["status"]

            if self_update_status not in all_status:
                all_status.append(self_update_status)
                logging.info(f"New OTA assignment Status appears - {self_update_status}")

            if self_update_status == exp_status:
                logging.info(f"Expected status - {self_update_status} of OTA assignment appears.")
                return all_status
            
            time.sleep(1)

        if ((time.time() > time_out_time) or ("UPDATE_FAILURE" in all_status) or ("UPDATE_SUCCESS" in all_status) or ("DOWNLOAD_FAILURE" in all_status)):
            logging.info(f"Wrong OTA assignment status appears. Current status is - {self_update_status}")
            return all_status


    def check_update_status(self, test_device, update_status, command, start_time, context):
        result = self.api_gen_obj.ssh_execute(context.devices_data[test_device][context.test_device+"_IP"],context.device_config_data['ssh_key'],command)
        if("exit" in str((result)[0])):
            self_update_status = re.search('%s(.*)%s' % ("with \"", "\" - it"), str((result)[0])).group(1)
            if (self_update_status == "0"):
                logging.info(f"Self update is successful for {test_device}, took {int(time.time() - start_time)} seconds")
                update_status[test_device] = "Success"
            else:
                logging.info(f"Self update is failed for {test_device} after {int(time.time() - start_time)} seconds")
                update_status[test_device] = "Failed"

        return update_status

    def revoke_assignment(self, assignment_id):
        etag = self.api_requests.get_etag(constants.OTA_CORE_ASSIGNMENT + assignment_id)
        r = self.api_requests.post_request(constants.OTA_CORE_ASSIGNMENT_ID_REVOKE.format(assignment_id), {}, {'if-match': etag})
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        assert r.json()['revocationRequested'] == True, "Revocation request is not processed by the application properly"

    def retry_assignment(self, assignment_id):
        etag = self.api_requests.get_etag(constants.OTA_CORE_ASSIGNMENT + assignment_id)
        r = self.api_requests.post_request(constants.OTA_CORE_ASSIGNMENT_ID_RETRY.format(assignment_id), {}, {'if-match': etag})
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        assert r.json()['retries']['totalCount'] != 0, "Retry request is not processed by the application properly"

    def revocation_failure_check(self, assignment_id):
        r = self.api_requests.get_request(constants.OTA_CORE_ASSIGNMENT + assignment_id)
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        if(r.json()["status"] not in ["UPDATE_SUCCESS","UPDATE_FAILURE"]):
            assert r.json()["status"] != "UPDATE_REVOKED", "Unexpected! Update is Revoked when it was not supposed to"

    def get_assignment_ids_and_status(self, status, ota_status_list, distribution_package, context):
        r = self.package_to_device_check(context.device_id, distribution_package)
        assert r.json()["status"] == status, "Unexpected. Self update package is not distributed to device "+context.device_id
        context.ota_update_assignment_details.append(r.json()["assignmentId"])
        logging.info("Distribution package is uploaded on device "+r.json()["target"]["cuId"]+" with assignment Id - "+r.json()["assignmentId"])
        logging.info("Distribution package status: "+r.json()["status"])
        #"""initial status will be 'UPDATE_ASSIGNED' and it becomes UPDAting and stays for 3..4 mins, then device reboot needed"""
        if (r.json()["status"] not in ota_status_list):
            ota_status_list.append(r.json()["status"])
            context.ota_status_list = ota_status_list

    def check_dp_device_compatibility(self,distribution_package,dp_device_compatible,device_id):  
        """Checks whether the Distribution Package under Consideration is Compatible with Device Version or Not

        Args:
            distribution_package: Distribution Package ID in consideration
            dp_device_compatible: Assumed Condition of Assignment Creation based upon compatibility
            device_id: Device ID
        """
        
        data = {
        "distributionPackageId":distribution_package,
        "cuId": device_id
        }

        r = self.api_requests.post_request(ep= constants.OTA_DISTRIBUTION_ASSIGNMENT, params=data)

        if dp_device_compatible == "Accepted":
            assert r.json()["status"] == "UPDATE_ASSIGNED", f"Unexpected Status - {r.json()['status']}. The Expected Status should be UPDATE_ASSIGNED."
            logging.info("Response Status Verified as UPDATE_ASSIGNED.")
            logging.info("Device Version Compatibility Verified during Assignment Creation")
        elif dp_device_compatible == "Rejected":
            assert r.json()["status"] == 422, f"Unexpected Status - {r.json()['status']}. The Expected Status should be 422."
            logging.info("Response Status Verified as 422.")
            message_response = r.json()["message"]
            logging.info(message_response)
            exp_error_message = "Compatibility check failed for device"
            assert exp_error_message in message_response,f"Error Message Validation Unsuccessful for the Device - {r.json()['message']} "
            logging.info("Device Version Incompatibility detected during Assignment Creation")

    def verify_ota_status(self, assignments, timer, exp_status, exception_status_list, exception_dict, context):
        self_update_flash_status = self.get_flash_status(assignments , timer, exp_status)
        for states in self_update_flash_status:
            if states not in context.ota_status_list:
                context.ota_status_list.append(states)

        if(self_update_flash_status[len(self_update_flash_status)-1] != exp_status):
            exception_status_list.append(states)
            exception_status_list.append(exp_status)
            exception_dict[assignments]=exception_status_list
        else:
            assert self_update_flash_status[len(self_update_flash_status)-1] == exp_status, "Expected Self Update Flashing status appears"

        return exception_status_list
    
    def verify_ota_logs(self, assignment_id, timer, assignment_type = "SUCCESSFUL"):
        """Checks for the availability of the logs in the OTA Assignment

        Args:
            assignment_id (UUID): Assignment ID of the OTA Assignment
            timer (sec): time in seconds till when the log file availability is checked
            ota_log_status (str): Log Status is either EXPECTED/ NOT_EXPECTED
            assignment_type (str): SUCCESS/FAILURE, if success one log should ge generated, and if failure two logs should be generated
        """
        
        log_file_count = 0
        self.job_result_files = 0
        self.err_log_files = 0
        self.files_with_incomplete_content = 0
        self.download_failure = 0
        self.api_gen_obj.update_timeout_time(timer)
        self.api_gen_obj.start_timer()
        
        while (self.api_gen_obj.check_timer() == True):
            r = self.api_requests.get_request(constants.OTA_CORE_ASSIGNMENT + assignment_id)
            assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
            if "logFile" in r.json()['_links']:
                log_file_count= len(r.json()['_links']["logFile"])
            time.sleep(5)
        
        logging.info(f'The log file count is {log_file_count} for this OTA assignment {assignment_id}')
        if(log_file_count > 0 ):
            self.__read_log_file(r.json()['_links']["logFile"])
        
        if assignment_type == "SUCCESSFUL" and ( log_file_count !=1 or self.job_result_files != 1 or self.err_log_files != 0 or self.files_with_incomplete_content != 0 or self.download_failure != 0):
            assert False, f'''Log validation failure for a successful OTA Assignment {assignment_id}
            Expected: log_file_count = 1 ,  job_result_files = 1, err_log_files = 0
            Actual: log_file_count = {log_file_count} ,  job_result_files = {self.job_result_files}, err_log_files = {self.err_log_files}
            Files with incomplete content = {self.files_with_incomplete_content}, Download Failure = {self.download_failure}'''
        elif assignment_type == "FAILED" and ( log_file_count !=2 or self.job_result_files != 1 or self.err_log_files != 1 or self.files_with_incomplete_content != 0 or self.download_failure != 0):
            assert False, f'''For a Failed OTA Assignment {assignment_id}
            Expected: log_file_count = 2 ,  job_result_files = 1, err_log_files = 1
            Actual: log_file_count = {log_file_count} ,  job_result_files = {self.job_result_files}, err_log_files = {self.err_log_files}
            Files with incomplete content = {self.files_with_incomplete_content}, Download Failure = {self.download_failure}'''
            
    def __read_log_file(self, log_file_links):
        """Reads the Log file and checks for the availability fo the predefined file list inside the extracted zip log file

        Args:
            log_file_links (dict/list): logFile variable from the OTA assignment
        """
        def verify_data(self, url):
            logging.info(url.split(constants.API_BASE_URL)[1])
            r = self.api_requests.get_request(url.split(constants.API_BASE_URL)[1])
            if r.status_code != requests.codes.ok:
                logging.error(f"Unable to download log file current status code: {r.status_code}")
                self.download_failure += 1
                return
            file_details = r.headers['content-disposition']
            if "JobResult" in file_details:
                self.job_result_files += 1
                exp_file_list = constants.OTA_JOB_RESULT_CONTENT
            elif "ETTDRLOG" in file_details:
                self.err_log_files += 1
                exp_file_list = constants.OTA_ETTDRLOG_CONTENT

            log_zip_file = ZipFile(BytesIO(r.content))
            log_file_names = log_zip_file.namelist()
               
            for exp_file in exp_file_list:
                logging.info(f"Checking existence of file - {exp_file} in generated device logs")
                if exp_file not in log_file_names:
                    if not re.search(exp_file, str(log_file_names), re.IGNORECASE):
                        logging.error(f"Downloaded device logs doesn't have expected file content, {exp_file} file not present")
                        self.files_with_incomplete_content += 1
        
        logging.info("Downloading log files for the assignment")
        if type(log_file_links) == list:
            for log_file_url in log_file_links:
                verify_data(self, log_file_url["href"])
        else:
            verify_data(self, log_file_links["href"])
    
    def verify_ota_status_history(self, assignment_id, exp_status, exception_status_list):
        actual_ota_status_list = self.get_ota_status_history(assignment_id)
        if exp_status in actual_ota_status_list:
            logging.warning(f"Assignment status are not in proper order but expected status - {exp_status} is present in status history")
            exception_status_list.clear()
        else:
            logging.error(f"Expected status:{exp_status} did not appear for assignment {assignment_id} in history, History data: {actual_ota_status_list}")
        return exception_status_list

    def fetch_expected_device_version(self, actual_version, config_userdata):
        device_type = config_userdata["device_type"].upper()
        desired_default_fw_version = self.api_gen_obj.fetch_fw_based_on_customer(device_type)
        expected_fw_version = config_userdata["Desired_FW_Version"] if "Desired_FW_Version" in config_userdata and config_userdata["Desired_FW_Version"] != '' else desired_default_fw_version
        logging.debug(f"Fetching expected device version: device type: {device_type}, Desired_default_fw = {desired_default_fw_version}, Expected_fw = {expected_fw_version}, actual_fw {actual_version}")
        if expected_fw_version != desired_default_fw_version:
            try:
                default_version = version.parse(desired_default_fw_version)
                desired_version = version.parse(expected_fw_version)
                if desired_version > default_version and len(expected_fw_version.split(".")) == 3:
                    self.api_gen_obj.update_default_customer_fw(device_type, expected_fw_version)
                    self.api_gen_obj.push_changes_to_repo(constants.DESIRED_FW_FILE, constants.DESIRED_FW_FILE)
                return expected_fw_version
            except Exception as e:
                logging.error(f"Failed to compare exp version:{expected_fw_version} and default version: {desired_default_fw_version} or publishing to git is failed {e}")
                return expected_fw_version
        elif desired_default_fw_version == constants.INITIAL_DEFAULT_VERSION:
            return actual_version
        else:
            return desired_default_fw_version
        

    def check_delta_package_availability(self, device_config_data, from_version, to_version):
        package_name = constants.DELTA_UPDATE_DP_FORMAT.format(from_version, to_version, device_config_data['su_security_option'],device_config_data['firmware_type'])
        distribution_package_id = self.search_distribution_package(package_name)
        if distribution_package_id is not None:
            package_availability = True
        else:
            logging.info(f"Distribution package doesn't exist with name: {package_name}. So, checking package in artifactory for given versions")
            package_availability = self.check_delta_package_in_artifact(device_config_data, from_version, to_version)
        return package_availability

    def perform_device_update(self,context,type_of_update,actual_device_version,specimen_device,exp_device_version):
        if actual_device_version != exp_device_version:
            if context.device_config_data["artifactory"] == "TCU_artifactory":
                if type_of_update == 'Delta_Update' and self.check_delta_package_availability(context.device_config_data, actual_device_version, exp_device_version):
                    context.execute_steps(f'''
                        Given Perform Delta update for device "{specimen_device}" from "{actual_device_version}" to "{exp_device_version}"
                    ''')
                elif type_of_update == 'USB_Update':
                    context.execute_steps(f'''
                        Given Perform USB update for device "{specimen_device}" to "{exp_device_version}"
                    ''')
                else:
                    context.execute_steps(f'''
                        Given Perform Full update of CCU device "{specimen_device}" to "{exp_device_version}"
                    ''')
            elif context.device_config_data["artifactory"] == "TCU2_artifactory":
                context.execute_steps(f'''
                    Given Perform Full update of CCU-M device "{specimen_device}" to "{exp_device_version}"
                ''')
            context.execute_steps('''
                Given Perform PEA update
            ''')
            logging.info(f"Device - {specimen_device} updated successfully and it has expected FW - {exp_device_version}")


    def __get_artifact_data(self, artifactory):
        """
            gets Artifactory related data and stores into a variable
        """
        self.path = os.path.dirname(os.path.abspath(__file__))
        config_data = self.api_gen_obj.parse_json_file(constants.TEST_CONFIG_JSON)
        self.device_env = re.search(constants.REGEX_ENVIRONMENT_URL, config_data["systemUnderTest"][self.env]["ApiBaseURI"]).groups()[0].split(".")[-2]
        logging.info(f"Device env = {self.device_env}")
        self.artifactory_url=config_data[artifactory]['url']
        artifactory_credentials= config_data[artifactory]['credentials']
        self.artifact_header = {
                                    'Authorization': "Basic " + artifactory_credentials,
                                    'accept': '*/*',
                                    'content-type': 'text/html',
                                    'User-Agent': 'Python Requests library'
                                }
        
        
    def download_from_artifactory(self, device_config_data,  to_version, from_version = None, package_type = "UPDATE_PACKAGE"):
        """Downloads the Delta/ Full update update package or USB Update Image from Artifactory

        Args:
            artifactory_path (_type_): Customer specific path to be fetched Eg: "Paccar/Debug"
            to_version (_type_): Version folder which to be fetched from Artifactory
            from_version (_type_, optional): Required in case of Delta Update. Else None, Full Update package will be created if from Version is None
            package_type (str, optional): There are two package types USB_UPDATE (USB Update Firmware), UPDATE_PACKAGE (Backend Update Package). Defaults to "UPDATE_PACKAGE".

        Returns:
            download_path: For USB Update, where the downloaded file is stored
            zip_name(string): name of the downloaded zip file for Update packages
        """
        self.__get_artifact_data(device_config_data['artifactory'])
        if package_type.upper() == "USB_UPDATE":
            download_path = self.path + constants.ARTIFACTORY_IMAGE_PATH
            self.download_image_zip_from_artifactory(device_config_data, download_path, to_version)
            return download_path
        else:
            download_path = self.path+constants.ARTIFACTORY_DOWNLOAD_FILE_PATH
            zip_name = self.download_package_from_artifactory(device_config_data, download_path, to_version, from_version)
            return zip_name

    def __artifactory_get_request(self, url):
        """
            Performs get request to the Artifactory

        Args:
            url (string): URL in the artifactory

        Returns:
            response: complete response of GET Request
        """
        r = requests.get(url, headers=self.artifact_header)
        assert r.status_code == requests.codes.ok, f"Request URL: {url}, Error: {self.api_gen_obj.assert_message(r)}"
        return r
    
    def fetch_hyperlink_from_html(self, html_response, regex_text, must_available = True):
        """Checks availability of  regex Text in html response, returns first available regex string

        Args:
            html_response (response.text): response in text format
            regex_text (string): regex to ge checked
            must_available (bool, optional): To check if the regex must be available in the system. Defaults to True.

        Returns:
            hyperlink: Hyperlink if its available else None
        """
        hyperlink = None
        html_file = BeautifulSoup(html_response.text, "html.parser")
        for link in html_file.find_all('a'):
            target_string=(link.get('href'))
            req_zip_link=re.search(regex_text, target_string, re.IGNORECASE)
            if req_zip_link != None:
                hyperlink=urllib.parse.unquote(target_string)
                break
        if must_available: #In Pipeline stage(Check device version), to avoid failing the test even though package is not available. i.e delta package is not available, perform FULL UPDATE
            assert hyperlink != None , f"The requested link: {regex_text} is not found in artifactory"
        return hyperlink
    
    def __download_zip_from_artifactory(self, download_url, download_path):
        """Performs zip download from artifactory and extracts the downloaded file

        Args:
            download_url (uri): URL of the zip file
            download_path (path): path where file should be downloaded and extracted
        """
        logging.info(f"Download URL: {download_url}")
        download_response = self.__artifactory_get_request(download_url)
        zip_file = ZipFile(BytesIO(download_response.content))
        zip_file.extractall(download_path)

    def download_package_from_artifactory(self,  device_config_data, download_path, update_to_version, update_from_version):
        """  Downloads the Update Package from Artifactory
        Args:
            download_path (_type_): Folder where file should be downloaded
            artifactory_path (_type_): Customer specific path to be fetched Eg: "Paccar/Debug"
            update_to_version (_type_): Version folder which to be fetched from Artifactory
            update_from_version (_type_, optional): Required in case of Delta Update. Else None, Full Update package will be created if from Version is None

        Returns:
            zip_file_name: Name of the downloaded zip file
        """
        artifactory_path =  device_config_data['artifact_customer'] + "/" +  device_config_data['firmware_type']
        if( device_config_data['artifactory'] == "TCU_artifactory"):
            regex_to_version_folder = constants.REGEX_TCU1_FOLDER.format(update_to_version = update_to_version)
            if update_from_version != None:
                zip_file_regex = constants.DELTA_UPDATE_TCU1_REGEX.format(update_from_version=update_from_version.replace(".","\."), update_to_version=update_to_version.replace(".","\."),firmware_type=device_config_data['firmware_type'] )
            else:
                zip_file_regex=constants.FULL_UPDATE_TCU1_REGEX.format(update_to_version=update_to_version.replace(".","\."),firmware_type= device_config_data['firmware_type'])
        else:
            regex_to_version_folder = constants.REGEX_TCU2_FOLDER.format(env=self.device_env.upper(),update_to_version=update_to_version.replace(".","\."))
            zip_file_regex = constants.FULL_UPDATE_TCU2_REGEX
        logging.debug(f"Regex to version folder: {regex_to_version_folder} Zipfile regex: {zip_file_regex}")
        logging.info(f"Downloading Update Package at {download_path}")
        artifactory_home_page_data = self.__artifactory_get_request(self.artifactory_url)
        base_folder_url = self.fetch_hyperlink_from_html(artifactory_home_page_data, regex_to_version_folder)
        logging.debug(f"Update_package base folder hyperlink: {base_folder_url}")
        folder_url = self.__get_folder_url(artifactory_path, base_folder_url, self.artifactory_url)
        su_folder_url = folder_url + "self-updates/"
        logging.debug(f"SU URL: {su_folder_url}")
        su_folder_response = self.__artifactory_get_request(su_folder_url)
        zip_file_name = self.fetch_hyperlink_from_html(su_folder_response, zip_file_regex)
        download_url=f"{su_folder_url}{zip_file_name}"
        self.__download_zip_from_artifactory(download_url,download_path)
        return zip_file_name

        
    def download_image_zip_from_artifactory(self, device_config_data, download_path, to_version):
        """
        Downloads the Image zip file from artifactory
        """
        artifactory_path = device_config_data['artifact_customer'] + "/" +  device_config_data['firmware_type']
        if( device_config_data['artifactory'] == "TCU_artifactory"):
            regex_to_version_folder = constants.REGEX_TCU1_FOLDER.format(update_to_version = to_version)
        else:
            regex_to_version_folder = constants.REGEX_TCU2_FOLDER.format(env=self.device_env.upper(),update_to_version=to_version)
        logging.info(f"Downloading USB Image at {download_path}")
        artifactory_home_page_data = self.__artifactory_get_request(self.artifactory_url)
        base_folder_url = self.fetch_hyperlink_from_html(artifactory_home_page_data,regex_to_version_folder)
        folder_url = self.__get_folder_url(artifactory_path, base_folder_url, self.artifactory_url)
        folder_response = self.__artifactory_get_request(folder_url)
        zip_file_name = self.fetch_hyperlink_from_html(folder_response,constants.USB_IMAGE_FILE)
        download_url = f"{folder_url}{zip_file_name}"
        self.__download_zip_from_artifactory(download_url, download_path)
        return zip_file_name


    def __get_folder_url(self, artifactory_path, base_folder_url, artifactory_url): 
        #Fw released after 4.11.1 has customer name (i.e) paccar and hino in end URL. To check given FW is released after or before 4.11.1 we have hardcorded 4.11.1 release date.
        fw_4_11_1_date = "2022-03-24" 
        date_list = str(base_folder_url).split('_')
        if fw_4_11_1_date >= date_list[0]:
            basic_url=f"{artifactory_url}{base_folder_url}Debug/"
        else:
            basic_url=f"{artifactory_url}{base_folder_url}{artifactory_path}/"
        return basic_url

    def check_delta_package_in_artifact(self, device_config_data, from_version, to_version):
        """
        Checks if Delta Package is available for the specified version in the artifactory

        Args:
            artifactory_path (string): path in artifactory eg: Paccar/Debug
            from_version (string): update from version
            to_version (string): update to version

        Returns:
            boolean: Returns true if delta update package exists, else false
        """
        self.__get_artifact_data(device_config_data['artifactory'])
        file_available = False
        artifactory_path = device_config_data['artifact_customer'] + "/" + device_config_data['firmware_type']
        if(device_config_data['artifactory'] == "TCU_artifactory"):
            regex_to_version_folder = constants.REGEX_TCU1_FOLDER.format(update_to_version = to_version)
            zip_file_regex = constants.DELTA_UPDATE_TCU1_REGEX.format(update_from_version=from_version.replace(".","\."), update_to_version=to_version.replace(".","\."),firmware_type=device_config_data['firmware_type'] )
        else:
            regex_to_version_folder = constants.REGEX_TCU2_FOLDER.format(env=self.device_env.upper(),update_to_version=to_version.replace(".","\."))
            zip_file_regex = constants.DELTA_UPDATE_TCU2_REGEX
            #TODO Logic in TCU2 to fetch Delta Package
            return False
        logging.debug(f"Regex to version_folder: {regex_to_version_folder} Zip File regex: {zip_file_regex}")
        try:
            artifactory_home_page_data = self.__artifactory_get_request(self.artifactory_url)
            base_folder_url = self.fetch_hyperlink_from_html(artifactory_home_page_data, regex_to_version_folder, must_available = False)
            if base_folder_url:
                folder_url = self.__get_folder_url(artifactory_path, base_folder_url, self.artifactory_url)
                su_folder_url = folder_url + "self-updates/"
                logging.info(f"SU URL: {su_folder_url}")
                su_folder_response = self.__artifactory_get_request(su_folder_url)
                file_data = self.fetch_hyperlink_from_html(su_folder_response, zip_file_regex,must_available= False)
                if file_data != None:
                    logging.info(f"Delta Update Package is available from {from_version} to version {to_version} in artifactory")
                    file_available = True
                else:
                    logging.info(f"Delta Update Package is not available from {from_version} to version {to_version} in artifactory")       
        except AssertionError as e:
            logging.error(f"Unable to locate the delta package in the Artifact, error {e}")
        return file_available
    
    def check_desired_state_package(self,package_name):
        """checks desired state package availability
        
        Args:
        package_name(string) : desired state package name to be searched

        Returns:
        boolean: True if available, False if not available
        """
        ep = constants.DS_PACKAGE_NAME.format(package_name)
        response = self.api_requests.get_request(ep=ep)
        if (response.status_code == requests.codes.ok):
            return True
        else:
            return False
        
    def create_desired_state_package(self, package_name):
        """creates desired package
        
        Args:
        package_name(string) : desired state package name, should be present in Desired_states.json
        """
        api_gen_obj = API_Generic_Class.ApiGenericClass()
        desired_state_json_data = api_gen_obj.parse_json_file(constants.DESIRED_STATE_JSON)
        desired_state_data = desired_state_json_data["packages"][package_name]
        response = self.api_requests.post_request(constants.DESIRED_STATE, params= desired_state_data)
        assert response.status_code == requests.codes.created, self.api_gen_obj.assert_message(response)
        logging.info(f"Desired state {package_name} created")
    
    def assign_desired_state_package(self, vehicle_id,package_name):
        """
        Assigns desired state assignment payload
        
        Args:
        vehicle_id(string): Vehicle id
        package_name(string): desired state package name

        Returns:
        desired_state_assignment_id(string): created desired stated assignment id

        """
        assignment_payload = {
                                "desiredState": {
                                    "name": package_name
                                },
                                "target": {
                                    "id": vehicle_id,
                                    "targetType": "VEHICLE"
                                }
                            }
        response = self.api_requests.post_request(constants.DESIRED_STATE_ASSIGNMENT, assignment_payload)
        assert response.status_code == requests.codes.created, self.api_gen_obj.assert_message(response)
        desired_state_assignment_id = response.json()['desiredStateAssignmentId']
        return desired_state_assignment_id
    
    def check_desired_state_assignment_status(self, desired_state_assignment_id, exp_status, exp_sub_status, timer):
        """Validates expected desired state assignment status and sub status 

        Args:
        desired_state_assignment_id(string): desired state assignment id
        exp_status(string): expected desired state assignment status to validate
        exp_sub_status(json): expected desired state assignment sub status to validate
        timer(string): 

        """
        all_status = []
        validation = False
        ep = constants.DESIRED_STATE_ASSIGNMENT_ID.format(desired_state_assignment_id)
        time_out_time = time.time() + (int(timer))*2
        while (time.time() < time_out_time) and not validation:
            r = self.api_requests.get_request(ep=ep)
            assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
            desired_state_status = r.json()["status"]
            if not validation:
                validation, actual_sub_status = self.check_sub_status_of_actions(validation,exp_sub_status,r.json())
            
            if desired_state_status not in all_status:
                all_status.append(desired_state_status)
                logging.info(f"New desired state status appears - {desired_state_status} and sub status - {actual_sub_status}")

            if desired_state_status == exp_status and validation:
                logging.info(f"Expected status - {desired_state_status} and sub status {actual_sub_status} of desired state assignment appears.")
                break   
            
            time.sleep(1)
        
        if (time.time() > time_out_time) and (desired_state_status != exp_status or not validation):
            assert False, f"Wrong Desired state status and sub status appears. Current status is - {desired_state_status} and {actual_sub_status}"
        logging.info(f"Desired state assignment all status {all_status}")
        
    def check_sub_status_of_actions(self,validation, exp_sub_status, response):
        """Checks sub status of each actions with expected sub status

        Args:
        validation (boolean): To validate actual sub status with expected sub status
        exp_sub_status (dict): expected sub status of desired state assignment 
        response (json): response of the desired state assignment

        returns:
        validation (boolean): True if expected sub status matches actual sub status else returns False
        actual_sub_status (dict): actual sub status of assigned desired state
        """
        actual_sub_status = {}
        exp_sub_status = json.loads(exp_sub_status)
        for each_component in exp_sub_status:
            for each_action in response["actions"]:
                if each_action["component"]["id"] == each_component:
                    actual_sub_status[each_component] = each_action["status"]
        if exp_sub_status == actual_sub_status: 
            validation = True 
        return validation, actual_sub_status   

    def check_desired_state_assignment_message(self, desired_state_assignment_id):
        """Checks desired state assignment message
        
        Args:
        desired_state_assignment_id(string): assigned desired state assignment id
        """

        ep = constants.DESIRED_STATE_ASSIGNMENT_ID.format(desired_state_assignment_id)    
        r = self.api_requests.get_request(ep=ep)
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        desired_state_message = r.json()["statusMessage"]
        return desired_state_message
       
