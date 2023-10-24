import requests
import os
from src.common import constants


class CloudStoreOperation():
    """
    This class is used to perform cloudstore related operations
    """

    def __init__(self) -> None:
        self.base_path = os.path.dirname(os.path.abspath(__file__))
    
    def upload_file_to_cloudstore(self,device_name,zip_name,proxy):
        """
        Used to upload files from device to cloudstore
        Args: 
                device_name : device_id used to upload
                zip_name    : file to upload
                proxy : proxy_address as per user 
        Returns: Blob_id 
        """
        cert_path = f"{constants.DEVICE_CERTIFICATES_PATH}{device_name}.crt.pem"
        key_path = f"{constants.DEVICE_CERTIFICATES_PATH}{device_name}.key.pem"
        file_path = f"{zip_name}"
        if proxy is None:
            proxies = {
                "http": "",
                "https": ""
            }
        else:
            proxies = {
                "http": f"http://{proxy}",
                "https": f"https://{proxy}"
            }
        params = {
            'ttlDays': '1',
            'Content-Type': 'multipart/form-data',
        }
        cert = (cert_path, key_path)
        files = {
            'file': open(file_path, 'rb'),
            'type':'application/octet-stream'
        }
        r = requests.post(constants.DEVICE_UPLOAD_BLOB_URL, params=params, files=files, cert=cert, proxies=proxies)
        return r.json()["contentId"]
