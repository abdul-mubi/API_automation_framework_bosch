import os
import json
import src.common.constants as constants
import re
import struct
import base64
from src.common.logger import get_logger
from atlassian_api.confluence_api import ConfluenceAPI
log = get_logger()

base_path = os.path.dirname(os.path.abspath(__file__)) + "/../../"

config_path = base_path + "common/TestData/testConfig.json"
with open(config_path, 'r') as dataFile:
    config_data = json.load(dataFile)

confluence_api = ConfluenceAPI(config_data["confluence"]["ApiBaseURI"], config_data["confluence"]["token"])

class ConfluenceOperation:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))

    def page_id_from_tiny_link(self, uri, _re=re.compile(r'/x/([-_A-Za-z0-9]+)')):
        """Converts tiny link to page Id
        
        Returns:
            Page Id: Returns Page Id
        """
        log.info("Page ID generated from tiny link")
        matched = _re.search(uri)
        if matched:
            tiny_url_id = matched.group(1)
        if isinstance(tiny_url_id, str):
            tiny_url_id = tiny_url_id.encode('ascii')
            tiny_url_id += b'=' * (len(tiny_url_id) % 4)
            page_id_bytes = (base64.b64decode(tiny_url_id, altchars=b'_-') + b'\0\0\0\0')[:4]
            return struct.unpack('<L', page_id_bytes)[0]
        else:
            raise ValueError("Not a tiny link: {}".format(uri))

    def tiny_id(self, page_id):
        """Return tiny link ID for the given page ID
        
        Args:
            page_id: Page Id of conflucence page
        Returns:
            Encoded ID: Returns tiny link
        """
        log.info("Generating Tiny link ID")
        return base64.b64encode(struct.pack('<L', int(page_id)).rstrip(b'\0'), altchars=b'_-').rstrip(b'=').decode('ascii')
    
    def validate_content_availablity_from_page_id(self, page_id):
        """validate content in confluence page
        
        Args:
            page_id: Page Id of conflucence page
        Returns:
            response_msg: Returns the status code on successful validation
        """
        log.debug("Validating Content in confluence page")
        r = confluence_api.get_content_from_page_id(page_id)
        if len(r.json()["body"]):
            return r.status_code
        else:
            return constants.RESPONSE_PAGENOTFOUND

    def get_page_id_from_title(self, space, title):
        """Get page Id from Title"""
        log.debug("Getting page ID from title")
        r = confluence_api.get_page_info_from_title(space, title)
        if len(r.json()["results"]):
            page_id = r.json()["results"][0]["id"]
            return page_id
        else:
            return constants.RESPONSE_PAGENOTFOUND