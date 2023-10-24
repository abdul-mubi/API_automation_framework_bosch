import requests
import logging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import os
import time
from prettytable import PrettyTable
import steps.utils.API_Requests as API_Requests
import steps.pageObjects.API_Generic_Class as API_Generic_Class
from datetime import datetime
from datetime import timedelta
import steps.constantfiles.constants_ota_function_calls_gx as constants

class ApiOTAFunctionCallsGXClass:
    
    def __init__(self, enviroment, log_api_details):
        self.api_request = API_Requests.ApiRequestsClass(enviroment, log_api_details)
        self.api_generic_obj = API_Generic_Class.ApiGenericClass()
        self.ep = "/remote-diagnostics"
        self.vehicle_ep = self.ep + "/vehicles"
        self.diag_func_ep = self.ep + "/diagnosticFunctions"
        self.diag_config_ep = self.ep + "/diagnosticConfigurations"
        

    def get_vehicle_latest_diag_config_status(self, vehicle_id):
        r = self.api_request.get_request(constants.RD_LATEST_VEHICLE_DIAG_CONFIG.format(constants.RD_VEHICLES,vehicle_id))
        if r.status_code == requests.codes.not_found:
            return ""
        elif r.status_code == requests.codes.ok:
            logging.info(f"Diagnostic status is {r.json()['state']}")
            return r.json()['state']
        else:
            assert False, self.api_generic_obj.assert_message(r)
            
    
    def get_vehicle_latest_diag_config_id(self, vehicle_id):
        r = self.api_request.get_request(constants.RD_LATEST_VEHICLE_DIAG_CONFIG.format(constants.RD_VEHICLES,vehicle_id))
        if r.status_code != requests.codes.ok:
            return ""
        else:
            return r.json()['vehicleDiagnosticConfigurationId']

    
    def deactivate_diag_config(self, vehicle_id):
        etag = self.api_request.get_etag(constants.RD_VEHICLE_ID.format(vehicle_id))
        ep_deactivate = constants.RD_VEHICLE_ID_ASSIGNMENTS.format(constants.RD_VEHICLES, vehicle_id)
        r = self.api_request.delete_request(ep = ep_deactivate, custom_header={'If-match': etag})
        assert r.status_code == requests.codes.no_content, self.api_generic_obj.assert_message(r)




    def delete_dtc(self, vehicle_id, vehicle_name):
        dtc_snapshot_id = []
        dtc_count = 0
        ep_dtc_history = constants.RD_VEHICLES +"/" + vehicle_id+ constants.DTC_SNAPSHOT_HISTORY
        r_dtc_history = self.api_request.get_request(ep_dtc_history)
        assert r_dtc_history.status_code == requests.codes.ok, self.api_generic_obj.assert_message(r_dtc_history)

        if ("_embedded" in r_dtc_history.json()):
            for dtc_list in r_dtc_history.json()['_embedded']['dtcsSnapshots']:
                dtc_snapshot_id = dtc_list['dtcsSnapshotId']
                ep_delete_dtc = constants.RD_VEHICLES +"/"+ vehicle_id+constants.DTC_SNAPSHOT+dtc_snapshot_id
                logging.info(f"Deleting {str(dtc_count)} DTC {dtc_snapshot_id} for vehicle {vehicle_name}")
                r_deactivate = self.api_request.delete_request(ep_delete_dtc)

                assert r_deactivate.status_code == requests.codes.no_content, self.api_generic_obj.assert_message(r_deactivate)
        else:
            logging.info(f"Vehicle - {vehicle_name} doesn't have any existing DTC")


    def delete_ecu(self,vehicle_id, vehicle_name):
        ep = constants.RD_VEHICLES + "/" + vehicle_id+constants.ECUS
        r = self.api_request.get_request(ep)
        assert r.status_code == requests.codes.ok, self.api_generic_obj.assert_message(r)
       
        if("_embedded" in r.json()):
            for ecu in r.json()['_embedded']['ecus']:
                ecu_id = ecu['ecuId']
                ecu_name = ecu["ecuInternalId"]
                ep_delete_ecu = constants.RD_VEHICLES +"/"+ vehicle_id+constants.ECUS +"/"+ecu_id
                logging.info(f"Deleting {ecu_name} ECU for vehicle {vehicle_name}")
                r_delete = self.api_request.delete_request(ep_delete_ecu)
                assert r_delete.status_code == requests.codes.no_content, self.api_generic_obj.assert_message(r_delete)
        else:
            logging.info(f"Vehicle - {vehicle_name} doesn't have any existing ECUs")

    
    def activate_diag_config(self, diag_config_name, vehicle_name, vehicle_id, slot_name):
        ''' gets diagnosticConfigurationId for diag_config_name'''
        logging.info(f"Getting Diagnostic configuration Id for a Diagnostic Config Job {diag_config_name}")
        r = self.api_request.get_request(constants.RD_DIAG_CONFIG_SEARCH_NAME.format(diag_config_name))
        assert r.status_code == requests.codes.ok, self.api_generic_obj.assert_message(r)
        assert '_embedded' in r.json(), f"No configuration found with name {diag_config_name}" 
        results = r.json()['_embedded']['diagnosticConfigurations'][0]
        if results['name'] == diag_config_name:
            diag_config_id = results['diagnosticConfigurationId']

        ''' get etag for Activating Diagnostic Configuration on vehicle'''
        logging.info(f"Etag for activating diagnostic Configuration on vehicle {vehicle_name}")
        etag_new = self.api_request.get_etag(constants.RD_VEHICLES+"/"+vehicle_id)

        '''activate diagnostic Configuration on vehicle'''
        ep = constants.RD_VEHICLES+"/"+vehicle_id+"/assignment"
        data = {
            "deviceSlot" : slot_name,
            "diagnosticConfigurationId" : diag_config_id
        }
        logging.info(f"Activating diagnostic Configuration {diag_config_name} on vehicle {vehicle_name}")
        r = self.api_request.post_request(ep=ep, params = data, custom_header={"If-match": etag_new})
        assert r.status_code == requests.codes.created, self.api_generic_obj.assert_message(r)
        return True


    def check_diag_config_state(self, state, vehicle_id, capability):
        self.api_generic_obj.start_timer()        
        diag_status_list = []
        diag_sub_status_list = []
        ep = constants.RD_VEHICLE_ID_VDC.format(vehicle_id)
        ''' gets the Diag COnfig state'''
        while ((self.api_generic_obj.check_timer() == True) and (state not in diag_status_list) and ("DEACTIVATION_FAILED" not in diag_sub_status_list) and ("ACTIVATION_FAILED" not in diag_sub_status_list)):
            r = self.api_request.get_request(ep)
            assert r.status_code == requests.codes.ok, self.api_generic_obj.assert_message(r)
            diag_job_state = r.json()['_embedded']['vehicleDiagnosticConfigurations'][0]['state']
            capability_ep = f'{capability}_1' if "REMOTE_FUNCTION" in capability else f'READ_{capability}'
            diag_job_sub_state = r.json()['_embedded']['vehicleDiagnosticConfigurations'][0]['_embedded']['diagnosticFunctionStates'][capability_ep]['substate']
            '''verifies Diag Config state with the expected State'''
            if diag_job_state not in diag_status_list:
                diag_status_list.append(diag_job_state)
                diag_sub_status_list.append(diag_job_sub_state)
                logging.info("New RD status - %s"%diag_job_state)
            
            if (diag_job_state == state):
                logging.info("Expected RD status - %s appears."%state)
                self.api_generic_obj.stop_timer()
                return diag_status_list, diag_sub_status_list

            time.sleep(5)
            
        if ((self.api_generic_obj.check_timer() == False) or ("DEACTIVATION_FAILED" in diag_sub_status_list) or ("ACTIVATION_FAILED" in diag_sub_status_list) or (state in diag_status_list)):
            logging.info(f"Unexpected RD status appears.{diag_status_list}")
            self.api_generic_obj.stop_timer()
            return diag_status_list, diag_sub_status_list

    
    def verify_dtc(self, table, vehicle_id,dtcs_of_ecu, total_dtc_count):
        b_dtc_state = True
        dtc_id_list = []
        dtc_actual_list = []
        dtc_expected_list = []
        for row in table:
            if dtcs_of_ecu != None:
                dtc_expected_list.append(row['ECU'])
            dtc_expected_list.append(row['Status'])
            dtc_expected_list.append(row['Code'])
        """verifies the DTC of Remote Diagnostic Job and compares it with expected DTC code and Status"""
        ''' gets the list of DTC history'''
        dtc_record_count = self.get_dtc_count(vehicle_id)
        diff_count = int(dtc_record_count - total_dtc_count)
        ep = constants.RD_VEHICLE_ID_DTCSS_HISTORY.format(vehicle_id)
        r = self.api_request.get_request(ep)
        assert r.status_code == requests.codes.ok, self.api_generic_obj.assert_message(r)
        assert "_embedded" in r.json(), "DTCs doesn't appear for RD activated vehicle"
        
        res = r.json()['_embedded']['dtcsSnapshots']
        for count in range(0, diff_count):
            dtc_id_list.append(res[count]['dtcsSnapshotId'])
        logging.info(f"Following DTCs are generated - ,{dtc_id_list}")
        ''' gets the DTC codes for all the DTC history and compares '''
        ''' create method that will return dtcId and dtcStatus for each 'dtc_id_list'''
        for dtc_id in dtc_id_list:
            logging.info(f" Verifying DTC - {dtc_id} ")
            ep = constants.RD_VEHICLES_ID_DTCSS_ID.format(vehicle_id,dtc_id)
            r = self.api_request.get_request(ep)
            assert r.status_code == requests.codes.ok, self.api_generic_obj.assert_message(r)
            dtc_res = r.json()['dtcs']
            for dtc_code in dtc_res:
                if dtcs_of_ecu != None:
                    dtc_actual_list.append(dtc_code['ecu']['ecuId'])
                dtc_actual_list.append(dtc_code['dtcStatus'])
                dtc_actual_list.append(dtc_code['dtcId'])

            logging.info(f"Expected Status and Code - {dtc_expected_list}")
            logging.info(f"Actual Status and Code - {dtc_actual_list}")

            if (dtc_actual_list!=dtc_expected_list):
                logging.info(f"Actual DTC code and status {str(set(dtc_actual_list)-set(dtc_expected_list))} is not same as expected {str(set(dtc_expected_list)-set(dtc_actual_list))} for DTC - {dtc_id}")
                b_dtc_state = False
                break
            logging.info(f"DTC is correct for DTC Id - {dtc_id}")
            dtc_actual_list.clear()
        return b_dtc_state, dtc_actual_list, dtc_expected_list

    def verify_ecu_details(self, identifiers, vehicle_id):
        ecus={}
        expected_ecus={}
        equal = True
        """verifies the ECU of Remote Diagnostic Job and compares it with expected DTC code and Status"""
        ep = constants.RD_VEHICLES + '/' + vehicle_id+constants.ECUS
        r = self.api_request.get_request(ep)
        assert r.status_code == requests.codes.ok, self.api_generic_obj.assert_message(r)
        assert "_embedded" in r.json(), "DTCs doesn't appear for RD activated vehicle"

        for ecu in r.json()['_embedded']['ecus']:
            ecu_details={}
            ecu_details["id"]=ecu['ecuInternalId']
            ecu_details["name"]=ecu['name']
            ecu_details["sw"]=ecu['swVersion']
            ecu_details["hw"]=ecu['hwVersion']
            ecu_details["serial"]=ecu['serialNumber']
            ecu_details["vendor"]=ecu['vendorIdentifier']
            ecus[ecu["ecuInternalId"]+"_ECU"]=ecu_details

        ecus = dict( sorted(ecus.items(), key=lambda x: x[0].lower()) )

        if(len(set(identifiers) - set(sorted(ecus.keys()))) != 0):
            equal = False
            logging.info(ecus.keys())
            logging.info("Actual ECUs are not same as expected ecus ")
            logging.info(identifiers)
            return equal


        logging.info(" ECUs details fetched form API -")
        x = PrettyTable()
        for k,v in ecus.items():
            x.field_names = v.keys()
            x.add_row(v.values())
        logging.info(x)
        for indentifier in identifiers:
            expected_ecus[indentifier] = self.api_generic_obj.parse_json_file("common\\TestData\\OTAFunctionCallsGX\\ECU_Info.json")['ECUs'][indentifier]
        expected_ecus  = dict( sorted(expected_ecus.items(), key=lambda x: x[0].lower()) )
        logging.info("Expected ECUs details")
        x = PrettyTable()
        for k,v in expected_ecus.items():
            x.field_names = v.keys()
            x.add_row(v.values())
        logging.info(x)
        
        '''Compare two dict'''
        not_found = []
        pretty_table = PrettyTable()
        pretty_table.field_names = ["ECU_Name","Field_Name","Expected_Value","Actual_Value"]
        for ecu_identifier in expected_ecus:
            equal = self.compare_expected_actual_ecus(ecu_identifier, expected_ecus, ecus, pretty_table, not_found, equal)

        if equal == False:
            logging.info("Unmatched value found ")
            if len(not_found) > 0:
                logging.info(f"Following ECUs are not found {not_found}")
            logging.info(pretty_table)

        return equal

    def compare_expected_actual_ecus(self, ecu_identifier, expected_ecus, ecus, pretty_table, not_found, equal):
        if ecu_identifier in ecus:
                first, second = expected_ecus[ecu_identifier], ecus[ecu_identifier]
                for key_expected_ecu in first:
                    if key_expected_ecu in second:
                        expected_ecu, actual_ecu = first[key_expected_ecu], second[key_expected_ecu]
                        if expected_ecu.strip() != actual_ecu.strip():
                            equal = False
                            pretty_table.add_row([ecu_identifier,key_expected_ecu,expected_ecu, actual_ecu])
                            
        else:
                equal = False
                not_found.add(ecu_identifier)

        return equal


    def create_diag_func(self, data, files):
        ep = constants.RD_DIAG_FUNC +"/"
        ''' creates a new Diagnostic Function '''
        r = self.api_request.post_request_file(ep=ep, params=data, dbc_file=files)
        assert r.status_code == requests.codes.created, self.api_generic_obj.assert_message(r)
        return True


    def edit_diag_func(self, diag_func_id, modifying_values):

        bstatus = False
        for ep1 in modifying_values.keys():
            logging.info(f"Modifying Diagnostic Function Attribute - {ep1}")
            
            '''getting eTag for modifying Diagnostic Function'''
            ep = constants.RD_DIAG_FUNC_ID_EP.format(diag_func_id, ep1)
            '''edit existing Diagnostic Function'''
            if (ep1 == "file"):
                etag = self.api_request.get_etag(constants.RD_DIAG_FUNC + "/{}".format(diag_func_id))
                path = os.path.dirname(os.path.abspath(__file__))
                file_name = modifying_values[ep1]
                file_path = path + "\\.." + constants.OTA_FUNCTION_CALL_GX + file_name
                logging.info(file_path)
                file = {'file': open(file_path, 'rb')}
                r = self.api_request.put_request_file(ep=ep, dbc_file = file, custom_header = {'if-match': etag})
            else:
                etag = self.api_request.get_etag(constants.RD_DIAG_FUNC_ID.format(diag_func_id))
                param = {ep1: modifying_values[ep1]}
                r = self.api_request.put_request(ep=ep, params=param, custom_header = {'if-match': etag})
            assert r.status_code == requests.codes.no_content, self.api_generic_obj.assert_message(r)
            bstatus = True
        
        return bstatus

    
    def verify_diag_func_values(self, diag_func_name, edited_values):
        b_status = False
        actual_value = ""
        ep = constants.RD_DIAG_FUNC_NAME.format(diag_func_name)
        r = self.api_request.get_request(ep)

        for edited_keys in edited_values.keys():
            actual_value = r.json()['_embedded']['diagnosticFunctions'][0][edited_keys]
            assert edited_values[edited_keys] == actual_value, "Unexpected. Actual changed value - "+actual_value+" is not same as expected - "+edited_values[edited_keys]
            b_status = True
        return b_status


    def create_diag_configuration(self, data):
        ep = constants.RD_DIAG_CONFIG
        r = self.api_request.post_request(ep = ep, 
                                params=data, custom_header={'if-match': "1"})
    
        assert r.status_code == requests.codes.created, self.api_generic_obj.assert_message(r)
        return True


    def edit_diag_configuration(self, diag_config_id, modifying_values):
        bstatus = False
        for ep1 in modifying_values.keys():
            logging.info(f"Modifying Diagnostic Configuration on Action - {ep1}")
            
            '''getting eTag for modifying Diagnostic Function'''
            etag = self.api_request.get_etag(constants.RD_DIAG_CONFIG_ID.format(diag_config_id))

            ep = constants.RD_DIAG_CONFIG_ID_EP.format(diag_config_id, ep1)
            ''' edit existing Diagnostic Function'''
            param = {ep1: modifying_values[ep1]}
            r = self.api_request.put_request(ep=ep, params=param, custom_header = {'if-match': etag})
            assert r.status_code == requests.codes.no_content, self.api_generic_obj.assert_message(r)
            bstatus = True
        
        return bstatus

    
    def verify_diag_config_values(self, diag_config_name, edited_values):
        b_status = False
        actual_value = ""
        ep = constants.RD_DIAG_CONFIG_SEARCH_NAME.format(diag_config_name)
        r = self.api_request.get_request(ep)

        for edited_keys in edited_values.keys():
            actual_value = r.json()['_embedded']['diagnosticConfigurations'][0][edited_keys]
            assert edited_values[edited_keys] == actual_value, "Unexpected. Actual changed value - "+actual_value+" is not same as expected - "+edited_values[edited_keys]
            b_status = True
        return b_status


    def get_dtc_count(self, vehicle_id):
        ep = constants.RD_VEHICLE_ID_DTCSS_HISTORY.format(vehicle_id)
        r = self.api_request.get_request(ep)
        dtc_count = r.json()['page']['totalElements']
        return dtc_count

    def get_end_point_for_capability(self,vehicle_id,capability):
        r = self.api_request.get_request(constants.RD_VEHICLE_ID.format(vehicle_id))
        assert r.status_code == requests.codes.ok, self.api_generic_obj.assert_message(r)
        if capability == "ECU" or capability == "DTC":
            uri = r.json()["_links"]["trigger_READ_"+capability]["href"]    
        elif "REMOTE_FUNCTION" in capability:
            uri = r.json()["_links"]["trigger_"+capability+"_1"]["href"]
        else:
            uri = r.json()["_links"]["trigger_"+capability]["href"]
        ep = uri.split("applications")[1]
        return ep

    def triggercapability(self,ep,data):
        r = self.api_request.post_request(ep = ep, params = data)
        assert r.status_code == requests.codes.created, self.api_generic_obj.assert_message(r)
        return r 

    def get_trigger_location(self,vehicle_id,capability,data):
        r = self.triggercapability(self.get_end_point_for_capability(vehicle_id,capability),data)
        assert r.status_code == requests.codes.created, self.api_generic_obj.assert_message(r)
        return r.headers['Location']

    def get_trigger_status(self,ep):
        r = self.api_request.get_request(ep)
        assert r.status_code == requests.codes.ok, self.api_generic_obj.assert_message(r)
        return r.json()['state']

    def get_diag_func_details_by_name(self, diag_func_name):
        r = self.api_request.get_request(constants.RD_DIAG_FUNC_NAME.format(diag_func_name))
        assert r.status_code == requests.codes.ok, self.api_generic_obj.assert_message(r)
        return r.json()

    def get_diag_config_details_by_name(self, diag_config_name):
        r = self.api_request.get_request(constants.RD_DIAG_CONFIG_SEARCH_NAME.format(diag_config_name))
        assert r.status_code == requests.codes.ok, self.api_generic_obj.assert_message(r)
        return r.json()

    def release_diag_func(self, diag_func_id):
        etag = self.api_request.get_etag(constants.RD_DIAG_FUNC_ID.format(diag_func_id))
        r = self.api_request.post_request(ep=constants.RD_DIAG_FUNC_ID_RELEASE.format(diag_func_id),params={}, custom_header={'if-match': etag})
        assert r.status_code == requests.codes.created, self.api_generic_obj.assert_message(r)

    def release_diag_confih(self, diag_config_id):
        etag = self.api_request.get_etag(constants.RD_DIAG_CONFIG_ID.format(diag_config_id))
        r = self.api_request.post_request(ep=constants.RD_DIAG_CONFIG_ID_RELEASE.format(diag_config_id), params={}, custom_header={'if-match': etag})
        assert r.status_code == requests.codes.created, self.api_generic_obj.assert_message(r)

    def get_diag_func_details_by_id(self, diag_func_id):
        r = self.api_request.get_request(constants.RD_DIAG_FUNC_ID.format(diag_func_id))
        assert r.status_code == requests.codes.ok, self.api_generic_obj.assert_message(r)
        return r.json()['state']

    def get_diag_config_details_by_id(self, diag_config_id):
        r = self.api_request.get_request(constants.RD_DIAG_CONFIG_ID.format(diag_config_id))
        assert r.status_code == requests.codes.ok, self.api_generic_obj.assert_message(r)
        return r.json()['state']

    def check_assigned_diagostic_config_state(self, vehicle_id, state):
        self.api_generic_obj.start_timer()        
        ep = constants.RD_VEHICLE_ID.format(vehicle_id)
        ''' gets the Diag Config state'''
        diagnostic_config_state = None
        while (self.api_generic_obj.check_timer() == True):
            r = self.api_request.get_request(ep)
            assert r.status_code == requests.codes.ok, self.api_generic_obj.assert_message(r)
            if 'vehicleDiagnosticConfigurationState' in r.json():
                diagnostic_config_state = r.json()['vehicleDiagnosticConfigurationState']
            if (diagnostic_config_state == state):
                logging.info("Expected RD Configuration State - %s appears."%state)
                self.api_generic_obj.stop_timer()
                break
            time.sleep(10)
        assert diagnostic_config_state == state, f"Unexpected Diagnostic configuration state appears, expected :{state} and actual:  {diagnostic_config_state}"

    def get_slot_with_pending_rd_assignment(self, vehicle_id):
        slot_name = None     
        ep = constants.RD_VEHICLE_ID.format(vehicle_id)
        ''' gets the Diag Config state'''
        r = self.api_request.get_request(ep)
        if("vehicleDiagnosticConfigurationState" in r.json()):
            if('_embedded' in r.json()):
                if('assignment' in r.json()['_embedded']):
                    # Inner if condition need to be removed once RD Slot Assigned state defect by @BRT4KOR is fixed
                    slot_name = r.json()['_embedded']['assignment']['deviceSlot']
            else:
                assert False, "Unexpected, Vehicle Diagnostic Details are missing"
        return slot_name


    def verify_dtcs_after_deactivation(self, vehicle_id, deactivation_time):
        ep_dtc_history = constants.RD_VEHICLES +"/" + vehicle_id+ constants.DTC_SNAPSHOT_HISTORY
        r_dtc_history = self.api_request.get_request(ep_dtc_history)
        assert r_dtc_history.status_code == requests.codes.ok, self.api_generic_obj.assert_message(r_dtc_history)
        deactivation_time = datetime.strptime(deactivation_time.strftime(constants.RD_DATE_AND_TIME), constants.RD_DATE_AND_TIME)
        if ("_embedded" in r_dtc_history.json()):
            for dtc in r_dtc_history.json()['_embedded']['dtcsSnapshots']:
                dtc_time = datetime.strptime(dtc['timestamp'][:dtc['timestamp'].rindex(":")], constants.RD_DATE_AND_TIME)
                assert (dtc_time - deactivation_time).min < timedelta(minutes=1), f"DTCs are generated after deactivation, deactivation_time : {deactivation_time}, dtc_time : {dtc_time}"
        else:
            assert False, "Vehicle does not have any existing DTC"

    def verify_diag_config_state(self, state, sub_status, capability, vehicle_id):
        diag_status = self.check_diag_config_state(state, vehicle_id, capability)
        assert diag_status[0][len(diag_status[0])-1] == state, "Unexpected RD status appears. Actual - %s and Expected - %s"%(diag_status[0][len(diag_status[0])-1],state)
        
        rd_activation_status = True
        if state == "ACTIVE":
            sub_status = "ACTIVATION_CONFIRMED"
        elif state == "ACTIVATION_PENDING" and sub_status == " ":
            sub_status = "IN_ACTIVATION"
        elif state == "INACTIVE":
            sub_status = "DEACTIVATION_CONFIRMED"
            rd_activation_status = False
        elif state == "DEACTIVATION_PENDING":
            sub_status = "IN_DEACTIVATION"
            rd_activation_status = False
        elif state == "ASSIGNED":
            sub_status = "IN_DEACTIVATION"

        assert diag_status[1][len(diag_status[1])-1] == sub_status, "Unexepected Diagnostic sub-status appears. Actual - %s and Expecetd - %s"%(diag_status[1][len(diag_status[1])-1],sub_status)
        logging.info("Expected Remote Diagnostic Sub-status - %s appears. "%sub_status)
        return rd_activation_status

    def deactivate_rd_config(self, vehicle_id, vehicle_name, assignment_state):
        deactivation_time = " "
        curr_status = self.get_vehicle_latest_diag_config_status(vehicle_id)
        if curr_status == "ACTIVE":
            self.deactivate_diag_config(vehicle_id)
            deactivation_time = datetime.utcnow()
        elif curr_status == "INACTIVE":
            if(assignment_state == "INACTIVE"):
                self.deactivate_diag_config(vehicle_id)
                logging.info("Successfully deactivated Inactive Assignment from Device")
            else:
                logging.info(f" vehicle {vehicle_name} Diagnostic Configuration is already in {curr_status} ")
        else:
            logging.info(f" vehicle {vehicle_name} doesn't have history of Diagnostic Configuration ")

        return deactivation_time


    def check_capability_status(self, trigger, capability, dtc_time, timeout_time, status):
        performed = False
        capability_triggered = False
        if capability in trigger:
            trigger_ep = trigger.split("applications")[1]
            capability_triggered = True
            while (time.time() < timeout_time):
                trigger_state = self.get_trigger_status(trigger_ep)
                if trigger_state == "EXECUTED" or trigger_state == "FAILED":
                    logging.info(f"Trigger of adhoc Read All {capability}s is performed and the state is {trigger_state}")
                    performed = True
                    break
                time.sleep(5)
            if performed != True:
                assert False, f'Trigger did not reach a conclusive state after {dtc_time}. Trigger state was - {trigger_state}'
            if status == "passes":
                assert trigger_state == "EXECUTED", f'adhoc Read All {capability} trigger is not executed. Current state is - {trigger_state}'
            elif status == "fails":
                assert trigger_state == "FAILED", f'adhoc Read All {capability} trigger is not failed. Current state is - {trigger_state}'
            else:
                assert False, f'Unknown trigger state provided - {status}'
        if capability_triggered is not True:
            assert False,f"Capability - {capability} is not activated on this vehicle" 