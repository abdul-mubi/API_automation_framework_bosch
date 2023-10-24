import json
import os
import xmltodict
import base64
import zipfile
import shutil
import pandas
from pathlib import Path
from src.common.logger import get_logger
from src.common import constants
log = get_logger()
class FileUtil:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__)) + "/../../"
    
    def parse_json_file(self, file_path):
        """Fetches Json file and returns the data as json object"""
        log.debug(f"Parsing JSON file from path: {file_path}")
        path = self.__fetch_path(file_path)
        with open(path, 'r', encoding='utf-8') as json_file:
            json_data = json.load(json_file)
        return json_data

    def write_json_file(self, file_path, json_data):
        """Writes the JSON value to the specified file"""
        log.debug(f"Writing to JSON file at path: {file_path}")
        path = self.base_path + file_path
        with open(path, 'w') as json_file:
            json_file.write(json.dumps((json_data),indent=2))
    
    def get_json_from_xml(self, file_path):
        """Parses xml to json and returns JSON Data"""
        log.debug(f"Reading XML: {file_path}")
        path = self.__fetch_path(file_path)
        with open(path, 'r') as xml_file:
            data_dict = xmltodict.parse(xml_file.read())
        log.debug("XML parsed to JSON successfully")
        return json.loads(json.dumps(data_dict))
    
    def convert_json_to_xml(self, file_path, json_data):
        """Parses JSON and converts the value into xml writes it to the file path specified"""
        log.debug(f"Converting json data to XML at path: {file_path}")
        path = self.base_path + file_path
        xml_data = xmltodict.unparse(json_data, pretty=True)
        with open(path, 'w') as xml_file:
            xml_file.write(xml_data)

    def encrypt_zip_to_base64(self, file_path):
        """Encrypts the zip file to the base64 encoded string and returns value of the base64 string"""
        log.debug(f"Encrypting Zip: {file_path} to Base64")
        path = self.base_path + file_path
        with open(path, "rb") as zip_file:
            bytes_data = zip_file.read()
        return base64.b64encode(bytes_data)
    
    def encrypt_base64(self, data):
        """Encrypts the content of variable to the base64 encoded string and returns value of the base64 string"""
        return base64.b64encode(data)
    
    def decrypt_base64_to_zip(self, file_path, encoded_string):
        """decrypts the base64 value and converts into the zip"""
        log.debug(f"Decrypting Base64 to Zip at: {file_path}")
        path = self.base_path + file_path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        bytes_data = base64.b64decode(encoded_string)
        with open(path, "wb") as zip_file:
            zip_file.write(bytes_data)
        zipfile.ZipFile.testzip(zipfile.ZipFile(path))
        
    def extract_zip_file(self, file_path, folder_name):
        """Extracts the contents of zip file and stores it into temp directory and returns the path to the extracted folder"""
        log.debug(f"Extracting Zip: {file_path} to {folder_name} folder")
        path = self.base_path + file_path
        folder_path = os.path.join(self.base_path,folder_name)
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(folder_path)
        return folder_path
    
    def make_zip_file(self, folder_name, file_path):
        "Prepares zip from the folder_name directory defined and stores into file_path as zip file "
        log.debug(f"Preparing Zip at: {file_path} from {folder_name} folder")
        zip_file = zipfile.ZipFile(self.base_path + file_path, 'w', zipfile.ZIP_DEFLATED)
        root_path = len(self.base_path + folder_name)
        for base, dirs, files in os.walk(self.base_path + folder_name):
            for file in files:
                fn = os.path.join(base, file)
                zip_file.write(fn, fn[root_path:])
        zip_file.close()
        log.debug("Zip created successfully")
        
    def move_dir(self, source_dir, dest_parent_dir):
        """To move contents fo directory from one path to another"""
        log.debug(f"Moving Dir: {source_dir} to {dest_parent_dir} folder")
        shutil.move(self.base_path + source_dir, self.base_path + dest_parent_dir)
        
    def delete_dir(self, dir_path):
        """To delete contents of directory from specified path"""
        log.debug(f"Deleting folder {dir_path}")
        shutil.rmtree(self.base_path + dir_path, ignore_errors = True)
        
    def copy_dir(self, source_dir, dest_dir):
        """To copy contents of directory from specified path to another"""
        log.debug(f"Copying contents from {source_dir} to {dest_dir} successfully")
        dest_path = self.base_path + dest_dir
        if os.path.exists(dest_path):
            log.debug(f"Dir: {dest_dir} already exists. Deleting the directory")
            shutil.rmtree(dest_path)
        shutil.copytree(self.base_path + source_dir, dest_path)
        log.debug(f"Copied contents from {source_dir} to {dest_dir} successfully")
        
    def delete_file(self, file_path):
        """To delete the file from specified path"""
        log.debug(f"Deleting {file_path}")
        path = self.base_path + file_path
        if os.path.exists(path): os.remove(path)
        
    def create_protobuf_file(self, proto_obj, file_name):
        """Creates protobuf file from protobuf object and stores it"""
        path = self.base_path + file_name
        os.makedirs(path)
        
        with open(os.path.join(path, Path(file_name).name + ".pb"), "wb") as f:
            f.write(proto_obj.SerializeToString())
        with open(os.path.join(self.base_path, file_name + ".pb_txt"), "w") as f:
            f.write(str(proto_obj))
        return path
    
    def read_file_as_binary(self, file_path):
        """Read the specified file and returns data"""
        path = self.__fetch_path(file_path)
        with open(path, 'rb') as file:
            data = file.read()
        return data
    
    def write_to_file_binary(self, path, file_name, bytes_data):
        """Writes the content to specified file"""
        log.debug(f"Writing to Binary file at path: {path}{file_name}")
        path = self.base_path + path
        os.makedirs(path,exist_ok=True)
        with open(os.path.join(path, file_name), 'wb') as data_file:
            data_file.write(bytes_data)

    def read_file_as_string(self, file_path):
        """Read the specified file as string and returns data"""
        path = self.__fetch_path(file_path)
        with open(path, 'r', encoding='utf-8') as file:
            data = file.read()
        return data
    
    def copy_file(self, src, dest):
        """Copies file from src path to destination with the specified file name on destination path"""
        src_path = self.base_path + src
        dest_path = self.base_path + dest
        os.makedirs(Path(dest_path).parent,exist_ok=True)
        shutil.copyfile(src_path , dest_path)
    
    def fetch_sub_folders(self, path):
        """Fetches sub directory in the directory and returns it as list

        Args:
            path (string): Path of the directory

        Returns:
            List: Contains name of the sub directories. In case there are no sub directories available empty list will be returned
        """
        sub_dir_list = []
        folder_path = self.base_path + path
        if os.path.exists(folder_path):
            directory_contents = os.listdir(folder_path)
            sub_dir_list =  [item for item in directory_contents if os.path.isdir(os.path.join(folder_path,item))]
        return sub_dir_list
    
    def cleanup_folder_content_by_time(self, path, unix_time):
        """Cleanup the folder contents based on time

        Args:
            path (string): Directory path
            unix_time (int/float): Epoch time, folder/ file created before this time will be cleared
        """
        folder_path = self.base_path + path
        if os.path.exists(folder_path):
            directory_contents = os.listdir(folder_path)
            for item in directory_contents:
                item_path = os.path.join(folder_path,item)
                if os.stat(os.path.join(folder_path,item)).st_ctime < unix_time:
                    shutil.rmtree(item_path) if os.path.isdir(item_path) else os.remove(item_path)
                        
    def read_csv(self, path):
        """Reads the CSV file and returns the data.
        Args:
            path (string): Path of the CSV file

        Returns:
            csv_data: CSV data
        """
        if self.read_file_as_string(self.__fetch_path(path)).startswith("Test-Step.ID"):
            log.debug("CSV file is from MC Backend, processing it with necessary actions")
            csv_data = pandas.read_csv(self.__fetch_path(path), skip_blank_lines=True, skiprows=[0,2],sep = ";")
            csv_data.drop(csv_data.columns[[0,1,2]],axis=1, inplace=True)
            column_names = list(csv_data)
            for id in range (0,len(column_names)):
                full_name = column_names[id]
                signal_name = full_name.split(" (")[0]
                column_names[id] = signal_name
            csv_data.columns = column_names
        else:
            csv_data =  pandas.read_csv(self.__fetch_path(path), skip_blank_lines=True)
        csv_data.fillna(method='bfill', inplace=True)
        return csv_data
    
    def check_file_availability(self, path):
        """Checks for availability of file

        Args:
            path (String): File path

        Returns:
            Boolean: True if file exists, else false
        """
        log.debug(f"Fetching file path {self.__fetch_path(path)}")
        return os.path.isfile(self.__fetch_path(path))
        
    
    def __fetch_path(self, path):
        """
        To fetch the path of the file or folder. 
        This method is intended to read data from different folders

        Args:
            path (String): Path of the file or folder

        Returns:
            path: if the path exists inside data generator dir, it returns relative path to the file/folder else returns the path value as it is.
        """
        
        rel_path = self.base_path + path
        if os.path.isfile(rel_path) or os.path.exists(rel_path):
            return rel_path
        else:
            return path