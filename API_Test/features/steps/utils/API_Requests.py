import requests
import logging
import os
import re
import json
import base64
import urllib3
import time
from requests.exceptions import ProxyError, ConnectTimeout
import steps.pageObjects.API_Generic_Class as API_Generic_Class
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import hashlib
import html
import urllib.parse
import steps.constantfiles.constants_request as constants


# These two lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.
# try:
#   import http.client as http_client
# except ImportError:
#   # Python 2
#   import httplib as http_client
# http_client.HTTPConnection.debuglevel = 2

# You must initialize logging, otherwise you'll not see debug output.
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

class ApiRequestsClass:
    environ = ""
    environment = ""
    user_login = ""
    user_password = ""
    config_data = {}
    client_id = "web-ui"

    def __init__(self, environmental_value, log_api_details = True):
        self.log_api_details = log_api_details
        self.environ = environmental_value
        self.api_gen_obj = API_Generic_Class.ApiGenericClass()
        self.config_data = self.api_gen_obj.parse_json_file(constants.TEST_CONFIG_JSON) 
        self.environment = self.config_data["systemUnderTest"][self.environ]["ApiBaseURI"]
        if self.environ == "azure_eu_bi":
            self.redirect_uri = self.config_data["systemUnderTest"][self.environ]["redirect_uri"]
        else:
            self.redirect_uri = self.environment
        self.user_login = self.config_data["systemUnderTest"][self.environ]["login"]["userName"]
        self.tenant = self.config_data["systemUnderTest"][self.environ]["login"]["tenant"]
        pwd = self.config_data["systemUnderTest"][self.environ]["login"]["password"]
        self.user_password = base64.b64decode(pwd).decode('utf-8')
        self.key_cloak_uri =self.config_data["systemUnderTest"][self.environ]["login"]["keycloakURI"]
        self.token_path = constants.TEST_DATA_TOKEN_JSON

    
    def get_auth_token(self):
        
        token = None
        try:
            if self.api_gen_obj.check_file_availability(self.token_path):
                token_details = self.api_gen_obj.parse_json_file(constants.TEST_DATA_TOKEN_JSON)
                if self.api_gen_obj.check_token_environment(token_details, self.environ):
                    if self.api_gen_obj.check_token_expiry(token_details["expiry_time"]):
                        token = token_details["token"]
                    elif self.api_gen_obj.check_token_expiry(token_details["refresh_expiry_time"]):
                        token = self.get_auth_token_from_refresh_token(token_details["refresh_token"])
        except OSError as e:
            logging.error(f"{e.errno}")
        except ValueError as e:
            logging.error(f"{e}")

        if not token:
            logging.debug("Token expired, generating new token")
            self.create_authorization_request()
            self.generate_authorization_code()
            r = requests.post(
                url = self.key_cloak_uri + self.tenant + "/protocol/openid-connect/token",
                data = {
                        "grant_type": "authorization_code",
                        "client_id": self.client_id,
                        "redirect_uri": self.redirect_uri,
                        "code": self.auth_code,
                        "code_verifier": self.code_verifier
                    },
                headers={"Cookie": "AUTH_SESSION_ID="+self.auth_session_id},
                allow_redirects=False
            )
            logging.debug(f"{r.status_code}")
            if (r.status_code != requests.codes.ok):
                logging.debug(f"Response Headers:{r.headers}")
                logging.debug(f"Response Requests{r.request}")
            assert r.status_code == requests.codes.ok, "Token generation failed with above Response:"
            token = self.store_and_get_token_details(r)
        return token


    def get_request(self, ep, retry=1):
        if(retry <= 5):
            try:
                token = self.get_auth_token()
                endpoint = self.environment 
                headers = {'Authorization': token}
                if self.log_api_details == True:
                    logging.debug("HTTP GET endpoint:{}{}".format(endpoint, ep))
                r = requests.get("{}{}".format(endpoint, ep),
                                headers=headers, verify = False)
                if (r.status_code != requests.codes.ok):
                    logging.debug(f"{r.headers}")
                if self.log_api_details == True:
                    logging.debug(f"status code:  {r.status_code}")
                return r
            except (ConnectionResetError, ProxyError, ConnectTimeout) as e:
                logging.warning(f"ConnectionReset / Proxy Issue:, {e}, Retry count =, {str(retry)}")
                return self.get_request(ep, retry + 1)
        else:
            assert False, "Connection-Reset error, unable to connect after 5 retries"

    def post_request(self, ep, params, custom_header={}, retry=1):
        if(retry <= 5):
            try:
                token=self.get_auth_token()
                endpoint = self.environment
                if self.log_api_details == True:
                    
                    logging.debug("HTTP POST: endpoint: {}{}".format(endpoint, ep))
                    logging.debug(f"payload: , {params}")
                headers = {'Authorization': token,
                        'accept': 'application/hal+json',
                        'content-type': 'application/json;charset=UTF-8',
                        'if-match': '0', 'X-Requested-With': 'XMLHttpRequest',
                        'User-Agent': constants.REQ_PYTHON_LIBRARY}
                # merge default and custom header, custom header rulezzz
                headers.update(custom_header)
                r = requests.post("{}{}".format(endpoint, ep),
                                headers=headers, verify=False, data=json.dumps(params))
                if (r.status_code != requests.codes.created):
                    logging.debug(f"{r.headers}")
                if self.log_api_details == True:
                    logging.debug(f"status code: {r.status_code}")
                return r
            except (ConnectionResetError, ProxyError, ConnectTimeout) as e:
                logging.warning(f"ConnectionReset / Proxy Issue:, {e}, Retry count =, {str(retry)}")
                return self.post_request(ep, params, custom_header, retry + 1)
        else:
            assert False, constants.REQ_UNABLE_TO_CONNECT

    def post_request_file(self, ep, params, dbc_file, endpoint=environment, retry=1):
        if(retry <= 5):
            try:
                if endpoint == '':
                    endpoint = self.environment
                token=self.get_auth_token()
                if self.log_api_details == True:
                    
                    logging.debug("HTTP POST: endpoint: {}{}".format(endpoint, ep))
                    logging.debug(f"payload: , {params}")
                headers = {'Authorization': token,
                            'X-Requested-With': 'XMLHttpRequest',
                            'User-Agent': constants.REQ_PYTHON_LIBRARY}
                r = requests.post("{}{}".format(endpoint, ep), headers=headers,
                                verify=False, data=params, files=dbc_file)

                if (r.status_code != requests.codes.created):
                    logging.debug(f"{r.headers}")
                if self.log_api_details == True:
                    logging.debug(f"status code: {r.status_code}")
                return r
            except (ConnectionResetError, ProxyError, ConnectTimeout) as e:
                logging.warning(f"ConnectionReset / Proxy Issue:, {e}, Retry count =, {str(retry)}")
                return self.post_request_file(ep, params, dbc_file, endpoint, retry + 1)
        else:
            assert False, constants.REQ_UNABLE_TO_CONNECT
            
# delete this method


    def put_request(self, ep, params, custom_header={}, retry=1):
        if(retry <= 5):
            try:
                endpoint = self.environment
                token=self.get_auth_token()        
                if self.log_api_details == True:
                    
                    logging.debug("HTTP PUT: endpoint: {}{}".format(endpoint, ep))
                    logging.debug(f"payload: , {params}")
                headers = {'Authorization': token,
                        'accept': 'application/hal+json',
                        'content-type': 'application/json',
                        'if-match': '0', 'X-Requested-With': 'XMLHttpRequest',
                        'User-Agent': constants.REQ_PYTHON_LIBRARY}
                headers.update(custom_header)
                r = requests.put("{}{}".format(endpoint, ep),
                                    headers=headers, verify=False, data=json.dumps(params))
                if (r.status_code != requests.codes.no_content):
                    logging.debug(f"{r.headers}")
                if self.log_api_details == True:
                    logging.debug(f"status code: {r.status_code}")
                return r
            except (ConnectionResetError, ProxyError, ConnectTimeout) as e:
                logging.warning(f"ConnectionReset / Proxy Issue:, {e}, Retry count =, {str(retry)}")
                return self.put_request(ep, params, custom_header, retry + 1)
        else:
            assert False, constants.REQ_UNABLE_TO_CONNECT


    def put_request_file(self, ep, dbc_file, custom_header={}, retry=1):
        if(retry <= 5):
            try:
                endpoint = self.environment
                token=self.get_auth_token()        
                if self.log_api_details == True:
                    
                    logging.debug("HTTP PUT: endpoint: {}{}".format(endpoint, ep))
                headers = { 'Authorization': token,
                        'content-type': False,
                        'if-match': '0',
                        'User-Agent': constants.REQ_PYTHON_LIBRARY}
                headers.update(custom_header)
                r = requests.put("{}{}".format(endpoint, ep),
                                    headers=headers, verify=False, data=dbc_file)

                if (r.status_code != requests.codes.no_content):
                    logging.debug(f"{r.headers}")
                if self.log_api_details == True:
                    logging.debug(f"status code: {r.status_code}")
                return r
            except (ConnectionResetError, ProxyError, ConnectTimeout) as e:
                logging.warning(f"ConnectionReset / Proxy Issue:, {e},  Retry count =, {str(retry)}")
                return self.put_request_file(ep, dbc_file, custom_header, retry + 1)
        else:
            assert False, constants.REQ_UNABLE_TO_CONNECT
        

    def delete_request(self, ep, custom_header={}, retry=1):
        if(retry <= 5):
            try:
                token=self.get_auth_token()
                headers = {'Authorization': token,
                'content-type': 'application/json', 'if-match': '0',
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': constants.REQ_PYTHON_LIBRARY}
                headers.update(custom_header)
                if self.log_api_details == True:
                    logging.debug("HTTP DELETE: endpoint: {}{}".format(self.environment, ep))
                r = requests.delete("{}{}".format(self.environment, ep),
                                    headers=headers, verify=False)

                if (r.status_code != requests.codes.no_content):
                    logging.debug(f"{r.headers}")
                if self.log_api_details == True:
                    logging.debug(f"status code: {r.status_code}")
                return r
            except (ConnectionResetError, ProxyError, ConnectTimeout) as e:
                logging.debug(f"ConnectionReset / Proxy Issue: {e}, Retry count =  {str(retry)}")
                return self.delete_request(ep, custom_header, retry + 1)
        else:
            assert False, constants.REQ_UNABLE_TO_CONNECT


    def get_etag(self, ep):
        r = self.get_request(ep)
        etag = r.headers['ETag']
        return etag.replace("\"", "")

    def create_authorization_request(self):
        self.__generate_code_verifier()
        r = requests.get(
            url = self.key_cloak_uri + self.tenant +  "/protocol/openid-connect/auth",
            params={
                "response_type": "code",
                "client_id": self.client_id,
                "scope": "openid",
                "redirect_uri": self.redirect_uri,
                "code_challenge": self.code_challenge,
                "code_challenge_method": "S256",
            },
            allow_redirects=False
        )
        assert r.status_code == requests.codes.ok, "Unable to get Login URL from the Authenticaion Page"
        self.auth_session_id = r.cookies['AUTH_SESSION_ID']
        page = r.text
        self.login_end_point = html.unescape(re.search('<form\s+.*?\s+action="(.*?)"', page, re.DOTALL).group(1))

    def generate_authorization_code(self):
        r = requests.post(
            url=self.login_end_point, 
            data={
                "username": self.user_login,
                "password": self.user_password,
            }, 
            headers={"Cookie": "AUTH_SESSION_ID="+self.auth_session_id},
            allow_redirects=False
        )
        assert r.status_code == requests.codes.found, "Login to Application is failed"
        redirect_uri_with_session = r.headers['Location']
        assert redirect_uri_with_session.startswith(self.redirect_uri), "Login is not redirected to expected Application Page"
        self.__extract_auth_code_from_url(redirect_uri_with_session)
        
    def __extract_auth_code_from_url(self, redirect_uri_with_session):
        query = urllib.parse.urlparse(redirect_uri_with_session).query
        redirect_params = urllib.parse.parse_qs(query)
        self.auth_code = redirect_params['code'][0]

    def __generate_code_verifier(self):
        code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8')
        self.code_verifier = re.sub('[^a-zA-Z0-9]+', '', code_verifier)
        code_challenge = hashlib.sha256(self.code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8')
        self.code_challenge = code_challenge.replace('=', '')

    def get_auth_token_from_refresh_token(self, refresh_token):
        r = requests.post(
            url = self.key_cloak_uri + self.tenant + "/protocol/openid-connect/token",
            data = {
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": self.client_id
                },
            allow_redirects=False
        )
        if(r.status_code == requests.codes.ok):
            return self.store_and_get_token_details(r)
        else: 
            raise ValueError("Refresh token is no longer valid")

    def store_and_get_token_details(self, r):
        
        token = r.json()['access_token']
        token = 'Bearer '+token
        token_data = {
                        "token": token, 
                        "expiry_time": time.time() + int(r.json()['expires_in']), 
                        "environment":self.environ,
                        "refresh_token":r.json()['refresh_token'], 
                        "refresh_expiry_time": time.time() + int(r.json()['refresh_expires_in']),
                        "id_token" : r.json()['id_token']
                        }
        self.api_gen_obj.write_json_file(self.token_path, token_data)
        return token

    def logout_from_app(self, id_token):
        r = requests.get(
            url = self.key_cloak_uri + self.tenant + "/protocol/openid-connect/logout?id_token_hint=" + id_token)
        assert r.status_code == requests.codes.ok, "Unable to logout from the Application"