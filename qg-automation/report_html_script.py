import json
import os
import src.common.constants as constants

class ReportHtmlFuncs:

    table = "<style>\ntable {border: 2px solid black; empty-cells: show;border-collapse: collapse; text-align: center;}\n tr,th,td{border: 1px solid black;border-collapse: collapse;} "
    table += ".selected{background-color: #AED6F1;} \n .VALID{color: green;} \n .INCONSISTENT{color:red;} \n .GREEN{color: green;} \n .YELLOW{color: yellow;} \n .time{color: grey;}\n .h{background-color: aqua;}\ntd{font-weight: bold;} </style>" 
    line_break = "</br>"
    REP_TABLE_ROW = "  <tr>\n"
    REP_TABLE_ROW_END = "  </tr>\n"
    REP_TABLE_DATA_CLASS = "<td class='{0}'>{1}</td>\n"
    
    def create_details_table(self,scenario, test):
        '''
            Creating table to display details 
        '''
        self.table += self.line_break
        self.table +=f"<h2>Quality Gate Test results {test}</h2>"
        self.table += "<table class='d'>\n"
       # Create the table's column headers
        self.table += self.REP_TABLE_ROW
        header_list = constants.HEADER_LIST
        for table_headers in header_list:
            self.table += "    <th>{0}</th>\n".format(table_headers)
        self.table += self.REP_TABLE_ROW_END
        self.create_table(scenario)
        return self.table

    def create_table(self,details):
        for k,v in details.items():
            scenario_url=constants.SCENARIO_URL + k
            self.table += "    <td class = '{0}'><a href = {1}> {2} </a></td>\n".format(k,scenario_url,k)
            self.create_value_table(v)
            self.table += self.REP_TABLE_ROW_END
        self.table += "</table>"
        self.table += self.line_break

    def create_value_table(self, test):
        for k1,v1 in test.items():
                if k1 == constants.SUMMARY_STR:
                    self.table += self.REP_TABLE_DATA_CLASS.format(test['QG_Status'],v1)
                elif k1 == constants.VALIDATION_LIST_STR:
                    self.create_validation_table(test, v1)
                elif k1 == constants.STATUS_STR:
                    self.table += self.REP_TABLE_DATA_CLASS.format(test['teststatus'], v1)
                elif k1 == constants.QGSTATUS_STR:
                    self.table += self.REP_TABLE_DATA_CLASS.format(test['QG_Status'], v1)

    def create_validation_table(self,test, v1):
        for k2,v2 in v1.items():
            if k2 == constants.URL_VALIDATION_STR:
                if v2 == []:
                    self.table += self.REP_TABLE_DATA_CLASS.format(test['QG_Status'],constants.NO_URL_STRING)
                else:
                    self.table += self.REP_TABLE_DATA_CLASS.format(test['QG_Status'],v2)
            elif k2 == constants.LINKED_DEFECT_STR:
                if v2 == []:
                    self.table += self.REP_TABLE_DATA_CLASS.format(test['QG_Status'],"")
                else:
                    self.table += self.REP_TABLE_DATA_CLASS.format(test['QG_Status'],v2)


    def get_validation_columns(self, details):
        validation_list = {}
        validation_list = set()
        for value in details.values():
            for k,v in value.items():
                if k == 'validation_list':
                    for k1,v1 in v.items():
                        validation_list.add(k1)
        return validation_list
