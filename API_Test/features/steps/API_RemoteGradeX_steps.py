import requests
import logging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import os
import time
import datetime
import dateutil.parser as parser
import pageObjects.API_Generic_Class as API_Generic_Class
import pageObjects.API_RemoteGradeX_Class as API_RemoteGradeX_Class
import steps.constantfiles.constants_remotegradex as constants


@step('task "{task}" is executed for "{count}" times')
@step('task "{task}" is executed')
@step('task "{task}" is executed on "{test_device}" device')
@step('task "{task}" is executed on device with id "{device_id}"')
def step_impl(context, task, count="1", test_device = None, device_id = None):
    """ Description     : Start the task for the 

        Pre-condition   : None

        Parameters      : task

        Expected result : starts the Remote Grade X task
    """
    context.task = task
    context.task_id = []
    context.trigger_time = []
    context.task_time = []
    if(device_id == None):
        device_id = context.device_id if test_device == None else context.devices_data[test_device]["device_name"]
    api_grade_x_obj = API_RemoteGradeX_Class.ApiRemoteGradeXClass(context.env, context.log_api_details)
    count = int(count)
    while (count > 0):
        context.trigger_time.append(datetime.datetime.now(datetime.timezone.utc).isoformat())
        context.task_time.append(datetime.datetime.now(datetime.timezone.utc).isoformat())
        path = os.path.dirname(os.path.abspath(__file__))
        file_path = path + constants.GRADEX_ZIP_FILE_PATH + task
        file_data = {'file': open(file_path, 'rb')}

        data =  {
            "deviceId": device_id,
            "filename":task 
        }
        logging.info(f" Creating {(count)} RDA task ")
        time.sleep(10)
        task_id = api_grade_x_obj.create_rda_task(data, file_data, device_id)
        context.task_id.append(task_id)
        logging.info(f" Created {context.task_id[len(context.task_id)-1]} RDA task ")
        count -=1

@step('verify "{status}" for "{task}" is available within "{time_in_min}" minutes for all "{count}" results')
@step('verify "{status}" for "{task}" is available within "{time_in_min}" minutes for all "{count}" tasks')
@step('verify "{status}" for "{task}" is available within "{time_in_min}" minutes')
@step('verify "{status}" for all tasks within "{time_in_min}" mins')
def step_impl(context, status,time_in_min,task ="Task", count="1"):
    """ Description     : Start the Remote Grade X task

        Pre-condition   : None

        Parameters      : task

        Expected result : starts the Remote Grade X task
    """

    api_grade_x_obj = API_RemoteGradeX_Class.ApiRemoteGradeXClass(context.env, context.log_api_details)
    count = int(count)       
    assert count == len(context.task_id), "Created RDA tasks count is not expected. Actual count - %s, Expected count - %s"%(len(context.task_id), count)
    # while (count > 0):
    for each_task in range(len(context.task_id)):
        api_gen_obj = API_Generic_Class.ApiGenericClass()
        api_gen_obj.update_timeout_time(int(time_in_min) * 60)
        api_gen_obj.start_timer()          
        rda_status_list = []
        if task == "Task":
            while ((api_gen_obj.check_timer() == True) and ("FAILED" not in rda_status_list) and ("EXECUTED" not in rda_status_list)):
                task_details = api_grade_x_obj.get_rda_task_details(context.task_id[each_task])              
                context.trigger_time =task_details['triggeredOn']
                state =task_details['state']      
                if state not in rda_status_list:
                    rda_status_list.append(state)       
                time.sleep(1)
            api_gen_obj.stop_timer()
                          
        elif task == "Job Result":
            while ((api_gen_obj.check_timer() == True) and ("JOB_SUCCESS" not in rda_status_list) and ("JOB_FAILURE" not in rda_status_list)):
                r = api_grade_x_obj.get_rda_job_result(context.device_id)
                assert r.status_code == requests.codes.ok, "RDA Job Result status not available"
                context.trigger_time = parser.parse(r.json()['_embedded']['rdaJobResults'][count-1]['startTime']).isoformat()
                state = r.json()['_embedded']['rdaJobResults'][count-1]['executionStatus']
                if state not in rda_status_list:
                    rda_status_list.append(state)
                time.sleep(1)
            api_gen_obj.stop_timer()

        exp_rda_status_list = status.split(",")
        logging.info(f" Checking status of Job Task / Results -{(each_task+1)}")
        for exp_status in exp_rda_status_list:
            assert exp_status in rda_status_list, "RDA status Mismatch: Expected status - {} and Actual status - {}".format(exp_rda_status_list, rda_status_list)
        logging.info(f" Checked status of Job Task / Results. EXPECTED result. -{(each_task+1)}")
        count -= 1
        assert context.trigger_time > context.task_time[0], "Task schedule is not current"


@step('verify Measurement Task executed for more than "{time}" minutes each for all "{count}" tasks')
@step('verify Measurement Task executed for more than "{time}" minutes')
def step_impl(context, time, count = "1"):
    api_grade_x_obj = API_RemoteGradeX_Class.ApiRemoteGradeXClass(context.env, context.log_api_details)
    
    count = int(count)
    while (count > 0):
        r = api_grade_x_obj.get_rda_job_result(context.device_id)
        assert r.status_code == requests.codes.ok, "RDA Job Result status not available"
        exec_dur = (parser.parse(r.json()['_embedded']['rdaJobResults'][count-1]['endTime']) - 
            parser.parse(r.json()['_embedded']['rdaJobResults'][count-1]['startTime'])).seconds
        assert exec_dur > (int(time))*60, "Execution time is not as expected"
        count -= 1


@step('verify RM GradeX result is as expected for all "{count}" Job results')
@step('verify RM GradeX result is as expected')
def step_impl(context, count="1"):
    api_grade_x_obj = API_RemoteGradeX_Class.ApiRemoteGradeXClass(context.env, context.log_api_details)
    
    count = int(count)
    while (count > 0):
        r = api_grade_x_obj.get_rda_job_result(context.device_id)
        assert r.status_code == requests.codes.ok, constants.RGX_JOB_RESULT
        logging.info(f" Checking Job result-{count} ")
        job_result_id = r.json()['_embedded']['rdaJobResults'][count-1]['jobResultId']
        r = api_grade_x_obj.ver_rda_job_result(job_result_id)
        assert r == True, "RDA Job result is NOT as expected"
        logging.info(f" Checked Job result. Expected.-{count}")
        count -= 1


@step('verify all "{count}" RM GradeX result can be deleted')
@step('verify RM GradeX result can be deleted')
def step_impl(context, count = "1"):
    api_grade_x_obj = API_RemoteGradeX_Class.ApiRemoteGradeXClass(context.env, context.log_api_details)
    
    count = int(count)
    while (count > 0):
        r = api_grade_x_obj.get_rda_job_result(context.device_id)
        assert r.status_code == requests.codes.ok, constants.RGX_JOB_RESULT
        job_result_id = r.json()['_embedded']['rdaJobResults'][count-1]['jobResultId']
        logging.info(f" Deleting {count} Job result.")
        r_del_op = api_grade_x_obj.del_rda_job_result(job_result_id)
        assert r_del_op.status_code == requests.codes.no_content, constants.RGX_JOB_RESULT
        logging.info(f" Deleted {count} Job result. Expected behavior.")
        count -= 1

@step('verify RD GradeX "{dtc_code_result}" is as expected for all "{count}" Job results')
@step('verify RD GradeX "{dtc_code_result}" is as expected')
def step_impl(context, dtc_code_result, count="1"):
    api_grade_x_obj = API_RemoteGradeX_Class.ApiRemoteGradeXClass(context.env, context.log_api_details)
    count = int(count)
    while (count > 0):
        r = api_grade_x_obj.get_rda_job_result(context.device_id)
        assert r.status_code == requests.codes.ok, constants.RGX_JOB_RESULT
        logging.info(f" Checking Job result -{count}")
        job_result_id = r.json()['_embedded']['rdaJobResults'][count-1]['jobResultId']
        result = api_grade_x_obj.verify_gx_rd_job_result(job_result_id, dtc_code_result)
        assert result == True, "RDA Job result is NOT as expected"
        logging.info(f" Checked Job result. Expected. -{count}")
        count -= 1