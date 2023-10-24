import fire
import json
import re
import os
import shutil
import os
import logging
from socket import gethostname
from atlassian_api.jira_api import JiraAPI,XRayAPI

base_path = os.path.dirname(os.path.abspath(__file__)) + "/../../"
device_map_path = base_path + "common/TestData/DeviceMap.json"
configuration_path = base_path + "common/TestData/config.json"

config_path = base_path + "common/TestData/testConfig.json"
with open(config_path, 'r') as dataFile:
    config_data = json.load(dataFile)

jira_api = JiraAPI(config_data["jira"]["ApiBaseURI"],config_data["jira"]["token"])
xray_api = XRayAPI(config_data["jira"]["ApiBaseURI"],config_data["jira"]["token"])

class JiraOperations:

    def fetch_jql_query(self, default_test_exec_id, test_suite):
        """
            Fetches JQL query from jql_query.json or from test_suite

        Args:
            default_test_exec_id (_type_): Test_exec Key in JQL Query
            test_suite (_type_): test_suite_details

        Returns:
            string: jql query
        """
        jql_query_data_path = base_path + "common/TestData/Pipeline/jql_query.json"
        with open(jql_query_data_path, 'r') as jql_query_file:
            jql_query_file = json.load(jql_query_file)
        try:
            jql_query= jql_query_file[default_test_exec_id]
        except KeyError:
            filter_id = (test_suite.split("-"))[0]
            jql_query = jira_api.fetch_jql_query_from_filter(filter_id)
        return jql_query

    def add_default_tp(self, test_suite, test_plan):
        """
            Adds Default TP to the Test plan and returns same object

        Args:
            test_suite (String): Type of test suite: Eg: SMOKE-CUSTOMER_A
            test_plan (String): "Additional TestPlan IDs"

        Returns:
            string: test_plan with Default tp in addition (test_plan = Default_tp,test_plan )
        """
        tp_data_path = base_path + "/common/TestData/Pipeline/defaultTestPlan.json"
        with open(tp_data_path, 'r') as tp_file:
            test_plan_json = json.load(tp_file)
        try:
            default_tp = test_plan_json[test_suite]
            if(test_plan.strip() == ""):
                return default_tp
            else:
                return test_plan
        except Exception:
            return test_plan

    def get_default_test_execution_ids_from_test_suite(self, test_suite):
        """ 
            Returns default TE IDs for the testExecutionMap.json
        """
        test_execution_map = base_path + "common/TestData/Pipeline/testExecutionMap.json"
        with open(test_execution_map, 'r') as test_execution_map_json:
            test_execution_map_json = json.load(test_execution_map_json)
        test_execution_ids = []
        for key, value in test_execution_map_json.items():
            if test_suite in key:
                test_execution_ids = value
                break
        return test_execution_ids

    def fetch_tests_from_filter(self,default_test_exec_id,test_suite):
        """
            Fetches tests from Filter and returns as List
        """
        jql_query = self.fetch_jql_query(default_test_exec_id,test_suite)
        tests_list = jira_api.get_issues_from_jql_query(jql_query)
        return tests_list

    def get_tests_by_status_from_te(self,test_exec_key, test_status):
        """
            Fetches tests from Test execution by defined status and returns as list
        """
        test_details = xray_api.get_tests_from_test_execution(test_exec_key)
        test_list = [ test['key'] for test in test_details if test['status'] == test_status]
        return test_list
        
    def fetch_pass_percentage_of_test(self,test_id):
        """
            Fetches pass percentage of test in past 10 iterations and returns the success rate as string
        """
        pass_percentage = xray_api.fetch_test_success_history(test_id)
        if pass_percentage == None:
            pass_percentage = "NA"
        else:
            pass_percentage = str(pass_percentage) +  " %"
        return pass_percentage

    def get_defects_linked_to_test(self,test_key, device = None):
        """
            Returns list of defects linked to the tests which are in is blocked by or created by state and not closed
        """

        linked_defects=[]
        linked_defects_final =[]

        if device == None or len(device) == 0:
            device = "CCU"
        with open(device_map_path, 'r') as dataFile:
            device_map_data = json.load(dataFile)
            hostname_device_data = device_map_data[gethostname()]
            customer_type = hostname_device_data[device]["device_config"]

        with open(configuration_path, 'r') as dataFile:
            configuration_data = json.load(dataFile)  
        device_config_data = configuration_data[customer_type]
        device_customer = device_config_data["jira_customer_type"]

        try:
            linked_issues = jira_api.get_linked_issues(test_key)
            for issues in linked_issues:
                if (issues['type']['inward']=="is blocked by" and 'inwardIssue' in issues):
                    if issues['inwardIssue']['fields']['issuetype']['name'] =="Bug" and issues['inwardIssue']['fields']['status']['name']!="Closed":
                        linked_defects.append(issues['inwardIssue']['key'])
                elif (issues['type']['inward']=="created by" or (issues['type']['inward']=="is blocked by" and 'outwardIssue' in issues)):
                    if issues['outwardIssue']['fields']['issuetype']['name'] =="Bug" and issues['outwardIssue']['fields']['status']['name']!="Closed":
                        linked_defects.append(issues['outwardIssue']['key'])
                else:
                    continue
            linked_defects = list(set(linked_defects))
            linked_defects_final = self.filter_defect_based_on_customer(test_key, device_customer, linked_defects, linked_defects_final)
        except Exception as e:
            logging.error(f"Error while fetching Jira Defect for test {test_key}: {e}")
        return linked_defects_final

    def filter_defect_based_on_customer(self, test_key, device_customer, linked_defects, linked_defects_final):
        """
            Returns list of defects linked to the tests based on the device customer
        """
        
        for defect in linked_defects:
            data = jira_api.get_issue_details(defect)
            defect_customer_detail = data['fields']['customfield_11200']
            
            if defect_customer_detail != None:
                customers = [detail['value'] for detail in defect_customer_detail]
                if device_customer in customers:
                    linked_defects_final.append(defect)
                    logging.debug(f"Device customer - {device_customer} is matched with the defect customer - {customers}")
                else:
                    logging.debug(f"Device customer - {device_customer} is not matched with the defect customer - {customers}")            
            else:
                linked_defects_final.append(defect)
                logging.warning(f"Error while fetching customer from Jira Defect for test {test_key}")
        return linked_defects_final
    
    def create_new_test_execution(self):
        """
            Creates a new Test execution in ETEMC Project
        """
        new_test_execution_id = jira_api.create_issue("Test Execution", "ETEMC", "Cucumber results - New TE")
        return new_test_execution_id
    
    def create_new_test_plan(self, customer_name, version):
        """
            Creates a new Test Plan in ETEMC Project based on Customer name and version
        """
        test_plan_id = jira_api.create_issue("Test Plan", "ETEMC", f"{customer_name} FW {version} Test Report")
        return test_plan_id

    def link_execution_to_testplan(self, test_execution_id, test_plan_ids):
        """
            Links Test execution to the Mentioned test plan IDs
        """
        test_plan_ids = test_plan_ids.split(',')
        for test_plan_id in test_plan_ids:
            xray_api.add_test_execution_in_test_plan(test_plan_id,[test_execution_id])

    def remove_extra_te_from_tp(self, test_execution_ids_ref, test_plan_ids):
        """
            Removes additional Test Executions from the mentioned Test Plans
        """
        act_test_exec_ids = []
        test_plan_ids = test_plan_ids.split(',')
        # it would be enough to remove extra TEs from only Default Test Plans.
        te_data = xray_api.get_test_execution_from_test_plan(test_plan_ids[0])
        for test_execution in te_data:
            act_test_exec_ids.append(test_execution['key'])
        extra_te = list(set(act_test_exec_ids) - set(test_execution_ids_ref))
        try:
            xray_api.remove_test_execution_from_test_plan(test_plan_ids[0],extra_te)
        except AssertionError as e:
            logging.debug(e)
        

    def prepare_test_executions(self, test_execution_ids, new_test_execution, test_plan_ids, tp_from_user, test_suite):
        """
            Prepares a Test Execution for testing, if TE Already exists it will update the tests and Reset status of all tests to TO DO state
        Args:
            test_execution_ids (list): List of test execution IDs
            new_test_execution (String): Supports two Values (Required / Not_Required), if required a new Test Execution will be created
            test_plan_ids (String): TP Ids to link to Test Execution
            tp_from_user (String): Test Plan id (User provided/Newly created)
            test_suite (String): Type of test suite

        Returns:
            list: Test Execution IDs
        """
        test_exec_ids = []

        for test_execution in test_execution_ids:
            test_list = self.fetch_tests_from_filter(test_execution,test_suite)
            if new_test_execution == "Not_Required" and tp_from_user == "":
                logging.debug("Creating new test execution will not happen on selecting 'Not_Required' in New Test Execution input filed")
            else:
                test_execution = self.create_new_test_execution()
            test_exec_ids.append(test_execution)
            existing_test_list = xray_api.get_tests_list_from_test_execution(test_execution)
            tests_to_add = list(set(test_list) - set(existing_test_list))
            tests_to_remove = list(set(existing_test_list) - set(test_list))
            xray_api.update_tests_in_test_execution(test_execution,tests_to_add,tests_to_remove)
            xray_api.reset_test_run_status_in_execution(test_execution)
            if (tp_from_user == "" and new_test_execution == "Required"):
                logging.debug("Test execution is not getting linked to the test plan")
            else:
                self.link_execution_to_testplan(test_execution, test_plan_ids)
        return test_exec_ids
    

    def fetch_tests_using_filter_id(self,filter_id):
        """
            Fetches tests using Filter ID and returns as List
        """
        jql_query = jira_api.fetch_jql_query_from_filter(filter_id)
        tests_list = jira_api.get_issues_from_jql_query(jql_query)
        return tests_list

    def prepare_test_executions_backend_workflow(self,filter_id,team_name):
        """
        Prepares a Test Execution for Backend Workflow for testing
        
        Args:
            filter_id: Filter ID that consists of all tests which needs to be mapped to the Test Execution for Triggering
            team_name: Team Name for which Backend Workflow is getting executed

        Returns:
            string: Test Execution ID for specific Team for Backend Integration Workflow

        """
        test_execution_map_key = ("TEBI-"+team_name)
        test_execution_id = self.get_default_test_execution_ids_from_test_suite(test_execution_map_key)[0]
        test_list = self.fetch_tests_using_filter_id(filter_id)
        existing_test_list = xray_api.get_tests_list_from_test_execution(test_execution_id)
        tests_to_add = list(set(test_list) - set(existing_test_list))
        tests_to_remove = list(set(existing_test_list) - set(test_list))
        # Updates tests in Test Execution
        xray_api.update_tests_in_test_execution(test_execution_id,tests_to_add,tests_to_remove)
        # Resets status of all tests in Test execution
        xray_api.reset_test_run_status_in_execution(test_execution_id)

        return test_execution_id



    def update_test_run_status(self, run_id, status = "TODO"):
        """
            Updates the test run status based on Run ID

        Args:
            run_id (string): run id in the test execution
            status (str, optional): Status of the run ID. Defaults to "TO DO".
        """
        
        if(run_id!= None):
            xray_api.update_test_run_status(run_id, status)
        else:
            logging.error("Run id is None for Current execution")
    
    
    def update_test_execution_with_defect(self, test_exec_key, status = "RED", tests_with_defects = None):
        """
            Checks the defects for the Tests with specific status in Execution Run and updates defect to the test run

        Args:
            test_exec_key (str): Test Execution ID
            status (str): Status of the tests for which defect should be checked (RED / FAILED)
            tests_with_defects (dictionary, optional): Details of defect list for each test in a dictionary
                                                        Format: {"TEST_ID":[DEFECT_ID_1, DEFECT_ID_2]}
                                                        Defaults to None.
        """
        tests_with_defect = self.get_tests_by_status_from_te(test_exec_key, status)
        for test in tests_with_defect:
            if(tests_with_defects != None):
                defect = tests_with_defects[test] if (test in tests_with_defects.keys()) else []
            else:
                defect = self.get_defects_linked_to_test(test)
            if defect !=[]:
                logging.debug(f"Defect for test {test} is {defect}")
                test_run_data = xray_api.get_test_run_details(test_exec_key,test)
                xray_api.update_defects_in_test_run(test_run_data[0]["id"],defect)

    def get_test_run_id(self,test_exec_key, test_id, create = False):
        """Gets the Test Run ID for the particular test

        Args:
            test_exec_key (string): test execution id
            test_id (string): Test ID
            create (bool, optional): Link the test to execution if test is not part of Test Execution. Defaults to False.

        Returns:
            string: Run ID / None: In case no Run ID Available
        """
        try:
            test_run_id = xray_api.get_test_run_id(test_exec_key,test_id)
            return test_run_id
        except AssertionError:
            if(create == True):
                xray_api.update_tests_in_test_execution(test_exec_key,[test_id])
                return self.get_test_run_id(test_exec_key, test_id)
            return None

    def __fetch_setup_detail(self, device_details, job_name):
        """
            Prepares Name for test Execution
        """
        if 'team_mercur' in job_name.lower():
            additional_title = "Team_Mercur CI/CD- "
        elif 'team_bets' in job_name.lower():
            additional_title = "Team_BeTS CI/CD- "
        elif 'team_be1' in job_name.lower():
            additional_title = "Team_BE1 CI/CD- "
        elif 'new_test_execution' in job_name.lower():
            additional_title = "TedTitans Test Dev-Team_Internal- "
        elif 'pr_merge' in job_name.lower():
            additional_title = "TedTitans PR Merge-Team_Internal- "
        elif 'team_hildesgrad' in job_name.lower():
            additional_title = "Team_Hildesgrad CI/CD- "
        elif re.search('^pipeline_.+_executor$', job_name.lower()):
            additional_title = f"Scheduled {job_name}- "
        else:
            additional_title = f"Scheduled {job_name}- "

        execution_title_details = {"Device_Version":"", "Customer":"", "Tenant":""}
        execution_title_details["Device_Version"] = [device_details[each_key]["Version"]["FW-Version"] for each_key in device_details.keys() if device_details[each_key]["Selected"] == "True"]
        execution_title_details["Customer"] = [device_details[each_key]["Customer"] for each_key in device_details.keys() if device_details[each_key]["Selected"] == "True"]
        execution_title_details["Tenant"] = [device_details[each_key]["Tenant"] for each_key in device_details.keys() if device_details[each_key]["Selected"] == "True"]
        return additional_title + "FW_Version: "+execution_title_details['Device_Version'][0] + ", " + "Customer: "+execution_title_details['Customer'][0] + ", "+ "Tenant: "+execution_title_details['Tenant'][0]

    
    def update_te_issue_fields(self, runner_name, runner_id, title = None, job_name = None):
        """
            Prepares the Issue field to update Test Execution Issue
        """
        version_path = base_path + "version.json"
        issue_field_path = base_path + "common/Jira/issue_fields.json"
        with open(version_path) as fp:
            device_details = json.load(fp)
        
        for key, value in device_details.items():
            firmware_version = device_details[key]['Version']['FW-Version']
            break
        if title != None:
            summary = title
        elif job_name != None:
            summary = self.__fetch_setup_detail(device_details, job_name)
        elif runner_id!= None:
            summary = f"FW-{firmware_version} Cucumber results (Generated by Github Action Runner:{runner_id} executed in {runner_name})"
        else:
            summary = f"FW-{firmware_version} Cucumber results (Generated by Test Automation: executed in {runner_name})"
        
        description = f"Device details in the machine: \n {device_details}"
        with open(issue_field_path) as ip:
            field_content = json.load(ip)
        field_content['fields']['summary'] = summary
        field_content['fields']['description'] = description
        logging.debug(field_content)
        with open(issue_field_path, 'w') as wf:
            json.dump(field_content, wf)
        return field_content
    
    def prepare_data_for_github_actions(self, suite, device_type, new_test_execution, suite_type= "NA", test_plan="", matrix= False, suite_type_applicability = "", version= ""):
        """
            Prepares data for Github Action run

        Args:
            suite (string): Suite type (Smoke/Regression/Load)
            device_type (string): Customer details
            new_test_execution (string): _description_
            suite_type (str, optional): "RM/Non-RM". Defaults to "NA".
            test_plan (str, optional): Tests plan for which tests should be linked. Defaults to "".
            matrix (bool, optional): Whether data is required for Matrix preparation. Defaults to "False".
            version (str, optional): Software version Details incase new Test Plan need to be c. Defaults to "".
        """
        suites =  suite.split(",") if type(suite) == str else list(suite)
        device_types = device_type.split(",") if type(device_type) == str else list(device_type)
        suite_types = suite_type.split(",") if type(suite_type) == str else list(suite_type)
        suite_type_applicability = suite_type_applicability.split(",") if type(suite_type_applicability) == str else list(suite_type_applicability)
        execution_data_list = []
        if len(device_types) == 1 and test_plan != "":
            tp_from_user = test_plan
        elif len(device_types) != 1 and test_plan != "":
            logging.debug("Test plan field should be null when Device Type is selected 'All_device_types'")
        else:
            tp_from_user = ""
        if(tp_from_user.lower() == "new" and version != ""): # if test_plan is new, then version is mandatory to create new test plan
            tp_from_user = self.create_new_test_plan(device_types[0], version)
        
        for each_suite in suites:
            if each_suite in suite_type_applicability:
                logging.debug(f"Preparing test execution for suite = {each_suite} with type = {suite_types}")
                self.__prepare_each_suite_data(execution_data_list, each_suite, device_types, suite_types, new_test_execution, tp_from_user)
            else:
                logging.debug(f"Preparing test execution for suite = {each_suite}")
                self.__prepare_each_suite_data(execution_data_list, each_suite, device_types, None, new_test_execution, tp_from_user)
        if matrix:
            print(str(json.dumps(execution_data_list)).replace('"','\\\"'))
        else:
            print(execution_data_list[0])
               
    def __prepare_each_suite_data(self, execution_data_list, suite, device_types, suite_types, new_test_execution, tp_from_user):
        """
            Prepares test execution data for each customer, this will be further fed into Github action Matrix
        """
        for device in device_types:
            try:
                test_suite = suite+ "-" + device
                test_plan_ids = self.add_default_tp(test_suite, tp_from_user)
                if(suite_types!= None and "TCU2" not in device): # Remove TCU2 condition once RM and Non-RM regression in place for TCU2
                    te_list =  []
                    for suite_type in suite_types:
                        test_suite_type = suite_type + "-" + test_suite
                        default_test_exec_ids = self.get_default_test_execution_ids_from_test_suite(test_suite_type)
                        test_execution_ids = self.prepare_test_executions(default_test_exec_ids, new_test_execution, test_plan_ids, tp_from_user, test_suite)
                        te_list += test_execution_ids
                        self.__prepare_execution_data(execution_data_list, device, suite, test_execution_ids, test_plan_ids,suite_type)
                        logging.debug(f"Successfully prepared suite data for device: {device} suite: {suite} and suite_type = {suite_type}")
                    self.remove_extra_te_from_tp(te_list, test_plan_ids)
                else:
                    default_test_exec_ids = self.get_default_test_execution_ids_from_test_suite(test_suite)
                    test_execution_ids = self.prepare_test_executions(default_test_exec_ids, new_test_execution, test_plan_ids, tp_from_user, test_suite)
                    self.remove_extra_te_from_tp(test_execution_ids, test_plan_ids)
                    self.__prepare_execution_data(execution_data_list, device, suite, test_execution_ids, test_plan_ids)
                    logging.debug(f"Successfully prepared suite data for device: {device} suite: {suite}")
            except Exception: # Incase there is some issue with TE/TP for customer, particular customer will be skipped
                continue
        return execution_data_list
    
    
    def __prepare_execution_data(self, execution_data_list, device, suite,test_execution_ids, test_plan_ids, suite_type = None):
        """
            Prepares test execution data for specific TE List, this will be further fed into Github action Matrix
        """
        for execution_id in test_execution_ids:
            data = {
                        "customer": device,
                        "suite":suite,
                        "test_plan":test_plan_ids,
                        "test_execution":execution_id
                    }
            if(suite_type!=None):
                data["machine_type"] = suite_type
            execution_data_list.append(data)
        return execution_data_list
        
    def import_test_from_jira(self, jira_id = None, filter_id = None):
        """Imports test executions to Local from Jira-Xray

        Args:
            jira_id (str, optional): Test ID or test Execution ID
            filter_id (str, optional): Filter ID
        """
        path = "xRay"
        try:
            os.makedirs(path)
        except FileExistsError:
            shutil.rmtree(path)
            os.makedirs(path)
        path = os.path.dirname(os.path.abspath(__file__)) + "/" + path
        if(jira_id!=None):
            jira_id = jira_id.replace(" ","").replace(",",";")
        xray_api.import_tests(path,jira_id, filter_id)


    def export_feature_to_jira(self, directory_path, file_name = None, time_hr=None):
        """Exports feature file to Jira

        Args:
            directory_path (path): Path to the feature file directory from Project root
            file_name (string, optional): Name of the file, if specific file need to be synced in Jira. Defaults to None.
            time_hr(int, optional): Incase files updated in past hours need to be updated
        """
        xray_api.export_tests("ETEMC", base_path + directory_path, file_name, time_hr)
        
    def cleanup_cucumber_report_data(self, report_json):
        """
            Cleans up double entry of a scenario in cucumber report in case scenario was auto retired
        """
        for feature in report_json:
            previous_scenario_name=''
            scenario_count = 0
            length_of_elements = len(feature['elements'])
            while scenario_count < length_of_elements:
                if (feature['elements'][scenario_count]['name'] in previous_scenario_name):
                    previous_scenario_name=feature['elements'][scenario_count]['name']
                    del (feature['elements'][scenario_count-1])
                    length_of_elements-=1
                else:
                    previous_scenario_name=feature['elements'][scenario_count]['name']
                    scenario_count+=1
        return report_json
    
    def mark_tests_with_defect_to_red(self,report_json, tests_with_defect_list = None):
        """
            Marks test with defect to RED state in the report json
        """
        check_defect_in_jira = True if tests_with_defect_list == None else False
            
        for feature in report_json:
            if feature['status'] == 'failed':
                for scenario in feature['elements']:
                    if(check_defect_in_jira or scenario["tags"][0]['name'] in tests_with_defect_list):
                        self.__check_and_mark_scenario_red(scenario, check_defect_in_jira)              
        return report_json
    
    def __check_and_mark_scenario_red(self, scenario, check_defect_in_jira):
        """
            Marks scenario red if its failed and has defect
        """
        for step in scenario["steps"]:
            if step['result']['status'] == 'failed':
                if(check_defect_in_jira == True):
                    defects = self.get_defects_linked_to_test(scenario["tags"][0]['name'])
                    if(len(defects))> 0:
                        step['result']['status'] = "RED"
                else:
                    step['result']['status'] = "RED"
                break
        return scenario
    
    def update_execution_details(self, result_json, execution_id):
        """
            Adds test execution ID as first tag in the report, so that once report is uploaded to Jira, it will be mapped to the required execution
        """
        te_stru_in_json = {"name": execution_id, "line": 1}
        for each_element in result_json:
            each_element["tags"].append(te_stru_in_json)
        return result_json

    def publish_execution_report_multipart(self):
        """
            Publishes multipart cucumber report to Jira
        """
        test_exec_key = xray_api.upload_cucumber_result(base_path + "cucumber_formated_result.json" , base_path + "common/Jira/issue_fields.json")
        return test_exec_key
        
    def publish_feature_report(self, feature_report_path):
        """
            publishes cucumber report to JIRA
        """
        test_exec_key = xray_api.upload_cucumber_result(base_path + feature_report_path)
        return test_exec_key
    
    def update_test_execution_summary(self, test_exec_key, run_id = None, title = None, job_name = None):
        """Updates Execution summary with additional details to the Jira

        Args:
            test_exec_key (str): Test execution ID
            run_id (str, optional): Run ID in Github. Defaults to None.
            title (str, optional): Title of the Execution report, can be skipped if job_name is provided. Defaults to None.
            job_name (str, optional): Job Name of the execution, can be skipped if title is provided. Defaults to None.
        """
        data = self.update_te_issue_fields(gethostname(),run_id, title, job_name)
        logging.info(f"Updating Issue fields for Jira Issue {test_exec_key} with data {data}")
        jira_api.update_issue(test_exec_key, data)
        
        
    def process_and_upload_cucumber_formatted_report(self, cucumber_report_path = "cucumber_formated_result.json", execution_id = ""):
        """Process and uploads the complete cucumber formatted report in one go after updating defects

        Args:
            cucumber_report_path (str, optional): Report file path. Defaults to "cucumber_formated_result.json".
            execution_id (str, optional): Execution ID. Defaults to "".
        """
        path = base_path + cucumber_report_path
        with open(path, 'r') as jql_query_file:
            cucumber_report = json.load(jql_query_file)
        self.cleanup_cucumber_report_data(cucumber_report)
        self.mark_tests_with_defect_to_red(cucumber_report)
        if(execution_id != ""):
            feature_result = self.update_execution_details(feature_result, execution_id)
        te_id = self.publish_feature_report(feature_result)
        if(te_id!= execution_id):
            print(f"Updated TE ID: {te_id}")
        self.update_test_execution_with_defect(te_id)
        
if __name__ == "__main__":
    fire.Fire(JiraOperations)
    