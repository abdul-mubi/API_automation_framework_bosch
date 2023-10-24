import os
import json
import sys
from report_html_script import ReportHtmlFuncs
from src.common.fileutils import FileUtil

class qg_reporthtml:

    details = {}
    summary = {}
    validation_list = []
    test = None

    def __init__(self):
        self.report_html_script_obj = ReportHtmlFuncs()
        self.fileutil_obj = FileUtil()
        self.path = os.path.dirname(os.path.abspath(__file__)) + "\\" +"report.html"
        self.console_path = os.path.dirname(os.path.abspath(__file__)) + "\\..\\temp\\console.txt"

    def qg_result(self, test_id):
        test_list = self.fileutil_obj.parse_json_file(f"userdata\\result\\qg_urldata_{test_id}.json")
        for test,values in test_list.items():
            self.details.update({test:values})
           
    def convert_json_to_html(self):
        print("Converting JSON into HTML Report")
        table = self.report_html_script_obj.create_details_table(self.details, self.test)        
        return table

    def write_to_html(self, test_id):
        self.test = test_id
        
        with open(self.path, 'w') as file:
            file.write(self.convert_json_to_html())

    def write_output_to_html(self, test_id):
        f = open(self.console_path, "r")
        key = f.read()
        with open(self.path, 'w') as file:
            file.write(f"<p>Clone of <a href='https://rb-tracker.bosch.com/tracker15/browse/{test_id}'>{test_id}</a>. Please find the new test execution ticket <a href='https://rb-tracker.bosch.com/tracker15/browse/{key}'>{key}</a> </p>")


if __name__ == "__main__":
    test_id = sys.argv[1]
    action = sys.argv[2]
    output = ''.join(sys.argv[3:])
    if action != "CLONE_TEST_EXECUTION":
        qg_reporthtml().qg_result(test_id)
        qg_reporthtml().write_to_html(test_id)
    else:
        qg_reporthtml().write_output_to_html(test_id)
    