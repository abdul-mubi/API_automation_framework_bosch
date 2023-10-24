import os
import requests
import bs4
import base64
from src.common.fileutils import FileUtil
import src.common.constants as constants
from src.jira_operation import JiraOperation
from src.confluence_operation import ConfluenceOperation
from src.common.apiutils import ApiRequests
from src.common.logger import get_logger
log = get_logger()

class URLValidation:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        test_config_data_path = self.base_path + "\\.." + constants.CONFIG_FILE_PATH
        self.test_file_path = self.base_path + constants.TEST_FILE_PATH
        self.fileutil_obj = FileUtil()
        self.api_util_obj = ApiRequests()
        self.jira_op_obj = JiraOperation()
        self.confluence_obj = ConfluenceOperation()
        config_data = self.fileutil_obj.parse_json_file(test_config_data_path)
        jira_credintials= config_data['jira']['token']
        self.confluence = config_data['confluence']
        self.soco = config_data['socialcoding']
        self.confluence_credential = {'Authorization': self.confluence['token']}
        self.credentials = {"JIRA":{'Authorization': jira_credintials,}, "SOCO":{'Authorization': self.soco['token']}}
        self.jira_url_list = []

    def extract_validate_url_in_comment(self, test_execution_id):
        """Method collects the information of all tests from 
            test execution and stores in JSON

        Args:
            test_execution_id (JIRA ID): Jira Test Execution ID
        """
        url_dict = {}
        url_data = self.base_path + constants.QG_URLDATA_PATH + str(test_execution_id) +constants.DOT_JSON
        global_qg_data = self.fileutil_obj.parse_json_file(self.test_file_path)
        log.info("QUALITY GATE URL VALIDATION HAS STARTED FOR PROVIDED TEST EXECUTION")
        for testrun in global_qg_data:
            testkey, test_json = self.construct_json_for_test(testrun)
            url_dict[testkey] = test_json
        self.fileutil_obj.write_json_file(url_data, url_dict)
        log.info(f"VALIDATION OF URL FOR QG IS DONE FOR {test_execution_id}")

    def construct_json_for_test(self, test):
        """ Method to construct the inner json for tests 
            with all values [Summary, url_validation and status]
        Args:
            test(JIRA-ID): Jira test ID
        Returns:
            test_key [Jira ID]: Returns Jira test ID
            test_json: Returns the json constructed
        """
        test_json = {}
        test_key = test["key"]
        summary = self.jira_op_obj.get_summary_for_test(test_key)
        comment = self.jira_op_obj.get_comment_for_testruns(test["id"], "rendered")
        test_json.update({"summary": summary})
        test_json.update({"validation_list": {}})
        test_json["validation_list"].update({"url_validation": [],"linked_defect": []})
        url = self.detect_url_in_comment(comment)
        if not url:
            log.info(f"url not found for testrun {test_key}")
            test_json.update(constants.VALID)
        else:
            test_json = self.add_url_validation_to_json(url, test_json, test_key)
        test_json = self.check_linked_defects(test_json, test)
        return test_key, test_json
    
    def detect_url_in_comment(self, comment):
        """Method to filter URL from comment message

        Args:
            comment(str): comment message of given test
        Returns:
            url (list): Returns the URL list
        """
        soup = bs4.BeautifulSoup(comment, "html.parser")
        url = [link['href'] for link in soup('a') if 'href' in link.attrs]
        return url

    def add_url_validation_to_json(self, url, test_json, test_key, count=1):
        """Updates the test json post URL validation with status and response code
        
        Args:
            url (list): has URL list to be validated for test
            test_json (JSON): Contains information of tests in JSON format
            test_key (JIRA ID): Holds the Jira Test ID
            count (int): Iterates for every URL validation
        Returns:
            test_json (Json): Returns the updated Json 
        """
        response_set = set()
        for link in url:
            resp_code = self.url_validator(link, test_key)
            resp_msg = self.get_url_response_msg(resp_code)
            value = {"url_"+str(count): link, "response_code": str(resp_code), "response_message": str(resp_msg)}
            test_json["validation_list"]["url_validation"].append(value)
            count += 1
            if test_json["validation_list"]["url_validation"] is not None:
                for url_dic in test_json["validation_list"]["url_validation"]:
                    response_set.add(url_dic["response_code"])
            if len(response_set) <= 1:
                if constants.RESPONSE_OK_STR in response_set or '' in response_set:
                    test_json.update(constants.VALID)
                else:
                    test_json.update(constants.INCONSISTENT)
            else:
                test_json.update(constants.INCONSISTENT)
        return test_json

    def check_linked_defects(self, test_json, test):
        """Method to check defects are linked for tests with
            with YELLOW or FAIL Status
        
        Args:
            test_json (Json): User constructed Json for final report
            test (Json): Holds the complete test info
        Returns:
            test_json: Returns with updated Json
        """
        defect_status_set = set()
        if test["status"] == constants.STATUS_YELLOW:
            if test["defects"] != []:
                for index in test["defects"]:
                    test_json["validation_list"]["linked_defect"].append({"key":index["key"],"status":index["status"]})
                    defect_status_set.add(index["status"])
                if constants.JIRA_STATUS_OPEN in defect_status_set:
                    test_json.update(constants.VALID)
                else:
                    test_json = self.jira_url_validation(test_json)
            else:
                test_json = self.jira_url_validation(test_json)
        test_json.update({"teststatus":test["status"]})
        return test_json
    
    def jira_url_validation(self, test_json):
        """Checks for status of JIRA URL is Open
        
        Args:
            test_json (Json): User constructed Json for final report
        Returns:
            test_json: Returns with updated Json
        """
        status = self.jira_op_obj.validate_jira_issue(self.jira_url_list)
        if status:
            test_json.update(constants.VALID)
        else:
            test_json.update(constants.INCONSISTENT)
        return test_json

    def url_validator(self, url, testrun):
        """Method validates the URL with requests API
        Args:
            url (list): has URL value to be validated
            testrun (JIRA ID): Holds the Jira Test ID
        Returns:
            r.status_code: Returns the status code of URL
        """
        url_type = self.get_url_type(url)
        try:
            if url_type == constants.CONFLUENCE_URL:
                status_code = self.validate_confluence_url(url)
                log.info("{} {}".format(testrun, status_code))
                return status_code
            elif url_type == constants.JIRA_URL or url_type == constants.SOCIALCODING_URL:
                if url_type == constants.JIRA_URL:
                    self.jira_url_list.append(url)
                r = self.api_util_obj.get_request(url,headers=self.credentials[url_type])
                log.info("{} {}".format(testrun, r.status_code))
                return r.status_code
            else:
                r = self.api_util_obj.get_request(url, headers=None)
                log.info("{} {}".format(testrun, r.status_code))
                return r.status_code
        except requests.exceptions.SSLError as e:
            return f"Exception occured for this request {e}"
        except OSError as ex:
            return f"OSError Proxy Authentication required {ex}" 

    def get_url_response_msg(self, response_code):
        """Method to get response message for response codes

        Args:
            response_code: Holds the API response code
        Returns:
            response_msg: Returns the response message
        """
        if response_code  == constants.RESPONSE_OK:
            response_msg = constants.RESPONSE_200
        elif response_code == constants.RESPONSE_AUTH_REQ:
            response_msg = constants.RESPONSE_401
        elif response_code == constants.RESPONSE_FORBIDDEN:
            response_msg = constants.RESPONSE_403
        elif response_code == constants.RESPONSE_BAD:
            response_msg = constants.RESPONSE_400
        elif response_code == constants.RESPONSE_MOVED_PERMANENTLY:
            response_msg = constants.RESPONSE_301
        elif response_code == constants.RESPONSE_PAGENOTFOUND:
            response_msg = constants.RESPONSE_404
        else:
            response_msg = response_code
     
        return response_msg
    
    def get_url_type(self, url):
        """Method to fetch type of URL [JiRA, Confluence, Socialcoding, etc]

        Args:
            url: Holds the url
        Returns:
            response_msg: Returns the URL Type
        """
        url_type_dict = constants.URL_DICT
        for key, value in url_type_dict.items():
            if value in url:
                return key

    def fetch_and_set_cookie_header(self,response):
        """Sets the cookie and fetches location

        Args:
            response: Holds the API response
        Returns:
            response_msg: Returns the location of available 
        """
        cookie= response.headers['Set-Cookie'].replace('; Path=/; Secure','')
        cookie = cookie.replace(',',';')
        self.cookie_header_get={'cookie': cookie}
        if 'location' in response.headers:
            return response.headers['location']
        
    def validate_confluence_url(self, url):
        """Validates confluence url is valid 
        
        Args:
            url: Holds the url to validate
        Returns:
            response_code: Returns the response code for the url
        """
        if "/x" in url:
            page_id = self.confluence_obj.page_id_from_tiny_link(url) 
        elif "pageId" in url:
            page_id = url.split("pageId=")[1]
        else:
            title = url.rsplit("/",1)[-1]
            space = url.rsplit("/",2)[-2]
            page_id = self.confluence_obj.get_page_id_from_title(space, title)
        if page_id != constants.RESPONSE_PAGENOTFOUND:
            response_code = self.confluence_obj.validate_content_availablity_from_page_id(page_id)
        else:
            response_code = page_id
        return response_code