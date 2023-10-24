import requests
import steps.utils.API_Requests as API_Request
import steps.pageObjects.API_Generic_Class as API_Generic_Class
import steps.constantfiles.constants_deviceprovisioning as constants

class ApiDeviceProvisioningClass():
    def __init__(self, enviroment, log_api_details):
        self.api_requests = API_Request.ApiRequestsClass(enviroment, log_api_details)
        self.api_gen_obj = API_Generic_Class.ApiGenericClass()


    def get_device_details(self, device_id):
        r = self.api_requests.get_request(constants.DP_DEVICES_ID.format(device_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r
    
    def dispatch_device(self, device_id, target_space):
        data = {
            "targetBackend":target_space
        }
        etag = self.api_requests.get_etag(constants.DP_DEVICES_ID.format(device_id))
        r = self.api_requests.put_request(constants.DP_DEVICES_ID_DISPATCH.format(device_id),params=data, custom_header = {'if-match': etag})
        assert r.status_code == requests.codes.no_content, self.api_gen_obj.assert_message(r)
    
    def undispatch_device(self, device_id, target_space):
        etag = self.api_requests.get_etag(constants.DP_DEVICES_ID.format(device_id))
        r = self.api_requests.put_request(constants.DP_DEVICES_ID_UNDISPATCH.format(device_id),params="", custom_header = {'if-match': etag})
        assert r.status_code == requests.codes.no_content,self.api_gen_obj.assert_message(r)

    def target_backends(self):
        r = self.api_requests.get_request(constants.DP_TARGET_BACKENDS)
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r.json()['_embedded']['targetBackendList']


