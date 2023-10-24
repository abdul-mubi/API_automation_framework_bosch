import json
import os
import logging
import API_Test.features.steps.constantfiles.constants_report as constants

class ReportHtmlFuncs:

    table = "<style>\ntable {border: 2px solid black; empty-cells: show;border-collapse: collapse; text-align: center;}\n tr,th,td{border: 1px solid black;border-collapse: collapse;} "
    table += ".selected{background-color: #AED6F1;} \n .passed{color: green;} \n .failed{color:red;} \n .skipped{color: orange;} \n .time{color: grey;}\n .h{background-color: aqua;}\ntd{font-weight: bold;} </style>" 
    line_break = "</br>"

    def parse_json_file(self,file_path):
        """  path should be from root of the repository  """
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),file_path)
        with open(path, 'r') as data_file:
            return json.load(data_file)

    def create_total_count_table(self,total_count):
        self.table += self.line_break
        '''
           Creating table to display count 
        '''
        self.table +="<h2>Total</h2>"
        self.table += constants.REP_TABLE_CLASS
       
       # Create the table's column headers
        self.table += constants.REP_TABLE_ROW
        for table_headers in ['Passed','Failed','Skipped','Total','Time(hh:mm:ss)']:
                 self.table += constants.REP_TABLE_HEADER.format(table_headers.strip())
        self.table += constants.REP_TABLE_ROW_END
         # Create the table's row data
        self.table += "  <tr style=' font-size: 20px;'>\n"
        for k,v in total_count.items():
             self.table += constants.REP_TABLE_DATA_CLASS.format(k,v)
        self.table += constants.REP_TABLE_ROW_END

        self.table += constants.REP_TABLE
        self.table += self.line_break

    def create_device_info_table(self):
        try:
            try:
                self.version = self.parse_json_file('version.json')
            except Exception:
                logging.error("Error in fetching version details")
            try:
                self.version['Version']['Browser'] = self.parse_json_file('UI_Test\\report\\result\\browserInfo.json')
            except Exception:
                logging.warning("API Scripts -> No browser info")
            self.table += self.line_break
            '''
            Creating table to display versions 
            '''
            self.table +="<h2>Device Info</h2>"
            self.table += constants.REP_TABLE_CLASS
            # Create the table's column headers
            self.table += constants.REP_TABLE_ROW
            for table_headers in ['Device/Software','Version','Device ID','Customer','Environment','Tenant']:
                self.table += constants.REP_TABLE_HEADER.format(table_headers.strip())
            self.table += constants.REP_TABLE_ROW_END
            # Create the table's row data
            for k,v in self.version.items():
                self.table += constants.REP_TABLE_ROW
                self.table += "    <td class = 'h'>{0}</td>\n".format(k.strip())
                row_type = ""
                if v['Selected'] == 'True':
                    row_type = "    <td class = '{0}'>\n".format('selected')
                else:
                    row_type = "    <td>\n"
                self.table += row_type
                for k1,v1 in v['Version'].items():
                    self.table += "      {0}->{1}</br>\n".format(k1,v1)
                self.table += constants.REP_TABLE_DATA_END
                self.table += row_type
                self.table += constants.REP_NEWLINE.format(v['Device-ID'])
                self.table += constants.REP_TABLE_DATA_END
                self.table += row_type
                self.table += constants.REP_NEWLINE.format(v['Customer'])
                self.table += constants.REP_TABLE_DATA_END
                self.table += row_type
                self.table += constants.REP_NEWLINE.format(v['Environment'])
                self.table += constants.REP_TABLE_DATA_END
                self.table += row_type
                self.table += constants.REP_NEWLINE.format(v['Tenant'])
                self.table += constants.REP_TABLE_DATA_END
                self.table += constants.REP_TABLE_ROW_END
            self.table += constants.REP_TABLE
            self.table += self.line_break
        except Exception:
            logging.warning("Unable to fetch")
    
    def create_summary_table(self,count):
        '''
           Creating table to display summary 
        '''
        self.table += self.line_break
        self.table +="<h2>Summary</h2>"
        self.table += constants.REP_TABLE_CLASS
         # Create the table's column headers
        self.table += constants.REP_TABLE_ROW
        for table_headers in ['Device type','Passed','Failed','Skipped','Total','Passed on rerun','Tests failed with defects','Time(hh:mm:ss)']:
                 self.table += constants.REP_TABLE_HEADER.format(table_headers.strip())
        self.table += constants.REP_TABLE_ROW_END
        for k,v in count.items():
            self.table += constants.REP_TABLE_ROW
            self.table += "    <td class='h'>{0}</td>\n".format(k.strip())
            for k1,v1 in v.items():
                self.table += constants.REP_TABLE_DATA_CLASS.format(k1,v1)
            self.table += constants.REP_TABLE_ROW_END

        self.table += constants.REP_TABLE
        self.table += self.line_break
    
    def create_failed_tests_table(self,failed_tests_details):
        '''
            Creating table to display failed tests without defects details
        '''
        self.table += self.line_break
        self.table +="<h2>Failed tests without defects details</h2>"
        self.table += constants.REP_TABLE_CLASS
        # Create the table's column headers
        self.table += constants.REP_TABLE_ROW
        for table_headers in ['Scenario','Name','Status','Message','Time[in Secs]','Open defects','Failure msg for previous run','Pass percentage']:
                self.table += constants.REP_TABLE_HEADER.format(table_headers.strip())
        self.table += constants.REP_TABLE_ROW_END
        self.create_table(failed_tests_details)
    
    def create_details_table(self,scenario):
        '''
            Creating table to display details 
        '''
        self.table += self.line_break
        self.table +="<h2>Details</h2>"
        self.table += constants.REP_TABLE_CLASS
       # Create the table's column headers
        self.table += constants.REP_TABLE_ROW
        for table_headers in ['Scenario','Name','Status','Message','Time[in Secs]','Open defects','Failure msg for previous run']:
                self.table += constants.REP_TABLE_HEADER.format(table_headers.strip())
        self.table += constants.REP_TABLE_ROW_END
        self.create_table(scenario)
        return self.table

    def create_table(self,details):
        for k,v in details.items():
            self.table += constants.REP_TABLE_ROW
            self.table += "    <td class = 'h'>{0}</td>\n".format(k.strip())
            self.table += constants.REP_TABLE_ROW_END
            for v1 in v:
                self.table += constants.REP_TABLE_ROW
                self.table += constants.REP_TABLE_ROW
                for k2,v2 in v1.items():
                    if k2=="scenario":
                        scenario_url=f"https://rb-tracker.bosch.com/tracker15/browse/{v2}"
                        self.table += "    <td class = '{0}'><a href = {1}> {2} </a></td>\n".format(v2,scenario_url,v2)
                    elif k2==constants.REP_FAILURE_MSG:
                        self.table +=constants.REP_TABLE_DATA_CLASS.format('failed',v2)
                    elif k2 =="defects" and v2 != []:
                        href_url= self.create_defect_link(v2)
                        self.table += "    <td class = '{0}'> <p>{1} </p></td>\n".format(v2,href_url)
                    else:
                        self.table += constants.REP_TABLE_DATA_CLASS.format(v1['status'],v2)
            self.table += constants.REP_TABLE_ROW_END
        self.table += constants.REP_TABLE
        self.table += self.line_break

    def create_defect_link(self,defects):
        href_url=''
        for defect in defects:
            defect_url=f"https://rb-tracker.bosch.com/tracker15/browse/{defect}"
            url = f"<a href = {defect_url}> {defect} </a>"
            if href_url == '':
                href_url = url
            else:
                 href_url = href_url +" , "+ url
        return href_url
