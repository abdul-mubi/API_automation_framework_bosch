import json
import requests
import logging
from requests.exceptions import ProxyError, ConnectionError, RequestException,HTTPError 

log = logging.getLogger()


class AtlassianAPIRequests():
    def __init__(self, base_url, token):
        
        self.exception_list = (ConnectionResetError, ProxyError, ConnectionError,HTTPError, RequestException)
        self.base_url = base_url
        self.token = token
        

    def assertion_message(self, request_ep, response, req_data = None):
        log.info(f"Status check failed for EP: {self.base_url}{request_ep}")
        log.debug(f"Request Data: {req_data}")
        log.debug(f"Response status code {response.status_code}")
        log.debug(f"Response body {response.text}")
        return f"Request URL: {self.base_url}{request_ep} returned status code {response.status_code}"  

    def get_request(self, url, retry=1):
        headers = {'Authorization': f"{self.token}"}
        if(retry <= 5):
            try:
                r = requests.get(self.base_url + url, headers=headers)
                assert r.status_code == requests.codes.ok, self.assertion_message(url, r)
                return r
            except self.exception_list as e:
                log.debug(f"ConnectionReset / Proxy Issue:, {e}, Retry count =, {str(retry)}")
                return self.get_request(url, retry + 1)
        else:
            assert False, f"Unable to perform GET to the URL: {url} after 5 retries"

    def post_request(self, url, data, retry =1):
        headers = {'Authorization': f"{self.token}",
                   'Content-Type': 'application/json'}
        if(retry <= 5):
            try:
                payload = json.dumps(data)
                r = requests.post(self.base_url + url, headers=headers, data=payload)
                assert r.status_code in [requests.codes.created,requests.codes.ok], self.assertion_message(url, r, req_data=data)
                return r
            except self.exception_list as e:
                log.debug(f"ConnectionReset / Proxy Issue:, {e}, Retry count =, {str(retry)}")
                return self.post_request(url, data, retry + 1)
        else:
            assert False, f"Unable to preform POST to the URL: {url} after 5 retries"
    
    def put_request(self, url, data, retry =1):
        headers = {'Authorization': f"{self.token}",
                   'Content-Type': 'application/json'}
        if(retry <= 5):
            try:
                r = requests.put(self.base_url + url, headers=headers, data=json.dumps(data))
                assert r.status_code in [requests.codes.no_content,requests.codes.ok], self.assertion_message(url, r, req_data=data)
                return r
            except self.exception_list as e:
                log.debug(f"ConnectionReset / Proxy Issue:, {e}, Retry count =, {str(retry)}")
                return self.post_request(url, data, retry + 1)
        else:
            assert False, f"Unable to preform PUT to the URL: {url} after 5 retries"
    
    def post_request_with_files(self,url, file_data, retry = 1):
        headers = {
                    'Authorization': f"{self.token}"
                   }
        if(retry <= 5):
            try:
                r = requests.post(self.base_url + url, headers=headers, files=file_data)
                assert r.status_code == requests.codes.ok, self.assertion_message(url, r, req_data=file_data)
                return r
            except self.exception_list as e:
                log.debug(f"ConnectionReset / Proxy Issue:, {e}, Retry count =, {str(retry)}")
                return self.post_request_with_multipart(url, file_data, retry + 1)
        else:
            assert False, f"Unable to preform POST to the URL: {url} after 5 retries"
    
    def put_request_with_file(self):
        #TODO
        pass
    
    def delete_request(self, url, retry = 1):
        headers = {'Authorization': f"Bearer {self.token}"}
        if(retry <= 5):
            try:
                r = requests.delete(self.base_url + url, headers=headers)
                assert r.status_code == requests.codes.ok, self.assertion_message(url, r)
                return r
            except self.exception_list as e:
                log.debug(f"ConnectionReset / Proxy Issue:, {e}, Retry count =, {str(retry)}")
                return self.delete_request(url, retry + 1)
        else:
            assert False, f"Unable to perform DELETE to the URL: {url} after 5 retries"