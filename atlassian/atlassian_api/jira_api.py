import io
import logging
import os
import re
import atlassian_api.constants as constant
from atlassian_api.atlassian_api_requests import AtlassianAPIRequests
import zipfile
import logging
import json
import time

log = logging.getLogger()


class JiraAPI:
    def __init__(self, base_url, token) -> None:
        """
        Requires the BASE URL of the JIRA System and the access token to to authorize user to the system

        Args:
            base_url (str): Base URL of JIRA (Eg: https://example.com )
            token (str): Access token (Basic and Bearer tokens can be added) Eg: Bearer <TOKEN> or Basic <B64-encoded-username&pwd>
        """
        self.jira_api = AtlassianAPIRequests(base_url, token)
        

    def create_issue(self, issue_type, project_key, summary = None, description = None):
        """
            Creates issue in JIRA
        Args:
            issue_type (string): Jira issue type Eg: Test Execution, Test Plan
            project_key (String): Jira Project Key
            summary (string): Optional parameter, summary of the Ticket
        Returns:
            Issue_ID: Created Jira Ticket ID
        """
        log.debug(f"Creating issue with type as {issue_type}")
        if summary == None:
            summary = "Automation " + issue_type
        if description == None:
            description = " "
            
        data = {
                "fields": {
                "project": {
                    "key": project_key
                },
                "summary": summary,
                "description": description,
                "issuetype": {
                        "name": issue_type
                        }
                    }
                }
        response = self.jira_api.post_request(constant.JIRA_URL + "issue", data=data)
        issue_id = response.json()['key']
        return issue_id


    def get_issue_details(self, issue_id):
        """Returns issue details JSON file

        Args:
            issue_id (str): Jira Ticket id

        Returns:
            dictionary: Details of the Issue
        """
        response = self.jira_api.get_request(constant.ISSUE_ID_URL.format(issue_id=issue_id))
        return response.json()
    
    def update_issue(self, issue_id, data):
        """Updates the specific issue with the provided Data

        Args:
            issue_id (str): Jira Ticket Id
            data (dictionary): Details about the fields which need to be updated
        """
        self.jira_api.put_request(constant.ISSUE_ID_URL.format(issue_id=issue_id),data)
    
    def get_linked_issues(self, issue_id):
        """
        Returns details of the linked issues to the Jira Ticket

        Args:
            issue_id (str): Jira Ticket Id

        Returns:
            List: Returns list of Dictionary that contains information about the linked issues
        """
        data = self.get_issue_details(issue_id)
        return data['fields']['issuelinks']
            
    def get_filter_details(self, filter_id):
        """Returns the Filter Details

        Args:
            filter_id (str): JIRA Filter ID

        Returns:
            Dictionary: Contains the filter Info
        """
        response = self.jira_api.get_request(constant.FILTER_ID_URL.format(filter_id=filter_id))
        return response.json()

    def fetch_jql_query_from_filter(self, filter_id):
        """Returns JQL Query of particular filter

        Args:
            filter_id (str): JIRA Filter ID

        Returns:
            str: JQL Query
        """
        filter_data = self.get_filter_details(filter_id)
        return filter_data["jql"]
    
    def perform_jql_query(self, query):
        """Performs search based on JQL query and returns ["key","issuetype","summary","priority","status","created","updated"] fields for the matching Jira Tickets

        Args:
            query (str): JQL Query

        Returns:
            Dictionary: Response that contains the data
        """
        data = {
            'jql': query,
            'fields': ["key","issuetype","summary","priority","status","created","updated"],
            "maxResults": 2000
        }
        response = self.jira_api.post_request(constant.SEARCH_URL, data)
        return response.json()
    
    def get_issues_from_jql_query(self, query):
        """Gets of issues from Provided JQL query and returns the list

        Args:
            query (str): JQL Query

        Returns:
            list: List of issues
        """
        issue_list = []
        data = self.perform_jql_query(query)
        if(data["issues"]):
            issue_list = [ issue['key'] for issue in data["issues"] ]
        return issue_list

class XRayAPI:
    def __init__(self,base_url, token) -> None:
        """
        Requires the BASE URL of the JIRA System and the access token to to authorize user to the system

        Args:
            base_url (str): Base URL of JIRA (Eg: https://example.com )
            token (str): Access token (Basic and Bearer tokens can be added) Eg: Bearer <TOKEN> or Basic <B64-encoded-username&pwd>
        """
        self.jira_api = AtlassianAPIRequests(base_url, token)

    def import_tests(self, path, jira_id = None, filter_id = None):
        """Imports the cucumber tests based on Jira ID/ Filter ID to the specified path

        Args:
            path (str): Path where, tests should be extracted
            jira_id (str, optional): Jira Test IDs, separated by semi column . Defaults to None.
            filter_id (str, optional): Jira Filter ID. Defaults to None.
        """
        if jira_id!= None:
            response = self.jira_api.get_request(constant.XRAY_URL + f"export/test?keys={jira_id}")
        elif filter_id!= None:
            response = self.jira_api.get_request(constant.XRAY_URL + f"export/test?filter={filter_id}")
        else:
            assert False, "Test ID/ Filter ID must be defined to import the tests"
        
        content_data =  response.headers.get("content-disposition")
        fname = re.findall('filename=(.+)', content_data)
        if len(fname) == 0:
            assert False, "No File is found in the response"
        file_name = fname[0].replace("\"","")
        
        if file_name == constant.DOWNLOADED_ZIP_NAME:
            print("Feature content is zip, unzipping the content")
            z = zipfile.ZipFile(io.BytesIO(response.content))
            z.extractall(path)
        elif constant.FEATURE_FILE_EXT in file_name:
            with open(path + "/" + file_name, 'wb') as f:
                f.write(response.content)
        else:
            assert False, f"Unable to process received file format {file_name}"


    def export_tests(self, project_key, path, file_name = None, time_hr = None):
        """Exports cucumber tests available in the specified path to the JIRA Project

        Args:
            project_key (str): JIRA Project Key
            path (str): Path where tests should be stored
            file_name (str, optional): Incase only Specific file should be synced. Defaults to None.
            time_hr(int, optional): Incase files updated in past hours need to be updated
        """
        
        file_modified_time = 0 if time_hr== None else time.time() - int(time_hr) * 3600
        try:
            if(file_name != None):
                file_data = open(path + "/" + file_name , 'rb')
                file_content = {'file': file_data }
                self.jira_api.post_request_with_files(constant.XRAY_URL + f"import/feature?projectKey={project_key}", file_content)
                file_data.close()
            else:
                filelist = []
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if os.stat(os.path.join(root,file)).st_mtime >= file_modified_time:
                            filelist.append(os.path.join(root,file))
                filelist   = [file_name for file_name in filelist if file_name.endswith(".feature")]
                with zipfile.ZipFile('features.zip', 'w') as zip_data:
                    for file in filelist:
                        zip_data.write(file, os.path.basename(file), compress_type=zipfile.ZIP_DEFLATED)
                file_data = open("features.zip" , 'rb')
                file_content = {'file': file_data}
                self.jira_api.post_request_with_files(constant.XRAY_URL + f"import/feature?projectKey={project_key}", file_content)
                file_data.close()
                os.remove("features.zip")
        except FileNotFoundError as e:
            assert False, f"Expected file / path is not available: {e}"


    def update_tests_in_test_execution(self, test_execution_id, tests_to_add_list = None, tests_to_remove_list = None):
        """Updates tests in Test Execution

        Args:
            test_execution_id (string): Test Execution ID
            tests_to_add_list (list, optional): Tests to be added to Test Execution list. Defaults to None.
            tests_to_remove_list (list, optional): Tests to be removed from Test Execution list. Defaults to None.
        """
        if tests_to_add_list is None:
            tests_to_add_list = []
        if tests_to_remove_list is None:
            tests_to_remove_list = []
        update = {"add": tests_to_add_list, "remove": tests_to_remove_list}
        self.jira_api.post_request(constant.XRAY_API_URL + f"testexec/{test_execution_id}/test", update)


    def get_tests_from_test_execution(self, test_execution_id):
        """Returns test details for the test execution

        Args:
            test_execution_id (string): Test Execution ID

        Returns:
            list: List of dictionary that contains tests
        """
        response = self.jira_api.get_request(constant.XRAY_API_URL + f"testexec/{test_execution_id}/test?detailed=true")
        return response.json()
    
    def get_tests_list_from_test_execution(self, test_execution_id):
        """Returns list of test keys from Test execution

        Args:
            test_execution_id (string): Test Execution ID
        Returns:
            list: Test Keys
        """
        test_data = self.get_tests_from_test_execution(test_execution_id)
        test_list = [test['key'] for test in test_data]
        return test_list


    def update_test_execution_in_test_plan(self, test_plan_id, execution_to_add_list=None, execution_to_remove_list=None):
        """Updates the test execution details in test plan, currently it uses V2 Xray APIs.
        
            Note: Slowness is observed while executing the following API call, Alternately add_test_execution_in_test_plan, remove_test_execution_from_test_plan methods can be used
        

        Args:
            test_plan_id (str): Test Plan ID
            execution_to_add_list (list, optional): List of Test Executions to be added. Defaults to None.
            execution_to_remove_list (list, optional): List of Test Executions to be removed. Defaults to None.
        """
        if execution_to_add_list is None:
            execution_to_add_list = []
        if execution_to_remove_list is None:
            execution_to_remove_list = []
        update = {"add": execution_to_add_list, "remove": execution_to_remove_list}
        self.jira_api.post_request(constant.TEST_PLAN_TE_URL.format(test_plan_id=test_plan_id), update)

    def add_test_execution_in_test_plan(self, test_plan_id, execution_to_add_list):
        """
            This uses V1 API of XRay to Add  test execution to the Test Plan
        Args:
            test_plan_id (str): Test Plan ID
            execution_to_add_list (list, optional): List of Test Executions to be added.
        """

        data = {"keys": execution_to_add_list}
        self.jira_api.post_request(constant.TEST_EXEC_UPDATE.format(test_plan_id = test_plan_id), data)
        
    def remove_test_execution_from_test_plan(self, test_plan_id, execution_to_remove_list):
        """Removes each Test execution Individually from Test Plan

        Args:
            test_plan_id (str): Test Plan ID
            execution_to_remove_list (list, optional): List of Test Executions to be removed.
        """
        
        for each_te in execution_to_remove_list:
            self.jira_api.delete_request(constant.TEST_PLAN_TE_URL.format(test_plan_id=test_plan_id) + f"/{each_te}")
    
    def get_test_execution_from_test_plan(self, test_plan_id):
        """Returns the Test execution details for test plan

        Args:
            test_plan_id (str): Test Plan ID

        Returns:
            dictionary: Details of the Test Executions
        """
        response = self.jira_api.get_request(constant.TEST_PLAN_TE_URL.format(test_plan_id=test_plan_id))
        return response.json()

    def upload_cucumber_result(self, cucumber_result_path, info_file_path = None):
        """Uploads the cucumber result json to the backend

        Args:
            cucumber_result_path (str): Path to cucumber JSON file
            info_file_path (str, optional): Path to Issue fields file. Defaults to None.

        Returns:
            str: Test Execution ID
        """
        if info_file_path == None:
            with open(cucumber_result_path, 'r') as dataFile:
                json_data = json.load(dataFile)
            response = self.jira_api.post_request(constant.XRAY_URL + "import/execution/cucumber", data = json_data)
        else:
            file_content = {'result': open(cucumber_result_path , 'rb'), 'info': open(info_file_path , 'rb')}
            response = self.jira_api.post_request_with_files(constant.XRAY_URL + "import/execution/cucumber/multipart", file_content)
        return response.json()["testExecIssue"]["key"]


    def get_details_by_run_id(self, test_run_id):
        """Returns Details for the test run id

        Args:
            test_run_id (str): Test run ID

        Returns:
            dictionary: Contains information related to test RUN
        """
        response = self.jira_api.get_request(constant.TEST_RUN_ID_URL.format(test_run_id=test_run_id))
        return response.json()


    def update_test_run_status(self, test_run_id, status): 
        """Updates the status of Test Run

        Args:
            test_run_id (str): Test run ID
            status (str): Status
        """
        update_data = {
            "status": status
            }
        self.jira_api.put_request(constant.TEST_RUN_ID_URL.format(test_run_id=test_run_id), update_data)


    def update_defects_in_test_run(self, test_run_id, defects_to_add_list = [], defects_to_remove_list = []): 
        """Updates defects for a Test Run

        Args:
            test_run_id (str): Test run ID
            defects_to_add_list (list, optional): List of Defects to add. Defaults to [].
            defects_to_remove_list (list, optional): List of Defects to removes. Defaults to [].
        """
        update_data = {
            "defects": {
                "add": defects_to_add_list, 
                "remove":defects_to_remove_list
                }
            }
        self.jira_api.put_request(constant.TEST_RUN_ID_URL.format(test_run_id=test_run_id), update_data)


    def add_comment_for_test_run(self, test_run_id, comment):
        """Adds comment for a particular test Run

        Args:
            test_run_id (str): Test run ID
            comment (str): comment string
        """
        update_data = {
            "comment": comment,
            }
        self.jira_api.put_request(constant.TEST_RUN_ID_URL.format(test_run_id=test_run_id), update_data)
        
    def get_test_run_details(self, test_execution_id, test_id):
        """Returns run details based on Test Execution ID and Test ID

        Args:
            test_execution_id (str): Test Execution ID
            test_id (str): Test Id

        Returns:
            dictionary: Run Details for the Test
        """
        response = self.jira_api.get_request(constant.TEST_RUN_ID_SEARCH_URL.format(test_exec_key = test_execution_id, test_key = test_id))
        return response.json()
    
    def get_test_run_id(self, test_execution_id, test_id):
        """Returns run ID based on Test Execution ID and Test ID

        Args:
            test_execution_id (str): Test Execution ID
            test_id (str): Test Id
        Returns:
            str: Run ID
        """
        data = self.get_test_run_details(test_execution_id, test_id)
        return data[0]["id"]

    def get_test_runs_for_test(self, test_id):
        """Gets the Test runs of a Particular test

        Args:
            test_id (str): Test ID

        Returns:
            list: list of dictionary containing details of the Test runs for the test
        """
        response = self.jira_api.get_request(constant.TEST_RUN_HISTORY.format(test_key = test_id))
        return response.json()
    
    def reset_test_run_status_in_execution(self, test_execution_id):
        """Resets status of all tests in Test execution

        Args:
            test_execution_id (str): Test Execution ID
        """
        test_list = self.get_tests_list_from_test_execution(test_execution_id)
        data = {"keys":test_list, "status":"1"}
        self.jira_api.post_request(constant.BATCH_RUN_URL.format(test_exec_key=test_execution_id), data)
        
    
    def fetch_test_success_history(self, test_id, iteration = 10):
        """
            Fetches the test success history for a particular test

        Args:
            test_id (str): Test ID
            iteration (int, optional): Number of iterations to be checked. Defaults to 10.

        Returns:
            int: Pass percentage value
        """
        pass_percentage = None
        try:
            test_runs = self.get_test_runs_for_test(test_id)
            test_run_data = [ run['status'] for run in test_runs if run['status'] != "TODO"]
            test_run_data.reverse()          
            total_test_runs = len(test_run_data)
            count_of_test_runs = iteration if iteration <= total_test_runs else total_test_runs
            tests_passed = 0
            for counter in range(count_of_test_runs):
                if test_run_data[counter] =="PASS":
                    tests_passed+=1
            pass_percentage = (tests_passed/count_of_test_runs) * 100
        except Exception as e:
            log.error(f"Exception while checking pass percentage: {e}")
        return pass_percentage
    

    def get_comment_for_test_run(self, test_run_id):
        """
            Gets the comment for the given test_id

        Args:
            test_id (str): Test ID

        Returns:
            String: Comment for the test
        """
        r = self.jira_api.get_request(constant.TEST_RUN_ID_COMMENT.format(test_run_id=test_run_id))
        return r
    
    def import_test_execution(self, test_json):
        """
            Creates new Test Execution with the Input Json data

        Args:
            test_json: Holds the test execution status which should be added in TE

        Returns:
            Json: testExecIssue Information
        """
        r = self.jira_api.post_request(constant.IMPORT_TEST_EXECUTION, data=test_json)
        return r.json()
    
    def export_test_execution(self, test_execution_id):
        """
            Export Test Execution with test execution ID
        
        Args:
            test_execution_id (string): Test Execution ID
        Returns:
            Json: Returns the response json
        """
        r = self.jira_api.get_request(constant.EXPORT_TEST_EXECUTION.format(test_exec_key=test_execution_id))
        return r.json()