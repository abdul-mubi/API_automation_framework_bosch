import os
import time
import src.common.constants as constants
from src.jira_operation import JiraOperation
from src.url_validation import URLValidation
from src import user_arguments
from src.common.logger import get_logger
log = get_logger()

class automated_qg:

    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.jira_obj = JiraOperation()
        self.url_validation_obj = URLValidation()

    def qg_validation(self, test_execution_id, action):
        """This method starts the QG Validation by reading the 
            Test Execution [QGM]
        
        Args:
            test_execution_id (JIRA ID): Holds the Test Execution ID
            action: QG action (Either EXECUTE or VALIDATE)
        """
        if action == constants.EXECUTE_ACTION:
            testrun_ids = self.jira_obj.read_testruns_from_testexec(test_execution_id)
            #self.jira_obj.update_testrun(testrun_ids) This is yet to be aligned, waiting for requirements
        elif action == constants.VALIDATE_ACTION:
            self.jira_obj.read_testruns_from_testexec(test_execution_id)
            self.url_validation_obj.extract_validate_url_in_comment(test_execution_id)
        elif action == constants.CREATE_NEW_TE_ACTION:
            test_execution_data = self.jira_obj.export_test_execution(test_execution_id)
            self.jira_obj.update_testrun_input_json(test_execution_id, test_execution_data)
            self.jira_obj.import_test_execution()

if __name__ == "__main__":
    automated_qg = automated_qg()
    arguments = user_arguments.UserArguments()
    start_time = time.time()
    test_execution_id = arguments.args.te_id
    action = arguments.args.action
    arguments.set_log_level()
    automated_qg.qg_validation(test_execution_id, action)
    end_time = time.time()
    total_exec_time = int(end_time) - int(start_time)
    log.info(f"Total Time Taken to Validate:{total_exec_time}")