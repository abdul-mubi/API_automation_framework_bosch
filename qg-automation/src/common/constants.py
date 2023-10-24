import time

#File Path
CONFIG_FILE_PATH = "\\userdata\\configuration.json"
TEST_FILE_PATH = "\\..\\userdata\\result\\dynamic_qgtestdata.json"
INPUT_DATA_PATH = "\\..\\userdata\\result\\input_data_te.json"
QG_URLDATA_PATH = "\\..\\userdata\\result\\qg_urldata_"
DOT_JSON = ".json"

#Headers constant
REQ_PYTHON_LIBRARY = "Python Requests library"
REQ_PYTHON_CONTENT_JSON = "application/json"

#Url Types
CONFLUENCE_URL = "CONFLUENCE"
JIRA_URL = "JIRA"
SOCIALCODING_URL = "SOCO"
URL_DICT = {"JIRA":"rb-tracker", "CONFLUENCE":"confluence", "SOCO":"socialcoding", "EU_APP":"eu", "US_APP":"us"}
ARTMC = "ARTMC"

#Status
VALID = {"QG_Status": "VALID"}
INCONSISTENT = {"QG_Status": "INCONSISTENT"}
GREEN = {"JIRA_Status": "GREEN"}
TODO = {"JIRA_Status": "TODO"}
YELLOW = {"JIRA_Status": "YELLOW"}
STATUS_YELLOW = "YELLOW"
JIRA_STATUS_OPEN = "Open"
JIRA_STATUS_IMPLEMENT = "Implementing"
JIRA_STATUS_CLOSED = "Closed"

#Math constant
UNIX_TIME = str(round(time.time() * 1000))
CURRENT_TIME = time.time()

#Response code message
RESPONSE_200 = "URL Validation success"
RESPONSE_401 = "Unauthorized, please check user access"
RESPONSE_403 = "client is forbidden from accessing a valid URL"
RESPONSE_404 = "requested page not found"
RESPONSE_400 = "Bad Request"
RESPONSE_301 = "the requested resource moved to the URL given by the Location headers"
RESPONSE_OK_STR = "200"
RESPONSE_OK = 200
RESPONSE_REDIRECT = 302
RESPONSE_PAGENOTFOUND = 404
RESPONSE_AUTH_REQ = 401
RESPONSE_BAD = 400
RESPONSE_FORBIDDEN = 403
RESPONSE_MOVED_PERMANENTLY = 301

#Action name
EXECUTE_ACTION = "EXECUTE"
VALIDATE_ACTION = "VALIDATE_QG"
CREATE_NEW_TE_ACTION = "CLONE_TEST_EXECUTION"

#Reporting
SCENARIO_URL = "https://rb-tracker.bosch.com/tracker15/browse/"
NO_URL_STRING = "No url found in the comment"
HEADER_LIST = ['Test-ID','Summary','Url_validation','Linked_defect','QG_Status','Jira_Status']
SUMMARY_STR = "summary"
VALIDATION_LIST_STR = "validation_list"
STATUS_STR = "teststatus"
QGSTATUS_STR = "QG_Status"
URL_VALIDATION_STR = "url_validation"
LINKED_DEFECT_STR = "linked_defect"

#JiraOperation

SUMMARY_ERROR_MSG = "No Summary Found in Jira"
STATUS_ERROR_MSG = "No Status found in Jira"
GET_COMMENT_ERROR_MSG = "GET comment JIRA request failed"
EXECUTION_ERROR_MSG = "Test Execution Failed"
