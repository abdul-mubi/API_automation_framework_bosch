import json
import os
import datetime
import logging
import API_Test.features.steps.constantfiles.constants_report as constants
import API_Test.features.jira_operations as jira_operations
import report_html_script as report_html_script

jira_api_obj = jira_operations.JiraOperations()
class ReportJsonToHtml:
    
    scenario = {}
    failed_tests_details = {}
    count = {}
    total_count={} 
    version = {}
    tests_failed_with_defects=0
    
    def __init__(self) -> None:
        try:
            self.tests_with_defect = self.parse_json_file("temp/test_with_defects.json")
        except Exception:
            self.tests_with_defect = None

    def get_defects_for_test(self, test_id):
        defects = []
        if(self.tests_with_defect != None):
            defects = self.tests_with_defect[test_id] if test_id in self.tests_with_defect.keys() else []
        else:
            defects = jira_api_obj.get_defects_linked_to_test(test_id)
        return defects
    
    def parse_json_file(self,file_path):
        """  path should be from root of the repository  """
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),file_path)
        with open(path, 'r') as data_file:
            return json.load(data_file)

    def test_results(self):
        data = self.parse_json_file("cucumber_formated_result.json")
        device_type =''
        for result in data:
            previous_status=''
            for element in result['elements']:
                for tag in element['tags']:
                    if ('CCU' in tag['name'].upper()) or ('ES740' in tag['name'].upper()):
                        device_type = tag['name'].upper()
                        break
                details = self.fetch_and_update_details(element)
                rerun_test=self.update_scenario_details(details,device_type)
                self.update_summary_count(details,rerun_test,previous_status,device_type) 
                previous_status = details['status']
        self.update_total_count()
    
    def fetch_and_update_details(self, element):
        details = {}
        details['scenario'] = element['tags'][0]['name']
        details['name'] =  element['name']
        duration = 0
        found = False
        details['status'] = 'passed'
        details['msg'] = ' '
        for step in element['steps']:
            if 'duration' in step['result']:
                duration += step['result']['duration']
            if found == False and (step['result']['status'] != 'passed'):
                if step['result']['status'] == 'undefined':
                    details['status']="skipped"
                else:
                    details['status']=step['result']['status']
                if 'error_message' in step['result']:
                    details['msg'] = step['result']['status'] + " -> " +step['result']['error_message']
                    found = True
        details['time'] = round(duration/1000000000,3)
        details['defects'] = self.get_defects_for_test(details['scenario'])
        if details['defects']==[]:
            details['defects']=' '
        elif details['status'] =='failed':
            self.tests_failed_with_defects += 1
        details[constants.REP_FAILURE_MSG] = ' '
        return details

    def update_scenario_details(self, details, device_type):
        rerun_test=False
        if device_type in self.scenario:
            if (details['name'] in self.scenario[device_type][len(self.scenario[device_type])-1]['name']):
                rerun_test = True
                self.scenario[device_type][len(self.scenario[device_type])-1][constants.REP_FAILURE_MSG]= self.scenario[device_type][len(self.scenario[device_type])-1]['msg']
                self.scenario[device_type][len(self.scenario[device_type])-1]['msg']= details['msg']
                self.scenario[device_type][len(self.scenario[device_type])-1]['time']= details['time']
                if details['status']=='passed':
                    self.scenario[device_type][len(self.scenario[device_type])-1]['status'] = constants.REP_PASSED_ON_RERUN
                elif details['status']=='failed':
                    self.scenario[device_type][len(self.scenario[device_type])-1]['status'] = 'failed on rerun'
                    self.update_failed_tests_without_defect_details(device_type)
                else:
                    self.scenario[device_type][len(self.scenario[device_type])-1]['status'] = 'skipped on rerun'
                    self.update_failed_tests_without_defect_details(device_type)
            else:
                self.scenario[device_type].append(details) 
        else:
            self.scenario[device_type] = [details]
        return rerun_test
    
    def update_failed_tests_without_defect_details(self,device_type):
        list_element_copied = self.scenario[device_type][len(self.scenario[device_type])-1].copy()
        if device_type in self.failed_tests_details:
            self.failed_tests_details[device_type].append(list_element_copied)
        else:
            self.failed_tests_details[device_type] = [list_element_copied]
        test_key = self.failed_tests_details[device_type][len(self.failed_tests_details[device_type])-1]['scenario']
        self.failed_tests_details[device_type][len(self.failed_tests_details[device_type])-1]['Pass_percentage']= jira_api_obj.fetch_pass_percentage_of_test(test_key)

    def update_summary_count(self,details,rerun_test,previous_status,device_type): 
        if device_type in self.count:
            self.count[device_type][details['status']]+=1
            self.count[device_type]['total']+=1
            self.count[device_type]['tests_failed_with_defects'] = self.tests_failed_with_defects
            self.count[device_type]['time']+=details['time'] 
            if rerun_test:
                self.count[device_type][previous_status]-=1
                self.count[device_type]['total']-=1
                if details['status']=='passed':
                    self.count[device_type][constants.REP_PASSED_ON_RERUN]+=1
        else:
            self.count[device_type] = {'passed':0,'failed':0,'skipped':0,'total':0,constants.REP_PASSED_ON_RERUN:0,'tests_failed_with_defects':0, 'time':0}
            self.count[device_type][details['status']]+=1
            self.count[device_type]['total']+=1
            self.count[device_type]['tests_failed_with_defects'] = self.tests_failed_with_defects
            self.count[device_type]['time']+=details['time']
    
    def update_total_count(self):    
        for k,v in self.count.items():
            for k1,v1 in v.items():
                if k1 in self.total_count:
                    self.total_count[k1] += v1 
                else:
                    self.total_count[k1] = v1
        del self.total_count[constants.REP_PASSED_ON_RERUN]
        del self.total_count['tests_failed_with_defects']
        #Converting total time to hh:mm:ss formate
        for k,v in self.count.items():
            v['time'] =datetime.timedelta(seconds=round(v['time']))
        #Converting total time to hours
        self.total_count['time'] = datetime.timedelta(seconds=round(self.total_count['time']))

    def convert_json_to_html(self):
        report_html_obj = report_html_script.ReportHtmlFuncs()
        logging.info("Converting")
        report_html_obj.create_total_count_table(self.total_count)
        report_html_obj.create_device_info_table()
        report_html_obj.create_summary_table(self.count)
        if self.failed_tests_details !={}:
            report_html_obj.create_failed_tests_table(self.failed_tests_details)
        table = report_html_obj.create_details_table(self.scenario)        
        return table
    
    def write_to_html(self):
        path = os.path.dirname(os.path.abspath(__file__)) + "\\" +"report.html"
        with open(path, 'w') as file:
            file.write(self.convert_json_to_html())     
       

if __name__ == "__main__":
    ReportJsonToHtml().test_results()
    ReportJsonToHtml().write_to_html()
    