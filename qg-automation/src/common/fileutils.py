import os
import json

class FileUtil:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))

    def write_json_file(self, file_path, json_data):
        """Fetches Json file and writes the data as json object"""
        with open(file_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)

    def parse_json_file(self, file_path):
        """Fetches Json file and returns the data as json object"""
        with open(file_path, 'r') as json_file:
            json_data = json.load(json_file)
        return json_data