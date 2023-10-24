BASE_URL = "/rest/"
XRAY_URL = BASE_URL + "raven/2.0/"
JIRA_URL = BASE_URL + "api/2/"
XRAY_API_URL = XRAY_URL + "api/"
CONFLUENCE_URL = BASE_URL + "api/"


TEST_RUN_ID_URL = XRAY_API_URL + "testrun/{test_run_id}"
TEST_RUN_ID_COMMENT = TEST_RUN_ID_URL + "/comment"
TEST_RUN_ID_SEARCH_URL = XRAY_API_URL + "testruns?testExecKey={test_exec_key}&testKey={test_key}"
ISSUE_ID_URL = JIRA_URL + "issue/{issue_id}"
FILTER_ID_URL = JIRA_URL + "filter/{filter_id}"
SEARCH_URL = JIRA_URL + "search"
TEST_RUN_HISTORY = XRAY_API_URL + "test/{test_key}/testruns"
BATCH_RUN_URL = BASE_URL + "raven/1.0/testexec/{test_exec_key}/executeTestBatch"

IMPORT_TEST_EXECUTION = XRAY_URL + "import/execution"
EXPORT_TEST_EXECUTION = BASE_URL + "raven/1.0/execution/result?testExecKey={test_exec_key}"
TEST_EXEC_UPDATE = BASE_URL + "raven/1.0/testplan/{test_plan_id}/testexec"
TEST_PLAN_TE_URL = XRAY_API_URL + "testplan/{test_plan_id}/testexecution"

CONFLUENCE_CONTENT = CONFLUENCE_URL + "content/{page_id}?expand=space,body.view"
GET_PAGE_BY_TITLE = CONFLUENCE_URL + "content?spaceKey={space}&title={title}"

DOWNLOADED_ZIP_NAME = "FeatureBundle.zip"
FEATURE_FILE_EXT = ".feature"