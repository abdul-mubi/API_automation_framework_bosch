import paramiko
import os
import json 
import argparse
import subprocess
from subprocess import Popen
import time
from scp import SCPClient
import zipfile, io
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
from pyunpack import Archive
import shutil

class FactoryReset:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.keypath = self.base_path + "\\developerKeyCCU"
        self.device_id = device_id
        self.hostname = device_hostname
        self.to_version = to_version
        self.art_credential = self.get_artifactory_credential()
        self.ssh_commands = self.get_ssh_commands()
        self.delete_auto_created_folder()
        self.customer_name = self.check_device_customer()
        self.platform_fw = self.get_patform_fw_name()
        self.device_vin = self.get_device_vin()
        self.factory_reset = factory_reset

    def ssh_execute(self, command):
        key = paramiko.RSAKey.from_private_key_file(self.keypath)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            print('-'*20 + 'Running SSH command' + '-'*20)
            client.connect( hostname = self.hostname, username= "root", password= "", pkey = key)
            print('-'*20 + 'Connected to device successfully' + '-'*7)
            stdin , stdout, stderr = client.exec_command(command)
            out = stdout.read().decode('unicode_escape').encode('utf-8')
            err = stderr.read().decode('unicode_escape').encode('utf-8')
        except Exception as e:
            print(f'Error message - {e}')
            out = " "
            err = f"Error while connecting to -> {self.hostname}" 
            print(f"{err}")
       
        client.close()
        return (out, err)
    
    def copy_to_repo_with_scp(self, source, destination):
        print('Starting SCP process...')
        key = paramiko.RSAKey.from_private_key_file(self.keypath)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect( self.hostname, 22, username = "root", password= "", pkey = key, timeout=150 )
        scp = SCPClient(client.get_transport())
        scp.get(source, destination)

    def copy_to_device_with_scp(self, source, destination):
        print('Starting SCP process...')
        key = paramiko.RSAKey.from_private_key_file(self.keypath)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect( self.hostname, 22, username = "root", password= "", pkey = key, timeout=150 )
        scp = SCPClient(client.get_transport())
        scp.put(source, destination)

    def assert_message(self, response_detail):
        try:
            if "error" in response_detail.json():
                return f'Failed with Response code - {response_detail.json()["status"]}, Type - {response_detail.json()["error"]}, Error message - {response_detail.json()["message"]}'
            elif "detail" in response_detail.json():
                return f'Failed with Response code -{response_detail.json()["status"]}, Detail - {response_detail.json()["detail"]}'
            else:
                return f'API request failed with response code {response_detail.status_code}'
        except json.decoder.JSONDecodeError:
            return f'Response body is absent. API request failed with response code {response_detail.status_code}'

    def get_artifactory_credential(self):
        test_prop_path = self.base_path + "\\testProp.json"
        with open(test_prop_path, 'r') as testPropFile:
            art_credential = json.load(testPropFile)
        return art_credential

    def get_ssh_commands(self):
        command_file_path = self.base_path + "\\sshCommand.json"
        with open(command_file_path, 'r') as command_file:
            ssh_commands = json.load(command_file)
        return ssh_commands

    def get_patform_fw_name(self):
        self.image_download_path = self.base_path + "\\images"
        os.chdir(self.image_download_path)
        platform_fw_7z = os.listdir('.')
        Archive(platform_fw_7z[0]).extractall(self.image_download_path)
        platform_fw = platform_fw_7z[0].replace('7z', 'ubifs')
        return platform_fw

    def start_factory_reset(self):   
        print("Factory reset started .......")
         
        print('Precondition before starting factory reset - Overall 3 steps to complete precondition')
        self.check_device_status()
        print('Stage 1/3 of the precondition completed')
        self.get_file_from_artifactory()
        print('Stage 2/3 of the precondition completed')
        self.backup_certificate_from_device()
        print('Stage 3/3 of the precondition completed')

        print('Performing USB update with deleting data partition for the given device FW version')
        self.perform_usb_update()

        if self.factory_reset:
            print('Install platform FW in one partition of the device -Overall 4 steps to complete factory reset')
            self.copy_full_update_to_device()
            print('Stage 1/4 of the factory reset completed')
            self.install_platform_fw()
            print('Stage 2/4 of the factory reset completed')

        #Performing full update (using tar.gz file) on the device for the given FW version
            self.check_device_stability(5)
            print('Stage 3/4 of the factory reset completed')
            self.execute_full_update()
            print('Stage 4/4 of the factory reset completed')

        print('After completing update process set device to normal state to connect with backend - Overall 4 steps to complete')
        self.upload_device_certificate()
        print('Stage 1/4 completed')
        # self.validate_mprm_file()
        self.validate_device_version()
        print('Stage 2/4 completed')
        self.implant_device_vin()
        print('Stage 3/4 completed')
        self.delete_auto_created_folder()
        print('Stage 4/4 completed')

        print("Factory reset completed .......")

    def check_device_customer(self):
        result = self.ssh_execute(self.ssh_commands['readDeviceCustomer']['CCU'])
        first_line = str(result[0]).split("'")[1].split("\\n")[0]
        value = first_line[first_line.index("val ")+4:].strip()
        if value == "( 50 01 )":
            customer_name = "PACCAR"
            print(f'{customer_name} is recognized as the customer')
        elif value == "( 48 01 )":
            customer_name = "HINO"
            print(f'{customer_name} is recognized as the customer')
        elif value == "( 50 02 )": 
            customer_name = "PACCAR_NON_NGD"
            print(f'{customer_name} is recognized as the customer')
        else:
            print(f'No customer matching the value {value} is found')
            assert False, f"Device - {self.device_id} is not a known customer, Please find the list of known customer - PACCAR, HINO, PACCAR_NON_NGD"
        return customer_name

    def check_device_status(self):
        proc = subprocess.Popen("ipconfig", shell=True, stdin=None, stdout=subprocess.PIPE, stderr=True)
        proc.wait()
        time.sleep(5)
        out,err = proc.communicate()
        assert err is None, f"Device ip - {self.hostname} is not proper, Please check the same. It returned error : {err}"
        device_host = self.fetch_device_host()
        assert device_host in str(out), f"Device - {self.device_id} with this hostname {self.hostname} is not ONLINE"
        print(f"Device with this ip - {self.hostname} is ONLINE")

    def fetch_device_host(self):
        device_host = ""
        required_host = False
        for c in reversed(self.hostname):
            if c == '.' and ~required_host :
                device_host = c + device_host
                required_host = True
            elif required_host:
                device_host = c+ device_host
        return device_host

    def get_file_from_artifactory(self):
        art_fact_url=self.art_credential['artifactory']['url']
        artifactory_credentials= self.art_credential['artifactory']['credentials']
        self.basic_auth_header = {'Authorization': "Basic "+artifactory_credentials,
        'accept': '*/*',
        'content-type': 'text/html',
        'User-Agent': 'Python Requests library'}

        print(f"Copying image and full update package from artifactory to working directory for device FW version - {self.to_version}")
        self.file_from_artifactory(art_fact_url,self.basic_auth_header,self.image_download_path, True, False)
        full_update_download_path=self.base_path+"\\full_update_package"
        os.makedirs(full_update_download_path)
        gz_file = self.file_from_artifactory(art_fact_url,self.basic_auth_header,full_update_download_path, False, True)
        gz_file_strip=gz_file.strip(",_(unzip_me_before_install).zip")
        self.gz_file_name=gz_file_strip+".tar.gz"
        
    def file_from_artifactory(self, url, basic_auth_header, download_path, get_image, get_full_update):
        regex_update_to_version=f"{self.to_version}/$"
        basic_url_request = self.artifactory_get_request(url,basic_auth_header)
        date_field_url=self.get_zip_file_name(basic_url_request,regex_update_to_version)
        basic_url = self.get_basic_url(date_field_url, url)

        if get_image:
            zip_file_name = "images.zip"
        elif get_full_update:
            basic_url = basic_url + "self-updates/"
            zip_file_name = f"^Full.*{self.to_version}.*Debug.*"
        
        download_path_url= self.artifactory_get_request(basic_url,basic_auth_header)
        zip_file_to_download=self.get_zip_file_name(download_path_url,zip_file_name)
        download_url=f"{basic_url}{zip_file_to_download}"

        zip_file_url= self.artifactory_get_request(download_url,basic_auth_header)
        zip_file = zipfile.ZipFile(io.BytesIO(zip_file_url.content))   
        zip_file.extractall(download_path)
        return zip_file_to_download

    def artifactory_get_request(self,url, headers):
        r = requests.get(url, headers=headers)
        assert r.status_code == requests.codes.ok, self.assert_message(r)
        return r

    def get_zip_file_name(self,parse_url,zip_file_name):
        file_found = False
        html_file = BeautifulSoup(parse_url.text, "html.parser")
        for link in html_file.find_all('a'):
            target_string=(link.get('href'))
            req_zip_link=re.search(zip_file_name, target_string, re.IGNORECASE)
            if req_zip_link != None:
                zip_file_unquote=urllib.parse.unquote(target_string)
                file_found = True
                break

        assert file_found == True , "The requested image version zip file is not found in artifactory"
        return zip_file_unquote

    def get_basic_url(self, date_field_url, url): 
        #Fw released after 4.11.1 has customer name (i.e) paccar and hino in end URL. To check given FW is released after or before 4.11.1 we have hardcorded 4.11.1 release date.
        fw_4_11_1_date = "2022-03-24" 
        date_list = str(date_field_url).split('_')
        if fw_4_11_1_date >= date_list[0]:
            basic_url=f"{url}{date_field_url}Debug/"
        else:
            if self.customer_name == "PACCAR" or self.customer_name == "PACCAR_NON_NGD":
                basic_url=f"{url}{date_field_url}Paccar/Debug/"
            elif self.customer_name == "HINO":
                basic_url=f"{url}{date_field_url}Hino/Debug/"
        return basic_url

    def backup_certificate_from_device(self):
        file_path = self.base_path + "\\Device_Certificate"
        path = os.path.join(file_path, self.device_id)
        os.makedirs(path)
        self.ssh_execute(self.ssh_commands['zipCrtFolder']['CCU'])
        self.copy_to_repo_with_scp("/data/encrypted/crt.zip",path)
        self.ssh_execute(self.ssh_commands['delCrtZip']['CCU'])

    def perform_usb_update(self):
        self.override_psfile(self.image_download_path + "\\flash_ubi_windows.ps1", '"Yes"', False) # Override $Result attribute as YES in ps1 file to always delete data partition
        self.execute_ps_file()
        print("USB update with deleting data partition is completed successfully.....")
        self.check_device_stability(5)

    def override_psfile(self, path, delete_data_partition, install_platform_fw):
        f = open(path, 'r')
        line_list = f.readlines()
        f.close()
        fw = open(path, 'w')
        lines_removed_1,lines_removed_2 = False, False
        lines_to_remove = []
        for i in range(len(line_list)):
            line = line_list[i]
            line = line.strip()
            if "$exitcode" in line and not lines_removed_1:
                lines_to_remove = self.get_index_of_lines_to_del(line_list, i+2, "$exitcode")
                lines_removed_1 = True
            elif "$Result" in line and not lines_removed_2:
                line = line[:10] + delete_data_partition
                lines_removed_2 = True
                lines_to_remove = self.get_index_of_lines_to_del(line_list, i+1, "$Result")
            elif install_platform_fw and "-1g.ubifs" in line:
                line = line[:10] + '"' + self.platform_fw + '"' + '}'
            if i not in lines_to_remove:
                print(f'>>>>{line}')
                fw.write(f'{line}\n')
        fw.close()

    def get_index_of_lines_to_del(self, line_list, index, function_name):
        index_of_lines = []
        for j in range(index, len(line_list)):
            if function_name not in line_list[j]:
                index_of_lines.append(j)
            else:
                break
        return index_of_lines

    def execute_ps_file(self):
        print("Current working directory: {0}".format(os.getcwd()))
        print("Changing working directory")
        os.chdir(self.image_download_path)
        print("Current working directory: {0}".format(os.getcwd()))
        self.ssh_execute(self.ssh_commands['rebootDevice']['CCU'])
        proc = subprocess.Popen(['powershell.exe', "./flash_ubi_windows.ps1"], stdin=None, stdout=subprocess.PIPE, stderr=True)
        out,err = proc.communicate() 
        assert err is None, f"USB flashing on device - {self.device_id} is not performed properly. It returned error : {err}"
        print(out.decode("utf-8").strip())
        print("Waiting for 90 seconds to let the device to reboot")
        time.sleep(90)

    def copy_full_update_to_device(self):
        remotepath = "/data/"
        file_path = self.base_path + f"\\full_update_package\\{self.gz_file_name}"
        print(f"File copying from : {file_path}  - > to : {remotepath}")
        self.copy_to_device_with_scp(file_path,remotepath)
        print("tar.gz file is copied successfully")

    def install_platform_fw(self):
        self.override_psfile(self.image_download_path + "\\flash_ubi_windows.ps1", '"No"', True)
        self.execute_ps_file()
        print("Platform FW installation is completed successfully....")

    def check_device_stability(self, count):
        connectivity = self.ssh_execute("date")
        print(connectivity)
        time.sleep(count*count)
        proc = subprocess.Popen("ipconfig", shell=True, stdin=None, stdout=subprocess.PIPE, stderr=True)
        proc.wait()
        out,err = proc.communicate()
        device_host = self.fetch_device_host()
        if device_host not in str(out):
            print("Device is not stable.. Reboot is not completed yet")
            time.sleep(60)
            count -= 1
            if count != 0:
                self.check_device_stability(count)
            else:
                assert False, f"Device is not accessable even after {60*count} second"
        else:
            print("Device is accessable now")

    def execute_full_update(self):
        command = "install_patch.sh /data/"+ self.gz_file_name +" 1 1"
        print('Running install patch command')
        out, err = self.ssh_execute(command)
        print(str(out))
        assert 'SUCCESS' in str(out), f"Install patch command is not executed successfully. Output - {str(out)} and Error - {str(err)}"
        self.ssh_execute(self.ssh_commands['rebootDevice']['CCU'])
        print("Waiting for 90 seconds to let the device to reboot")
        time.sleep(90)
        self.check_device_stability(5)
        print("Running tail command to complete full update. Once full update is done, device will reboot on its own")
        tail_out = self.ssh_execute(self.ssh_commands['tailCommand']['CCU'])
        print(str(tail_out))
        print("Device auto reboot is started....")
        time.sleep(90)
        self.check_device_stability(5)
        print(f"Full update for device FW - {self.to_version} is completed successfully.....")

    def upload_device_certificate(self):
        remotepath = "/data/encrypted/"
        file_path = self.base_path + f"\\Device_Certificate\\{self.device_id}\\crt.zip"
        print(f"File copying from : {file_path}  - > to : {remotepath}")
        self.copy_to_device_with_scp(file_path,remotepath)
        print("Certificate copied successfully")
        self.ssh_execute(self.ssh_commands['delCrtFolder']['CCU'])
        output = self.ssh_execute("cd .. && unzip /data/encrypted/crt.zip")
        print(output)
        print("crt folder is unzipped")
        self.ssh_execute(self.ssh_commands['delCrtZip']['CCU'])
        print("Setting up device by executing config client commands")
        self.device_setup()
        print("Rebooting the device.....")
        self.ssh_execute(self.ssh_commands['rebootDevice']['CCU'])
        print("Final reboot - Waiting for 90 seconds to let the device to reboot")
        time.sleep(90)
        self.check_device_status()

    def device_setup(self):
        command_list = ["DeviceProfileId","Esim","LTEAntenna","DeviceSerialNumber"]
        for i in range(len(command_list)):
            if command_list[i] == "DeviceProfileId":
                command = self.ssh_commands["implant"+command_list[i]+self.customer_name]['CCU']
                out = self.ssh_execute(command)
            elif command_list[i] == "DeviceSerialNumber":
                device_serial_num = self.device_id.split('_')[1]
                serial_hex = str.encode(device_serial_num).hex()
                serial_hex = ' '.join(a+b for a,b in zip(serial_hex[::2], serial_hex[1::2]))
                command = self.ssh_commands["implant"+command_list[i]]['CCU']
                out = self.ssh_execute(command+serial_hex)
            else:
                command = self.ssh_commands["implant"+command_list[i]]['CCU']
                out = self.ssh_execute(command)
            assert "SUCCESS" in str(out), f"Config client command to implant {command_list[i]} for {self.customer_name} not executed successfully - {out}"
        print("---------Deleting mprm.prs file from device------------")
        self.ssh_execute(self.ssh_commands['delmprmFile']['CCU'])

    def validate_mprm_file(self):
        out = self.ssh_execute(self.ssh_commands['getmprmFile']['CCU'])
        lines_list = str(out).split("\\n")
        exp_line_list = []
        for line in lines_list:
            if "provisioning.spid" in line:
                assert line.split("=")[1] == self.device_id,f"provisioning.spid attribute has different device id, Expected device id - {self.device_id}"
                exp_line_list.append(line)
            elif "prm.name" in line:
                assert line.split("=")[1] == self.device_id,f"prm.name attribute has different device id, Expected device id - {self.device_id}"
                exp_line_list.append(line)
            elif "javax.net.ssl.keyStore=" in line:
                assert line.split("=")[1] == f"/data/encrypted/crt/{self.device_id}.p12", "device certificate is not available at the expected location"
                exp_line_list.append(line)

        if len(exp_line_list) == 3:
            print(f"Device - {self.device_id} has proper certificate and serial number as implanted")
        else:
            assert False, f"FW installation failed. Device - {self.device_id} has no proper certificate and serial number."
    
    def validate_device_version(self):
        out = self.ssh_execute(self.ssh_commands['getCCUVersion']['CCU'])
        lines_list = str(out).split("\\n")
        for line in lines_list:
            if "Short_Version" in line:
                assert self.to_version in line.split(":")[1], f"Device - {self.device_id} has wrong version. Expected device version is {self.to_version}"
                break
        print(f"Device - {self.device_id} has expected version - {self.to_version}")

    def get_device_vin(self):
        out, err = self.ssh_execute(self.ssh_commands['getDeviceVIN']['CCU'])
        if 'No such file or directory' in str(err):    
            print('device has no vin')
            device_vin = ''
        else:
            device_vin = str(out).split("'")[1].replace("'","")
            assert len(device_vin) == 17, f"Device vin doesn't have 17 digit value. Detected device vin - {device_vin}"
        return device_vin

    def implant_device_vin(self):
        if self.device_vin != '':
            out, err= self.ssh_execute(self.ssh_commands['eraseDeviceVIN']['CCU'])
            assert "SUCCESS" in str(out), f"Device vin is not erased properly. Error message - {str(err)} "
            vin_hex = str.encode(self.device_vin).hex()
            vin_hex = ' '.join(a+b for a,b in zip(vin_hex[::2], vin_hex[1::2]))
            command = self.ssh_commands['implantDeviceVIN']['CCU']
            out, err = self.ssh_execute(command + vin_hex)
            assert "SUCCESS" in str(out), f"Device vin is not implanted properly. Error message - {str(err)} "
            print(f"Vin - {self.device_vin} is implanted on the device - {self.device_id}.")
        else:
            print('No vin is implanting as device has no vin while starting the factory reset.')

    def delete_auto_created_folder(self):
        folders_to_delete = ['Device_Certificate','full_update_package', 'images']
        for folder_to_delete in folders_to_delete:
            if folder_to_delete == 'images':
                self.delete_image_content(folder_to_delete)
            elif os.path.exists(self.base_path + '/'+ folder_to_delete):
                try:
                    shutil.rmtree(self.base_path + '/'+ folder_to_delete)
                    print(f"Folder '{folder_to_delete}' deleted successfully.")
                except OSError as e:
                    print(f"Error: {e}")
            else:
                print(f"Folder '{folder_to_delete}' does not exist.")
    
    def delete_image_content(self, folder_to_delete):
        for root, dirs, files in os.walk(self.base_path + '/'+ folder_to_delete):
            for file in files:
                file_path = os.path.join(root, file)
                if '7z' not in file:
                    try:
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,add_help=False)
    parser.add_argument('--help', action='help', default=argparse.SUPPRESS, help='Device reset Help')
    parser.add_argument("--device",help='ID of the Device \nEg: E2E_OTA_DEVICE_001',type=str, required=True)
    parser.add_argument("--hostname",help='Device IP\nNote : Not mandatory to send hostname if its value is 192.168.1.40 \nEg: 192.168.1.40',type=str, required=True)
    parser.add_argument("--to_version",help='Device FW version needs to be installed in the device \nEg: 4.11.1',type=str, required=True)
    parser.add_argument("--factory_reset",help='Type True if you want to perform factory reset \nType False if you want to perform basic reset',type=str, default=False , required=False)
    args = parser.parse_args()
    device_id = args.device
    device_hostname = args.hostname
    to_version = args.to_version
    factory_reset = False
    if args.factory_reset:
        factory_reset = args.factory_reset

    factory_reset_obj = FactoryReset()
    factory_reset_obj.start_factory_reset()
