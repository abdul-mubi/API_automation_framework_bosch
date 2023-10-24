import unittest
import jira_api.jira_api as jira_api
import time
import resource.test_constants as constant
import os

import unittest

base_path = os.path.dirname(os.path.abspath(__file__))

class TestJiraAPI(unittest.TestCase):
    
    def setUp(self):
        self.jira = jira_api.JiraAPI(constant.BASE_URL,constant.CREDENTIAL)
        self.start_time = time.time()

    def test_create_issue(self):  
        issue_id = self.jira.create_issue("Test Execution",constant.PROJECT_ID, "Test Execution", "Test Description")
        self.assertIn(constant.PROJECT_ID + "-", issue_id,msg= f"Invalid type of issue ID {issue_id}")
    
    def test_get_issue_details(self):
        self.jira.update_issue(constant.DEFAULT_ISSUE_ID,{"fields": {"description": f"Updated Description at {self.start_time}"}})
    
    def test_update_issue(self):
        issue_details = self.jira.get_issue_details(constant.DEFAULT_ISSUE_ID) 
        self.assertIsInstance(issue_details, dict,"Issue details is not a dictionary")
        self.assertTrue("Updated Description" in issue_details['fields']["description"], f"Failed, Invalid description is seen expected: Updated Description, actual: {issue_details['fields']['description']}")

    def test_get_linked_issues(self):
        linked_issues = self.jira.get_linked_issues("ETEMC-469")
        self.assertIsInstance(linked_issues, list, f"Expected type of linked issues as list but found {type(linked_issues)}")
    
    def test_get_filter_details(self):
        details = self.jira.get_filter_details(constant.DEFAULT_FILTER_ID)
        self.assertIsInstance(details, dict,"Filter details is not a Dictionary")
    
    def test_fetch_jql_query_from_filter(self):
        query = self.jira.fetch_jql_query_from_filter(constant.DEFAULT_FILTER_ID)
        self.assertTrue(query ==constant.DEFAULT_QUERY, f"Invalid query value received expected: {constant.DEFAULT_QUERY} and actual: {query}" )    
        
    def test_perform_jql_query(self):
        details = self.jira.perform_jql_query(constant.DEFAULT_QUERY)
        self.assertIsInstance(details, dict,"JQL Query results is not a dictionary")
        
    def test_get_issues_from_jql_query(self):
        issue_list = self.jira.get_issues_from_jql_query(constant.DEFAULT_QUERY)
        self.assertIsInstance(issue_list, list,"Issue list is not a list value")
        self.assertTrue(len(issue_list)>0, f"Received no content as part of filter query, actual {len(issue_list)}")
        
class TestXrayAPI(unittest.TestCase):
    
    def setUp(self):
        self.xray = jira_api.XRayAPI(constant.BASE_URL, constant.CREDENTIAL)
        
    def test_import_tests(self):
        path = base_path + "/xRay"
        os.makedirs(path,exist_ok=True)
        self.xray.import_tests(path,constant.TEST_ID)
        
    def test_export_tests(self):
        self.xray.export_tests(constant.PROJECT_ID, base_path + "/" + constant.FEATURE_FILE_PATH)
    
    def test_update_tests_in_test_execution(self):
        self.xray.update_tests_in_test_execution(constant.TE_ID, [constant.TEST_ID])
        
    def test_get_tests_from_test_execution(self):
        tests_data = self.xray.get_tests_from_test_execution(constant.TE_ID)
        self.assertIsInstance(tests_data, list,"Filter details is not a list")
        self.assertTrue(len(tests_data)>0, f"No tests are available in provided TE, count: {len(tests_data)}")
    
    def test_get_test_list_from_test_execution(self):
        tests_list = self.xray.get_tests_list_from_test_execution(constant.TE_ID)
        self.assertIsInstance(tests_list, list,"Filter details is not a dictionary")
        self.assertTrue(len(tests_list)>0, f"No tests are available in provided TE, count: {len(tests_list)}")
        
    def test_update_test_execution_in_test_plan(self):
        self.xray.update_test_execution_in_test_plan(constant.TP_ID,[constant.TE_ID])
        
    def test_add_test_execution_in_test_plan(self):
        self.xray.add_test_execution_in_test_plan(constant.TP_ID,[constant.TE_ID])
    
    def test_get_test_execution_from_test_plan(self):
        tests_data = self.xray.get_test_execution_from_test_plan(constant.TP_ID)
        self.assertIsInstance(tests_data, list,"TE Data from TP is not a list")
        
    def test_upload_cucumber_result(self):
        self.xray.upload_cucumber_result(constant.CUCUMBER_RESULT_PATH)
    
    def test_get_details_by_run_id(self):
        run_details = self.xray.get_details_by_run_id(constant.TEST_RUN_ID)
        self.assertIsInstance(run_details, dict,"Test run details is not a dictionary")
    
    def test_update_test_run_status(self):
        self.xray.update_test_run_status(constant.TEST_RUN_ID, "PASS")
    
    def test_update_defects_in_test_run(self):
        self.xray.update_defects_in_test_run(constant.TEST_RUN_ID, [constant.DEFECT_TO_ADD])
        
    def test_add_comment_for_test_run(self):
        self.xray.add_comment_for_test_run(constant.TEST_RUN_ID, "Test comment")
        
    def test_get_test_run_details(self):
        details = self.xray.get_test_run_details(constant.TE_ID, constant.TEST_ID)
        self.assertIsInstance(details, list,"Test Run Data is not a list")

    def test_get_test_run_id(self):
        run_id = self.xray.get_test_run_id(constant.TE_ID, constant.TEST_ID)
        self.assertIsInstance(run_id, int,"Test Run ID is not a valid string")
        self.assertTrue(run_id>0, "Test Run ID is empty")
    
    def test_get_test_runs_for_test(self):
        self.xray.get_test_runs_for_test(constant.TEST_ID)
    
    def test_reset_test_run_status_in_execution(self):
        self.xray.reset_test_run_status_in_execution(constant.TE_ID)
    
    def test_fetch_test_success_history(self):
        percentage = self.xray.fetch_test_success_history(constant.TEST_ID)
        self.assertTrue(0<=percentage<=100, f"Invalid pass percentage actual value = {percentage}")

if __name__ == '__main__':
    unittest.main()