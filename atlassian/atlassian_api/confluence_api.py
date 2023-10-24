import logging
import atlassian_api.constants as constant
from atlassian_api.atlassian_api_requests import AtlassianAPIRequests
log = logging.getLogger()


class ConfluenceAPI:
    def __init__(self, base_url, token):
        """
        Requires the BASE URL of the JIRA System and the access token to to authorize user to the system

        Args:
            base_url (str): Base URL of JIRA (Eg: https://example.com )
            token (str): Access token (Basic and Bearer tokens can be added) Eg: Bearer <TOKEN> or Basic <B64-encoded-username&pwd>
        """
        self.confluence_api = AtlassianAPIRequests(base_url, token)

    def get_content_from_page_id(self, page_id):
        """Gets content from confluence page

        Args:
            page_id (str): Confluence page id

        Returns:
            dictionary: Content of the page
        """
        log.debug("Getting contents from Confluence Page")
        r = self.confluence_api.get_request(constant.CONFLUENCE_CONTENT.format(page_id=page_id))
        return r
    
    def get_page_info_from_title(self, space, title):
        """Gets page ID from Confluence Title

        Args:
            title (str): Confluence page title
            space (str): Confluence Space

        Returns:
            page_id: page ID
        """
        log.debug("Getting Page information from title")
        r = self.confluence_api.get_request(constant.GET_PAGE_BY_TITLE.format(space=space,title=title))
        return r