import requests
import logging
import behave
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time
import steps.utils.API_Requests as API_Requests
import steps.pageObjects.API_Generic_Class as API_Generic_Class
import csv
import dateutil.parser as parser
import operator
import json
import io
import pandas
import datetime
from copy import deepcopy
import re
import steps.constantfiles.constants_ota_vehicle_data as constants
import itertools

class ApiOTAVehicleDataClass:

    env = None
    log_details = None

    def __init__ (self, environment, log_api_details):
        self.api_requests = API_Requests.ApiRequestsClass(environment, log_api_details)
        self.api_gen_obj = API_Generic_Class.ApiGenericClass()
        self.env = environment
        self.log_details = log_api_details
    
    def get_signal_collection_id(self, signal_collection):
        sig_collection = self.api_requests.get_request(constants.RM_SIG_COL_SEARCH_NAME.format(signal_collection))
        assert sig_collection.status_code == requests.codes.ok, self.api_gen_obj.assert_message(sig_collection)
        logging.info(sig_collection)
        if '_embedded' in sig_collection.json():
            return sig_collection.json()['_embedded']['signalCollections'][0]['signalCollectionId']
        else:
             logging.info(f'Signal Collection with  {signal_collection} name is not present')
             return None

    def get_measurement_configuration_id(self, measruement_configuration_name):
        r = self.api_requests.get_request(constants.RM_MEASURE_CONFIG_SEARCH_NAME.format(measruement_configuration_name))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        if '_embedded' not in r.json():
            logging.info(f'Measurement Configuration with {measruement_configuration_name} is not found')
            return None
        return r.json()['_embedded']['measurementConfigurations'][0]['measurementConfigurationId']
    
    def get_measurement_timeout(self, measurement_configuration_id):
        r = self.api_requests.get_request(constants.RM_MEASURE_CONFIG_ID.format(measurement_configuration_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r.json()['timeout']
    
    def edit_measurement_timeout(self, measurement_configuration_id, timeout):
        state_changed= self.set_measurement_configuration_state(measurement_configuration_id, "draft")
        
        data ={'timeout': timeout}
        etag = self.api_requests.get_etag(constants.RM_MEASURE_CONFIG_ID.format(measurement_configuration_id))
        r = self.api_requests.put_request(constants.RM_MEASURE_CONFIG_ID_TIMEOUT.format(measurement_configuration_id), params=data, custom_header={'if-match': etag})
        assert r.status_code == requests.codes.no_content, self.api_gen_obj.assert_message(r)

        if state_changed:
            self.set_measurement_configuration_state(measurement_configuration_id, "releases")
        return r

    def get_measurement_config(self, measruement_configuration_id):
        r = self.api_requests.get_request(constants.RM_MEASURE_CONFIG_ID.format(measruement_configuration_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r
    
    def get_measurement_configuration_details(self,measruement_configuration_id):
        r = self.get_measurement_config(measruement_configuration_id)
        return r.json()['state']

    def get_vehicle_teststep_id(self, vehicle_id):
        r = self.api_requests.get_request(constants.RM_TEST_STEPS_VEHICLE_ID.format(vehicle_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        element_count = r.json()['page']['totalElements'] 
        r = self.api_requests.get_request(constants.RM_TEST_STEPS_ELEMENTCOUNT_VEHICLE_ID.format(element_count+5,vehicle_id))   
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r

    def get_measure_config_teststep_id(self, measurement_configuration_id):
        r = self.api_requests.get_request(constants.RM_TEST_STEPS_MEASURE_CONFIG_ID.format(measurement_configuration_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r

    def delete_vehicle_rm_test_step(self,vehicle_id, rm_activation_date, past_rm_test_step_time):
        r = self.get_vehicle_teststep_id(vehicle_id)
        if r.status_code != requests.codes.ok:
            return r
        total_count =  r.json()['page']['totalElements']

        for te_no in range(total_count):
            test_step_id = r.json()['_embedded']['testSteps'][te_no]['testStepId']
            total_rm_seconds = self.rm_test_step_time_diff(vehicle_id, rm_activation_date,r.json()['_embedded']['testSteps'][te_no]['creationDate'])   
            past_rm_seconds = past_rm_test_step_time *3600*-1
            if total_rm_seconds>=0 or total_rm_seconds <= past_rm_seconds:
                logging.info(f"Deleting RM test step id: {test_step_id}")
                ret = self.api_requests.delete_request(constants.RM_TEST_STEPS_ID.format(test_step_id))
                if ret.status_code != requests.codes.no_content:
                    assert False, f"Failed to delete the test step with ID: {test_step_id}"
                logging.info(f"{test_step_id} is deleted")

    def validate_measurement_duration(self, test_result, start_time, end_time, test_duration):
        tr_cnt = 0
        while tr_cnt < len(test_result):
            # Commented validating start/end time code as new response doesn't have respective data.
            s_time_fm = parser.parse(test_result[tr_cnt][0][0].split(',')[7].split('=')[1]).isoformat()
            e_time_fm = parser.parse(test_result[tr_cnt][0][0].split(',')[8].split('=')[1]).isoformat()
            if start_time.isoformat() > s_time_fm:
                logging.info(f"Expected Start Time  {start_time.isoformat()}  Received start Time  {s_time_fm}")
                return False
            if end_time.isoformat() < e_time_fm:
                logging.info(f"Expected end Time  {end_time.isoformat()}  Received end Time  {e_time_fm}")
                return False
            t_dur = int(test_result[tr_cnt][0][0].split(',')[9].split('=')[1])
            logging.info(f"Expected duration  {str(round(test_duration / 1000))}  Received duration {str(round(t_dur / 1000))}")            
            if abs(round(test_duration / 1000) - round(t_dur / 1000)) > 50:
                logging.info(f"Expected duration  {str(round(test_duration / 1000))}  Received duration {str(round(t_dur / 1000))}")
                return False
            tr_cnt += 1
        return True
    

    def time_stamp_check(self, test_result, variable, timestamp_diff, threshold):
        tr_cnt = 0
        while tr_cnt < len(test_result):
            # find the variable if it is available
            if variable in test_result[tr_cnt][1]:   
                index = test_result[tr_cnt][1].index(variable)
                first = 3
                first, second =  self.__get_values_from_test_result(test_result, tr_cnt, first, index)
                index = 2                        
                threshold_in_ms = ( float(timestamp_diff) * float(threshold) ) / 100                        
                if float(test_result[tr_cnt][second][index]) < (float(test_result[tr_cnt][first][index]) + float(timestamp_diff) - threshold_in_ms) or float(test_result[tr_cnt][second][index]) > (float(test_result[tr_cnt][first][index]) + float(timestamp_diff) + threshold_in_ms):
                    logging.info("Time stamp check failed")
                    return False
            else:
                logging.info(f"Variable {variable} is not available")
                return False
            tr_cnt += 1
        return True        


    def value_check(self, test_result, variable, increment):
        tr_cnt = 0
        while tr_cnt < len(test_result):
            # find the variable if it is available
            if variable in test_result[tr_cnt][1]:   
                index = test_result[tr_cnt][1].index(variable)
                first = 3
                first, second =  self.__get_values_from_test_result(test_result, tr_cnt, first, index)              
                if ((float(test_result[tr_cnt][second][index]) != (float(test_result[tr_cnt][first][index]) + float(increment)))
                and (float(test_result[tr_cnt][second][index]) != (float(test_result[tr_cnt][first][index]) - float(increment)))):
                    logging.info("Value check failed")
                    return False
            else:
                logging.info(f"Variable {variable} is not available ")
                return False
            tr_cnt += 1
        return True
    

    def __get_values_from_test_result(self, test_result, tr_cnt, first, index):
        while first < len(test_result[tr_cnt]):
            if(test_result[tr_cnt][first][index] != ''):
                break
            else:
                first += 1
        second = first + 1
        while second < len(test_result[tr_cnt]):
            if(test_result[tr_cnt][second][index] != ''):
                break
            else:
                second += 1
        return first, second

    def trigger_measurement_activation(self, vehicle_id, device_id, measurement_id):
        data = { "measurementConfigurationId": measurement_id, "deviceId": device_id }
        etag = self.api_requests.get_etag(constants.RM_VEHICLES_ID.format(vehicle_id))
        r = self.api_requests.post_request(constants.RM_VEHICLES_ID_MEASURE_JOB.format(vehicle_id), params=data, custom_header={'if-match': etag})
        assert r.status_code == requests.codes.created, self.api_gen_obj.assert_message(r)
        return True

    def check_measurement_status(self, vehicle_id, status, assignment_job_id, timer="10"):
        self.api_gen_obj = API_Generic_Class.ApiGenericClass()
        measurement_status_list = []
        measurement_substatus_list = []
        if(timer is not None):
            self.api_gen_obj.update_timeout_time(int(timer)*60)
        self.api_gen_obj.start_timer()
        while ((self.api_gen_obj.check_timer() == True) and (status not in measurement_status_list) and ("DEACTIVATION_FAILED" not in measurement_substatus_list) and ("ACTIVATION_FAILED" not in measurement_substatus_list)):

            assignment_details = self.get_assignment_job_details(vehicle_id, assignment_job_id)
            try:
                if assignment_details['currentStatus']  not in measurement_status_list:
                    measurement_status_list.append(assignment_details['currentStatus'])
                    logging.info(f"New Measurement Status - {assignment_details['currentStatus']}")
                if assignment_details['currentSubstatus'] not in measurement_substatus_list:
                    measurement_substatus_list.append(assignment_details['currentSubstatus'])
                    logging.info(f"New Measurement Substatus - {assignment_details['currentSubstatus']}")
                if assignment_details['currentStatus'] == status:
                    logging.info("Expected Measurement Status - %s appears."%assignment_details['currentStatus'])
                    self.api_gen_obj.stop_timer()
                    return measurement_status_list, measurement_substatus_list
            except KeyError as e:
                assert False, ("KeyError occured - reason %s is not available in API Response" %e )

        if ((self.api_gen_obj.check_timer() == False) or (status in measurement_status_list) or ("DEACTIVATION_FAILED" in measurement_substatus_list) or ("ACTIVATION_FAILED" in measurement_substatus_list)):
            logging.info(f"Unexpected Measurement status-{measurement_status_list} or substatus appears-{measurement_substatus_list}")
            self.api_gen_obj.stop_timer()
            return measurement_status_list, measurement_substatus_list
    
    def trigger_measurement_deactivation(self, vehicle_id, measurement_id):
        etag = self.api_requests.get_etag(constants.RM_VEHICLES_ID.format(vehicle_id))
        r = self.api_requests.put_request(constants.RM_VEHICLES_ID_MEASURE_JOB_DEACTIVATE.format(
            vehicle_id, measurement_id), params={}, custom_header={'if-match': etag})
        assert r.status_code == requests.codes.no_content, self.api_gen_obj.assert_message(r)
        return True
        
    
    def set_measurement_configuration_state(self, measurement_configuration_id,state):
        if state == 'releases':
            state = ['releases', 'RELEASED']
        elif state == 'draft':
            state = ['draft', 'DRAFT']
        logging.info(f'Attempting to set measurement configuration to state {state[1]}')
        meas_conf_state = self.get_measurement_configuration_details(measurement_configuration_id)
        state_changed = False
        if meas_conf_state == state[1]:
            logging.info(f'Appropriate {state[1]} state of measurement configuration')
        elif meas_conf_state == "RELEASED" or meas_conf_state == "DRAFT":
            logging.info(f'Measurement configuration in undesirable state {meas_conf_state}')
            etag = self.api_requests.get_etag(constants.RM_MEASURE_CONFIG_ID.format(measurement_configuration_id))
            r = self.api_requests.post_request(constants.RM_MEASURE_CONFIG_ID_PARAM.format(measurement_configuration_id, state[0]), params={}, custom_header={'if-match': etag})
            assert r.status_code == requests.codes.created, self.api_gen_obj.assert_message(r)
            state_changed = True
            logging.info(f'Modified measurement configuration to {state[1]} state')
        else:
            assert False, f"Measurement configuration in unexpected state - {meas_conf_state}"
        return state_changed

    def get_invalid_signals_status(self,measruement_configuration_id):
        r = self.get_measurement_config(measruement_configuration_id)
        return r.json()['hasInvalidSignals']

    def release_signal_collection(self,signal_collection_id):
        etag = self.api_requests.get_etag(constants.RM_SIG_COL_ID.format(signal_collection_id))
        r = self.api_requests.post_request(constants.RM_SIG_COL_ID_RELEASE.format(signal_collection_id), params={},custom_header={'if-match': etag})
        logging.info(r)
        if r.status_code != requests.codes.created:
            assert False, f'Could not release the signal'

    def draft_measurement_configuration(self, measurement_id):
        etag = self.api_requests.get_etag(constants.RM_MEASURE_CONFIG_ID.format(measurement_id))
        r = self.api_requests.post_request(constants.RM_MEASURE_CONFIG_ID_DRAFT.format(measurement_id), params={}, custom_header={'if-match': etag})
        assert r.status_code == requests.codes.created, self.api_gen_obj.assert_message(r)
        return r

    def get_test_results(self, vehicle_id, rm_activation_date):
        csv_file_name = []
        r = self.get_vehicle_teststep_id(vehicle_id)
        if r.status_code != requests.codes.ok:
            return csv_file_name
        total_element = r.json()['page']['totalElements']
        logging.info(f"Elements of Test results - {total_element} ")
        element =0
        while (element < total_element):     
            test_step_id = r.json()['_embedded']['testSteps'][element]['testStepId']
            total_rm_seconds = self.rm_test_step_time_diff(vehicle_id, rm_activation_date,r.json()['_embedded']['testSteps'][element]['creationDate'])      
            if total_rm_seconds>0:
            #preparing download of measured data
                download_prepare = self.api_requests.put_request(constants.RM_TEST_STEPS_ID_TARGET_FORMAT_CSV.format(test_step_id), params={})
                assert download_prepare.status_code == requests.codes.accepted, self.api_gen_obj.assert_message(download_prepare)
                time.sleep(60) # wait time to check if preparing download is completed
                test_result = self.api_requests.get_request(constants.RM_TEST_STEPS_ID_MEASURE_JOB_RESULTS_CSV.format(test_step_id))
                if test_result.status_code == requests.codes.ok:    
                    cr = csv.reader(test_result.content.decode('utf-8').splitlines(), delimiter = ";" )
                    csv_file_name.append(list(cr))
            element+= 1
        return csv_file_name

    def get_measurement_results(self, vehicle_id, rm_activation_date, download_prepared = False, preview_prepared = False, preview_data = None):
        test_step_results = json.loads(json.dumps({}))
        r = self.get_vehicle_teststep_id(vehicle_id)
        if r.status_code != requests.codes.ok:
            return test_step_results
        element_count = r.json()['page']['totalElements'] 
        logging.info(f"Elements of Test results - {element_count}")
        element =  0
        while (element<element_count ):
            test_step_id = r.json()['_embedded']['testSteps'][element]['testStepId']
            total_rm_seconds = self.rm_test_step_time_diff(vehicle_id, rm_activation_date,r.json()['_embedded']['testSteps'][element]['creationDate'])           
            if total_rm_seconds>0:
                if (not download_prepared):
                    self.prepare_csv(test_step_id)
                test_result_csv = self.download_csv_as_string(test_step_id)
                assert test_result_csv != '', 'Blank CSV file with no content!'
                duration_from_csv = self.__get_duration_from_csv(test_result_csv)
                test_result_csv= self.update_signal_names_in_csv(test_result_csv)
                test_result_json = self.__convert_csv_to_json(test_result_csv)
                start_time = self.__get_start_time_from_csv(test_result_csv)
                end_time = self.__get_end_time_from_csv(test_result_csv)
                rm_config_version = r.json()['_embedded']['testSteps'][element]["measurementConfiguration"]["version"]
                preview_data_json = None
                if preview_data is not None:
                    if (not preview_prepared):
                        self.prepare_preview(test_step_id)
                    preview_data_json = self._get_preview_data(test_step_id)
                # Test step results are stored in the order - newest to the oldest
                test_step_results.update({test_step_id : {"results" : test_result_json, "preview_data": preview_data_json, "duration" : duration_from_csv, "start-time":start_time, "end-time":end_time, "rm_config_version":rm_config_version}})
            else:
                break
            element+= 1
        return test_step_results
    
    def rm_test_step_time_diff(self, vehicle_id, rm_activation_date,test_step_date):  
        test_step_date = test_step_date.split(".")[0]
        test_step_date = test_step_date.replace("Z","")
        test_step_date_format = datetime.datetime.strptime(test_step_date,"%Y-%m-%dT%H:%M:%S")
        diff = test_step_date_format - rm_activation_date 
        total_rm_seconds = int(diff.total_seconds())
        return total_rm_seconds


    def prepare_csv(self, test_step_id):
        download_prepare = self.api_requests.put_request(constants.RM_TEST_STEPS_ID_TARGET_FORMAT_CSV.format(test_step_id), params={})
        assert download_prepare.status_code == requests.codes.accepted, self.api_gen_obj.assert_message(download_prepare)
        time.sleep(5)

    def download_csv_as_string(self, test_step_id):
        retry_count = 5
        while(retry_count >= 0):
            test_result = self.api_requests.get_request(constants.RM_TEST_STEPS_ID_MEASURE_JOB_RESULTS_CSV.format(test_step_id))
            if test_result.status_code == requests.codes.not_found:
                retry_count -= 1
                time.sleep(5)
            else:
                assert test_result.status_code == requests.codes.ok, self.api_gen_obj.assert_message(test_result)
                break
        return test_result.text

    def __get_duration_from_csv(self, csv_as_string):
        first_line_of_csv = csv_as_string.split('\n', 1)[0]
        duration = first_line_of_csv[first_line_of_csv.index("Measurement.Duration=")+21:]
        return duration
    
    def update_signal_names_in_csv(self, csv_as_string):
        csv_as_string=re.sub("[\ (].*?[\)]", "", csv_as_string)
        return csv_as_string

    def __get_start_time_from_csv(self, csv_as_string):
        first_line_of_csv = csv_as_string.split('\n', 1)[0]
        return first_line_of_csv[first_line_of_csv.index("Measurement.Start-Time=")+23:first_line_of_csv.index(",Measurement.End-Time=")]

    def  __get_end_time_from_csv(self, csv_as_string):
        first_line_of_csv = csv_as_string.split('\n', 1)[0]
        return first_line_of_csv[first_line_of_csv.index("Measurement.End-Time=")+21:first_line_of_csv.index(",Measurement.Duration=")]


    def __convert_csv_to_json(self, csv_as_string):
        test_result_csv = csv_as_string.split('\n', 1)[1] # To remove first line of the csv
        test_result_csv = test_result_csv.replace(',', '') # To remove all the commas in the csv
        test_result_csv = pandas.DataFrame(pandas.read_csv(io.StringIO(test_result_csv), sep = ";", low_memory=False))
        test_result_csv = test_result_csv.sort_values(by=['time'])
        test_result_json = test_result_csv.to_json(orient = 'table')
        test_result_json = json.loads(test_result_json)
        data_size = len(test_result_json['data'])
        if (data_size > 1):
            unit_row = test_result_json['data'][data_size - 1]
            if (unit_row['index'] == 0):
                test_result_json['data'].insert(0, unit_row)
                del test_result_json['data'][data_size]
        return test_result_json

    def validate_teststep_duration(self, test_step_results, time_span, offset):
        total_duration_from_teststeps = 0
        for test_step_id in list(test_step_results.keys()):
            total_duration_from_teststeps = total_duration_from_teststeps + int(test_step_results[test_step_id]['duration'])
        logging.info(f'Total duration from test steps - {total_duration_from_teststeps}')
        logging.info(f'Total duration from timer - {time_span}')
        assert abs(round(time_span / 1000) - round(total_duration_from_teststeps / 1000)) < offset, "Expected duration - " + str(round(time_span / 1000)) + " Received duration - " +  str(round(total_duration_from_teststeps / 1000))


    def create_signal_collection(self,endpoint,payload,files):
        r = self.api_requests.post_request_file(ep=endpoint,params=payload,dbc_file=files)
        return r

    def create_measurement_configuration(self,endpoint,payload):
        r = self.api_requests.post_request(ep=endpoint,params=payload)
        return r   
    
    def calculate_duration_in_ms(self, start_time, end_time):
        duration = end_time - start_time
        duration_in_ms = duration.total_seconds()*1000
        return duration_in_ms

    def get_signal_collection(self,signal_collection_name):
        r = self.api_requests.get_request(constants.RM_SIG_COL_SEARCH_NAME.format(signal_collection_name))
        return r
    
    def get_measurement_config_source(self, measurement_configuration_id):
        r = self.api_requests.get_request(constants.RM_MEASURE_CONFIG_ID_SOURCES.format(measurement_configuration_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r

    def get_signals_of_signal_collection(self,signal_collection_id,page=0):
        r = self.api_requests.get_request(constants.RM_SIG_COL_ID_SIGNAL_PAGE.format(signal_collection_id,page))
        return r

    def add_sources_to_measure_config(self,signal_collection_id,measurement_configuration_id,signal_collection_name):
        state_changed = self.set_measurement_configuration_state(measurement_configuration_id, "draft")

        payload = {"sourceName":signal_collection_name,"signalCollectionId":signal_collection_id}
        etag = self.api_requests.get_etag(constants.RM_MEASURE_CONFIG_ID.format(measurement_configuration_id))
        r = self.api_requests.post_request(constants.RM_MEASURE_CONFIG_ID_SOURCES.format(measurement_configuration_id),params=payload, custom_header={'if-match': etag})
        
        if state_changed:
            self.set_measurement_configuration_state(measurement_configuration_id, "releases")
        return r

    def get_signal_details_in_signal_collection(self,signal_collection_id,signal_name):
        r = self.api_requests.get_request(constants.RM_SIG_COL_ID_SIGNAL_NAME.format(signal_collection_id,signal_name))
        return r    

    def add_signal(self, measurement_configuration_id, source_id, signal_id, downsampling_rate = ""):
        state_changed = self.set_measurement_configuration_state(measurement_configuration_id, "draft")

        data = { "signalId": signal_id, "downsamplingRate": downsampling_rate }
        etag = self.api_requests.get_etag(constants.RM_MEASURE_CONFIG_ID.format(measurement_configuration_id))
        r = self.api_requests.post_request(constants.RM_MEASURE_CONFIG_ID_SOURCES_ID_SIGNALS.format(measurement_configuration_id, source_id), params=data, custom_header={'if-match': etag})
        logging.info(f'Signal is added to measurement configuration')

        if state_changed:
            self.set_measurement_configuration_state(measurement_configuration_id, "releases")
        return r

    def add_calculated_signal_with_formula(self, measurement_configuration_id,calculated_signal_name,calculated_signal_downsampling,formula):
        self.set_measurement_configuration_state(measurement_configuration_id, "draft")
        
        data= { "name": calculated_signal_name,"downsamplingRate": calculated_signal_downsampling, "unit": "S", "description": ""}
        etag = self.api_requests.get_etag(constants.RM_MEASURE_CONFIG_ID.format(measurement_configuration_id))
        r = self.api_requests.post_request(constants.RM_MEASURE_CONFIG_ID_CALCULATED_SIGNALS.format(measurement_configuration_id), params=data, custom_header={'if-match': etag})
        assert r.status_code == requests.codes.created, self.api_gen_obj.assert_message(r)
        logging.info(f'Calculated signal is added to measurement configuration')
        self.add_formula( measurement_configuration_id, calculated_signal_name, formula)
    
        return r

    def add_formula (self, measurement_configuration_id,calculated_signal_name,formula):
        formula,caclulated_signal_id = self.add_calculated_signal_id_to_json(measurement_configuration_id,calculated_signal_name,formula)
        etag = self.api_requests.get_etag(constants.RM_MEASURE_CONFIG_ID.format(measurement_configuration_id))
        r = self.api_requests.put_request(constants.RM_MEASURE_CONFIG_ID_CALCULATED_SIGNAL_ID.format(measurement_configuration_id,caclulated_signal_id), params=formula, custom_header={'if-match': etag})
        assert r.status_code == requests.codes.no_content, self.api_gen_obj.assert_message(r)
        logging.info(f'Calculated signals formula is added to measurement configuration')

    def edit_signal_downsampling_rate(self, measurement_configuration_id, source_id, signal_id, downsampling_rate = ""):
        state_changed=self.set_measurement_configuration_state(measurement_configuration_id, "draft")

        data = { "downsamplingRate": downsampling_rate }
        etag = self.api_requests.get_etag(constants.RM_MEASURE_CONFIG_ID.format(measurement_configuration_id))
        r = self.api_requests.put_request(constants.RM_MEASURE_CONFIG_ID_SOURCES_ID_SIGNALS_ID.format(measurement_configuration_id, source_id, signal_id), params=data, custom_header={'if-match': etag})
        assert r.status_code == requests.codes.no_content, self.api_gen_obj.assert_message(r)

        if state_changed:
            self.set_measurement_configuration_state(measurement_configuration_id, "releases")
        return r

    def remove_signal(self, measurement_configuration_id, source_id, signal_id):
        state_changed = self.set_measurement_configuration_state(measurement_configuration_id, "draft")

        etag = self.api_requests.get_etag(constants.RM_MEASURE_CONFIG_ID.format(measurement_configuration_id))
        r = self.api_requests.delete_request(constants.RM_MEASURE_CONFIG_ID_SOURCES_ID_SIGNALS_ID.format(measurement_configuration_id, source_id,signal_id), {'if-match': etag})
        assert r.status_code == requests.codes.no_content, self.api_gen_obj.assert_message(r)
        logging.info(f'Signal is removed from measurement configuration')
        
        if state_changed:
            self.set_measurement_configuration_state(measurement_configuration_id, "releases")

    def remove_source(self, measurement_id, source_id):
        etag = self.api_requests.get_etag(constants.RM_MEASURE_CONFIG_ID.format(measurement_id))
        r = self.api_requests.delete_request(constants.RM_MEASURE_CONFIG_ID_SOURCES_ID.format(measurement_id, source_id), {'if-match': etag})
        if r.status_code == requests.codes.precondition_failed:
            logging.info(constants.RM_LOGREF_MSG.format(r.json()['logref'], r.json()['message']))
        elif r.status_code == requests.codes.no_content:
            logging.info(f'Signal is remove from measurement configuration')
        else:
            assert False, constants.RM_LOGREF_MSG.format(r.json()['logref'], r.json()['detail'])


    def add_signals(self, measurement_config, signal):
        r = self.get_measurement_config_source(measurement_config)
        source_count = len(r.json()['_embedded']['sources'])
        while (source_count > 0):
            source_id = r.json()['_embedded']['sources'][source_count-1]['sourceId']
            signals = self.get_signals_of_signal_collection(r.json()['_embedded']['sources'][source_count-1]['_embedded']['selectedSignalCollection']['signalCollectionId'])
            signals.json()['page']['size']
            total_pages = signals.json()['page']['totalPages']
            while(total_pages > 0):
                signals = self.get_signals_of_signal_collection(r.json()['_embedded']['sources'][source_count-1]['_embedded']['selectedSignalCollection']['signalCollectionId'],total_pages-1)
                page_signals = len(signals.json()['_embedded']['signals'])
                while(page_signals > 0):
                    signal_id = signals.json()['_embedded']['signals'][page_signals-1]['signalId']
                    self.add_signal(measurement_config, source_id, signal_id)
                    page_signals -= 1
                total_pages -= 1
            source_count -= 1
        # Get Measurement configuration and source ID
        # Get ETAG from measurement configuration 
        # Get signal iD from signal collection
        return r

    def get_messages_of_signal_collection(self,signal_collection_id,message_name):
        r = self.api_requests.get_request(constants.RM_SC_ID_SEARCH_NAME.format(signal_collection_id,message_name))
        return r

    def add_message(self, measurement_configuration_id, source_id, message_id,message_downsampling):
        state_changed = self.set_measurement_configuration_state(measurement_configuration_id, "draft")

        data = { "messageId": message_id, "downsamplingRate": message_downsampling }
        etag = self.api_requests.get_etag(constants.RM_MEASURE_CONFIG_ID.format(measurement_configuration_id))
        r = self.api_requests.post_request(constants.RM_MEASURE_CONFIG_ID_SOURCES_ID_MSG.format(measurement_configuration_id, source_id), params=data, custom_header={'if-match': etag})

        if state_changed:
            self.set_measurement_configuration_state(measurement_configuration_id, "releases")
        return r


    def edit_message_downsampling_rate(self, measurement_configuration_id, source_id, message_id, downsampling_rate = ""):
        state_changed = self.set_measurement_configuration_state(measurement_configuration_id, "draft")
        

        data = { "downsamplingRate": downsampling_rate }
        etag = self.api_requests.get_etag(constants.RM_MEASURE_CONFIG_ID.format(measurement_configuration_id))
        r = self.api_requests.put_request(constants.RM_MEASURE_CONFIG_ID_SOURCES_ID_MSG_ID.format(measurement_configuration_id, source_id, message_id), params=data, custom_header={'if-match': etag})
        assert r.status_code == requests.codes.no_content, self.api_gen_obj.assert_message(r)

        if state_changed:
            self.set_measurement_configuration_state(measurement_configuration_id, "releases")
        return r

    def get_latest_measurement_job_status(self, vehicle_id, device_id, measurement_config):
        r = self.api_requests.get_request(constants.RM_VEHICLES_ID_MEASURE_JOB.format(vehicle_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        status_arr = []
        measurement_job_count = 0
        count = 0
        if '_embedded' in r.json():
             measurement_job_count = len(r.json()['_embedded']['measurementJobs'])
        while (count<measurement_job_count):
            rm_config_to_vehicle = r.json()['_embedded']['measurementJobs'][count]['_embedded']['releasedMeasurementConfiguration']['name']
            if((r.json()['_embedded']['measurementJobs'][count]['deviceId'] == device_id) and (rm_config_to_vehicle == measurement_config)):
                status_arr.append(r.json()['_embedded']['measurementJobs'][count]['status'])
                status_arr.append(r.json()['_embedded']['measurementJobs'][count]['substatus'])
                break
            count+=1
        logging.info(status_arr)
        return status_arr
    
    def get_measurement_job_id_by_config_id(self, vehicle_id, device_id, measurement_configuration_id):
        r = self.api_requests.get_request(constants.RM_VEHICLES_ID_MEASURE_JOB.format(vehicle_id))
        measurement_job_count = 0
        count = 0
        job_found=False
        if '_embedded' in r.json():
             measurement_job_count = len(r.json()['_embedded']['measurementJobs'])
             while (count<measurement_job_count):
                if r.json()['_embedded']['measurementJobs'][count]['deviceId'] == device_id and r.json()['_embedded']['measurementJobs'][count]['_embedded']['releasedMeasurementConfiguration']['measurementConfigurationId'] == measurement_configuration_id:
                    measurement_job_id = r.json()['_embedded']['measurementJobs'][count]['measurementJobId']
                    job_found=True
                    break
                count+=1
        else:
            assert False, constants.RM_NO_JOBID_AVAILABLE
        assert job_found,f'No measurement job not found for vehicle {vehicle_id} configuration {measurement_configuration_id} and device {device_id}'
        logging.info(f'measuremnt job ID for vehicle {vehicle_id} and device {device_id} for measurement configuration id {measurement_configuration_id} is {measurement_job_id}')
        return measurement_job_id

    def get_latest_measurement_job_id(self, vehicle_id, slot_name):
        device_id = ''
        r = self.api_requests.get_request(constants.RM_VEHICLES_ID.format(vehicle_id))
        if '_embedded' in r.json():
            for deviceslot in r.json()['_embedded']['deviceSlots']:
                if deviceslot['name'] == slot_name:
                    device_id = deviceslot['deviceId']
        r = self.api_requests.get_request(constants.RM_VEHICLES_ID_MEASURE_JOB.format(vehicle_id))
        if '_embedded' in r.json():
            if r.json()['_embedded']['measurementJobs'][0]['deviceId'] == device_id:
                measurement_job_id = r.json()['_embedded']['measurementJobs'][0]['measurementJobId']
            else:
                assert False, f"Latest measurement job in vehicle {vehicle_id} doesn't belong to device {device_id}"
        else:
            assert False, constants.RM_NO_JOBID_AVAILABLE
        logging.info(f'Latest measuremnt job ID for vehicle {vehicle_id} and device {device_id} is {measurement_job_id}')
        return measurement_job_id
		
    def get_trigger_id_of_mc(self, measurement_configuration_id):
        r = self.api_requests.get_request(constants.RM_MEASURE_CONFIG_ID_TRIGGERS.format(measurement_configuration_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        
        if r.json()['page']['totalElements'] == 1:
            return r.json()['_embedded']['triggers'][0]['triggerId']
        else:
            logging.info(f"Configuration - {measurement_configuration_id} doesn't have any Triggers.")
            return None


    def get_trigger_info_of_mc(self, measurement_configuration_id):
        r = self.api_requests.get_request(constants.RM_MEASURE_CONFIG_ID_TRIGGERS.format(measurement_configuration_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        assert len(r.json()['_embedded']['triggers']) == 1, "Issue. Unexepcted count of trigger is created. Expected Count - 1; Actual Trigger Count - %s"%(str(len(r.json()['_embedded']['triggers'])))
        return r.json()['_embedded']['triggers'][0]

    
    def get_trigger_condition_details(self, measurement_configuration_id, trigger_id, trigger_phase):
        r = self.api_requests.get_request(constants.RM_MEASURE_CONFIG_ID_TRIGGERS_ID_PHASE.format(measurement_configuration_id,trigger_id,trigger_phase))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r
    
    def check_and_get_trigger_data(self, measurement_configuration_id, trigger_id, trigger_phase):
        trigger_data = None
        try:
            r = self.get_trigger_condition_details(measurement_configuration_id, trigger_id, trigger_phase)
            trigger_data = r.json()
        except AssertionError as e :
            logging.debug(f'unable to get the trigger details {e}')
        return trigger_data


    def get_measure_config_signals(self, measurement_configuration_id):
        r = self.api_requests.get_request(constants.RM_MEASURE_CONFIG_ID_SIGNALS.format(measurement_configuration_id))
        logging.info(r)
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r.json()['_embedded']['selectedSignals']

    def get_measure_config_selected_messages(self, measurement_configuration_id):
        r = self.api_requests.get_request(constants.RM_MEASURE_CONFIG_ID_MSG.format(measurement_configuration_id))
        logging.info(r)
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r.json()['_embedded']['selectedMessages']

    def get_measure_config_total_elements(self, measurement_configuration_id, measurement_parameter):
        r = self.api_requests.get_request(constants.RM_MEASURE_CONFIG_ID_PARAM.format(measurement_configuration_id,measurement_parameter))
        total_elements=r.json()['page']['totalElements']
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return total_elements

    def get_teststep_recorded_duration(self,teststep_id):
        """
            Fetches test step recorded duration
        Args:
            teststep_id (_type_): meausrement result teststep_id
        Returns: 
            recorded duration of test step and upload interval of measurement configuration
        """
        measurement_config_id = self.get_measurement_config_id_from_teststep_id(teststep_id)
        upload_interval = self.get_measurement_config_upload_interval(measurement_config_id)
        r = self.get_teststep_from_id(teststep_id)
        recorded_duration = r['measurement']['duration']
        return recorded_duration, upload_interval

    def verify_measurement_entity_count(self, measurement_configuration_id,measurement_entity,count):
        count_array = count.split(",")
        measurement_entity_array = measurement_entity.split(",")
        assert (len(count_array) == len(measurement_entity_array)), f"wrong measurement entity parameters are passed"
        for index,measurement_entity_name in enumerate(measurement_entity_array):
            actual_count = self.get_measure_config_total_elements(measurement_configuration_id,measurement_entity_name)
            assert (str(actual_count)==count_array[index]), f"Measurement configuration has {actual_count} number of {measurement_entity_name}, Expected is {count_array[index]}" 
            logging.info(f"Total {actual_count} number of {measurement_entity_name} are present and verified")
        logging.info("validation of count is successful")    

    def validate_measurement_data_integrity(self,measurement_test_result,separation_time,signals_to_be_excluded,number_of_rows_to_validate=None, measurement_configuration_version = None):
        """Validate data integrity for given signal or calculated signal or calculated list signal or message

        Args:
            measurement_test_result (dict): teststepid as key and measurement data as value
            separation_time (sec): 
            signals_to_be_excluded (list): Signal will be exculuded for validation
            number_of_rows_to_validate (int): Number of rows to valiadate in the csv data
            measurement_configuration_version (str): Version of a given measurement configuration
        """
        if(separation_time is None):
            separation_time = 0
        self.separation_time = separation_time
        for teststep_id in list(measurement_test_result.keys()):
            result = measurement_test_result[teststep_id]
            if measurement_configuration_version != None:
                assert result['rm_config_version'] == measurement_configuration_version, f"Measurement- {teststep_id} generated from wrong rm config version. Activated RM config version is {measurement_configuration_version} but measurement generated from this version - {result['rm_config_version']}"
            data_array = result['results']['data']
            assert len(data_array) > 1, "No data in the measurement, measurement data is empty"
            measurement_configuration_id = self.get_measurement_config_id_from_teststep_id(teststep_id)

            total_signals = self.get_measure_config_total_elements(measurement_configuration_id,"signals")
            total_calculated_signals = self.get_measure_config_total_elements(measurement_configuration_id,"calculatedSignals")
            total_messages = self.get_measure_config_total_elements(measurement_configuration_id, "messages")
            total_calculated_list_signals = self.get_measure_config_total_elements(measurement_configuration_id,"calculatedListSignals")

            if(total_signals != 0) and (total_calculated_list_signals ==0):
                self.verify_signals_data(data_array,measurement_configuration_id, signals_to_be_excluded, number_of_rows_to_validate)
            if (total_calculated_signals !=0):
                self.verify_calculated_signals_data(data_array,measurement_configuration_id,total_signals,total_messages, number_of_rows_to_validate)
            if (total_messages != 0):
                self.verify_messages_data(data_array,measurement_configuration_id, number_of_rows_to_validate)
            if (total_calculated_list_signals !=0):
                self.verify_calculated_list_signals_data(data_array,measurement_configuration_id,0, number_of_rows_to_validate)

    def verify_calculated_signals_data(self, data_array, measurement_configuration_id,total_signals,total_messages,number_of_rows_to_validate = None):
        total_no_of_rows_recorded = len(data_array)-1
        configuration_type = self.get_measure_config_type(measurement_configuration_id)
        selected_calculated_signals = self.get_measure_config_calculated_signals(measurement_configuration_id)
        rows_to_validate = self.fetch_number_of_rows_to_validate(data_array,number_of_rows_to_validate)
        invalid_event = False
        for calculated_signal in selected_calculated_signals:
            logging.info(f"Validating calculated signal - {calculated_signal['name']}")
            assert calculated_signal['name'] in data_array[0].keys(), f"Calculated signal with name {calculated_signal['name']} not found in headers"
            count_rows_of_calculated_signals = self.get_totalrows_recorded_for_measurement_entities(data_array,calculated_signal)
            assert count_rows_of_calculated_signals !=0, f"No data in the measurement for calculated signal {calculated_signal['name']}"
            if configuration_type == "CONTINUOUS":
                down_sampling_rate = calculated_signal['downsamplingRate']
                if not invalid_event :
                    logging.info("Validating Timestamp of calculated signal's measured data...")
                    exception_msg = self.canraw_time_check(data_array, calculated_signal, down_sampling_rate, rows_to_validate)
                    assert exception_msg=='', f"{exception_msg}"
            elif configuration_type == "SINGLE_SHOT":
                signal_data_array = self.__get_data_array_having_value_for_signal(data_array, calculated_signal) 
                assert len(signal_data_array) == 2, f"Measurement for message {calculated_signal['name']} has {len(signal_data_array)} data while expected to be 2"
            else:
                assert False, f'Measurement configuration type {configuration_type} is not valid!'
            if (total_signals > 0 or total_messages > 0):
                assert (count_rows_of_calculated_signals == total_no_of_rows_recorded), f"Calculated signal rows mismatch for {calculated_signal['name']}, Actual {count_rows_of_calculated_signals} Expected {total_no_of_rows_recorded}"
            if calculated_signal['name']=='Calculated_Signal_1' or calculated_signal['name'] == 'Divide_by_signal':
                invalid_event = self.validate_invalid_event_during_calculation(data_array, calculated_signal)
        logging.info("Validation of calculated signals is successfull")

    def verify_calculated_list_signals_data(self, data_array, measurement_configuration_id,data_validation_index,number_of_rows_to_validate = None, trigger_condition_name = None,trigger_type=None):
        
        """ Description     : It validates the data related to calculated list signals within measurement results

        Arguments           : data_array - Measurement Result data against Test Step ID,
                              measurement_configuration_id = Id of the measurement config,
                              data_validation_index = index of row data to be validated for single shot data validation,
                              number_of_rows_to_validate (optional) =  Number of rows to be validated,
                              trigger_condition_name (optional) = Name of the Trigger Condition,
                              trigger_type (optional) = Name of the Type of Trigger


        Expected result : It should validate the data related to calculated list signal in the measurement result

        """


        dm1_config = False
        if trigger_type == 'DM1_Extend_Message':
            dm1_config = True
        
        configuration_type = self.get_measure_config_type(measurement_configuration_id)
        selected_calculated_list_signals = self.get_measure_config_calculated_list_signals(measurement_configuration_id)
        rows_to_validate = self.fetch_number_of_rows_to_validate(data_array,number_of_rows_to_validate)
        selected_warning_telltales_signal = self.fetch_warning_telltales_signal(measurement_configuration_id)

        selected_signals = self.get_measure_config_selected_signals(measurement_configuration_id)
        selected_messages = self.get_measure_config_messages(measurement_configuration_id)

        #signal name is required to compare signal data with calculated list signal data
        for calculated_list_signal in selected_calculated_list_signals:
            logging.info(f"Validating calculated list signal - {calculated_list_signal['name']}")
            assert calculated_list_signal['name'] in data_array[0].keys(), f"Calculated list signal with name {calculated_list_signal['name']} not found in headers"
            if configuration_type == "CONTINUOUS":
                count_rows_of_calculated_list_signals = self.get_totalrows_recorded_for_measurement_entities(data_array,calculated_list_signal)
                if dm1_config == False:
                    assert count_rows_of_calculated_list_signals !=0, f"No data in the measurement for calculated list signal {calculated_list_signal['name']}"
            elif dm1_config == False and configuration_type == "SINGLE_SHOT":
                act_calculated_list_signal_value = self.__get_data_array_having_value_for_daf_signal(data_array, calculated_list_signal)
                if trigger_condition_name != None:
                    actual_type = calculated_list_signal['formula']['anchor']['type']
                    if actual_type == 'DELTA_LIST':
                        calculated_list_signal_type = calculated_list_signal['formula']['anchor']['change']
                    elif actual_type == 'CHANGED_POSITIONS_LIST':
                        calculated_list_signal_type = actual_type
                    trigger_data = self.api_gen_obj.parse_json_file(constants.RM_TRIGGER_JSON)
                    exp_calculated_list_signal_value = trigger_data["triggerTestData"][trigger_condition_name]["dataValidation"]
                    assert len(exp_calculated_list_signal_value[data_validation_index][calculated_list_signal_type]) == len(act_calculated_list_signal_value), f"Measurement for Calculated List signal {calculated_list_signal['name']} has {len(act_calculated_list_signal_value)} data while expected to be {len(exp_calculated_list_signal_value[data_validation_index][calculated_list_signal_type])}"
                    assert exp_calculated_list_signal_value[data_validation_index][calculated_list_signal_type] == act_calculated_list_signal_value,f"Calculated List signal - {calculated_list_signal['name']} has unexpected value - {act_calculated_list_signal_value}. Exp value - {exp_calculated_list_signal_value[data_validation_index][calculated_list_signal_type]}"
                else:
                    assert len(act_calculated_list_signal_value) == 1, f"Measurement for message {calculated_list_signal['name']} has {len(act_calculated_list_signal_value)} data while expected to be 1"
        
        if configuration_type == "CONTINUOUS":
            if dm1_config == False:
                self.check_calculated_list_signals(data_array,selected_calculated_list_signals,rows_to_validate,selected_warning_telltales_signal)
            else:
                if len(data_array) > 1:
                    self.check_dm1_extend_message_signals(data_array,rows_to_validate,selected_messages,selected_signals,selected_calculated_list_signals)
                else:
                    logging.info('Unable to Validate Calculated List Signals as there is no Data Available in the Measurement File.')
            logging.info("Validation of calculated list signals is successful")
        
        elif dm1_config == True and configuration_type == "SINGLE_SHOT":
            logging.info('Validating Single Shot RM for DM1 Extended')
            assert len(data_array) > 1, f"Measurement of DM1 Extended RM with Single Shot Config has {len(data_array)} data while expected data should be greater than 1"
            logging.info("Validation of Data in Single Shot Config Measurement File is successful")

    def check_dm1_extend_message_signals(self, data_array,rows_to_validate,selected_messages,selected_signals,selected_calculated_list_signals):
        
        """ Description     : It analyzes and validates the messages and signals data related to dm1 extend trigger type

        Arguments           : data_array - Measurement Result data against Test Step ID,
                              rows_to_validate = Number of rows to be validated,
                              selected_messages = messages associated with the used measurement config,
                              selected_signals =  signals associated with the used measurement config,
                              selected_calculated_list_signals = calculated list signals associated with the used measurement config

        Expected result : It should validate the messages and signals data related to dm1 extend trigger type

        """

        logging.info("Analyzing and Validating Messages and Signals for DM1 Extend")
        
        list_dm1_messages  =[]
        for message in selected_messages:
            list_dm1_messages.append(message['name'])
        
        for msg_index in range(0,len(list_dm1_messages)):

            previous_ecu_dict = {
                "previous_ecu_msg_val": None,
                "previous_ecu_spn_val": None,
                "previous_ecu_fmi_val": None,
                "previous_ecu_oc_val":None
            }

            current_ecu_dict = {
                "current_ecu_msg_val": None,
                "current_ecu_spn_val": None,
                "current_ecu_fmi_val": None,
                "current_ecu_oc_val":None
            }

            current_signal_condition = None
            message_for_evaluation = list_dm1_messages[msg_index]

            # Get the Filtered Signal Names based upon the Message Name 
            filtered_signal_list = [signals['displayName'] for signals in selected_signals if signals['messageName'] == message_for_evaluation]
            # SPN Column Name for Specific Message
            spn_field = list(filter(lambda signal_name: ('SuspectParameterNumber' in signal_name), filtered_signal_list))[0] 
            # FMI Column Name for Specific Message
            fmi_field = list(filter(lambda signal_name: ('FailureModeIdentifier' in signal_name), filtered_signal_list))[0]
            # OC Column Name for Specific Message
            oc_field = list(filter(lambda signal_name: ('OccurrenceCount' in signal_name), filtered_signal_list))[0]
            # Get Calculated List Signal Names based upon the Signals used in Filter for Calculated List Signal
            value_calculated_list_signal = [calc_list_signal_name['name'] for calc_list_signal_name in selected_calculated_list_signals if calc_list_signal_name['formula']['anchor']['filters'][0]['signalName'] in filtered_signal_list]
            # Removing OC Calculated List Signal as we dont want it for computation Purpose
            # value_calculated_list_signal = [x for x in value_calculated_list_signal if 'OC' not in x]

            for row_index in range(1,(rows_to_validate+1)):
                if data_array[row_index][message_for_evaluation] != "[]" and data_array[row_index][message_for_evaluation] != None and data_array[row_index][message_for_evaluation] != previous_ecu_dict["previous_ecu_msg_val"]:
                    
                    current_ecu_dict["current_ecu_msg_val"] = data_array[row_index][message_for_evaluation]
                    current_ecu_dict["current_ecu_spn_val"] = data_array[row_index][spn_field]
                    current_ecu_dict["current_ecu_fmi_val"] = data_array[row_index][fmi_field]
                    current_ecu_dict["current_ecu_oc_val"] = data_array[row_index][oc_field]

                    self.determine_dm1_extend_signal_condition_for_validation(row_index,data_array,previous_ecu_dict,current_ecu_dict,current_signal_condition,value_calculated_list_signal)
                           
                    previous_ecu_dict["previous_ecu_msg_val"] = current_ecu_dict["current_ecu_msg_val"]
                    previous_ecu_dict["previous_ecu_spn_val"] = current_ecu_dict["current_ecu_spn_val"]
                    previous_ecu_dict["previous_ecu_fmi_val"] = current_ecu_dict["current_ecu_fmi_val"]
                    previous_ecu_dict["previous_ecu_oc_val"] = current_ecu_dict["current_ecu_oc_val"]


    def determine_dm1_extend_signal_condition_for_validation(self,row_index,data_array,previous_ecu_dict,current_ecu_dict,current_signal_condition,value_calculated_list_signal):

        """ Description     : It determines the signal condition on specific row index of measurement data and filter out the calculated list signals to be validated according to the signal condition

        Arguments           : row_index =  Row Index for which validation is going to happen
                              data_array = Measurement Result data against Test Step ID,
                              previous_ecu_dict = Dictionary to store the value of Different ECU Parameter Value (MSG/SPN/FMI/OC) for the last row,
                              current_ecu_dict =  Dictionary to store the value of Different ECU Parameter Value (MSG/SPN/FMI/OC) for the current row,
                              current_signal_condition = Signal condition which has happened in the specific index(Appeared/Disappeared/Appeared & Disappeared),
                              value_calculated_list_signal = Calculated List Signal Names based upon the Signals used in Filter for Calculated List Signal
                              

        Expected result : It should determine the signal condition on specific row index of measurement data and filter out the calculated list signals

        """

        #Filter out the Calculated List Condition based upon the status of the Signal Condition
        calculated_list_signal_to_be_validated = None

        # Decide the Signal Condition for Current Index Position under Evaluation 
        if (previous_ecu_dict["previous_ecu_msg_val"] != None or previous_ecu_dict["previous_ecu_msg_val"] == constants.RM_BLANK_MESSAGE_DM1_EXTEND) and (previous_ecu_dict["previous_ecu_spn_val"] == None and previous_ecu_dict["previous_ecu_fmi_val"] == None and previous_ecu_dict["previous_ecu_oc_val"] == None)  and  (current_ecu_dict["current_ecu_spn_val"] != None and current_ecu_dict["current_ecu_fmi_val"] != None and current_ecu_dict["current_ecu_oc_val"] != None):                        
            current_signal_condition = 'Appeared'
            calculated_list_signal_to_be_validated = [calc_list_signal_name for calc_list_signal_name in value_calculated_list_signal if 'Appeared' in calc_list_signal_name]
        elif previous_ecu_dict["previous_ecu_msg_val"] != None and current_ecu_dict["current_ecu_msg_val"] != None and (previous_ecu_dict["previous_ecu_spn_val"] != None and previous_ecu_dict["previous_ecu_fmi_val"] != None and previous_ecu_dict["previous_ecu_oc_val"] != None) and  (current_ecu_dict["current_ecu_spn_val"] != None and current_ecu_dict["current_ecu_fmi_val"] != None and current_ecu_dict["current_ecu_oc_val"] != None):
            current_signal_condition = 'Appeared_and_Disappeared'
            calculated_list_signal_to_be_validated = value_calculated_list_signal
        elif previous_ecu_dict["previous_ecu_msg_val"] != None and current_ecu_dict["current_ecu_msg_val"] != None and (previous_ecu_dict["previous_ecu_spn_val"] != None and previous_ecu_dict["previous_ecu_fmi_val"] != None and previous_ecu_dict["previous_ecu_oc_val"] != None) and  (current_ecu_dict["current_ecu_spn_val"] == None and current_ecu_dict["current_ecu_fmi_val"] == None and current_ecu_dict["current_ecu_oc_val"] == None):
            current_signal_condition = 'Disappeared'
            calculated_list_signal_to_be_validated = [calc_list_signal_name for calc_list_signal_name in value_calculated_list_signal if 'Disappeared' in calc_list_signal_name]
            
        # Validate the Calculated List Signal for Current Index Position
        if current_signal_condition != None and calculated_list_signal_to_be_validated != None:
            self.validate_dm1_extend_calculated_list_signals(data_array,current_signal_condition,calculated_list_signal_to_be_validated,row_index)

    def validate_dm1_extend_calculated_list_signals(self,data_array,current_signal_condition,calculated_list_signal_to_be_validated,row_index):
        
        """ Description     : It validates the data related to calculated list signal on specific row index of measurement data based upon the signal condition

        Arguments           : data_array - Measurement Result data against Test Step ID,
                              current_signal_condition = Signal condition which has happened in the specific index(Appeared/Disappeared/Appeared & Disappeared),
                              calculated_list_signal_to_be_validated = list of calculated list signals to be validated at the specific index,
                              row_index =  Row Index for which validation is going to happen

        Expected result : It should validate the data related to calculated list signal at specific row index of measurement data based upon the signal condition

        """
        
        logging.info("Analyzing and Validating Targeted Calculated List Signals for DM1 Extended")
        for calc_list_signal in calculated_list_signal_to_be_validated:
            logging.info(f"Validating Calculated List Signal - {calc_list_signal} at Index {row_index} ")
            match current_signal_condition:
                case "Appeared":
                    assert data_array[row_index][calc_list_signal] != None, f"Calculated List Signal Value is None for Appearing of Signal. Expecting Appeared Calculated List Signal Value for Calculated List Signal - {calc_list_signal}"
                case "Disappeared":
                    assert data_array[row_index][calc_list_signal] != None, f"Calculated List Signal Value is None for Disappearing of Signal. Expecting Disappeared Calculated List Signal Value for Calculated List Signal - {calc_list_signal}"
                case "Appeared_and_Disappeared":
                    assert data_array[row_index][calc_list_signal] != None, f"Calculated List Signal Value is None for Appearing and Disappearing of Signal. Expecting Calculated List Signal Value for Calculated List Signal - {calc_list_signal}"
                case _:
                    logging.info("Invalid Signal Condition.Unable to Validate Calculated List Signal Value")


    def fetch_warning_telltales_signal(self, measurement_configuration_id):
        selected_signals = self.get_measure_config_selected_signals(measurement_configuration_id)
        warning_telltales_signal = None
        for selected_signal in selected_signals:
            if selected_signal['displayName'] == 'WarningId01':
                warning_telltales_signal = 'WarningId01'
            elif selected_signal['displayName'] == 'TT01_to_TT15':
                warning_telltales_signal = 'TT01_to_TT15'
        return warning_telltales_signal

    def check_calculated_list_signals(self, data_array,selected_calculated_list_signals,rows_to_validate,selected_warning_telltales_signal):
        logging.info('Validating Calculated list signal')
        previous_warning_val = "[]"
        warning_len = 0
        calculated_list_signal_names = self.fetch_calculated_list_signal_name(selected_calculated_list_signals)
        for i in range(1,rows_to_validate):
            if data_array[i][selected_warning_telltales_signal] != "[]" and data_array[i][selected_warning_telltales_signal] != None and data_array[i][selected_warning_telltales_signal] !=previous_warning_val:
                previous_warning_val = data_array[i][selected_warning_telltales_signal]
                warning_len = self.validate_warnings_telltales(data_array,warning_len,previous_warning_val,calculated_list_signal_names,i)
            elif data_array[i][selected_warning_telltales_signal] == "[]" and calculated_list_signal_names[1] != None and data_array[i][calculated_list_signal_names[1]] != None:
                assert previous_warning_val == '['+ ' '.join([s.split('.')[0] for s in data_array[i][calculated_list_signal_names[1]].strip('[]').split()]) + ']', f"Unexpected last Disappeared warning list at index - {data_array[i]['index']}"     
            else:
                if calculated_list_signal_names[0] != None:
                    assert data_array[i][calculated_list_signal_names[0]] == None, f"Appeared warning list is not None. Expecting Appeared warning list to be None in index - {data_array[i]['index']}"
                if calculated_list_signal_names[1] != None:
                    assert data_array[i][calculated_list_signal_names[1]] == None, f"Disappeared warning list is not None. Expecting Disappeared warning list to be None in index - {data_array[i]['index']}"
    
    def validate_warnings_telltales(self, data_array,warning_len,previous_warning_val,calculated_list_signal_names,index):
        if len(previous_warning_val) > warning_len and calculated_list_signal_names[0] != None:
            logging.info(f'Appeared warning list - {data_array[index][calculated_list_signal_names[0]]}')
            assert data_array[index][calculated_list_signal_names[0]] != None, f"Appeared warning list is None. Expecting Appeared warning list in index - {data_array[index]['index']}"
            warning_len = len(previous_warning_val)
        elif len(previous_warning_val) < warning_len and calculated_list_signal_names[1] != None:
            logging.info(f'Disappeared warning list - {data_array[index][calculated_list_signal_names[1]]}')
            assert data_array[index][calculated_list_signal_names[1]] != None, f"Disappeared warning list is None. Expecting Disappeared warning list in index - {data_array[index]['index']}"
            warning_len = len(previous_warning_val)
        
        if calculated_list_signal_names[2] != None:
            logging.info(f'Full list - {data_array[index][calculated_list_signal_names[2]]}')
            assert data_array[index][calculated_list_signal_names[2]] != None, f"Full list is None. Expecting some value for Full list in index - {data_array[index]['index']}"

        if calculated_list_signal_names[3] != None and warning_len != 0 :
            logging.info(f'Changed list-Position - {data_array[index][calculated_list_signal_names[3]]}')
            assert data_array[index][calculated_list_signal_names[3]] != None, f"Changed List-Position is None. Expecting some value for Changed List-Position in index - {data_array[index]['index']}"
        elif calculated_list_signal_names[3] != None and warning_len == 0 :
            logging.info(f'Changed list-Position - {data_array[index][calculated_list_signal_names[3]]}')
            assert data_array[index][calculated_list_signal_names[3]] == None, f"Changed List-Position is not None. Expecting no value for Changed List-Position in index - {data_array[index]['index']}"
            warning_len = len(previous_warning_val)
        return warning_len

    def fetch_calculated_list_signal_name(self,selected_calculated_list_signals):
        appeared_signal_name, disappeared_signal_name, full_list_signal_name, changed_list_signal_name = None, None, None, None
        calculated_list_signal_names = [appeared_signal_name, disappeared_signal_name, full_list_signal_name, changed_list_signal_name]
        for calculated_list_signal in selected_calculated_list_signals:
            actual_type = calculated_list_signal['formula']['anchor']['type']
            if actual_type == 'DELTA_LIST':
                actual_change = calculated_list_signal['formula']['anchor']['change']
                if actual_change == 'APPEARED':
                    calculated_list_signal_names[0] = calculated_list_signal['name']
                elif actual_change == 'DISAPPEARED':
                    calculated_list_signal_names[1] = calculated_list_signal['name']
                elif actual_change == 'FULL_LIST':
                    calculated_list_signal_names[2] = calculated_list_signal['name']
            elif actual_type == 'CHANGED_POSITIONS_LIST':
                calculated_list_signal_names[3] = calculated_list_signal['name']
        return calculated_list_signal_names

    def verify_messages_data(self, data_array,measurement_configuration_id, number_of_rows_to_validate = None):
        configuration_type = self.get_measure_config_type(measurement_configuration_id)
        selected_messages = self.get_measure_config_selected_messages(measurement_configuration_id)
        rows_to_validate = self.fetch_number_of_rows_to_validate(data_array,number_of_rows_to_validate)
        for selected_message in selected_messages:
            logging.info(f"Validating message  - {selected_message['name']}")
            assert selected_message['name'] in data_array[0].keys(), f"Message with name {selected_message['name']} not found in headers"
            count_rows_of_message = self.get_totalrows_recorded_for_measurement_entities(data_array,selected_message)
            assert count_rows_of_message!=0, f"No data in the measurement for message {selected_message['name']}"
            if configuration_type == "CONTINUOUS":
                down_sampling_rate = selected_message['downsamplingRate']
                logging.info("Validating Timestamp of CANraw message's measure data...")
                exception_msg = self.canraw_time_check(data_array, selected_message, down_sampling_rate, rows_to_validate)
                assert exception_msg=='', f"{exception_msg}"
            elif configuration_type == "SINGLE_SHOT":
                signal_data_array = self.__get_data_array_having_value_for_signal(data_array, selected_message) 
                assert len(signal_data_array) == 2, f"Measurement for message {selected_message['name']} has {len(signal_data_array)} data while expected to be 2"
            else:
                assert False, f'Measurement configuration type {configuration_type} is not valid!'
            logging.info(f"Validation of message {selected_message['name']} is successfull")
        logging.info("Validation of messages is successfull")

    def get_totalrows_recorded_for_measurement_entities(self,data_array,measurement_entity):
        count_rows_of_measurement_entity=0
        if 'signalName' in measurement_entity:
            entity_name = 'signalName'
        else:
            entity_name = 'name'
        for i in range(1,len(data_array)):
            if (data_array[i][measurement_entity[entity_name]] is not None):
                count_rows_of_measurement_entity+=1
        return count_rows_of_measurement_entity

    def validate_invalid_event_during_calculation(self, data_array,calculated_signal):
        def find_invalid_event_and_validate(signal_value, assert_message):
            for i in range(1,len(data_array)):
                if (data_array[i][calculated_signal['name']] == signal_value):
                    assert data_array[i]['Calculated_Signal_2'] is None, f"Reused Calculated_Signal_2 has value when {calculated_signal['name']} {assert_message}"
                return signal_value
                
        if calculated_signal['name'] == 'Calculated_Signal_1':
            assert_message = "not defined yet for calculation"
            find_invalid_event_and_validate(None,assert_message)
            invalid_event= False
        else:
            invalid_event= True
            assert_message = "formula is invalid"
            find_invalid_event_and_validate("0.0",assert_message)
        logging.info('Invalid event during calculation is validated successfully')
        return invalid_event

    def add_trigger(self, measurement_configuration_id, data):
        logging.info(f"data-{data}")
        trigger_id = self.get_trigger_id_of_mc(measurement_configuration_id)

        if (trigger_id is None):
            logging.info(f"data-{data}")
            etag = self.api_requests.get_etag(constants.RM_MEASURE_CONFIG_ID.format(measurement_configuration_id))
            r = self.api_requests.post_request(constants.RM_MEASURE_CONFIG_ID_TRIGGERS.format(measurement_configuration_id), params=data, custom_header={'if-match': etag})
            assert r.status_code == requests.codes.created, self.api_gen_obj.assert_message(r)
            trigger_id = self.get_trigger_id_of_mc(measurement_configuration_id)
            return trigger_id

        else:
            logging.info("There is already a Trigger defined for the RM Configuration. Hence intitating editing of existing Trigger...")
            self.edit_trigger(measurement_configuration_id, data)
    
    def edit_trigger(self, measurement_configuration_id, data):
        trigger_id = self.get_trigger_id_of_mc(measurement_configuration_id)
        
        if (trigger_id is not None):
            etag = self.api_requests.get_etag(constants.RM_MEASURE_CONFIG_ID.format(measurement_configuration_id))
            r = self.api_requests.put_request(constants.RM_MEASURE_CONFIG_ID_TRIGGERS_ID.format(measurement_configuration_id,trigger_id), params=data, custom_header={'if-match': etag})
    
            if (r.status_code != requests.codes.no_content):
                logging.info(constants.RM_LOGREF_MSG.format(r.json()['logref'], r.json()['message']))
                assert False, self.api_gen_obj.assert_message(r)
            return trigger_id
        else:
            assert False, "There's no existing Trigger for Measurement Configuration %s"%measurement_configuration_id


    def del_trigger(self, measurement_configuration_id):
        trigger_id = self.get_trigger_id_of_mc(measurement_configuration_id)
            
        etag = self.api_requests.get_etag(constants.RM_MEASURE_CONFIG_ID.format(measurement_configuration_id))
        if trigger_id is not None:
            r = self.api_requests.delete_request(constants.RM_MEASURE_CONFIG_ID_TRIGGERS_ID.format(measurement_configuration_id,trigger_id), {'if-match': etag})
            assert r.status_code == requests.codes.no_content, self.api_gen_obj.assert_message(r)
        
        else:
            logging.info("Trigger is not present, so deleting trigger is not performed.")


    def set_trigger_state(self, measurement_configuration_id, trigger_state):
        trigger_id = self.get_trigger_id_of_mc(measurement_configuration_id)
        r = self.api_requests.get_request(constants.RM_MEASURE_CONFIG_ID_TRIGGERS_ID.format(measurement_configuration_id,trigger_id))
        
        if (trigger_state.upper() == "ACTIVATE"):
            exp_trigger_status = "ACTIVE"
        elif (trigger_state.upper() == "DEACTIVATE"):
            exp_trigger_status = "INACTIVE"
        if (exp_trigger_status != r.json()['status'].upper()):
            etag = self.api_requests.get_etag(constants.RM_MEASURE_CONFIG_ID.format(measurement_configuration_id))
            r = self.api_requests.put_request(constants.RM_MEASURE_CONFIG_ID_TRIGGERS_ID_PHASE.format(measurement_configuration_id,trigger_id,trigger_state), params={}, custom_header={'if-match': etag})
            assert r.status_code == requests.codes.no_content, self.api_gen_obj.assert_message(r)

        elif (exp_trigger_status == r.json()['status']):
            logging.info(f"Trigger status is already in {trigger_state} state. No further action required.")
        else:
            assert False, ("Unknown trigger state is passed as test data.")


    def get_trigger_element (self, measurement_configuration_id, trigger_id, trigger_phase):
        logging.info(f"Fetching details of trigger element -{trigger_phase} of Configuration {measurement_configuration_id} ")
        r = self.api_requests.get_request(constants.RM_MEASURE_CONFIG_ID_TRIGGERS_ID_PHASE.format(measurement_configuration_id,trigger_id,trigger_phase))
        if ("name" in r.json()):
            return r.json()['name']
        else:
            logging.info(r.json()['detail'])
            return None
                
    def prepare_trigger_payload(self, phase_data):
        trigger_data = self.api_gen_obj.parse_json_file(constants.RM_TRIGGER_JSON)
        all_trigger_data = trigger_data["triggerTestData"]

        template = deepcopy(all_trigger_data[phase_data["template"]])
        
        del phase_data["template"]
        template.update(phase_data)
        for key, val in phase_data.items():
            if key == "triggerElements":
                template[key] = [self.prepare_trigger_payload(inner_trigger_element) for inner_trigger_element in val]
        
        return template


    def add_trigger_element(self, measurement_configuration_id, trigger_phase, data):
        trigger_id = self.get_trigger_id_of_mc(measurement_configuration_id)
        data=self.get_signal_or_message_id_source_id(measurement_configuration_id,data)

        assert data is not None, 'Signals/messages required for start trigger are not available'

        logging.info(f"Before Adding new trigger Element, checking presence of existing {trigger_phase}, if any.")
        trigger_name = self.get_trigger_element(measurement_configuration_id, trigger_id, trigger_phase)
        if (trigger_name is not None):
            logging.info(f"There is existing {trigger_phase} defined. Deleting it now ...")
            self.del_trigger_element(measurement_configuration_id, trigger_phase)

        logging.info(f"Now, there is no existing {trigger_phase}. Adding {trigger_phase} to configuration {measurement_configuration_id} ...")
        etag = self.api_requests.get_etag(constants.RM_MEASURE_CONFIG_ID.format(measurement_configuration_id))
        r = self.api_requests.post_request(constants.RM_MEASURE_CONFIG_ID_TRIGGERS_ID_PHASE.format(measurement_configuration_id,trigger_id,trigger_phase), params=data, custom_header={'if-match': etag})
        assert r.status_code == requests.codes.created, self.api_gen_obj.assert_message(r)
        

    def edit_trigger_element(self, measurement_configuration_id, trigger_phase, data):
        trigger_id = self.get_trigger_id_of_mc(measurement_configuration_id)
          
        data=self.get_signal_or_message_id_source_id(measurement_configuration_id,data)
        assert data is not None, 'Signals/messages required for start trigger are not available' 

        etag = self.api_requests.get_etag(constants.RM_MEASURE_CONFIG_ID.format(measurement_configuration_id))
        r = self.api_requests.put_request(constants.RM_MEASURE_CONFIG_ID_TRIGGERS_ID_PHASE.format(measurement_configuration_id,trigger_id,trigger_phase), params=data, custom_header={'if-match': etag})
        assert r.status_code != requests.codes.no_content, self.api_gen_obj.assert_message(r)


    def del_trigger_element(self, measurement_configuration_id, trigger_phase):
        trigger_id = self.get_trigger_id_of_mc(measurement_configuration_id)

        etag = self.api_requests.get_etag(constants.RM_MEASURE_CONFIG_ID.format(measurement_configuration_id))
        r = self.api_requests.delete_request(constants.RM_MEASURE_CONFIG_ID_TRIGGERS_ID_PHASE.format(measurement_configuration_id,trigger_id,trigger_phase), {'if-match': etag})
        assert r.status_code == requests.codes.no_content, self.api_gen_obj.assert_message(r)


    def get_signal_or_message_id_source_id(self, measurement_configuration_id, data):
        for key, val in data.items():
            if key == 'type' and val == 'CONDITION_SIGNAL' or val == 'CONDITION_INTERVAL':
                logging.info("Get the signal collection value")
                selected_signals_or_messages = self.get_measure_config_signals(measurement_configuration_id)
                if not self.add_signal_or_message_name_to_json(data, selected_signals_or_messages, 'signalId', 'signalName'): return None
                break
            elif key == 'type' and val == 'CONDITION_MESSAGE':
                logging.info("Get the message collection value")
                selected_signals_or_messages = self.get_measure_config_selected_messages(measurement_configuration_id)
                if not self.add_signal_or_message_name_to_json(data, selected_signals_or_messages, 'messageId', 'name'): return None
                break
            elif isinstance(val,dict) or isinstance(val, list):
                self.__get_source_id(measurement_configuration_id, val)
        return data

    
    def __get_source_id(self, measurement_configuration_id, val):
        if isinstance(val,dict):
            if self.get_signal_or_message_id_source_id(measurement_configuration_id, val) is None:return None
        elif isinstance(val, list):
            for item in val:
                if self.get_signal_or_message_id_source_id(measurement_configuration_id, item) is None:return None


    def add_signal_or_message_name_to_json(self, data, selected_signals_or_messages, signal_type, name):
        signal_found = False
        for selected_signal_or_message in (selected_signals_or_messages):
            if selected_signal_or_message[name] == data[signal_type]:
                data['sourceId'] = selected_signal_or_message['sourceId']
                data[signal_type] = selected_signal_or_message[signal_type]
                signal_found = True
                break
        return signal_found
    
    def add_calculated_signal_id_to_json(self, measurement_configuration_id,calculated_signal_name,formula):
        selected_calculated_signals = self.get_measure_config_calculated_signals(measurement_configuration_id)
        for selected_calculated_signal in selected_calculated_signals:
            if (selected_calculated_signal['name']==calculated_signal_name):
                calculated_signal_id = selected_calculated_signal['signalId']
            if (selected_calculated_signal['name']== formula["formula"]['anchor']['operand1']['signalId']):
                formula["formula"]['anchor']['operand1']['signalId'] = selected_calculated_signal['signalId']
        return formula,calculated_signal_id

    def get_trigger_status(self, measurement_configuration_id):
        trigger_id = self.get_trigger_id_of_mc(measurement_configuration_id)    
        r = self.api_requests.get_request(constants.RM_MEASURE_CONFIG_ID_TRIGGERS_ID.format(measurement_configuration_id,trigger_id))
        logging.info(r)
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r.json()['status']

    def get_rm_signal_details(self, measurement_configuration_id):
        r = self.api_requests.get_request(constants.RM_MEASURE_CONFIG_ID_SIGNALS.format(measurement_configuration_id))
        if "_embedded" in r.json():
            return r.json()["_embedded"]["selectedSignals"]
        else:
            logging.info("No signal details found for RM configuration - %s"%measurement_configuration_id)
            return None

    def measured_message_appear_check(self, exp_value,trigger_phase,context):
        message_appear_start= exp_value["message_appear_start_check"]
        message_appear_stop= exp_value["message_appear_stop_check"]
        results=context.measurement_test_result
        measurement_result=len(results)-1
        while measurement_result >= 0:
            teststep_id = list(results.keys())[measurement_result]
            result = results[teststep_id]
            data_array=result['results']['data']
            if len(data_array) > 1:
                if (trigger_phase is None or trigger_phase == "START"):
                    assert message_appear_start in data_array[0].keys(), f"message {message_appear_start} is not present in measurement"
                    assert (data_array[1][message_appear_start] is not None), f"Unexpected, message start {message_appear_start} did not appear at start."
                    assert (data_array[1][message_appear_stop] is None), f"Unexpected, message stop {message_appear_stop} appears at start."
                    logging.info(f'start message appear check validation passed')
                if( trigger_phase is None or trigger_phase == "STOP"):
                    assert message_appear_stop in data_array[0].keys(), f"message {message_appear_stop} is not present in measurement"
                    assert (data_array[len(data_array)-1][message_appear_stop] is not None), f"Unexpected, message stop {message_appear_stop} did not appear at stop."
                    assert (data_array[len(data_array)-1][message_appear_start] is None), f"Unexpected, message start {message_appear_start} appears at stop."
                    logging.info(f'stop message appear check validation passed')
                logging.info(f'message appears check validation passed')
                break
            else:
                assert False, f"No data in the measurement for message {message_appear_start}/{message_appear_stop}"
        measurement_result-= 1   

    def pre_trigger_check (self,exception_time,data_array,pre_trigger_time,exp_start_values,length_exp_values,message_name,message_or_signal_min ):
        data_row = 1
        actual_start_time= data_array[data_row]["time_relative"]
        actual_start_time_interval= float(data_array[data_row]["time_relative"])
        while data_row < len(data_array):
            actual_start_value = data_array[data_row][message_name]
            if actual_start_value != exp_start_values[length_exp_values][1]:
                actual_start_time_interval= float(data_array[data_row]["time_relative"])-float(actual_start_time)
                if (float(actual_start_time_interval) > float(pre_trigger_time)+exception_time):
                    assert False, "Unexpected. Measurement didn't start at correct value and pre trigger time, Actual Value - %s with pre trigger time - %s. Expected Value - %s and pre trigger time - %s."%(actual_start_value,round(actual_start_time_interval,3),exp_start_values[length_exp_values][1],pre_trigger_time)
            elif(float(actual_start_time_interval) < float(pre_trigger_time)+exception_time):
                actual_start_time_interval= float(data_array[data_row]["time_relative"])-float(actual_start_time)
                if(float(actual_start_time_interval) < float(pre_trigger_time)-exception_time) and (message_or_signal_min!=data_array[1][message_name]):
                    assert False, constants.RM_NOT_STARTED_TRIGGER_TIME%(actual_start_value,round(actual_start_time_interval,3),exp_start_values[length_exp_values][1],pre_trigger_time)
                logging.info(f'message/signal start value check and pre trigger time check according to trigger passed')
                break
            else:
                assert False, constants.RM_NOT_STARTED_TRIGGER_TIME%(actual_start_value,round(actual_start_time_interval,3),exp_start_values[length_exp_values][1],pre_trigger_time)
            data_row+=1

    def post_trigger_check (self,exception_time,data_array,post_trigger_time,exp_stop_values,length_exp_values,message_name ):
        data_row = len(data_array)-1
        actual_stop_time= data_array[data_row]["time_relative"]
        actual_stop_time_interval= float(data_array[data_row]["time_relative"])
        while data_row > 0:
            actual_stop_value = data_array[data_row][message_name]
            if actual_stop_value != exp_stop_values[length_exp_values][1]:
                actual_stop_time_interval= float(actual_stop_time) - float(data_array[data_row]["time_relative"])
                if (float(actual_stop_time_interval) > float(post_trigger_time)+exception_time):
                    assert False, "Unexpected. Measurement didn't stop at correct value and post trigger time, Actual Value - %s with post trigger time - %s. Expected Value - %s and post trigger time - %s."%(actual_stop_value,round(actual_stop_time_interval,3),exp_stop_values[length_exp_values][1],post_trigger_time)
            elif (float(actual_stop_time_interval) < float(post_trigger_time)+exception_time) or (float(actual_stop_time_interval) > float(post_trigger_time)-exception_time):
                logging.info(f'message/signal stop value check and post trigger time check according to trigger passed')
                break
            else:
                assert False, constants.RM_NOT_STARTED_TRIGGER_TIME%(actual_stop_value,round(actual_stop_time_interval,3),exp_stop_values[length_exp_values][1],post_trigger_time)
            data_row-=1

    def trigger_measured_time_check(self,trigger_type,rm_activation_date,vehicle_id,exp_value,trigger_phase,context):
        results=context.measurement_test_result
        message_or_signal_name = exp_value["signalId"] 
        exp_interval = int(exp_value["interval"])*60
        teststep_time_list = []
        r = self.get_vehicle_teststep_id(vehicle_id)
        if r.status_code != requests.codes.ok:
            return r
        element = r.json ()['page']['totalElements']-1
        while (element > 0):
            test_step_id =  r.json()['_embedded']['testSteps'][element]['testStepId']
            test_step_date = r.json()['_embedded']['testSteps'][element]['creationDate']
            test_step_date = test_step_date.split(".")[0]
            test_step_date = test_step_date.replace("Z","")
            test_step_date_format = datetime.datetime.strptime(test_step_date,"%Y-%m-%dT%H:%M:%S")
            diff = test_step_date_format - rm_activation_date 
            total_rm_seconds = int(diff.total_seconds())
            if total_rm_seconds>0:
                teststep_time_list.append(test_step_date_format)
                result = results[test_step_id]
                data_array=result['results']['data']
                if message_or_signal_name in data_array[0].keys():
                    if len(data_array) > 1:
                        logging.info(f'Measurement data is present for message/signal {message_or_signal_name}')
                    else:
                        assert False, f"No data in the measurement for message/signal {message_or_signal_name}"
            element-=1
        list_len = len(teststep_time_list)
        for i in range(1,list_len):
            teststep_time_diff = teststep_time_list[list_len-i] - teststep_time_list[list_len-i-1]
            teststep_time_diff_sec = int(teststep_time_diff.total_seconds())
            logging.info(f'Time difference between test step in seconds is {teststep_time_diff_sec}')
            assert self.api_gen_obj.is_approximately_equal(teststep_time_diff_sec,exp_interval,10),f"Test step time difference does not match with the expected interval, Test step difference: {teststep_time_diff_sec} -> Interval duration: {exp_interval}"

    def convert_to_required_time_format(self,actual_time):
        if actual_time !=0:
            if isinstance(actual_time,str):
                actual_time=actual_time.split("T")
            else:
                actual_time=str(actual_time).split()
            actual_time = actual_time[1].split(".")
            return actual_time[0]
        else:
            return actual_time

    def trigger_measured_timestamp_check(self,exp_result,context):
        start_trigger = exp_result[0]["start_trigger"]
        if start_trigger == "Ignition_on":
            exp_start_time = self.convert_to_required_time_format(context.ignition_on_time)
            exp_stop_time = self.convert_to_required_time_format(context.ignition_off_time)
        elif start_trigger == "Ignition_off":
            exp_start_time = self.convert_to_required_time_format(context.ignition_off_time)
            exp_stop_time = self.convert_to_required_time_format(context.ignition_on_time)
        exp_exception_time = exp_result[0]["exception_time_in_seconds"]
        results = context.measurement_test_result
        measurement_result=len(results)-1
        while measurement_result >= 0:
            if (len(results) > 1 and measurement_result==len(results)-1):
                measurement_result-= 1
                continue
            teststep_id = list(results.keys())[measurement_result]
            measurement_configuration_id = self.get_measurement_config_id_from_teststep_id(teststep_id)
            configuration_type = self.get_measure_config_type(measurement_configuration_id)
            result = results[teststep_id]
            data_array=result['results']['data']
            if len(data_array) > 1:
                actual_start_time = data_array[1]['time_ISO_8601']
                actual_start_time = self.convert_to_required_time_format(actual_start_time)
                actual_stop_time = data_array[len(data_array)-1]['time_ISO_8601']
                actual_stop_time = self.convert_to_required_time_format(actual_stop_time)
                if context.ignition_on_time !=0:
                    start_time_difference_in_seconds = (datetime.datetime.strptime(actual_start_time, '%H:%M:%S') - datetime.datetime.strptime(exp_start_time, '%H:%M:%S')).total_seconds()
                    start_time_difference_in_seconds = start_time_difference_in_seconds+context.pre_trigger
                    assert -1 <= start_time_difference_in_seconds <= (1 + exp_exception_time),f"Ignition on and measurement start time has difference of {start_time_difference_in_seconds} seconds" 
                if configuration_type != "SINGLE_SHOT":     
                    stop_time_difference_in_seconds = (datetime.datetime.strptime(actual_stop_time, '%H:%M:%S') - datetime.datetime.strptime(exp_stop_time, '%H:%M:%S')).total_seconds()
                    stop_time_difference_in_seconds = stop_time_difference_in_seconds-context.pre_trigger
                    assert -1 <= stop_time_difference_in_seconds <= (1 + exp_exception_time),f"Ignition off and measurement stop time has difference of {stop_time_difference_in_seconds} seconds"  
                print("Trigger validation is successfull")
            else:
                assert False, f"No data in the measurement for message/signal"
            measurement_result-= 1

    def trigger_measured_value_check(self,trigger_type, exp_value,trigger_phase,context):
        exp_start_values=exp_value["start_value"]
        exp_stop_values=exp_value["stop_value"]
        message_or_signal_name = exp_value["name"]
        message_or_signal_min = exp_value["min"]
        results=context.measurement_test_result
        pre_trigger_time=context.pre_trigger
        post_trigger_time=context.post_trigger
        actual_length_exp_values=len(exp_start_values)
        length_exp_values=0
        config_data = self.api_gen_obj.parse_json_file(constants.TEST_CONFIG_JSON)
        exception_time = config_data["exception_time"]
        if(trigger_type == "OneTime_Message"):
            exception_time = exception_time + 5
        elif(trigger_type == "SIGNAL_INTERVAL"):
            exception_time = exception_time + 1
        logging.info(f"Exeception time for the given trigger mode is ,{float(exception_time)}")
        pre_or_post_value_none = False
        configuration_type = self.get_measure_config_type(context.measurement_configuration_id)
        if(pre_trigger_time==0 and post_trigger_time==None or configuration_type == 'SINGLE_SHOT'):
            pre_or_post_value_none = True
        
        measurement_result=len(results)-1
        while measurement_result >= 0:
            if (len(results) > 1 and measurement_result==0):
                break
            if (len(results) > 1 and "cycle" in exp_value.keys() and measurement_result== len(results)-1):
                measurement_result-=1
                continue
            teststep_id = list(results.keys())[measurement_result]
            result = results[teststep_id]
            data_array=result['results']['data']

            self.verify_message_or_signal_in_trigger(message_or_signal_name, data_array, exp_value, trigger_phase, pre_or_post_value_none, exp_start_values, length_exp_values, exception_time, pre_trigger_time, post_trigger_time, message_or_signal_min, exp_stop_values)
    
            length_exp_values+=1
            if length_exp_values == actual_length_exp_values:
                length_exp_values = 0
            measurement_result-= 1

    def verify_message_or_signal_in_trigger(self, message_or_signal_name, data_array, exp_value, trigger_phase, pre_or_post_value_none, exp_start_values, length_exp_values, exception_time, pre_trigger_time, post_trigger_time, message_or_signal_min, exp_stop_values):
        if message_or_signal_name in data_array[0].keys():
            if len(data_array) > 1:
                self.monotony_value_check(exp_value,data_array,message_or_signal_name,len(data_array)-1)
                logging.info("CANraw Monotony check and Value check passed.")

                actual_message_start_value = data_array[1][message_or_signal_name]
                if actual_message_start_value is None:
                    actual_message_start_value = data_array[2][message_or_signal_name]
                    if actual_message_start_value is None:
                        actual_message_start_value = data_array[3][message_or_signal_name]

                actual_message_stop_value = data_array[len(data_array)-1][message_or_signal_name]
                if actual_message_stop_value is None:
                    actual_message_stop_value = data_array[len(data_array)-2][message_or_signal_name]
                    if actual_message_stop_value is None:
                        actual_message_stop_value = data_array[len(data_array)-3][message_or_signal_name]

                self.trigger_phase_start_stop(actual_message_start_value, actual_message_stop_value, message_or_signal_name, data_array, trigger_phase, pre_or_post_value_none, exp_start_values, length_exp_values, exception_time, pre_trigger_time, post_trigger_time, message_or_signal_min, exp_stop_values)
            
            else:
                assert False, f"No data in the measurement for message/signal {message_or_signal_name}"
        else:
            assert False, f"message/signal {message_or_signal_name} is not present in measurement"

    def trigger_phase_start_stop(self, actual_message_start_value, actual_message_stop_value, message_or_signal_name, data_array, trigger_phase, pre_or_post_value_none, exp_start_values, length_exp_values, exception_time, pre_trigger_time, post_trigger_time, message_or_signal_min, exp_stop_values):
        if (trigger_phase != "STOP") and pre_or_post_value_none and len(exp_start_values)>0:
            assert actual_message_start_value in exp_start_values[length_exp_values], "Unexpected. Measurement didn't start at correct value, Actual Value - %s. Expected Value - %s."%(actual_message_start_value,exp_start_values[length_exp_values][1])
            logging.info("message start value check according to trigger passed")
        else:
            if(pre_trigger_time!=0):
                self.pre_trigger_check (exception_time,data_array,pre_trigger_time,exp_start_values,length_exp_values,message_or_signal_name,message_or_signal_min)
            if(trigger_phase == "START") and (post_trigger_time!=None):
                self.post_trigger_check (exception_time,data_array,post_trigger_time,exp_start_values,length_exp_values, message_or_signal_name)
                    
        if(trigger_phase != "START") and pre_or_post_value_none and len(exp_stop_values)>0:
            assert actual_message_stop_value in exp_stop_values[length_exp_values], "Unexpected. Measurement didn't stop at correct value, Actual Value - %s. Expected Value - %s."%(actual_message_stop_value,exp_stop_values[length_exp_values][1])
            logging.info("message stop value check according to trigger passed")
        elif(trigger_phase != "START") and len(exp_stop_values)>0:
            self.post_trigger_check (exception_time,data_array,post_trigger_time,exp_stop_values,length_exp_values, message_or_signal_name)
                        
        logging.info(f'message/signal started from {actual_message_start_value} and stoped at {actual_message_stop_value}')

    def get_latest_measurement_config_version(self, measruement_configuration_id):
        r = self.get_measurement_config(measruement_configuration_id)
        return r.json()['version']
    
    def get_measurement_config_upload_interval(self, measruement_configuration_id):
        """
            Fetches Upload interval of measurement configuration
        Args:
            measruement_configuration_id (_type_): measruement_configuration_id
        Returns:
            string: upload interval
        """
        r = self.get_measurement_config(measruement_configuration_id)
        return r.json()['uploadInterval']

    def get_measure_config_messages(self, measurement_configuration_id):

        """ Description     : It fetches the messages associated with a specific Measurement Configuration Id

        Arguments           : measurement_configuration_id - Specific Measurement Configuration Id for which details of Messages is required

        Expected result     : It should fetch the messages for the specified Measurement Configuration Id

        """

        r = self.api_requests.get_request(constants.RM_MEASURE_CONFIG_ID_MSG.format(measurement_configuration_id))
        if "_embedded" not in r.json(): 
            logging.info('No Messages available in this Configuration.')
            return None
        else:
            assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
            return r.json()['_embedded']['selectedMessages']

    def get_measure_config_selected_signals(self, measruement_configuration_id):
        version = self.get_latest_measurement_config_version(measruement_configuration_id)
        r = self.api_requests.get_request(constants.RM_MEASURE_CONFIG_ID_RELEASE_VERSION.format(measruement_configuration_id,version))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r.json()['_embedded']['selectedSignals']
    
    def get_measure_config_calculated_signals(self, measurement_configuration_id):
        r = self.api_requests.get_request(constants.RM_MEASURE_CONFIG_ID_CALCULATED_SIGNALS.format(measurement_configuration_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r.json()['_embedded']['calculatedSignals']

    def get_measure_config_calculated_list_signals(self, measurement_configuration_id):
        r = self.api_requests.get_request(constants.RM_MEASURE_CONFIG_ID_CALCULATED_LIST_SIGNALS.format(measurement_configuration_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r.json()['_embedded']['calculatedListSignals']

    def get_measure_config_type(self, measurement_configuration_id):
        r = self.api_requests.get_request(constants.RM_MEASURE_CONFIG_ID.format(measurement_configuration_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        config_type = r.json()['type']
        logging.info(f'Measurement configuration type is {config_type}')
        return config_type
    
    def get_teststep_from_id(self, teststep_id):
        r = self.api_requests.get_request(constants.RM_TEST_STEPS_ID.format(teststep_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r.json()

    def get_measurement_config_id_from_teststep_id(self, teststep_id):
        mesurement_config_id = self.get_teststep_from_id(teststep_id)['measurementConfiguration']['measurementConfigurationId']
        logging.info(f'Measurement configuration id of teststep {teststep_id} is {mesurement_config_id}')
        return mesurement_config_id

    def verify_encoded_signals_data(self, results,separation_time, rows_to_validate = None, table = None):
        if(separation_time is None):
            separation_time = 0
        self.separation_time = separation_time
        for teststep_id in list(results.keys()):
            result = results[teststep_id]
            data_array=result['results']['data']
            measurement_configuration_id = self.get_measurement_config_id_from_teststep_id(teststep_id)
            selected_signals = self.get_measure_config_selected_signals(measurement_configuration_id)
            if rows_to_validate == None:
                rows_to_validate = len(data_array)-1
            else:
                rows_to_validate = rows_to_validate-1
            assert rows_to_validate > 0, "Unable to verify Value encoded signal, as data is empty in result csv"
            self.encoding_value_check(data_array, table, rows_to_validate)
            for signal in selected_signals:
                down_sampling_rate = signal['downsamplingRate']
                self.canraw_time_check(data_array, signal, down_sampling_rate, rows_to_validate)
            logging.info('Encoding value check passed!')

    def fetch_number_of_rows_to_validate(self, data_array, rows_to_validate):
        if rows_to_validate == None:
            rows_to_validate = len(data_array)-1
        else:
            # For accommodating it in the range() function inside the value and time check function calls which follow
            rows_to_validate = rows_to_validate + 1
            assert rows_to_validate <= (len(data_array) - 1), f'No of data rows is {len(data_array) - 1} but validation requested for {rows_to_validate} rows'
        return rows_to_validate

    def verify_signals_data(self, data_array, measurement_configuration_id,signals_to_be_excluded, number_of_rows_to_validate = None):
        exception_msg_list = []
        selected_signals = self.get_measure_config_selected_signals(measurement_configuration_id)
        rows_to_validate = self.fetch_number_of_rows_to_validate(data_array,number_of_rows_to_validate)
        for signal in selected_signals:
            assert signal['signalName'] in data_array[0].keys(), f"Signal with name {signal['signalName']} not found in headers"
            count_rows_of_signal = self.get_totalrows_recorded_for_measurement_entities(data_array,signal)
            assert count_rows_of_signal !=0, f"No data in the measurement for signal {signal['signalName']}"
            exception_msg_list = self.__verify_all_signals(signal, data_array,measurement_configuration_id,rows_to_validate, signals_to_be_excluded, exception_msg_list)
        assert len(exception_msg_list) == 0, f" {len(exception_msg_list)} of the signals failed in validation are {chr(10)}{exception_msg_list}"

    
    def __verify_all_signals(self, signal, data_array,measurement_configuration_id,rows_to_validate, signals_to_be_excluded, exception_msg_list):
        if(signal["signalType"] in ["SIGNAL","SYSTEM_SIGNAL"]):
            try:
                logging.info(f'Validating signal {signal["signalName"]} ...')
                message = self.__choose_and_validate_signal(signal, data_array, measurement_configuration_id, rows_to_validate)
            except AssertionError as error:
                if not ('No data in the measurement' in str(error) and signal['signalName'].lower() in signals_to_be_excluded):
                    message = error
                logging.warning(f'No data for signal {signal["signalName"]}')
            if message != "":
                exception_msg_list.append(f"{message}")
        elif(signal["signalType"]=="MULTIPLEXED_SIGNAL"):
            try:
                self.validate_multiplexed_signal_data(signal, data_array,measurement_configuration_id,rows_to_validate)
            except AssertionError as error:
                exception_msg_list.append(f"{len(exception_msg_list)+1} {error}")
        return exception_msg_list

    def __choose_and_validate_signal(self, signal, data_array, measurement_configuration_id, rows_to_validate):
        message = ''
        if("voltage" in signal['signalName'].lower()):
            message = self.validate_voltage_data(data_array, signal, measurement_configuration_id, rows_to_validate)
        elif("gps" in signal['signalName'].lower()):
            message = self.validate_gps_data(data_array, signal, measurement_configuration_id, rows_to_validate)
        else:
            message = self.validate_canraw_data(data_array, signal, measurement_configuration_id, rows_to_validate)
        return message

    def get_signal_properties(self, measurement_configuration_id, signal):
        signal_source_id = signal['sourceId']
        signal_id = signal['signalId']
        r = self.api_requests.get_request(constants.RM_MEASURE_CONFIG_ID_SOURCES_ID_SIGNALS_ID.format(measurement_configuration_id,signal_source_id,signal_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        sig_property = r.json()
        return sig_property

    def validate_multiplexed_signal_data(self, signal, data_array, measurement_configuration_id, rows_to_validate):
        logging.info(f"Fetching properties of Multiplexed signal - {signal['signalName']}")
        signal_properties = self.get_signal_properties(measurement_configuration_id, signal)
        message_name =signal_properties["messageName"] #Message_1
        expected_multiplex_value=signal_properties["multiplexValue"] #0
        for i in range(1,rows_to_validate):
            actual_multiplex_value = None
            message_hex = data_array[i][message_name] #0x0010000000000000
            if message_hex is not None:
                actual_multiplex_value = int(message_hex[0:4],16) #0
                message_byte_signal_value = int(message_hex[4:6],16) #16
            if (data_array[i][signal['signalName']] is not None):
                assert actual_multiplex_value == expected_multiplex_value, f"{signal['signalName']} is transmitted when multiplexor signal value is {actual_multiplex_value}, Expected multiplexor value = {expected_multiplex_value} at row {i+3}"
                #Validate signal value with message byte
                assert message_byte_signal_value == data_array[i][signal['signalName']], f"multiplexed signal - {signal['signalName']} has wrong value - {data_array[i][signal['signalName']]}, Expected value = {message_byte_signal_value} at row {i+3}"
            else:
                assert actual_multiplex_value != expected_multiplex_value,f"{signal['signalName']} is not transmitted when multiplexor signal value is {actual_multiplex_value}, Expected multiplexor value = {expected_multiplex_value} at row {i+3}"
        logging.info("perform monotony check for multiplexed signal for first 15 rows")
        self.monotony_value_check(signal_properties, data_array, signal['signalName'], rows_to_validate=15)
        logging.info("Multiplexed signal Monotony check passed.")
        logging.info(f"Multiplexed signal {signal['signalName']} validation check passed !")

    def encoding_value_check(self, data_array, table, rows_to_validate):
        signal_list = table.headings
        no_of_signals = len(signal_list)
        row_data = {}
        verify_from_next_row = False
        for i in range(1,rows_to_validate):
            emptycell_in_row = False
            for item in range(0,no_of_signals):
                if data_array[i][signal_list[item]] is not None:
                    row_data[signal_list[item]] = data_array[i][signal_list[item]]
                else:
                    emptycell_in_row = True

            if(len(row_data) == no_of_signals):
                try:
                    verify_from_next_row = self.__encoded_value_in_row(signal_list, row_data, table, emptycell_in_row, verify_from_next_row, (i+3))
                except (ValueError, TypeError) as e:
                    logging.warning(f"Unable to Process the signal data in the required format at rowNum, {str(i+3)}, verify csv manually , Error: , {str(e)}") 
                    assert False, "Error:On Row Num: " + str(i+3) + " Unable to Process the signal data in the required format, verify csv manually"  
            else:
                logging.info(f"No enough data is available to verify the Encoded value in CSV at Row Num, {str(i+3)}")    

    def __encoded_value_in_row(self,signal_list, row_data, table, emptycell_in_row, verify_from_next_row, row_number):
        signals_to_check = len(signal_list) - 1
        value_verified_flag = False
        encoded_value = row_data[signal_list[signals_to_check]]
        for item in range(0,signals_to_check):
            value=float(row_data[signal_list[item]])
            for row in table:
                value_range = row[signal_list[item]].split("-")
                if(value>= float(value_range[0]) and value<= float(value_range[1]) and encoded_value == row[signal_list[signals_to_check]]):
                    value_verified_flag = True
                    verify_from_next_row = False
                    break
            if (emptycell_in_row and (not value_verified_flag) and (not verify_from_next_row)) :
                verify_from_next_row = True
            else :
                assert value_verified_flag == True, f"At row num:{row_number} Unable to verify the value {value} in specified Encoded value range"
        return verify_from_next_row

    def convert_data_array_from_hex_to_decimal(self,data_array,rows_to_validate,signal_or_message_name):
        for i in range(1,rows_to_validate):
            if(data_array[i][signal_or_message_name]!= None):
                data_array[i][signal_or_message_name] = int(data_array[i][signal_or_message_name], 16)
        return data_array
    
    def convert_data_array_from_decimal_to_hex(self,data_array,rows_to_validate,signal_or_message_name):
        for i in range(1,rows_to_validate):
            if(data_array[i][signal_or_message_name]!= None):
                data_array[i][signal_or_message_name] = hex(data_array[i][signal_or_message_name])
                if(len(data_array[i][signal_or_message_name])<4):
                    data_array[i][signal_or_message_name]=data_array[i][signal_or_message_name][:2]+'0'+data_array[i][signal_or_message_name][2:]
        return data_array

    '''TO DO: RMConfigDetails another parameter that holds trigger configuration, and validation will be around - RMConfigDetails data'''
    def monotony_value_check(self, signal_properties, data_array, signal, rows_to_validate):
        canraw_previous_data = 0
        is_value_in_hex= False
        signal_or_message_name=signal
        condition_gt_lt = operator.lt
        logging.info(f"Verifying Monotony and Measured value for Signal/Message - {signal_or_message_name}")
        if (signal_properties['signalType']=="MESSAGE"):
            is_value_in_hex= True
            start_value = int(signal_properties['min'],16)
            end_value = int(signal_properties['max'],16)
            signal_factor_change = signal_properties['factor']
            data_array= self.convert_data_array_from_hex_to_decimal(data_array,rows_to_validate, signal_or_message_name)
        else:
            start_value = signal_properties['min']
            end_value = signal_properties['max']
            signal_factor_change = signal_properties['factor']

        if (start_value < end_value):
            condition_gt_lt = operator.gt
        
        for i in range(1,rows_to_validate):
            if data_array[i][signal_or_message_name] != None:
                canraw_data_obj = float(data_array[i][signal_or_message_name])
                assert min(start_value, end_value) <= canraw_data_obj <= max(end_value, start_value), f"Actual Measured value-{canraw_data_obj} is out of bound - [{start_value}, {end_value}]"
                
                if (canraw_previous_data!=0):
                    if (canraw_data_obj == start_value):
                        assert abs(canraw_data_obj-canraw_previous_data) == abs(end_value-start_value), f"{signal_or_message_name} is not having correct consucutive recorded value difference. At data row-{i}: Previous Value-{canraw_previous_data} and Current Value-{canraw_data_obj} with factor change of-{signal_factor_change}"
                    else:
                        assert abs(canraw_data_obj-canraw_previous_data) == signal_factor_change, f"{signal_or_message_name} is not having correct consecutive recorded value difference. At data row-{i}: Previous Value-{canraw_previous_data} and Current Value-{canraw_data_obj} with factor change of-{signal_factor_change}"
                        assert condition_gt_lt(canraw_data_obj, canraw_previous_data), f"Wrong monotony of recorded value for signal - {signal_or_message_name}. Previous Value-{canraw_previous_data}, Current Value-{canraw_data_obj}"
                canraw_previous_data = canraw_data_obj

        if is_value_in_hex:
            data_array= self.convert_data_array_from_decimal_to_hex(data_array,rows_to_validate,signal_or_message_name)
                       
    def __get_data_array_having_value_for_signal(self, data_array, measurement_entity):
        ''' From the data_array, only the units object and json objects which don't containt the signal data as null are returned in array format
            Eg.- For signal = S_STD_0x201_S8 in data_array below, data_array[1] won't be included in the return object
                [{
                    "index": 0,
                    "time": "ms",
                    "time_ISO_8601": null,
                    "time_relative": "s",
                    "GPS": null,
                    "S_STD_0x201_S8": null
                },
                {
                    "index": 1,
                    "time": "1602668382966",
                    "time_ISO_8601": "2020-10-14T09:39:42.966Z",
                    "time_relative": "0.746",
                    "GPS": 246.0,
                    "S_STD_0x201_S8": null
                }] '''
        measurement_entity_data_array = [data_array[0]]
        for data in data_array[1:]:
            if 'signalName' in measurement_entity:
                entity_name = 'signalName'
            else:
                entity_name = 'name'
            if data[measurement_entity[entity_name]] != None:
                measurement_entity_data_array.append(data)
        return measurement_entity_data_array

    def set_time_stamp_rate (self, down_sampling_rate,signal_properties):
        separation_time=self.separation_time
        if separation_time == 'highloadidents':
            try:
                signal_id = hex(signal_properties['_embedded']['parentMessage']['canId'])
                if signal_id[:4]=="0x81":
                    separation_time = 100
                elif signal_id[:3]=="0x2":
                    separation_time = 200
            except TypeError as e:
                logging.info(f"Unable to find CAN ID from property {e}, choosing default seperation time as 100")
                separation_time = 100
        if down_sampling_rate == 0:
            time_stamp_rate = separation_time
        elif down_sampling_rate >= float(separation_time):
            time_stamp_rate = down_sampling_rate
        else:
            time_stamp_rate = separation_time
        return time_stamp_rate

    def canraw_time_check(self, data_array, measurement_entity, down_sampling_rate, rows_to_validate,signal_properties=None):
        exception_message = ''
        previous_time_stamp=0
        time_stamp_rate= self.set_time_stamp_rate(down_sampling_rate,signal_properties) 
        if 'signalName' in measurement_entity:
            entity_name = 'signalName'
        else:
            entity_name = 'name'
        for i in range(1,rows_to_validate):
            if data_array[i][measurement_entity[entity_name]] != None:
                if previous_time_stamp !=0 :
                    btimestamp_valid = self.api_gen_obj.is_approximately_equal(float(time_stamp_rate), (float(data_array[i]['time_relative'])- previous_time_stamp)*1000, 20)
                    if not btimestamp_valid:
                        exception_message = f" {measurement_entity[entity_name]} ->  Timestamp check failed at index :{i} , Actual time difference: {(float(data_array[i]['time_relative'])- previous_time_stamp)*1000}, expected time difference is {time_stamp_rate} in ms"
                        break
                previous_time_stamp = float(data_array[i]['time_relative'])
        return exception_message

    def validate_canraw_data(self, data_array, signal, measurement_configuration_id, rows_to_validate):
        exception_msg = ''
        logging.info(f"Fetching properties of CANraw signal - {signal['signalName']}")
        configuration_type = self.get_measure_config_type(measurement_configuration_id)
        signal_properties = self.get_signal_properties(measurement_configuration_id, signal)
        if configuration_type == "CONTINUOUS":
            down_sampling_rate = signal['downsamplingRate']
            if down_sampling_rate == 0:
                self.monotony_value_check(signal_properties, data_array, signal['signalName'], rows_to_validate)
                logging.info("CANraw Monotony check and Value check passed.")

            logging.info("Validating Timestamp of CANraw signal's measure data...")
            exception_msg = self.canraw_time_check(data_array, signal, down_sampling_rate, rows_to_validate,signal_properties)
        elif configuration_type == "SINGLE_SHOT":
            # 1st row contains units; actual data starts from 2nd row
            signal_data_array = self.__get_data_array_having_value_for_signal(data_array, signal)
            assert len(signal_data_array) == 2, f"Measurement for signal {signal['signalName']} has {len(signal_data_array)} data while expected to be 2"
            logging.info("CANraw index check passed.")
            signal_start_value = signal_properties['min']
            signal_end_value = signal_properties['max']
            canraw_data_obj = float(signal_data_array[1][signal['signalName']])
            assert min(signal_start_value, signal_end_value) <= canraw_data_obj <= max(signal_end_value, signal_start_value), f"Actual Measured value-{canraw_data_obj} is out of bound - [{signal_start_value}, {signal_end_value}]"
            logging.info("CANraw value check passed.")
        else:
            assert False, f'Measurement configuration type {configuration_type} is not valid!'
        return exception_msg

    def voltage_value_check(self, data_array, signal, default_voltage, rows_to_validate):
        exception_msg = ''
        ''' TO-DO : Make the range as "(1,len(data_array)-1)" after defect is fixed '''
        for i in range(2,rows_to_validate):
            if data_array[i][signal['signalName']] != None and int(data_array[i][signal['signalName']]) not in default_voltage:
                exception_msg = f" {signal['signalName']} ->  Data Integrity test failed at index :{i} , time : {data_array[i]['time_ISO_8601']} and value : {data_array[i][signal['signalName']]} but expected value was : {default_voltage}"
                break
        return exception_msg

    def validate_voltage_data(self, data_array, signal, measurement_configuration_id, rows_to_validate):
        exception_msg = ''
        exception_msg1 = ''
        default_voltage = range(12,25)
        logging.info("Verifying Voltage details")
        configuration_type = self.get_measure_config_type(measurement_configuration_id)
        assert signal['signalName'] in data_array[0].keys(), f"Signal with name {signal['signalName']} not found in headers"
        if('unit' in signal.keys() and signal['unit'] != ''):
            assert signal['unit'] == data_array[0][signal['signalName']], f"Unit is matching for signal {signal['signalName']} : {signal['unit']}"
        if configuration_type == "CONTINUOUS":
            down_sampling_rate = signal['downsamplingRate']
            exception_msg = self.voltage_value_check(data_array, signal, default_voltage, rows_to_validate)
            exception_msg1 = self.canraw_time_check(data_array, signal, down_sampling_rate, rows_to_validate)
            if exception_msg1 != '':
                if exception_msg == '':
                    exception_msg = exception_msg1
                else:
                    exception_msg = exception_msg + exception_msg1
        elif configuration_type == "SINGLE_SHOT":
            # 1st row contains units; actual data starts from 2nd row
            signal_data_array = self.__get_data_array_having_value_for_signal(data_array, signal)
            assert len(signal_data_array) == 2, f"Measurement for signal {signal['signalName']} has {len(signal_data_array)} data while expected to be 2"
            logging.info("Voltage signal index check passed.")
            canraw_data_obj = signal_data_array[1][signal['signalName']]
            assert int(canraw_data_obj) in default_voltage , f'Actual Measured value-{canraw_data_obj} is out of approximation range with voltage value-{default_voltage}'
            logging.info("Voltage value check passed.")
        else:
            assert False, f'Measurement configuration type {configuration_type} is not valid!'
        return exception_msg

    def gps_value_time_check(self, data_array, signal, down_sampling_rate, rows_to_validate):
        exception_msg = ''
        latitude_value = 0.0000
        for i in range(1,rows_to_validate):
                if data_array[i][signal['signalName']] != None:
                    gps_data_obj = data_array[i][signal['signalName']]
                    new_latitude_value = gps_data_obj[gps_data_obj.index("latitude=")+9:gps_data_obj.index("elevation=")-1]
                    new_latitude_value = round(float(new_latitude_value), 4)
                    if latitude_value != 0 and latitude_value != new_latitude_value and round(abs(latitude_value - new_latitude_value), 3) != round(0.008983, 3):
                        exception_msg = f"{signal['signalName']} ->  Data Integrity test failed at time : {data_array[i]['time_ISO_8601']} and at index :{i}, value : {data_array[i][signal['signalName']]} ; previous index :{i-1}, value : {data_array[i-1][signal['signalName']]}"
                        break
                    latitude_value = new_latitude_value
                    
                    if (i > 1) and not self.api_gen_obj.is_approximately_equal(down_sampling_rate, (float(data_array[i]['time_relative'])- float(data_array[i-1]['time_relative'])), 500):
                        exception_msg = f" {signal['signalName']} ->  Timestamp check failed at index :{i} , time : {data_array[i]['time_ISO_8601']} and values : {data_array[i]['time_relative']}, {data_array[i-1]['time_relative']}"
                        break
        return exception_msg

    def validate_gps_data(self, data_array, signal, measurement_configuration_id, rows_to_validate):
        exception_msg = ''
        logging.info("Verifying GPS details")
        configuration_type = self.get_measure_config_type(measurement_configuration_id)
        assert signal['signalName'] in data_array[0].keys(), f"Signal with name {signal['signalName']} not found in headers"
        if('unit' in signal.keys() and signal['unit'] != ''):
            assert signal['unit'] == data_array[0][signal['signalName']], f"Unit is matching for signal {signal['signalName']} : {signal['unit']}"
        if configuration_type == "CONTINUOUS":
            if signal['downsamplingRate'] == 0:
                down_sampling_rate = 5
            else:
                down_sampling_rate = signal['downsamplingRate']
            exception_msg = self.gps_value_time_check(data_array, signal, down_sampling_rate, rows_to_validate)
        elif configuration_type == "SINGLE_SHOT":
            # 1st row contains units; actual data starts from 2nd row
            signal_data_array = self.__get_data_array_having_value_for_signal(data_array, signal)
            assert len(signal_data_array) == 2, f"Measurement for signal {signal['signalName']} has {len(signal_data_array)} data while expected to be 2"
            logging.info("GPS signal index check passed.")
        else:
            assert False, f'Measurement configuration type {configuration_type} is not valid!'
        return exception_msg

    def find_signal_rectify_downsampling(self, signal_id, source_id, signal_collection_id, measurement_configuration_id, selected_signals, signal_downsampling):
        signal_found = False
        for selected_signal in selected_signals:
            if signal_id == selected_signal['signalId'] and signal_collection_id == selected_signal['signalCollectionId']:
                signal_found = True
                if signal_downsampling == "":
                    signal_downsampling = "0"
                if signal_downsampling == str(selected_signal['downsamplingRate']):
                    logging.info(f'No modification to signal required')
                else:
                    self.edit_signal_downsampling_rate(measurement_configuration_id, source_id, signal_id, signal_downsampling)
        return signal_found

    def remove_calculated_signals(self, measurement_configuration_id, selected_calculated_signals):
        self.set_measurement_configuration_state(measurement_configuration_id, "draft")
        for calculated_signal in selected_calculated_signals:
            if calculated_signal['name'] != 'Matrix_operator':
                calculated_signal_id=calculated_signal['signalId']
                etag = self.api_requests.get_etag(constants.RM_MEASURE_CONFIG_ID.format(measurement_configuration_id))
                r = self.api_requests.delete_request(constants.RM_MEASURE_CONFIG_ID_CALCULATED_SIGNAL_ID.format(measurement_configuration_id, calculated_signal_id), {'if-match': etag})
                assert r.status_code == requests.codes.no_content, self.api_gen_obj.assert_message(r)
                logging.info(f'Calculated signal is removed from measurement configuration')
       
    def get_recorded_time(self, result):
        data_array = result["results"]['data']
        no_of_rows = len(data_array)
        try:
            start_time = parser.parse(data_array[1]["time_ISO_8601"])
            end_time = parser.parse(data_array[no_of_rows - 1]["time_ISO_8601"])
            logging.info(f"Record Start time = ,{start_time}")
            logging.info(f"Record Stop time = , {end_time}")
            total_time = end_time - start_time
            time_in_sec = total_time.seconds
            return time_in_sec
        except IndexError: return None
        

    def get_measurement_assignment_details(self, vehicle_id, measurement_id, slot_name):
        r = self.api_requests.get_request(constants.RM_VEHICLES_ID_ASSIGNMENTS.format(vehicle_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        assignment_details = self.get_measurement_assignment(r, slot_name, measurement_id)
        assert assignment_details is not None, f"Unable to find Measurement details for vehicleId:{vehicle_id} on device slot {slot_name}"
        return assignment_details

    def trigger_measurement_assignment_deactivation(self, vehicle_id, slot_name, assignment_id):
        etag = self.api_requests.get_etag(constants.RM_VEHICLES_ID.format(vehicle_id))
        r = self.api_requests.put_request(constants.RM_VEHICLES_ID_DEVICESLOTS_NAME_ASSIGNMENTS_ID_DEACTIVATE.format(
            vehicle_id, slot_name, assignment_id), params={}, custom_header={'if-match': etag})
        assert r.status_code == requests.codes.no_content, self.api_gen_obj.assert_message(r)
        return True

    def trigger_measurement_assignment_activation(self, vehicle_id, slot_name, measurement_id):
        data = { "measurementConfigurationId": measurement_id}
        etag = self.api_requests.get_etag(constants.RM_VEHICLES_ID.format(vehicle_id))
        r = self.api_requests.post_request(constants.RM_VEHICLES_ID_DEVICESLOTS_NAME_ASSIGNMENTS.format(vehicle_id, slot_name), params=data, custom_header={'if-match': etag})
        assert r.status_code == requests.codes.created, self.api_gen_obj.assert_message(r)

    def trigger_measurement_assignment_reactivation(self, vehicle_id, slot_name, assignment_id):
        etag = self.api_requests.get_etag(constants.RM_VEHICLES_ID_ASSIGNMENT.format(vehicle_id))
        r = self.api_requests.put_request(constants.RM_VEHICLES_ID_DEVICESLOTS_NAME_ASSIGNMENTS_ID_ACTIVATE.format(vehicle_id, slot_name, assignment_id), params={}, custom_header={'if-match': etag})
        assert r.status_code == requests.codes.no_content, self.api_gen_obj.assert_message(r)
        return True

    def get_latest_assignment_job_id(self, vehicle_id, slot_name):
        r = self.api_requests.get_request(constants.RM_VEHICLES_ID_ASSIGNMENT.format(vehicle_id))
        assignment_job_id = None
        if '_embedded' in r.json():
            for assignment in r.json()['_embedded']['assignments']:
                if assignment['deviceSlotName'] == slot_name:
                    assignment_job_id = assignment['mc2SlotAssignmentId']
                    break
        else:
            assert False, constants.RM_NO_JOBID_AVAILABLE
        logging.info(f'Latest measuremnt job ID for vehicle {vehicle_id} and device slot {slot_name} is {assignment_job_id}')
        return assignment_job_id

    def find_message_rectify_downsampling(self, message_id, source_id, signal_collection_id, measurement_configuration_id, selected_messages, message_downsampling):
        message_found = False
        for selected_message in selected_messages:
                if message_id == selected_message['messageId'] and signal_collection_id == selected_message['signalCollectionId']:
                    message_found = True
                    if message_downsampling == "":
                        message_downsampling = "0"
                    if message_downsampling == str(selected_message['downsamplingRate']):
                        logging.info(f'No modification to message required')
                    else:
                        self.edit_message_downsampling_rate(
                            measurement_configuration_id, source_id, message_id, message_downsampling)
        return message_found

    def get_slot_with_pending_rm_assignment(self, vehicle_id):
        slotlist = []
        self.api_gen_obj = API_Generic_Class.ApiGenericClass()
        r = self.api_requests.get_request(constants.RM_VEHICLES_ID_ASSIGNMENTS.format(vehicle_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        if '_embedded' in r.json() and r.json()['_embedded']['assignments'] is not None:
            for assignment in r.json()['_embedded']['assignments']:
                if(assignment['currentStatus'] != "INACTIVE" or 
                    assignment['targetStatus'] != "INACTIVE") and assignment['deviceSlotName'] not in slotlist:
                    slotlist.append(assignment['deviceSlotName'])
        return slotlist

    def trigger_vsg_measurement_activation(self, vsg_id, slot_name, measurement_id):
        data = { "measurementConfigurationId": measurement_id}
        etag = self.api_requests.get_etag(constants.RM_VSG_ID.format(vsg_id))
        r = self.api_requests.post_request(constants.RM_VSG_ID_DEVICESLOTS_NAME_ASSIGNMENTS.format(vsg_id, slot_name), params=data, custom_header={'if-match': etag})
        assert r.status_code == requests.codes.created, self.api_gen_obj.assert_message(r)

    def get_vsg_rm_assignment_detail(self, vsg_id, measurement_id, slot_name):
        self.api_gen_obj = API_Generic_Class.ApiGenericClass()
        r = self.api_requests.get_request(constants.RM_VSG_ID_ASSIGNMENTS.format(vsg_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return self.get_measurement_assignment(r, slot_name, measurement_id)

    def get_measurement_assignment(self, r, slot_name, measurement_id):
        assignment_details = None
        if '_embedded' in r.json() and r.json()['_embedded']['assignments'] is not None:
            for assignment in r.json()['_embedded']['assignments']:
                if(assignment['deviceSlotName'] == slot_name and 
                    assignment['_embedded']['releasedMeasurementConfiguration']['measurementConfigurationId'] == measurement_id):
                    assignment_details = assignment
                    break
        return assignment_details

    def trigger_vsg_rm_deactivation(self, vsg_id, slot_name, measurement_id):
        etag = self.api_requests.get_etag(constants.RM_VSG_ID.format(vsg_id))
        r = self.api_requests.put_request(constants.RM_VSG_ID_DEVICESLOTS_NAME_ASSIGNMENTS_ID_DEACTIVATE.format(
            vsg_id, slot_name, measurement_id), params={}, custom_header={'if-match': etag})
        assert r.status_code == requests.codes.no_content, self.api_gen_obj.assert_message(r)

    def verify_status_sync_progress_for_vsg(self, exp_statistic_value, vsg_id, measurement_id, slot_name):
        self.api_gen_obj = API_Generic_Class.ApiGenericClass()
        assignment = None
        self.api_gen_obj.start_timer()
        actual_statistic_value = {}
        while(self.api_gen_obj.check_timer() == True):
            r = self.api_requests.get_request(constants.RM_VSG_ID_ASSIGNMENTS.format(vsg_id))
            assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
            for value in exp_statistic_value.keys():
                assignment = self.get_measurement_assignment(r, slot_name, measurement_id)
                assignment = assignment['_embedded']['assignmentStatistics']
                actual_statistic_value[value] = assignment[value]
            if exp_statistic_value == actual_statistic_value:
                logging.info("Vehicle setup group sync bar has expected statistical value")
                self.api_gen_obj.stop_timer()
                break
            time.sleep(10)

        if(self.api_gen_obj.check_timer() == False):
            assert exp_statistic_value == actual_statistic_value, f'Expected {exp_statistic_value} but actual - {actual_statistic_value}'

    def trigger_vsg_rm_reactivation(self, vsg_id, slot_name, assignment_id):
        etag = self.api_requests.get_etag(constants.RM_VSG_ID.format(vsg_id))
        r = self.api_requests.put_request(constants.RM_VSG_ID_DEVICESLOTS_NAME_ASSIGNMENTS_ID_ACTIVATE.format(vsg_id, slot_name, assignment_id), params={}, custom_header={'if-match': etag})
        assert r.status_code == requests.codes.no_content, self.api_gen_obj.assert_message(r)

    def get_rm_vsg_target_status(self, exp_state, vsg_id, measurement_id, slot_name):
        r = self.api_requests.get_request(constants.RM_VSG_ID_ASSIGNMENTS.format(vsg_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        assignment = self.get_measurement_assignment(r, slot_name, measurement_id)
        target_status = assignment['targetStatus']
        assert exp_state == target_status, f'Expected status is {exp_state} but actual status is {target_status}'
        return target_status
        
    def get_test_step_id_info(self,teststep_id,trigger_phases,status):
        trigger_phase_list = trigger_phases.split(',')
        for trigger_phase in trigger_phase_list:
            r = self.api_requests.put_request(constants.RM_TEST_STEPS_ID_TRIGGER_REASON.format(teststep_id,trigger_phase), params={})
            if status == "SUCCESS":
                assert r.status_code == requests.codes.accepted, self.api_gen_obj.assert_message(r)
            elif status == "FAILURE":
                assert r.status_code == requests.codes.precondition_failed, self.api_gen_obj.assert_message(r)
            time.sleep(5)
        test_step_id_info = self.api_requests.get_request(constants.RM_TEST_STEPS_ID.format(teststep_id))
        assert test_step_id_info.status_code == requests.codes.ok, self.api_gen_obj.assert_message(test_step_id_info)
        return test_step_id_info

    def measurement_start_or_stop_reason_check(self,expected_reason,trigger_condition_name,test_step_ids_info,index = 1):
        if expected_reason in ['DRIVE_CYCLE_START', 'START_TRIGGER', 'JOB_INSTALLATION']:
            trigger_start_stop_reason_var = ["startReasonInformation", "start_trigger_condition"]
        else :
            trigger_start_stop_reason_var = ["stopReasonInformation", "stop_trigger_condition"]
        for key,value in test_step_ids_info.items():
            if expected_reason == '':
                start_or_stop_reason_info = value['response'][trigger_start_stop_reason_var[0]]
                for key, val in start_or_stop_reason_info.items():
                    assert key != 'reason', 'Failed : Measurement should not have a reason but it has measurement reason as '  + val
                logging.info('No measurement reason available as expected')
            else :
                start_or_stop_reason_info = value['response'][trigger_start_stop_reason_var[0]]['reason']
                assert start_or_stop_reason_info == expected_reason, "Unexpected. Measurement reason is wrong, Actual Value - %s. Expected Value - %s."%(start_or_stop_reason_info,expected_reason)
                logging.info(f"measurement reason check passed, Reason -  {start_or_stop_reason_info}")
                if("TRIGGER" in expected_reason):
                    logging.info('Measurement reason has Triggers. Fetching trigger details')
                    json_data = self.api_gen_obj.parse_json_file(constants.RM_TRIGGER_JSON)
                    operator_type = value['response'][trigger_start_stop_reason_var[0]]['startStopTrigger']['operatorType']
                    exe_start_or_stop_condition_info,index = self.fetch_exe_start_or_stop_condition(operator_type,json_data,trigger_condition_name,trigger_start_stop_reason_var,index)
                    actual_start_or_stop_condition_info = value['response'][trigger_start_stop_reason_var[0]]['startStopTrigger']
                    self.measurement_result_condition_check(actual_start_or_stop_condition_info,exe_start_or_stop_condition_info)

    def fetch_exe_start_or_stop_condition(self,operator_type,json_data,trigger_condition_name,trigger_start_stop_reason_var,index):
        if operator_type == 'AND':
            exe_start_or_stop_condition_info = json_data['triggerTestData'][trigger_condition_name]['Enrich_RM_Reason_Validation'][trigger_start_stop_reason_var[1]]
        elif operator_type == 'OR':
            exe_start_or_stop_condition_info = json_data['triggerTestData'][trigger_condition_name]['Enrich_RM_Reason_Validation'][trigger_start_stop_reason_var[1]+'_'+str(index)]
            index += 1
        return exe_start_or_stop_condition_info,index

    def measurement_result_condition_check(self,actual_start_or_stop_condition_info,exe_start_or_stop_condition_info):
        expected_trigger_condition = ''
        for key, val in actual_start_or_stop_condition_info.items():
            if key == 'name':
                logging.info('Fetching expected trigger condition value for "' + val + '"')
                expected_trigger_condition = exe_start_or_stop_condition_info[val]
                logging.info('Expected trigger condition value for "' + val + '"' + ' is ' + expected_trigger_condition)
            elif key == 'triggerFired':
                logging.info('Validating measurement trigger condition value')
                assert val == expected_trigger_condition, "Unexpected. Measurement trigger condition is wrong, Actual Value - %s. Expected Value - %s."%(val,expected_trigger_condition)
                logging.info('Success : Measurement trigger condition has expected value')    
            elif isinstance(val,dict):
                self.call_measurement_result_condition_check(val,exe_start_or_stop_condition_info)
            elif isinstance(val, list):
                for item in val:
                    self.call_measurement_result_condition_check(item,exe_start_or_stop_condition_info)

        return exe_start_or_stop_condition_info

    def call_measurement_result_condition_check(self, val,exe_start_or_stop_condition_info):
        r_data = self.measurement_result_condition_check(val,exe_start_or_stop_condition_info)
        if r_data is None: 
            return None
    
    def get_assignment_job_details(self, vehicle_id, assignment_job_id):
        rm_assignment_details = None
        r = self.api_requests.get_request(constants.RM_VEHICLES_ID_ASSIGNMENT.format(vehicle_id))
        if r.json()['_embedded']['assignments'] is not None:
            for assignment in r.json()['_embedded']['assignments']:
                if assignment['mc2SlotAssignmentId'] == assignment_job_id:
                    rm_assignment_details = assignment
                    break
        else:
            assert False, constants.RM_NO_JOBID_AVAILABLE
        logging.debug(f'Latest measuremnt job ID for vehicle {vehicle_id} and device slot is {assignment_job_id}')
        return rm_assignment_details

    def verify_gps_and_trip_distance(self, results, geo_status, new_trip = False):      
        for teststep_id in list(results.keys()):
            result = results[teststep_id]
            data_array = result['results']['data']
            measurement_configuration_id = self.get_measurement_config_id_from_teststep_id(teststep_id)
            selected_signals = self.get_measure_config_selected_signals(measurement_configuration_id)
            assert len(data_array) > 1, f"No data in the measurement for selected signals, measurement data is empty"
            processed_data = self.__process_gps_data(data_array,selected_signals)
            self.__verify_geo_data(processed_data,selected_signals,geo_status,new_trip)
            
    def __process_gps_data (self, data_array, selected_signals):
        processed_data = []
        relative_time = 0
        rows_to_validate = self.fetch_number_of_rows_to_validate(data_array,None)
        data_at_time = {}
        for i in range (1, rows_to_validate):
            if(float(data_array[i]['time_relative']) > relative_time + 3 or relative_time== 0):
                if(len(data_at_time)!=0):
                    processed_data.append(data_at_time)
                relative_time = float(data_array[i]['time_relative'])
                data_at_time = {}
                data_at_time['time_relative'] = relative_time
                data_at_time['time_ISO_8601'] = data_array[i]['time_ISO_8601']
            for signal in selected_signals:
                if data_array[i][signal['signalName']]!= None:
                    data_at_time[signal['signalName']] = data_array[i][signal['signalName']]
        return processed_data
    
    def __verify_geo_data(self, processed_data, selected_signals,geo_status, new_trip):
        exception_msg_list = []
        self.trip_distance_value = None
        exception_msg_list = self.__gps_signal_time_check(processed_data,selected_signals)
        for gps_data in processed_data:
            vehicle_geo_status = self.__get_vehicle_gps_status(geo_status,gps_data['time_ISO_8601'])
            if(vehicle_geo_status == "DISABLED"):
                assert len(gps_data) == 3, "Unexpected Data is getting generated when GPS was disabled"
            else:
                try:
                    if gps_data['GPSFix'] == 3:
                        exception_msg_list.extend(self.__verify_gps_data_by_row(selected_signals,gps_data,new_trip))
                except KeyError as err:
                    if(vehicle_geo_status != "TRANSIENT"):
                        exception_msg_list.append(f"At time: {gps_data['time_relative']} {err} parameter is missing in the measurement")
        if len(exception_msg_list) > 0:
            mismatch_count = len([s for s in exception_msg_list if "value mismatch" in s])
            time_check_fail_count = len([s for s in exception_msg_list if "Timestamp check failed" in s])
            trip_distance_fail_count = len([s for s in exception_msg_list if "Trip distance value" in s])
            missing_sample_count =  len([s for s in exception_msg_list if "sample is missing for Signal" in s]) + len([s for s in exception_msg_list if "parameter is missing" in s])
            logging.info(f"Error Details in GPS Validation {exception_msg_list}")  
            assert False, f"GPS Data verification is Falied due following issues, scalar data mismatch: {mismatch_count}, Downsampling time check fail: {time_check_fail_count}, trip distance check fail: {trip_distance_fail_count} and data sample is missing: {missing_sample_count}"
    
    def __get_vehicle_gps_status(self, geo_status, iso_time):
        vehicle_status = "TRANSIENT"
        time_delta = datetime.timedelta(0, 10)
        time_to_check = parser.parse((iso_time).replace('Z',""))
        for change_time, status in geo_status.items():
            time = parser.parse(change_time)
            if(time_to_check > time + time_delta):
                vehicle_status = status
            elif(time_to_check > time):
                vehicle_status = "TRANSIENT"
            else:
                break
        return vehicle_status

    def __gps_signal_time_check(self, data_array, selected_signals):
        exception_msg_list = []
        rows_to_validate = self.fetch_number_of_rows_to_validate(data_array, None)
        for signal in selected_signals:
            if signal['downsamplingRate'] == 0:
                down_sampling_rate = 10
            else:
                down_sampling_rate = signal['downsamplingRate']/ 1000
            for i in range(1, rows_to_validate):
                if(signal['signalName'] in data_array[i] and signal['signalName'] in data_array[i-1]):
                    btimestamp_valid = self.api_gen_obj.is_approximately_equal(down_sampling_rate, (float(data_array[i]['time_relative'])- float(data_array[i-1]['time_relative'])), 20)
                    if not btimestamp_valid:
                        exception_msg_list.append(f" {signal['signalName']} ->  Timestamp check failed at index :{i} , time : {data_array[i]['time_ISO_8601']} and values : {data_array[i]['time_relative']}, {data_array[i-1]['time_relative']}")
                        break
                elif(signal['signalName']=='GPSFix'):
                    exception_msg_list.append(f" {signal['signalName']} ->  Timestamp check failed at index :{i} , time : {data_array[i]['time_ISO_8601']} and values : {data_array[i]['time_relative']}, {data_array[i-1]['time_relative']}")
        return exception_msg_list

    def __verify_trip_distance_data(self, trip_distance_recorded, previous_value, new_trip):
        self.trip_distance_value = trip_distance_recorded
        if previous_value is None:
            if new_trip:
                assert trip_distance_recorded == 0, f"Trip distance value didn't start from 0, initial value displayed is {trip_distance_recorded}"
            else:
                assert trip_distance_recorded >= 0, "Initial Trip Distance value is not greater than or equal to 0"
        else:
            assert 0 <= (trip_distance_recorded - previous_value) < 50, f"Trip distance value is not varying as expected from {previous_value} and {trip_distance_recorded}" 

    def __verify_gps_data_by_row(self, selected_signals, gps_data,new_trip):
        gps_string_data = {}
        exception_msg_list = []
        gps_string_data['GPSLatitude'] = re.search('latitude=([^\s]+)', gps_data['GPS']).group(1)
        gps_string_data['GPSLongitude'] = re.search('longitude=([^\s]+)', gps_data['GPS']).group(1)
        gps_string_data['GPSAltitude'] = re.search('elevation=([^\s]+)', gps_data['GPS']).group(1)
        gps_string_data['GPSHeading'] = re.search('direction=([^\s]+)', gps_data['GPS']).group(1)
        gps_string_data['GPSSpeed'] = re.search('gpsSpeed=([^\s]+)', gps_data['GPS']).group(1)
        for signal in selected_signals:
            try:
                if signal['signalName'] == "GPSTripDistance":
                    self.__verify_trip_distance_data(float(gps_data['GPSTripDistance']),self.trip_distance_value,new_trip)
                elif signal['signalName'] in ("GPSFix", "GPS"):
                    continue
                else:
                    assert round(float(gps_string_data[signal['signalName']]), 10) == float(gps_data[signal['signalName']]), f"Signal value mismatch for {signal['signalName']}, data in GPS struct: {round(float(gps_string_data[signal['signalName']]), 10)} but as Scalar: {gps_data[signal['signalName']]}"
            except AssertionError as error:
                exception_msg_list.append(f"At time: {gps_data['time_relative']} {error}")
            except KeyError as e:
                exception_msg_list.append(f"At time: {gps_data['time_relative']} sample is missing for Signal: {e}")
        return exception_msg_list

    def set_rm_start_or_end_time(self, exp_state, substate, assignment_job_id, context):
        if exp_state == "ACTIVE" and substate != "IN_DEACTIVATION":
            context.all_assignment_jobs[assignment_job_id]['measurement_start_time'] = datetime.datetime.now(datetime.timezone.utc)
            context.all_assignment_jobs[assignment_job_id]['status'] = "active"
            context.rm_activation_status = True
        elif exp_state == "INACTIVE":
            context.all_assignment_jobs[assignment_job_id]['measurement_end_time'] = datetime.datetime.now(datetime.timezone.utc)
            context.all_assignment_jobs[assignment_job_id]['status'] = "inactive"
        elif exp_state == "ASSIGNED" and hasattr(context, 'rm_activation_status') and context.rm_activation_status == True :
            context.all_assignment_jobs[assignment_job_id]['end_time'] = datetime.datetime.now(datetime.timezone.utc)

    def rm_status_check(self,exp_state,substate,target_status,timer,measurement_config_id, assignment_job_id, context):
        if(timer is not None):
            self.api_gen_obj.update_timeout_time(int(timer)*60)
        assignment_details = self.fetch_assignment_details_of_exp_status(measurement_config_id, assignment_job_id, exp_state, substate, context)
        assert assignment_details['currentStatus'].strip() == exp_state, "Unexpected RM configuration status appeared, Expected status is " + exp_state + ", but current status is " + assignment_details['currentStatus']
        if (substate is not None):
            assert assignment_details['currentSubstatus'].strip() == substate, "Unexpected RM configuration sub-status appeared, Expected sub-status is " + substate + ", but current sub-status is " + assignment_details['currentSubstatus']
        if (target_status is not None):
            assert assignment_details['targetStatus'].strip() == target_status, "Unexpected RM configuration target status appeared, Expected target status is " + target_status + ", current target status is " + assignment_details['targetStatus']

    def get_rm_assignment_details(self, measurement_config_id, vehicle_id, device_slot_name=None, assignment_job_id=None):
        """Fetch assignment details using given measurement_config_id or assignment_job_id
        Args:
            measurement_config_id (str): id of a measurement configuration
            vehicle_id (str): id of a vehicle
            device_slot_name (str): name of a device slot in a vehicle
            assignment_job_id (str): assignement id of a meaurement job on a vehicle
        """
        if measurement_config_id is not None:
            assignment_details = self.get_measurement_assignment_details(vehicle_id, measurement_config_id, device_slot_name)
        if assignment_job_id is not None:
            assignment_details = self.get_assignment_job_details(vehicle_id, assignment_job_id)
        return assignment_details
    
    def fetch_assignment_details_of_exp_status(self, measurement_config_id, assignment_job_id, exp_state, substate, context):
        self.api_gen_obj.start_timer()
        timer_check_value = 180
        while (self.api_gen_obj.check_timer() == True):
            assignment_details = self.get_rm_assignment_details(measurement_config_id, context.vehicle_id, context.device_slot_name, assignment_job_id)
            if(assignment_details['currentStatus'].strip() == exp_state):
                self.api_gen_obj.stop_timer()
                if assignment_job_id is None:
                    assignment_job_id = assignment_details['mc2SlotAssignmentId']
                self.set_rm_start_or_end_time(exp_state, substate, assignment_job_id, context)
                break
            elif('currentSubstatus' in assignment_details and (assignment_details['currentSubstatus'].strip() == "DEACTIVATION_FAILED"  or assignment_details['currentSubstatus'].strip() == ("ACTIVATION_FAILED"))):
                self.api_gen_obj.stop_timer()
                assert False, "Activation or Deactivation of the RM configuration is failed, current sub status is " + assignment_details['currentSubstatus']
            if self.api_gen_obj.fetch_time_difference(self.api_gen_obj.timer_start_time) > timer_check_value :
                assert assignment_details['currentSubstatus'].strip() in ["IN_ACTIVATION","IN_DEACTIVATION"],f"RM configuration is not in expected status {exp_state} and also not in IN_ACTIVATION or IN_DEACTIVATION status after {self.api_gen_obj.fetch_time_difference(self.api_gen_obj.timer_start_time)} sec"
                measurement_job_id = self.get_latest_measurement_job_id(context.vehicle_id,context.device_slot_name)
                self.retry_rm_activation_deactivation(3,context.vehicle_id, measurement_job_id)
                timer_check_value += timer_check_value
            time.sleep(5)
        return assignment_details

    def remove_unwanted_signal_from_config(self, measurement_configuration_id, actual_signals, signal_array):
        updated_selected_signals = []
        expected_signals = []
        for signal in signal_array: expected_signals.append(signal.split(':')[0])
        for actual_signal in actual_signals:
            if actual_signal['signalName'] in expected_signals:
                updated_selected_signals.append(actual_signal)
            else:
                logging.info('Measurement config has unwanted signal, Removing it...')
                signal_id = actual_signal['signalId'] 
                source_id = actual_signal['sourceId']
                self.remove_signal(measurement_configuration_id, source_id, signal_id)
        return updated_selected_signals

    def verify_number_of_samples(self, measurement_result, signal_list, number_of_sample):
        exception_list = []
        for teststep_id in list(measurement_result.keys()):
            result = measurement_result[teststep_id]
            data_array = result['results']['data']
            for signal in signal_list:
                count = 0
                for data in data_array[1:]:
                    if data[signal] != None:
                        count +=1
                if count != number_of_sample:
                    exception_list.append(f"Number of samples for signal {signal} is not matching. Expected: {number_of_sample} Actual: {count}")
        if(len(exception_list) > 0):
            logging.info(f"Issues when checking number of samples: {exception_list}")
            assert False, f"Measurement sample count mismtach for {len(exception_list)} signals, please check the log for the details"
        logging.info("Signal sample check passed.")

    def prepare_preview(self, test_step_id):
        preview_prepare = self.api_requests.put_request("/remote-measurement/testSteps/{}/triggerPreview?targetFormat=JSON".format(test_step_id), params={})
        assert preview_prepare.status_code == requests.codes.accepted, self.api_gen_obj.assert_message(preview_prepare)
        time.sleep(5) #preview data takes few sec to load in the backend after prepare preview

    def _get_preview_data(self, test_step_id):
        preview_data = self.api_requests.get_request("/remote-measurement/testSteps/{}/series?resolution=200".format(test_step_id))
        assert preview_data.status_code == requests.codes.ok, self.api_gen_obj.assert_message(preview_data)
        return json.loads(preview_data.text)
        

    def validate_preview_signal_or_message_count(self, measurement_test_result, test_step_id, measurement_configuration_id, actual_message_and_signal_count):
        logging.info(f"Validating preview count for test step id : {test_step_id}")
        if actual_message_and_signal_count == 0 :
            assert False, f'No preview data for test step id :{test_step_id}'
        total_signals = self.get_measure_config_total_elements(measurement_configuration_id,"signals")
        total_calculated_signals = self.get_measure_config_total_elements(measurement_configuration_id,"calculatedSignals")
        total_messages = self.get_measure_config_total_elements(measurement_configuration_id, "messages")
        exp_other_series_count = total_messages
        exp_numeric_series_count = total_signals + total_calculated_signals
        actual_other_series_count = 0
        actual_numeric_series_count = 0
        for i in range(actual_message_and_signal_count):
            signal_or_message_valuetype = measurement_test_result[test_step_id]['preview_data']["_embedded"]["series"][i]["valueType"]
            if signal_or_message_valuetype == "BYTES":
                actual_other_series_count += 1
            elif signal_or_message_valuetype == "DOUBLE":
                actual_numeric_series_count += 1   
        assert actual_other_series_count == exp_other_series_count, f'signal or calculated signal count mismatch. Actual count is {actual_other_series_count} but expected count is {exp_other_series_count}'
        assert actual_numeric_series_count == exp_numeric_series_count, f'signal or calculated signal count mismatch. Actual count is {actual_numeric_series_count} but expected count is {exp_numeric_series_count}'
        logging.info(f"Successfully validated preview count for test step id : {test_step_id}")

    def validate_preview_data(self, measurement_test_result, measurement_configuration_id):
        for test_step_id in list(measurement_test_result.keys()):
            actual_message_and_signal_count = len(measurement_test_result[test_step_id]['preview_data']["_embedded"]["series"])
            self.validate_preview_signal_or_message_count(measurement_test_result, test_step_id, measurement_configuration_id, actual_message_and_signal_count)
            logging.info(f"Validating preview data value for test step id : {test_step_id}")
            data_array = measurement_test_result[test_step_id]['results']['data']
            for i in range(actual_message_and_signal_count):
                preview_data = measurement_test_result[test_step_id]['preview_data']["_embedded"]["series"][i]["dataPoints"]
                logging.info(f'preview data row count {len(preview_data)}')
                signal_or_message_name = measurement_test_result[test_step_id]['preview_data']["_embedded"]['series'][i]['seriesName']
                csv_data_array = self.fetch_csv_data_row(data_array, signal_or_message_name)
                csv_data_row_count = len(csv_data_array)
                logging.info(f'csv data row count {csv_data_row_count}')
                assert csv_data_row_count == len(preview_data), f'Mismatch in preview data row count and csv data row count. Csv data row count is {csv_data_row_count} and Preview data row count is {len(preview_data)}' 
                logging.info(f'Preview row count for {signal_or_message_name } is matching with csv row count')
                if signal_or_message_name in data_array[0].keys():
                    logging.info(f'{signal_or_message_name} is present in csv file... Continue to validating its values')
                    for row in range(0,len(preview_data)):
                        preview_value = preview_data[row]['value']
                        assert str(preview_value) == str(csv_data_array[row]), f'Mismatch in preview data and CSV data at row {row+4}. Preview data is {str(preview_value)} and CSV data is {str(csv_data_array[row])}'

    def validate_calculated_preview_data(self,measurement_test_result,calculated_signal):
        for test_step_id in list(measurement_test_result.keys()):
            actual_message_and_signal_count = len(measurement_test_result[test_step_id]['preview_data']["_embedded"]["series"])
            for i in range(actual_message_and_signal_count):
                preview_data = measurement_test_result[test_step_id]['preview_data']["_embedded"]["series"][i]["dataPoints"]
                signal_type = measurement_test_result[test_step_id]['preview_data']["_embedded"]["series"][i]["type"]
                if signal_type == calculated_signal.upper():
                    for count in range(len(preview_data)):
                        data_val = measurement_test_result[test_step_id]['preview_data']["_embedded"]["series"][i]["dataPoints"][count]["value"]
                        assert data_val != None,"No preview data is available for calculated signal"

    def fetch_csv_data_row(self, data_array, signal_or_message_name):
        return [data_array[i][signal_or_message_name] for i in range(1, len(data_array)) if (data_array[i][signal_or_message_name] is not None)]

    def validate_dm1_messages(self, json_data, measurement_configuration_id, measurement_test_result):
        selected_messages = self.get_measure_config_selected_messages(measurement_configuration_id)
        results=measurement_test_result
        measurement_result=len(results)-1
        teststep_count=0
        while measurement_result >= 0:
            teststep_id = list(results.keys())[measurement_result]
            result = results[teststep_id]
            data_array=result['results']['data']
            for selected_message in selected_messages:
               logging.info(f"Message name = {selected_message['name']}")
               spn_details = json_data["DM1_data"][selected_message['name']]
               rpm_range = json_data["DM1_data"][selected_message['name']+'_RPM_range']
               if selected_message['name'] in data_array[0].keys() and len(spn_details[teststep_count]) > 0 and len(rpm_range[teststep_count]) > 0:
                    logging.info(data_array)
                    if len(data_array) > 1:
                       self.validate_spn_data(spn_details[teststep_count], data_array, selected_message['name'], rpm_range[teststep_count])
                    else:
                       assert False, f"No data in the measurement for message - {selected_message['name']} or spn - {spn_details[teststep_count][0]}"
            teststep_count += 1
            measurement_result -= 1

    def validate_spn_data(self, spn_details, data_array, message_name, rpm_range):
        for i in range(1,len(data_array)):
            if data_array[i][message_name] != None:
                rpm_value = self.fetch_rpm_value(data_array, i)
                spn_value = data_array[i][spn_details[0]]
                self.check_dm1_spn(spn_details, rpm_value, spn_value, message_name, rpm_range)
                if float(rpm_value) == 60.0:
                    break
            else:
                if spn_details[1] == "DM1_RERAISED":
                    assert data_array[i][spn_details[0]] is None, f"SPN value for message {message_name} appeared at unexpected rpm-{rpm_value}, Expected RPM range is {rpm_range}"

    def fetch_rpm_value(self,data_array,index):
        rpm_value = data_array[index]['EngineSpeed']
        if rpm_value is not None and isinstance(float(rpm_value),float):
            return rpm_value
        else: 
            for i in range(-1,3):
                rpm_value = data_array[index+i]['EngineSpeed']
                if rpm_value is not None and rpm_value != "rpm" and isinstance(float(rpm_value),float):
                    break
        return rpm_value

    def check_dm1_spn(self, spn_details, rpm_value, spn_value, message_name, rpm_range):
        if spn_details[1] == "DM1_RERAISED":
            logging.info(f"Engine current RPM rate is {rpm_value}")
            assert float(rpm_value) in list(itertools.chain(range(rpm_range[0][0],rpm_range[0][1]), range(rpm_range[1][0],rpm_range[1][1]))), f"Message - {message_name} value is appeared at unexpected rpm-{rpm_value}, Expected RPM range is {rpm_range}"
            assert spn_value == spn_details[2], f"Unexpected SPN value recorded -{spn_value} for message {message_name} at rpm {rpm_value}, Expected SPN value is {spn_details[2]}"
        elif spn_details[1] == "DM1_RAISED":
            logging.info(f"Engine current RPM rate is {rpm_value}")
            if float(rpm_value) in range(rpm_range[0],rpm_range[1]):
                assert spn_value == spn_details[2],f"SPN value -{spn_details[2]} for message {message_name} does not appeared when RPM is {rpm_value}, Expected RPM range is {rpm_range}. Actual SPN values appeared is {spn_value}"
            else:
                assert spn_value is None, f"SPN value for message {message_name} appeared at unexpected rpm-{rpm_value}, Expected RPM range is {rpm_range}"
        elif spn_details[1] == "SINGLESHOT":
            logging.info(f"Engine current RPM rate is {rpm_value}")
            assert float(rpm_value) in rpm_range, f"Message - {message_name} value is appeared at unexpected rpm-{rpm_value}, Expected RPM range is {rpm_range}"
            assert spn_value == spn_details[2], f"Unexpected SPN value recorded -{spn_value} for message {message_name} at rpm {rpm_value}, Expected SPN value is {spn_details[2]}"

    def add_rm_campaign_vehicle_details(self, campaign_id, count, campaign_vehicle_id, start_time, context):
        for vehicle in context.vehicle_data:
            vehicle_id = context.vehicle_data[vehicle]["vehicle_id"]
            if vehicle_id == campaign_vehicle_id and len(context.vehicle_data[vehicle]["device_data"]) != 0:
                if count != None:
                    mc_config_id = context.measurement_configuration_ids[count-1]
                else:
                    mc_config_id = context.measurement_configuration_id
                assignment_details = self.get_measurement_assignment_details(vehicle_id, mc_config_id, context.campaign_slot_name)
                context.assignment_job_id = assignment_details['mc2SlotAssignmentId']
                context.vehicle_data[vehicle]["remote_measurement"].update({"rm_job_id"+campaign_id+vehicle_id : context.assignment_job_id})
                context.all_assignment_jobs[context.assignment_job_id] = {'start_time': start_time, 'measurement_start_time': '', 'end_time': '', 'measurement_end_time': '', 'status': ''}
                rm_activation_date = str(start_time).split(".")
                rm_activation_date = datetime.datetime.strptime(rm_activation_date[0],"%Y-%m-%d %H:%M:%S")
                context.vehicle_data[vehicle]["remote_measurement"].update({"rm_activation_date"+campaign_id+vehicle_id : rm_activation_date})
                logging.info(f"Campaign ID: {campaign_id}, rm_activation_date: {rm_activation_date}")
                
    def campaign_rm_status_check(self, exp_state,substate,target_status,timer,measurement_config_id,vehicle_name,context):
        logging.info("inside campaign_rm_status_check")
        for assignment_job_id in context.all_assignment_jobs:
            for campaign_id in context.activation_campaign_ids:
                if context.vehicle_id in context.campaign_vehicle_data[campaign_id]["vehicle_ids"] and assignment_job_id == context.vehicle_data[vehicle_name]["remote_measurement"]["rm_job_id"+campaign_id+context.vehicle_id]:
                    logging.info("inside campaign_rm_status_check 1")
                    self.rm_status_check(exp_state,substate,target_status,timer,measurement_config_id,assignment_job_id,context)
                    context.campaign_rm_active = True if exp_state == 'ACTIVE' else False

    def check_vehicle_rm_status(self, vehicle_id, assignment_id, exp_state): 
        self.api_gen_obj.start_timer()
        while (self.api_gen_obj.check_timer() == True):
            assignment_details = self.get_assignment_job_details(vehicle_id, assignment_id)
            if(assignment_details['currentStatus'].strip() == exp_state):
                self.api_gen_obj.stop_timer()
            elif('currentSubstatus' in assignment_details and (assignment_details['currentSubstatus'].strip() == "DEACTIVATION_FAILED"  or assignment_details['currentSubstatus'].strip() == ("ACTIVATION_FAILED"))):
                assert False, "Activation or Deactivation of the RM configuration is failed, current sub status is " + assignment_details['currentSubstatus']
        return assignment_details

    def retrieve_signal_collection_source_id(self, source_name, source_details, source_id, measurement_configuration_name):
        source_found_in_measureconfig = False
        if source_name is None:
            signal_collection_id = source_details.json()['_embedded']['sources'][0]['_embedded']['selectedSignalCollection']['signalCollectionId']
            source_id =  source_details.json()['_embedded']['sources'][0]['sourceId']
        else:
            for source in source_details.json()['_embedded']['sources']:
                if source['name'] == source_name:
                    signal_collection_id = source['_embedded']['selectedSignalCollection']['signalCollectionId']
                    source_id = source['sourceId']
                    source_found_in_measureconfig = True
            assert source_found_in_measureconfig, f'{source_name} source is not added to measurement configuration {measurement_configuration_name}'
        return signal_collection_id, source_id

    def verify_upload_interval(self, context, start_time, upload_interval, measurement_loaded, offset, upload_duration):
        while int(time.time() - start_time) <= upload_interval + upload_interval//2:
            measurement_results = self.get_measurement_results(context.vehicle_id, context.rm_activation_date)
            if len(measurement_results) > 0 and not measurement_loaded:
                logging.info(f"Measurement data loaded in {time.time() - start_time}")
                measurement_loaded = True
                measurement_result_list  = measurement_results[list(measurement_results.keys())[0]]
                if len(measurement_result_list["results"]["data"]) > 1:
                    offset = int(float(measurement_result_list["results"]["data"][1]["time_relative"]))
                    upload_duration = int(measurement_result_list["duration"])//1000
                    upload_duration = upload_duration - offset
                    break
                else:
                    assert False, "Measurement data is empty" 
            elif measurement_loaded:
                upload_duration_latest = int(measurement_results[list(measurement_results.keys())[0]]["duration"])//1000 - offset
                if upload_duration_latest > upload_duration:
                    upload_duration = upload_duration_latest
                    logging.info(f"Measurement data updated in {time.time() - start_time}")
                    break
                else:
                    time.sleep(upload_interval/10)
            else:
                time.sleep(upload_interval/10)

        return measurement_loaded, upload_duration

    def verify_rm_status_check(self, context, *args):
        vehicle_name, device_slot_name, measurement_config_name, exp_state, substate, target_status, timer, campaign_detail, measurement_config_id, assignment_job_id = [args[i] for i in range(len(args))]
        vehicles = vehicle_name.split(",")
        for vehicle_name in vehicles:
            context.vehicle_id = context.vehicle_data[vehicle_name]['vehicle_id']
            if device_slot_name is not None:
                context.device_slot_name = device_slot_name + "_" + context.device_slot_type
            if measurement_config_name is not None:
                measurement_config_id = self.get_measurement_configuration_id(measurement_config_name)
                self.rm_status_check(exp_state,substate,target_status,timer,measurement_config_id,assignment_job_id,context)
            elif campaign_detail is not None:
                self.campaign_rm_status_check(exp_state,substate,target_status,timer,measurement_config_id,vehicle_name,context)
            else:
                self.assignment_rm_status_check(context,vehicle_name, exp_state, substate, target_status, timer, measurement_config_id)
    
    def assignment_rm_status_check(self, context, vehicle_name, exp_state, substate, target_status, timer, measurement_config_id):
        for assignment_job_id in context.all_assignment_jobs:
            for measurement_configuration in context.measurement_configuration_list:
                if assignment_job_id == context.vehicle_data[vehicle_name]["remote_measurement"][measurement_configuration]["rm_job_id"+context.device_slot_name]:
                    self.rm_status_check(exp_state,substate,target_status,timer,measurement_config_id,assignment_job_id,context)
                
    def fetch_source_id_and_remove_rm_sources(self, context, r, rm_sources):
        if '_embedded' in r.json():
            source_list = r.json()['_embedded']['sources']
            for rm_source in rm_sources:
                for source in source_list:
                    if source["name"] == rm_source:
                        source_id =  source['sourceId']
                        self.remove_source(context.measurement_configuration_id,source_id)
        else:
            logging.info("RM configuration doesn't have any assigned Signal collection / Source.")

        
    def add_or_edit_trigger_element(self, context, element, trigger_phase, trigger_payload, state, status, trigger_condition_name):
        for key,val in context.trigger_json_data["triggerTestData"].items():
            if (key == element):
                pay_load = self.prepare_trigger_payload(val[trigger_phase])
                trigger_payload[key] = pay_load

        try:
            if (state.upper() == "ADD"):
                self.add_trigger_element(context.measurement_configuration_id, trigger_phase, trigger_payload[element])
            else:
                self.edit_trigger_element(context.measurement_configuration_id, trigger_phase, trigger_payload[element])
        except Exception as e:
            if status.upper() == "SUCCESS":
                assert False, "Error in adding trigger phase : {}".format(e)
            else:
                if status.upper() != "SUCCESS":
                    assert False, "Test adds erroneous trigger phase"

        context.exp_trigger_name = trigger_payload[element]['name']
        for trigger_condition in trigger_payload[element]["triggerElements"]:
            trigger_condition_name.append(trigger_condition["name"])
        context.trigger_condition_name = trigger_condition_name

    def add_sources_to_rm_config(self, source_collection, source_in_measurement_configuration, measurement_configuration_name, measurement_configuration_id, api_gen_obj):
        for source_name in source_collection:
            if source_name in source_in_measurement_configuration:
                logging.info(f'{source_name} is already added to {measurement_configuration_name}')
            else:
                signal_collection_id = self.get_signal_collection_id(source_name)
                if signal_collection_id is not None:
                    r =  self.add_sources_to_measure_config(signal_collection_id,measurement_configuration_id,source_name)
                    logging.info(r)
                    assert r.status_code == requests.codes.created, api_gen_obj.assert_message(r)
                    logging.info(f'signal collection {source_name} is added to measurement configuration {measurement_configuration_name}')
                else:
                    assert False, source_name + ' is not found in signal collection list'

    def verify_rm_download_and_preview_prepared(self, context):
        download_prepared = False
        preview_prepared = False

        if context.all_assignment_jobs[list(context.all_assignment_jobs)[-1]]['end_time'] != '':
            start_time = context.all_assignment_jobs[list(context.all_assignment_jobs)[-1]]['start_time']
            end_time = context.all_assignment_jobs[list(context.all_assignment_jobs)[-1]]['end_time']
            context.test_duration_ms_latest_measurement = self.calculate_duration_in_ms(start_time, end_time)
            logging.info(f'Measurement was active for a duration of {str(context.test_duration_ms_latest_measurement/1000)} seconds')
    
        if (hasattr(context, 'rm_download_prepared') and context.rm_download_prepared is True):
            download_prepared = True

        if (hasattr(context, 'rm_preview_prepared') and context.rm_preview_prepared is True):
            preview_prepared = True

        return download_prepared, preview_prepared
    
    def check_measurement_configuration_status(self, vsg_id, vsg_name):
 
        r = self.api_requests.get_request(constants.RM_VSG_ID_ASSIGNMENTS.format(vsg_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        
        if '_embedded' not in r.json():
            state = "no active"
            logging.info(f'No Assigned or Active RM configurations found in {vsg_name}')
            return state
        else:
            state = "active"
            logging.info(f'Assigned or Active RM configurations found in {vsg_name}')
            return state
    
    def validate_data_for_signals(self,rows_to_validate,signal_name,signal_value,data_array):
        if signal_name == "VUsedFuel":
                assert signal_name in data_array[0].keys(), f"Signal with name {signal_name} not found in headers"
                for i in range(1,rows_to_validate):
                    if data_array[i][signal_name] != None:
                        assert data_array[i][signal_name] ==signal_value, f"The expected data {signal_value} is not matching with actual data {data_array[i][signal_name]} for the signal {signal_name}"
                        break
        elif signal_name == "Distance":
            actual_distance=self.validate_data_for_distance(rows_to_validate,data_array)
            assert float(abs(actual_distance)) == float(signal_value), f"The expected data {signal_value} is not matching with actual data {actual_distance} for the signal {signal_name}"
        
    def validate_data_for_distance(self,rows_to_validate,data_array):
        value_vehicle_distance_flag=False
        value_start_total_distance_flag=False
        for i in range(1,rows_to_validate):
                if data_array[i]['TotalVehicleDistanceHighResolution']!= None:
                    value_vehicle_distance=data_array[i]['TotalVehicleDistanceHighResolution']
                    value_vehicle_distance_flag=True
                if data_array[i]['StartTotalVehicleDistanceHighResolution']!= None:
                    value_start_total_distance=data_array[i]['StartTotalVehicleDistanceHighResolution']
                    value_start_total_distance_flag=True
                if value_vehicle_distance_flag==True and value_start_total_distance_flag==True:
                    break    
        actual_distance=float(value_start_total_distance)-float(value_vehicle_distance)
        return actual_distance    
    
    def deactivate_vsg_rm_config(self, slot_assignment_ids, vsg_id, vsg_device_slot):
        for slot_assignment_id in slot_assignment_ids:
            self.trigger_vsg_rm_deactivation(vsg_id, vsg_device_slot, slot_assignment_id) 
        return False 

    def update_data_with_pre_post_trigger_time(self,pretrigger,posttrigger,data):
        pre_trigger=float(pretrigger)
        data["preTriggerTime"]=pre_trigger
        post_trigger = None
        if posttrigger != None:
            post_trigger=float(posttrigger)
            post_trigger_data = {"postTriggerTime": post_trigger}
            data.update(post_trigger_data)
        return pre_trigger,post_trigger,data
    
    def __get_data_array_having_value_for_daf_signal(self, data_array, measurement_entity):
        calculated_list_signal_value = []
        for data in data_array[1:]:
            if data[measurement_entity['name']] != None:
                calculated_list_signal_value.append(data[measurement_entity['name']])
        return calculated_list_signal_value
        
    def prepare_expected_trigger_data(self, measurement_configuration_id, data ):
        data = self.prepare_trigger_payload(data)
        self.get_signal_or_message_id_source_id(measurement_configuration_id, data)
        return data
    
    def compare_trigger_data(self,actual_data,expected_data):
        
        if actual_data == None and expected_data == None:
            return True
        elif actual_data == None or expected_data == None:
            return False
        else:
            trigger_datas_matching = self.validate_trigger_datas(actual_data, expected_data)
            return trigger_datas_matching

    def validate_trigger_datas(self, actual_data, expected_data):
        trigger_check = True
        for key,value in actual_data.items():
            if key in expected_data or key in ["message", "signal"]:
                if isinstance(value,list):
                    for index in range(0, len(value)):
                        trigger_check = self.validate_trigger_datas(value[index], expected_data[key][index])
                elif isinstance(value,dict) and key !="sourceFilter":
                    trigger_check = self.validate_trigger_datas(actual_data[key], expected_data)
                else:
                    trigger_check = (value == expected_data[key])
                if trigger_check == False:
                    break
        return trigger_check

    def add_expected_start_stop_trigger_conditions(self, context, trigger_phase, data):

        logging.info(f"Adding the expected trigger conditions for {trigger_phase} to configuration {context.measurement_configuration_id} ...")
        etag = self.api_requests.get_etag(constants.RM_MEASURE_CONFIG_ID.format(context.measurement_configuration_id))
        r = self.api_requests.post_request(constants.RM_MEASURE_CONFIG_ID_TRIGGERS_ID_PHASE.format(context.measurement_configuration_id, context.trigger_id, trigger_phase), params=data, custom_header={'if-match': etag})
        assert r.status_code == requests.codes.created, self.api_gen_obj.assert_message(r)
            
    
    def retry_rm_activation_deactivation(self, count, vehicle_id, measurement_job_id):
        """Retry the activation or deactivation of the given measurement config on a given vehicle
        Args:
            count (int): number of times to be retry the activation or deactivation of the given measurement config
            vehicle_id (str): id of a vehicle
            measurement_job_id (str): measurement configuration id to be activated on the given vehicle
        """
        for retry_count in range(0,count):
            etag = self.api_requests.get_etag(constants.RM_VEHICLES_ID.format(vehicle_id))
            r = self.api_requests.put_request(constants.RM_VEHICLES_ID_MEASURE_JOB_RETRY.format(vehicle_id,measurement_job_id), params={}, custom_header={'if-match': etag})
            assert r.status_code == requests.codes.no_content, f"Error at retry count {retry_count} - {self.api_gen_obj.assert_message(r)}"

    def get_measurement_configuration_version(self,measruement_configuration_id):
        r = self.api_requests.get_request(constants.RM_MEASURE_CONFIG_ID.format(measruement_configuration_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r.json()['version']
