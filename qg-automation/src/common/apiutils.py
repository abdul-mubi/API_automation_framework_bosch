import os
import requests
import json
import src.common.constants as constants
from src.common.logger import get_logger
log = get_logger()
## This python file will be removed post few days after this PR Merge
class ApiRequests:
    def __init__(self):
        self.basepath = os.path.dirname(os.path.abspath(__file__))

    def get_request(self, ep, headers=None, **kwargs):
        log.debug("HTTP GET: endpoint: {}".format(ep))
        if headers != None:
            r = requests.get(ep, headers=headers, **kwargs)
        else:
            r = requests.get(ep)
        log.debug(f"status code:  {r.status_code}")
        if (r.status_code != requests.codes.ok):
            log.debug(f"{r.headers}")
        return r

    def post_request(self, ep, params, custom_header={}):
        log.debug("HTTP POST: endpoint: {}".format(ep))
        log.debug(f"payload: , {params}")
        r = requests.post(ep, headers=custom_header, data=params)
        log.debug(f"status code:  {r.status_code}")
        if (r.status_code != requests.codes.ok):
            log.debug(f"{r.headers}")
        return r

    def put_request(self, ep, params, custom_header={}):
        log.debug("HTTP PUT: endpoint: {}".format(ep))
        log.debug(f"payload: , {params}")
        headers = { 'Content-type': constants.REQ_PYTHON_CONTENT_JSON,
        'User-Agent': constants.REQ_PYTHON_LIBRARY}
        headers.update(custom_header)
        r = requests.put(ep, headers=headers, data=params)
        log.debug(f"status code:  {r.status_code}")
        if (r.status_code != requests.codes.no_content):
            log.debug(f"{r.headers}")
        return r