from asyncio import constants
import requests
import logging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time
import logging
import math
import datetime
import steps.pageObjects.API_Generic_Class as API_Generic_Class
import steps.pageObjects.API_Campaign_Class as API_Campaign_Class
import steps.pageObjects.API_Inventory_Class as API_Inventory_Class
import steps.pageObjects.API_OTA_Updates_Class as Api_Ota_Updates_Class
import pageObjects.API_OTA_Vehicle_Data_Class as API_OTA_Vehicle_Data_Class
import steps.constantfiles.constants_campaign as constants

@step('a new campaign "{campaign_detail}" is "{action}"ed')
@step('a existing campaign is "{action}"ed with "{campaign_detail}"')
@step('"{count:d}" new Campaigns "{campaign_detail}" are "{action}"ed')
def step_impl(context, campaign_detail, action, count=1):
    """
        Description: Campaign action Create/Edit is performed

        Pre-condition:  None

        Parameters: campaign_detail = name of campaign; can be string for single campaign, list for multiple Campaigns
                    IMP: length of list of campaign_detail is preferred while creating new campaign
                    count > 1 will create campaign of duplicate type with same camapign details
                    count = none, with campaign_detail = list of campaigns, 
                        will create different campaigns (=len(list)) as per different campaign details

                    action = create / edit

                    count = number of Campaigns to be created; default value = 1

        Expected result:    Campaign action (create/edit) is performed
    """
    api_campaign_obj = API_Campaign_Class.ApiCampaignClass(context.env, context.log_api_details)
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    campaign_ids = []

    context.json_data = api_gen_obj.parse_json_file(constants.CAMPAIGN_JSON_PATH)
    campaign_detail_list = campaign_detail.split(",")

    for index in range(max(count,len(campaign_detail_list))):
        context.campaign_edited = False
        context.is_scheduled_campaign = False
        context.campaign_detail = campaign_detail

        if (len(campaign_detail_list)==1):
            pay_load = context.json_data[campaign_detail_list[0]][action.lower()]
        else:
            pay_load = context.json_data[campaign_detail_list[index]][action.lower()]

        if "name" in pay_load:
            context.campaign_name = pay_load["name"]
        if ("plannedStart" in pay_load):
            context.is_scheduled_campaign = True        # used to check for automatic Campaign State check when Campaign start/end is scheduled
            context.planned_start = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5)
            start_time = str(context.planned_start).replace(str(context.planned_start)[-9:], "Z")
            pay_load["plannedStart"] = start_time.replace(" ","T")

            context.campaign_duration = len(context.all_vehicle_id)*5       # taking 5 minutes as time to complete 1 vehicle's flashing process
            context.planned_end = context.planned_start + datetime.timedelta(minutes=context.campaign_duration)
            end_time = str(context.planned_end).replace(str(context.planned_end)[-9:], "Z")
            pay_load["plannedEnd"] = end_time.replace(" ","T")

        # switching as per different Campaign actions
        if action.upper() == "ADD":
            logging.info("Adding a new Campaign")
            campaign_id = api_campaign_obj.add_campaign(pay_load)
            campaign_ids.append(campaign_id)
            context.campaign_ids = campaign_ids
            if pay_load["type"] == "REMOTE_MEASUREMENT" or pay_load["type"] == "REMOTE_DIAGNOSTICS_ACTIVATION":
                context.activation_campaign_ids = campaign_ids
        elif action.upper() == "EDIT":
            logging.info(f"Editing a Campaign {context.campaign_name}")
            api_campaign_obj.edit_campaign(context.campaign_name, pay_load)
            context.campaign_edited = True
        else:
            assert False,  "%s is not the expected input."%action

        #context.campaign_ids = list(set(context.campaign_ids)) # to get unique campaign Ids, as editing action was creating duplicate Campaign IDs


@step('campaign "{count:d}" status "{campaign_status}" is verified')
@step('campaign status "{campaign_status}" is verified within "{timer}" minutes')
@step('campaign status "{campaign_status}" is verified after scheduled duration')
@step('campaign status "{campaign_status}" is verified')
@step('measurement campaign status "{campaign_status}" is verified')
@step('measurement campaign "{count:d}" status "{campaign_status}" is verified')
@step('RD activation campaign status "{campaign_status}" is verified')
@step('RD deactivation campaign status "{campaign_status}" is verified')
@step('RD activation campaign "{count:d}" status "{campaign_status}" is verified')
@step('RD deactivation campaign "{count:d}" status "{campaign_status}" is verified')
def step_impl(context, campaign_status, timer = "2", count=None):
    """
        Description: Campaign status is checked

        Pre-condition:  None

        Parameters: campaign_status = CREATED/RUNNING/FINISHED

                    timer = DEFALUT 2 MINUTES

        Expected result: Campaign status is checked
    """
    api_campaign_obj = API_Campaign_Class.ApiCampaignClass(context.env, context.log_api_details)

    if (context.is_scheduled_campaign):
        if (campaign_status == "RUNNING"):
            while (datetime.datetime.now(datetime.timezone.utc) < context.planned_start):
                time.sleep(5)

        if (campaign_status == "FINISHED"):
            while (datetime.datetime.now(datetime.timezone.utc) < context.planned_end):
                time.sleep(5)

    if count is None:
        for campaign_id in context.campaign_ids:
            state_check, campaign_state = api_campaign_obj.is_campaign_state(campaign_id, campaign_status, timer)
            assert state_check == True, f"Unexpected Campaign state - {campaign_state} appears. Expected State - {campaign_status}"
            logging.info(f"Expected Campaign state - {campaign_status} appears for Campaign Id - {campaign_id}")
    else:
        state_check, campaign_state = api_campaign_obj.is_campaign_state(context.campaign_ids[count-1], campaign_status, timer)
        assert state_check == True, "Unexpected Campaign state - {campaign_state} appears. Expected State - {campaign_status}"
        logging.info(f"Expected Campaign state - {campaign_status} appears for Campaign Id - {context.campaign_ids[count-1]}")


@step('content "{dp_name}" is added to the Campaign "{count:d}"')
@step('content "{dp_name}" is added to the Campaign')
def step_impl(context, dp_name, count=None):
    """
        Description: Distributiion package is added to particular campaign

        Pre-condition:  a new campaign "{campaign_detail}" is "{action}"ed

        Parameters: dp_name = name of distribution package

        Expected result: Distribution package gets assigned to Campaign
    """
    api_campaign_obj = API_Campaign_Class.ApiCampaignClass(context.env, context.log_api_details)
    api_ota_update_obj = Api_Ota_Updates_Class.ApiOtaUpdatesClass(context.env, context.log_api_details)

    if "_delta" in dp_name:
        dp_name = constants.DELTA_UPDATE_DP_FORMAT.format(context.from_version, context.to_version, context.device_config_data['su_security_option'], context.device_config_data['firmware_type'].upper())

    distribution_package_id = api_ota_update_obj.search_distribution_package(dp_name)

    data = {
  "assignableItem": {
    "id": distribution_package_id
  }
}
    
    if count is None:
        for campaign_id in context.campaign_ids:
            api_campaign_obj.add_content_vehicles(campaign_id, data)
    else:
        api_campaign_obj.add_content_vehicles(context.campaign_ids[count-1], data)


@step('vehicles are added to the Campaign "{count:d}" using static list')
@step('vehicles are added to the Campaign using dynamic filter "{dynamic_filter}"')
@step('vehicles are added to the Campaign using static list')
@step('vehicles "{vehicle_list}" are added to the "{campaign_type}" campaign using dynamic filter "{dynamic_filter}"')
@step('vehicles "{vehicle_list}" are added to the "{campaign_type}" campaign using static list')
@step('vehicles "{vehicle_list}" are added to the "{campaign_type}" campaign "{count:d}" using static list')
@step('vehicles "{vehicle_list}" are added to the "{campaign_type}" campaign "{count:d}" using dynamic filter "{dynamic_filter}"')
def step_impl(context, vehicle_list = None, dynamic_filter = None, campaign_type = None, count = None):
    """
        Description: Vehicles are added to particular campaign

        Pre-condition:  a new campaign "{campaign_detail}" is "{action}"ed

        Parameters: dynamic_filter = None (Default)

        Expected result: Vehicles get assigned to Campaign
    """
    api_campaign_obj = API_Campaign_Class.ApiCampaignClass(context.env, context.log_api_details)

    if (dynamic_filter is not None):
        data = context.json_data[context.campaign_detail][dynamic_filter]
    else:
        data = {"vehicleIds": context.all_vehicle_id}

    if campaign_type is not None:
        context.campaign_slot_name = api_campaign_obj.add_vehicle_to_rm_rd_campaign(count, data, vehicle_list, context.vehicle_data, context.campaign_ids)
    else:
        api_campaign_obj.add_vehicle_to_ota_campaign(count, data, context.campaign_ids)
    time.sleep(20)

@step('campaign "{count:d}" is "{campaign_action}"ed')
@step('campaign is "{campaign_action}"ed')
@step('"{campaign_type}" campaign is "{campaign_action}"ed')
@step('"{campaign_type}" campaign "{count:d}" is "{campaign_action}"ed')
def step_impl(context, campaign_action, count=None, campaign_type=None):
    """
        Description: Campaign action (Schedule/Running) is performed

        Pre-condition:  a new campaign "{campaign_detail}" is "{action}"ed

        Parameters: campaign_action = Schedule/Finish

        Expected result: Campaign action of Schedule/Finish is performed
    """
    logging.info(f"{campaign_action}ing the above created Campaign...")
    api_campaign_obj = API_Campaign_Class.ApiCampaignClass(context.env, context.log_api_details)
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)

    if not hasattr(context, 'start_time') or context.start_time =="":
        context.start_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=30)

    if count is None:
        for campaign_id in context.campaign_ids:
            api_campaign_obj.post_campaign_action(campaign_id, campaign_action)
            if campaign_type == "REMOTE_MEASUREMENT" and campaign_action=="schedule": 
                campaign_vehicles_id_list = api_campaign_obj.get_campaign_vehicles_id(campaign_id)
                context.campaign_vehicle_data[campaign_id] = {"vehicle_ids" : campaign_vehicles_id_list}
                for campaign_vehicle_id in campaign_vehicles_id_list:
                    api_rm_obj.add_rm_campaign_vehicle_details(campaign_id, count, campaign_vehicle_id, context.start_time, context)
    else:
        api_campaign_obj.post_campaign_action(context.campaign_ids[count-1], campaign_action)
        if campaign_type == "REMOTE_MEASUREMENT" and campaign_action=="schedule":
            campaign_vehicles_id_list = api_campaign_obj.get_campaign_vehicles_id(context.campaign_ids[count-1])
            context.campaign_vehicle_data[context.campaign_ids[count-1]] = {"vehicle_ids" : campaign_vehicles_id_list}
            for campaign_vehicle_id in campaign_vehicles_id_list:
                api_rm_obj.add_rm_campaign_vehicle_details(context.campaign_ids[count-1], count, campaign_vehicle_id, context.start_time, context)

    context.max_parallel_job = 100          # as default value is 100 in VMS application
    if (context.campaign_edited):
        campaign_data = context.json_data[context.campaign_detail]["edit"]
    else:
        campaign_data = context.json_data[context.campaign_detail]["add"]
    
    if "maxRunningAssignments" in campaign_data.keys():
        context.max_parallel_job = campaign_data["maxRunningAssignments"]
    
    context.flashing_iteration = math.ceil(len(context.all_vehicle_id)/int(context.max_parallel_job))
    context.number  = context.flashing_iteration


@step('flashing is verified for the vehicles in Campaign using "{fota}" and "{fota_identifier}" as per maximum parallel job configuration')
def step_impl(context, fota, fota_identifier):
    """
        Description: Campaign flashing is performed with multiple flash iteration (maximum parallel job is set)

        Pre-condition:  a new campaign "{campaign_detail}" is "{action}"ed

        Parameters: fota = Canalization

                fota_identifier = Flash_Start_ES740

        Expected result: Campaign flashing is verified for all vehicles in sequence
    """
    
    while (context.flashing_iteration > 0):
        logging.info(f"Verifying Campaign iteration -{context.number+1-context.flashing_iteration} with Maximum parallel job = {context.max_parallel_job}")
        context.execute_steps(f'''
            When flashing assignment status "WAITING_FOR_UPDATE_CONDITION" is verified for the vehicles within "600" seconds
            And trigger flashing using protocol "{fota}" Identifier "{fota_identifier}"
            And flashing assignment completing with "UPDATE_SUCCESS" is verified for the vehicles within "600" seconds
        ''')
        context.flashing_iteration -= 1


@step('flashing assignment completing with "{flash_status}" is verified for the vehicles in Campaign "{campaign_count:d}" within "{timer}" seconds')
@step('flashing assignment status "{flash_status}" is verified for the vehicles in Campaign "{campaign_count:d}" within "{timer}" seconds')
@step('flashing assignment completing with "{flash_status}" is verified for the vehicles within "{timer}" seconds')
@step('flashing assignment status "{flash_status}" is verified for the vehicles within "{timer}" seconds')
def step_impl(context, flash_status, timer, campaign_count=None):
    """
        Description: Campaign flashing status is checked

        Pre-condition:  a new campaign "{campaign_detail}" is "{action}"ed

        Parameters: flash_status = <expected flash status>

                        timer = Time till flashing status is checked

        Expected result: Campaign flash status is verified
    """
    context.device_for_fota = []

    vehicle_to_be_flashed = min(int(context.max_parallel_job), len(context.all_vehicle_id))
    context.vehicle_to_be_flashed = vehicle_to_be_flashed
    logging.info(f"Verifying Campaign flashing status - {flash_status} for {vehicle_to_be_flashed} vehicles")

    api_campaign_obj = API_Campaign_Class.ApiCampaignClass(context.env, context.log_api_details)
    
    if campaign_count is None:
        for campaign_id in context.campaign_ids:
            api_campaign_obj.validate_campaign_flash_status(campaign_id, flash_status, vehicle_to_be_flashed, timer, context)
    else:
        api_campaign_obj.validate_campaign_flash_status(context.campaign_ids[campaign_count-1], flash_status, vehicle_to_be_flashed, timer, context)


@step('the assignment from Campaign "{count:d}" in pending "{approval_mode}" is "{action_status}"')
@step('the assignment of Campaign "{count:d}" in pending "{approval_mode}" is "{action_status}" with scheduled time after "{time_stamp}"')
@step('the assignment with pending "{approval_mode}" is "{action_status}" at scheduled time after "{time_stamp}"' )
@step('the assignment in pending "{approval_mode}" is "{action_status}"')
def step_impl(context, approval_mode, action_status, time_stamp=None, count=None):
    """
        Description: Campaign flashing status is checked

        Pre-condition:  a new campaign "{campaign_detail}" is "{action}"ed

        Parameters: flash_status = <expected flash status>

                        timer = Time till flashing status is checked

        Expected result: Campaign flash status is verified
    """
    api_campaign_obj = API_Campaign_Class.ApiCampaignClass(context.env, context.log_api_details)
    moment = {}

    if time_stamp is not None:
        time_stamp = time_stamp.split(':')
        day = int(time_stamp[0])
        hour = int(time_stamp[1])
        minute = int(time_stamp[2])
        planned_schedule = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days= day,hours=hour, minutes=minute,seconds=0)
        start_time = str(planned_schedule).replace(str(planned_schedule)[-9:], "Z")
        moment["schedulingTime"] = start_time.replace(" ","T")
        moment["approvalMessage"] = "scheduled approval" #default message

    if count is None:
        for campaign_id in context.campaign_ids:
            vehicles_list = api_campaign_obj.get_campaign_vehicles_details(campaign_id)
            assignment_id_list = api_campaign_obj.get_assignment_id_in_campaign(campaign_id,vehicles_list)
            api_campaign_obj.approve_or_reject_assignment_in_campaign(assignment_id_list, approval_mode, action_status, moment)
    else:
        vehicles_list = api_campaign_obj.get_campaign_vehicles_details(context.campaign_ids[count-1])
        assignment_id_list = api_campaign_obj.get_assignment_id_in_campaign(context.campaign_ids[count-1],vehicles_list)
        api_campaign_obj.approve_or_reject_assignment_in_campaign(assignment_id_list, approval_mode, action_status, moment)

    
@step('flashing assignments are not created for remaining vehicles of campaign "{campaign_count:d}"')
@step('flashing assignments are not created for remaining vehicles')
def step_impl(context, campaign_count=None):
    """
        Description: Campaign flashing assignment not created check

        Pre-condition:  a new campaign "{campaign_detail}" is "{action}"ed

        Parameters: None

        Expected result: Vehciles with no flashing assignment is checked
    """
    api_campaign_obj = API_Campaign_Class.ApiCampaignClass(context.env, context.log_api_details)

    if campaign_count is None:
        for campaign_id in context.campaign_ids:
            api_campaign_obj.check_vehicle_count(campaign_id, context)

    else:
        api_campaign_obj.check_vehicle_count(context.campaign_ids[campaign_count-1], context)


@step('campaign "{campaign_count:d}" statistics are verified as per campaign "{campaign_detail}"')
@step('campaign statistics are verified as per campaign "{campaign_detail}"')
def step_impl(context, campaign_detail, campaign_count=None):
    """
        Description: Checks the campaign statistics

        Pre-condition:  a new campaign "{campaign_detail}" is "{action}"ed

        Parameters: campaign_detail = campaign name

        Expected result: verifies the actual and expected campaign details
    """
    def verify_campaign_stat_data(expected_json, actual_json):
        exception_list = []
        for key in expected_json.keys():
            try:
                if(expected_json[key] != actual_json[key]):
                    exception_list.append(f"Key: {key}, Exp: {expected_json[key]}, Act: {actual_json[key]}")
            except KeyError as e:
                exception_list.append(f"Value {e} is not found in the response from backend")
        logging.debug(f'Campaign status mismatch list: {exception_list}')
        return exception_list
    
    api_campaign_obj = API_Campaign_Class.ApiCampaignClass(context.env, context.log_api_details)
    
    exp_campaign_stats = context.json_data[campaign_detail]["stats_validation"]
    if campaign_count is None:
        for campaign_id in context.campaign_ids:
            actual_campaign_stats = api_campaign_obj.get_campaign_stats(campaign_id)
            
            exception_list = verify_campaign_stat_data(exp_campaign_stats,actual_campaign_stats["overview"])
            assert len(exception_list) == 0, f'Campaign Status mismatch {exception_list}'
    else:
        actual_campaign_stats = api_campaign_obj.get_campaign_stats(context.campaign_ids[campaign_count-1])
        exception_list = verify_campaign_stat_data(exp_campaign_stats,actual_campaign_stats["overview"])
        assert len(exception_list) == 0, f'Campaign Status mismatch {exception_list}'

@step('verify that "{vehicle_count}" vehicles should be listed for the campaign "{campaign_count:d}"')
@step('verify that "{vehicle_count}" vehicles should be listed for the campaign')
def step_impl(context, vehicle_count, campaign_count=None):
    """
        Description: Checks the expected vehicle count in campaign

        Pre-condition:  a new campaign "{campaign_detail}" is "{action}"ed

        Parameters: vehicle_count = vehicle count to verify

        Expected result: verifies the expected vehicle count in campaign
    """
    api_campaign_obj = API_Campaign_Class.ApiCampaignClass(context.env, context.log_api_details)
    
    # vehicle list takes time to update, in total checks for 60 seconds max. approximately.
    vehicle_list_retry = 10
    while (vehicle_list_retry >= 0):
        campaign_detail = api_campaign_obj.get_campaign_details(context.campaign_name)
        vehicle_list_retry -= 1

        if campaign_count is None:
            for campaign_index in range(len(context.campaign_ids)):
                if (int(vehicle_count) > 0 and int(campaign_detail.json()["_embedded"]["campaigns"][campaign_index]["vehicleCount"]) > 0):
                    assert int(vehicle_count) == int(campaign_detail.json()["_embedded"]["campaigns"][campaign_index]["vehicleCount"]), "Wrong count of vehicles lised for Campaign. Expected Count - %s, Actual Count - %s"%(vehicle_count, campaign_detail.json()["_embedded"]["campaigns"][campaign_index]["vehicleCount"])
            break        
        else:
            if (int(vehicle_count) > 0  and int(campaign_detail.json()["_embedded"]["campaigns"][len(context.campaign_ids)-campaign_count]["vehicleCount"]) > 0):
                assert int(vehicle_count) == int(campaign_detail.json()["_embedded"]["campaigns"][len(context.campaign_ids)-campaign_count]["vehicleCount"]), "Wrong count of vehicles lised for Campaign. Expected Count - %s, Actual Count - %s"%(vehicle_count, campaign_detail.json()["_embedded"]["campaigns"][campaign_count-1]["vehicleCount"])
                break
        time.sleep(6)
    logging.info("Expected count of Vehicles are listed for Dynamic Filter in Campaign")


@step('flashing assignment status "{flash_status}" is verified for the vehicle mapped to "{device}" within "{timer}" seconds')
def step_impl(context, flash_status, device, timer):
    """
        Description: particular vehicle campaign assignment status is checked 

        Pre-condition:  a new campaign "{campaign_detail}" is "{action}"ed

        Parameters: flash_status = flashing status to verify

                            timer = time span to verify

        Expected result: verifies the expected assignment status for a vehicle
    """
    api_campaign_obj = API_Campaign_Class.ApiCampaignClass(context.env, context.log_api_details)

    actual_status = ""
    device_id = context.devices_data[device]["device_name"]

    time_out = time.time() + int(timer)
    while ((time.time() < time_out) and (flash_status not in actual_status) and ("UPDATE_FAILURE" not in actual_status)):
        vehicles_detail = api_campaign_obj.get_campaign_vehicles_details(context.campaign_id)
        for vehicle_detail in vehicles_detail:
            if vehicle_detail['deviceId'] == device_id:
                actual_status = vehicle_detail['assignment']['state']
                if actual_status == flash_status:
                    logging.info("Expected vehicles assignment status appears")
                    break
    
    assert actual_status == flash_status, "Expected flashing status doesn't appear. Actual status - %s, Expected status - %s"%(actual_status, flash_status)


@step('Measurement configuration "{config_name}" is added to the measurement campaign')
@step('Measurement configuration "{config_name}" is added to the measurement campaign "{count:d}"')
def step_impl(context, config_name, count=None):
    """
        Description: Distributiion package is added to particular campaign

        Pre-condition:  a new campaign "{campaign_detail}" is "{action}"ed

        Parameters: config_name = name of distribution package

        Expected result: Distribution package gets assigned to Campaign
    """
    api_campaign_obj = API_Campaign_Class.ApiCampaignClass(context.env, context.log_api_details)

    r = api_campaign_obj.search_rm_configuration_name(config_name)
    assert r.status_code == requests.codes.ok, "Retrieving Distribution package details failed."
    if "_embedded" in r.json():
        rm_config_id = r.json()["_embedded"]["measurementConfigurations"][0]["measurementConfigurationId"]
        context.measurement_configuration_id = rm_config_id
        if count is not None:
            context.rm_config_ids.append(context.measurement_configuration_id)
            context.measurement_configuration_ids = context.rm_config_ids
    else:
        assert False, "Distribution package (Content) - %s not found."%config_name
    
    data = {
            "assignableItem":
            {
                "id":rm_config_id
            }
        }
    
    if count is None:
        for campaign_id in context.campaign_ids:
            api_campaign_obj.add_content_vehicles(campaign_id, data)
    else:
        api_campaign_obj.add_content_vehicles(context.campaign_ids[count-1], data)

@step('Diagnostic configuration "{config_name}" is added to the activation campaign')
@step('Diagnostic configuration "{config_name}" is added to the deactivation campaign')
@step('Diagnostic configuration "{config_name}" is added to the activation campaign "{count:d}"')
@step('Diagnostic configuration "{config_name}" is added to the deactivation campaign "{count:d}"')
def step_impl(context, config_name, count=None):
    """
        Description: Distributiion package is added to particular campaign

        Pre-condition:  a new campaign "{campaign_detail}" is "{action}"ed

        Parameters: config_name = name of distribution package

        Expected result: Distribution package gets assigned to Campaign
    """
    api_campaign_obj = API_Campaign_Class.ApiCampaignClass(context.env, context.log_api_details)
    
    context.diag_config_name = config_name
    r = api_campaign_obj.search_rd_configuration_name(config_name)
    assert r.status_code == requests.codes.ok, "Retrieving Distribution package details failed."
    if "_embedded" in r.json():
        rd_config_id = r.json()["_embedded"]["diagnosticConfigurations"][0]["diagnosticConfigurationId"]
        context.diag_config_id = rd_config_id
    else:
        assert False, "Distribution package (Content) - %s not found."%config_name
    
    data = {
            "assignableItem":
            {
                "id":rd_config_id
            }
        }
    
    if count is None:
        for campaign_id in context.campaign_ids:
            api_campaign_obj.add_content_vehicles(campaign_id, data)
    else:
        api_campaign_obj.add_content_vehicles(context.campaign_ids[count-1], data)


@step('vehicle status inside campaign "{count:d}" is "{vehicle_status}"')
@step('vehicle status inside campaign is "{vehicle_status}"')
def step_impl(context, vehicle_status, count=None):
    """
        Description: Distributiion package is added to particular campaign

        Pre-condition:  a new campaign "{campaign_detail}" is "{action}"ed

        Parameters: config_name = name of distribution package

        Expected result: Distribution package gets assigned to Campaign
    """

    api_campaign_obj = API_Campaign_Class.ApiCampaignClass(context.env, context.log_api_details)

    update_timer = 300
    if count is not None:
        campaign_vehicles = api_campaign_obj.get_campaign_vehicles_details(context.campaign_ids[count-1])
        api_campaign_obj.verify_campaign_vehicles_status(campaign_vehicles, vehicle_status, context.campaign_ids[count-1], update_timer)
    else:
        for campaign_id in context.campaign_ids:
            campaign_vehicles = api_campaign_obj.get_campaign_vehicles_details(campaign_id)
            api_campaign_obj.verify_campaign_vehicles_status(campaign_vehicles, vehicle_status, campaign_id, update_timer)
                

@step('verify vehicle status inside campaign is "{vehicle_status_count}"')
@step('verify vehicle status inside campaign is "{vehicle_status_count}" within "{update_timer}"')
def step_impl(context, vehicle_status_count=None, update_timer=300):
    """
        Description: Distributiion package is added to particular campaign

        Pre-condition:  a new campaign "{campaign_detail}" is "{action}"ed

        Parameters: config_name = name of distribution package

        Expected result: Distribution package gets assigned to Campaign
    """

    api_campaign_obj = API_Campaign_Class.ApiCampaignClass(context.env, context.log_api_details)
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    
    vehicle_status_count_list = vehicle_status_count.split(',')
    for status_count in vehicle_status_count_list:
        status_count_list = status_count.split(':')
        vehicle_status = status_count_list[0]
        count = status_count_list[1]
        actual_count = 0
        index_value = []
        api_gen_obj.update_timeout_time(update_timer)
        api_gen_obj.start_timer()
        while (api_gen_obj.check_timer() == True):
            for campaign_id in context.campaign_ids:
                campaign_vehicles = api_campaign_obj.get_campaign_vehicles_details(campaign_id)
                actual_count = api_campaign_obj.verify_campaign_specific_vehicle_status(vehicle_status, count, actual_count, index_value, campaign_vehicles)

            if int(count) == actual_count:
                api_gen_obj.stop_timer()
                break
        
        assert int(count) == actual_count, f"Actual vehicle count - {actual_count} is not matching with expected vehicle count - {count} for {vehicle_status}"


@step('revoking the vehicle "{vehicle}" from campaign by altering the vehicle "{vehicle_attribute}"')
@step('re-adding the vehicle "{vehicle}" to campaign by altering the vehicle "{vehicle_attribute}"')
def step_impl(context, vehicle, vehicle_attribute):
    """
        Description: re-adding and revoking the vehicles inside campaign by altering the vehicle attributes

        Pre-condition: Vehicles are added/removed from campaign

        Parameters: GEO_POSITIONING - Enabled / Disabled

        Expected result: should be able to re-add and revoke the vehicles inside campaign by altering the vehicle attributes
    """

    vehicle_filter = vehicle_attribute.split("_")
    if vehicle_filter[0] == "GPS":
        vehicle_attribute_option = vehicle_filter[1]
        context.execute_steps(f'''
                Given geo positioning in "{vehicle}" is "{vehicle_attribute_option}"
            ''')


@step('prepare data for multiple device ota update via campaign')
def step_impl(context):
    """ 
        Prepares data for Multiple device update Campaign
        And stores the data to the context variable 
    """
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    api_inventory_obj = API_Inventory_Class.ApiInventoryClass(context.env, context.log_api_details)
    delta_dp_id, full_dp_id = None, None
    
    device_type  = context.devices_data[context.specimen_device]["device_config"]
    env = context.devices_data[context.specimen_device]["device_env"]
    to_version = context.config.userdata["Desired_FW_Version"]
    type_of_update = context.config.userdata["Type_of_update"]
    
    logging.info(f"Fetching devices by device Type: {device_type} and env {env}")
    
    device_list = api_gen_obj.get_similar_devices_from_device_map(device_type, env)
    assert len(device_list) > 0, f"Failed to fetch devices in device map with type {device_type} and env: {env}"
    logging.debug(f"Device List: {device_list}")
    
    device_with_same_ver, device_with_diff_ver = api_inventory_obj.compare_devices_with_matching_version(device_list, context.fw_version, to_version)
    
    logging.info(f" {device_with_same_ver}, {device_with_diff_ver}")
    actual_device_version = context.fw_version.strip(",._DEBUG")
    
    if(type_of_update == "Delta_Update"):
        try:
            context.execute_steps(f'''
                Given check CCU Self update distribution package from "{actual_device_version}" to "{to_version}" available, create if not present
            ''')
            delta_dp_id = context.distribution_package_id.pop()
        except AssertionError as e:
            logging.error(f"Faced error while creating the Delta DP err: {e}, Proceeding with Full update for all devices")
            device_with_diff_ver.extend(device_with_same_ver)
            device_with_same_ver.clear()
            type_of_update = "Full_Update"
    if(type_of_update == "Full_Update") or len(device_with_diff_ver) > 0:
        context.execute_steps(f'''
            Given check CCU Full update "full_update" distribution package to "{to_version}" available, create if not present
        ''')
        full_dp_id = context.distribution_package_id.pop()
    else: assert False, f"Type of update  : {type_of_update} is not supported for multiple devices"
    context.multi_device_update_data = {"Delta_Update": {"device_list": device_with_same_ver, "package": delta_dp_id, "campaign_id": None},
                                        "Full_Update": {"device_list": device_with_diff_ver, "package": full_dp_id, "campaign_id": None }}


@step('perform campaign for multiple device update')
def step_impl(context):
    """
    Performs update of the multiple devices via campaign and performs PEA Update at the end of campaign
    """
    api_campaign_obj = API_Campaign_Class.ApiCampaignClass(context.env, context.log_api_details)
    api_inventory_obj = API_Inventory_Class.ApiInventoryClass(context.env, context.log_api_details)
    api_ota_update_obj = Api_Ota_Updates_Class.ApiOtaUpdatesClass(context.env, context.log_api_details)
    
    if len(context.multi_device_update_data["Delta_Update"]["device_list"]) > 0:
        context.multi_device_update_data["Delta_Update"]["campaign_id"] = api_campaign_obj.create_multiple_device_ota_campaign("Delta_Update_Campaign", context.multi_device_update_data["Delta_Update"]["device_list"], context.multi_device_update_data["Delta_Update"]["package"])
    if len(context.multi_device_update_data["Full_Update"]["device_list"]) > 0:
        context.multi_device_update_data["Full_Update"]["campaign_id"]  = api_campaign_obj.create_multiple_device_ota_campaign("Full_Update_Campaign", context.multi_device_update_data["Full_Update"]["device_list"], context.multi_device_update_data["Full_Update"]["package"])
    logging.info(f'Delta ID: {context.multi_device_update_data["Delta_Update"]["campaign_id"]} and Full Campaign ID: {context.multi_device_update_data["Full_Update"]["campaign_id"]}')
    time_to_wait_min = 30 if context.multi_device_update_data["Delta_Update"]["campaign_id"] != None else 20
    
    context.execute_steps(f'''
            When test waits for "{time_to_wait_min}" minutes
        ''')
    
    for each_device in context.multi_device_update_data["Delta_Update"]["device_list"] + context.multi_device_update_data["Full_Update"]["device_list"]:
        context.execute_steps(f'''
            When task "rebootDevice.zip" is executed on device with id "{each_device}"
        ''')
        
    context.execute_steps('''
        Then verify "EXECUTED" for all tasks within "10" mins
        ''')

    if(context.multi_device_update_data["Delta_Update"]["campaign_id"] != None):
        api_campaign_obj.check_campaign_completion_with_timeout(context.multi_device_update_data["Delta_Update"]["campaign_id"], 45*60)
    if(context.multi_device_update_data["Full_Update"]["campaign_id"] != None):
        api_campaign_obj.check_campaign_completion_with_timeout(context.multi_device_update_data["Full_Update"]["campaign_id"], 30*60)
    
    device_with_failed_update = {}
    
    for each_device in context.multi_device_update_data["Delta_Update"]["device_list"] + context.multi_device_update_data["Full_Update"]["device_list"]:
        sw_version = api_inventory_obj.get_device_inventory(each_device)['_embedded']['inventoryItemList'][0]['swVersion']
        if(context.config.userdata["Desired_FW_Version"] not in sw_version):
            device_with_failed_update[each_device] = sw_version
    
    pea_update_package = api_ota_update_obj.search_distribution_package(constants.PEA_UPDATE_PACKAGE)
    pea_campaign_id = api_campaign_obj.create_multiple_device_ota_campaign("PEA_Update_Campaign", context.multi_device_update_data["Delta_Update"]["device_list"] + context.multi_device_update_data["Full_Update"]["device_list"], pea_update_package)
    pea_update_status = api_campaign_obj.check_campaign_completion_with_timeout(pea_campaign_id, 5*60)
    assert pea_update_status == True and len(device_with_failed_update) == 0, f"Failed to finish the PEA Update of the campaign {pea_campaign_id} at the last step / Update failed for devices {device_with_failed_update}, please check logs"