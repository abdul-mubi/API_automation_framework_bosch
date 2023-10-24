import os
import json
import time
from src.common.fileutils import FileUtil
import src.common.constants as constants
from src.common.apiutils import ApiRequests
from atlassian_api.jira_api import JiraAPI,XRayAPI
from src.common.logger import get_logger
log = get_logger()

base_path = os.path.dirname(os.path.abspath(__file__)) + "/../../"

config_path = base_path + "common/TestData/testConfig.json"
with open(config_path, 'r') as dataFile:
    config_data = json.load(dataFile)

jira_api = JiraAPI(config_data["jira"]["ApiBaseURI"],config_data["jira"]["qg_token"])
xray_api = XRayAPI(config_data["jira"]["ApiBaseURI"],config_data["jira"]["qg_token"])

class JiraOperation:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.test_file_path = self.base_path + constants.TEST_FILE_PATH
        self.input_data_path = self.base_path + constants.INPUT_DATA_PATH
        self.file_util_obj = FileUtil()
        self.api_util_obj = ApiRequests()

    def read_testruns_from_testexec(self, test_execution_key):
        """Reads and stores testruns from test execution details as per input data
        Args:
            test_execution_key (str): JIRA Test Execution ID
        """
        r = xray_api.get_tests_from_test_execution(test_execution_key)
        self.file_util_obj.write_json_file(self.test_file_path, r)

    def update_testrun(self, status=None):
        """Execute all testruns from json and updates with status
        Args:
            status (str): JIRA Test Status [PASS, FAIL, GREEN, TODO]
        """
        qg_testdata = self.file_util_obj.parse_json_file(self.test_file_path)
        for testrun in qg_testdata:
            testrun_id = testrun["id"]
            if status is not None:
                xray_api.update_test_run_status(testrun_id,testrun["status"])
                xray_api.add_comment_for_test_run(testrun_id,testrun["comment"])
            else:
                xray_api.update_test_run_status(testrun_id,status)
            time.sleep(5)

    def get_comment_for_testruns(self, testrun_id, returntype):
        """ Method to read comments for testruns input
        Args:
            testrun_id (JIRA-ID): Jira testrun ID
            returntype: Raw or Rendered from json response
        Returns:
            [Json value]: Returns requested action type value [Rendered or Raw]
        """
        try:
            r = xray_api.get_comment_for_test_run(testrun_id)
            if returntype == "raw":
                return r.json()["raw"]
            else:
                return r.json()["rendered"]
        except AssertionError:
            return "Comment not found"
        

    def get_summary_for_test(self, test_key):
        """Gets Summary for the provided input test
        Args:
            test_key (str): JIRA Test ID
        Returns:
            [String]: Returns summary of Jira Test
        """
        r = jira_api.get_issue_details(test_key)
        return r["fields"]["summary"]

    def get_status_for_test(self, test_key):
        """Gets Status for the provided input test
        Args:
            test_key (str): JIRA Test ID
        Returns:
            [String]: Returns status of Jira Test
        """
        r = jira_api.get_issue_details(test_key)
        return r["fields"]["status"]["name"]

    def validate_jira_issue(self, url_list):
        """Method to validate Jira issue status
        Args:
            jira_url (str): JIRA URL
        Returns:
            [Boolean]: Returns True or False depends on Jira issue status
        """
        status = set()
        for jira_url in url_list:
            if constants.ARTMC in jira_url:
                issue = jira_url.split("browse")[1].strip("/")
                issue_status = self.get_status_for_test(issue)
                if status != constants.JIRA_STATUS_CLOSED:
                    status.add(issue_status)
        if status:
            return True
        else:
            return False

    def export_test_execution(self, test_execution_id):
        """
            Export Test Execution with test execution ID
        
        Args:
            test_execution_id (string): Test Execution ID
        Returns:
            Json: Returns the response json
        """
        overall_execution_status = xray_api.export_test_execution(test_execution_id)
        return overall_execution_status

    def update_testrun_input_json(self, test_execution_id, test_execution_data):
        """
        Filters the parameters from testrun json to form input json
        Args:
            testrun_json: Holds the testrun for TE
        Returns:
            Json: Returns the filtered json
        """
        input_data_json = self.file_util_obj.parse_json_file(self.input_data_path)
        input_data_json["tests"] = input_data_json["tests"] + test_execution_data
        for testrun in input_data_json["tests"]:
            del testrun["id"]
            del testrun["testExecKey"]
            del testrun["archived"]
        input_data_json["info"]["summary"] = f"Cloned - {test_execution_id}"
        input_data_json["info"]["project"] = test_execution_id.split("-")[0]
        self.file_util_obj.write_json_file(self.input_data_path, input_data_json)

    def import_test_execution(self):
        """
        Import Test Execution along with Input Json data

        Args:
            test_json: Holds overall test execution status which imported in TE
        Returns:
            Json: testExecIssue Information
        """
        input_json = self.file_util_obj.parse_json_file(self.input_data_path)
        r = xray_api.import_test_execution(input_json)
        key = r["testExecIssue"]["key"]
        log.info(f"New TE created with same execution info. Please find the Jira Ticket: {key}")
        path = base_path + "temp/console.txt"
        with open(path, "w+") as text_file: text_file.write(key)