import requests
import logging
import urllib3
import logging
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time
import steps.utils.API_Requests as API_Request
import steps.pageObjects.API_Generic_Class as API_Generic_Class
import steps.pageObjects.API_FleetManagement_Class as API_FleetManagement_Class
import steps.constantfiles.constants_campaign as constants
import steps.constantfiles.constants_fleetmanagement as constantsfm

class ApiCampaignClass:
    def __init__ (self, environment, log_api_details):
        self.api_requests = API_Request.ApiRequestsClass(environment, log_api_details)
        self.api_fleet_obj = API_FleetManagement_Class.ApiFleetManagementClass(environment, log_api_details)
        self.api_gen_obj = API_Generic_Class.ApiGenericClass()

    def add_campaign(self, data):
        r = self.api_requests.post_request(constants.RFC_CAMPAIGNS, data)
        assert r.status_code == requests.codes.created, self.api_gen_obj.assert_message(r)
        return r.json()["campaignId"]

    def get_campaign_details(self, campaign_name):
        r = self.api_requests.get_request(constants.RFC_CAMPAIGNS_SEARCH_NAME.format(campaign_name))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r

    def edit_campaign(self, campaign_name, data):
        campaign_detail = self.get_campaign_details(campaign_name)
        campaign_id = campaign_detail.json()["_embedded"]["campaigns"][0]["campaignId"]

        etag = self.api_requests.get_etag(constants.RFC_CAMPAIGNS_ID.format(campaign_id))
        r = self.api_requests.put_request(constants.RFC_CAMPAIGNS_ID.format(campaign_id), params=data, custom_header={'if-match': etag})
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r.json()["campaignId"]

    def search_rm_configuration_name(self, config_name):
        ep = constants.RM_CONFIG_NAME.format(config_name)
        r = self.api_requests.get_request(ep=ep)
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r

    def search_rd_configuration_name(self, config_name):
        ep = constants.RD_CONFIG_NAME.format(config_name)
        r = self.api_requests.get_request(ep=ep)
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r

    def add_content_vehicles(self, campaign_id, data):
        #same function add_config_and_vehicle in API_RM_Campaign_Class
        etag = self.api_requests.get_etag(constants.RFC_CAMPAIGNS_ID.format(campaign_id))
        r = self.api_requests.put_request(constants.RFC_CAMPAIGNS_ID.format(campaign_id), params=data, custom_header={'if-match': etag})
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)

    def add_slot_to_campaign(self, campaign_id, vehicle_data, vehicles):
        campaign_slot_name = vehicle_data[vehicles[0]]["device_data"]["slot_name"]
        for vehicle in vehicles:
            slot_name = vehicle_data[vehicle]["device_data"]["slot_name"]
            #have to add proper assert message
            assert campaign_slot_name == slot_name, f"{vehicle_data[vehicle]} slot name is different from {vehicle_data[vehicles[0]]}"
        ep = constants.RFC_CAMPAIGNS_ID.format(campaign_id)
        data = {
                "devicePairing": 
                {
                    "deviceSlot": campaign_slot_name
                }
            }
        etag = self.api_requests.get_etag(constants.RFC_CAMPAIGNS_ID.format(campaign_id))
        r = self.api_requests.put_request(ep, params=data, custom_header={'if-match': etag})
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return campaign_slot_name

    def post_campaign_action(self, campaign_id, campaign_action):
        etag = self.api_requests.get_etag(constants.RFC_CAMPAIGNS_ID.format(campaign_id))

        r = self.api_requests.post_request(constants.RFC_CAMPAIGNS_ID_ACTION.format(campaign_id,campaign_action), params={}, custom_header={'if-match': etag})
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)

    def get_campaign_vehicles_details(self, campaign_id):
        time.sleep(5) #added hard-wait as sometimes Assignment details take time to populate in Campaign section
        r = self.api_requests.get_request(constants.RFC_CAMPAIGNS_ID_VEHICLE.format(campaign_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r.json()["_embedded"]["vehicles"]

    def get_assignment_id_in_campaign(self, campaign_id, vehicle_list):
        r = self.api_requests.get_request(constants.RFC_CAMPAIGNS_ID_VEHICLE.format(campaign_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        """ Created a list to store all the assignment id for each vehicle using list comprehension """
        return [r.json()["_embedded"]["vehicles"][index]["assignmentId"] for index in range(0,len(vehicle_list))] 

    def approve_or_reject_assignment_in_campaign(self,assignment_id_list,approval_mode,action_status, pay_load): 
        json_data = self.api_gen_obj.parse_json_file(constants.CAMPAIGN_JSON_PATH)
        campaign_approve_or_reject = json_data["campaign_action_parameters"]
        for assignment_id in assignment_id_list:
            each_header = {}

            r_etag = self.api_requests.get_etag(constants.RFC_OTA_ID.format(assignment_id))
            each_header['if-match'] = r_etag
            logging.info(f"Generated ETAG = {r_etag} for responding to pending {approval_mode} assignments")

            for action,end_point in campaign_approve_or_reject.items():
                if action == approval_mode+'_'+action_status:
                    r = self.api_requests.post_request(constants.RFC_OTA_ID_EP.format(assignment_id,end_point), params=pay_load, custom_header=each_header)
                    assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
            
    def is_campaign_state(self, campaign_id, campaign_state, timer):
        state = ""
        timer = int(timer)*60
        
        while (timer > 0):
            r = self.api_requests.get_request(constants.RFC_CAMPAIGNS_ID.format(campaign_id))
            assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
            state = r.json()["state"]
            
            if (state == campaign_state):
                logging.info(f"Expected Campaign state - {state} appears.")
                return True, state
            elif campaign_state == "RUNNING" and state == "FINISHED":
                logging.info("Campaign status already reached FINISHED so making this step pass")
                campaign_state = "FINISHED"
            else:
                time.sleep(5)
                timer -= 5
        
        if (campaign_state == state):
            return True, state
        else:
            logging.info(f"Unexpected Campaign state appears. Actual State - {state}, Expected State - {campaign_state}")
            return False, state


    def verify_campaign_flash_status(self, campaign_id, exp_flash_status, vehicle_to_be_flashed, timer, context):

        vehicles_flash_status = []
        is_campaign_parallel_job = False
        flashing_repeat = 1

        vehicles_len = self.get_campaign_vehicles_details(campaign_id)
        if (vehicle_to_be_flashed < len(vehicles_len)):
            is_campaign_parallel_job = True 
            flashing_repeat = len(vehicles_len)/vehicle_to_be_flashed
        for vehicle_index in range(0,len(vehicles_len)):
            flash_status = self.get_vehicle_ota_status(campaign_id, vehicle_index, exp_flash_status, timer)
            if flash_status is not None:
                vehicles_flash_status.append(flash_status)

        if (is_campaign_parallel_job and exp_flash_status == "UPDATE_SUCCESS"):
            if (context.flashing_iteration > 2):
                assert len(vehicles_flash_status) == vehicle_to_be_flashed*((context.number+1-context.flashing_iteration)+1), f"Simultaneous Flashing for Wrong count of vehicle. Expected vehicle count- {vehicle_to_be_flashed*((context.number+1-context.flashing_iteration)+1)}, Actual Vehicle Count - {len(vehicles_flash_status)}"
            else:
                assert len(vehicles_flash_status) == vehicle_to_be_flashed*flashing_repeat, f"Simultaneous Flashing for Wrong count of vehicle. Expected vehicle count- {vehicle_to_be_flashed*flashing_repeat}, Actual Vehicle Count - {len(vehicles_flash_status)}"
        else:
            if (context.flashing_iteration > 1):
                assert len(vehicles_flash_status) == vehicle_to_be_flashed*(context.number+1-context.flashing_iteration), f"Simultaneous Flashing for Wrong count of vehicle. Expected vehicle count- {vehicle_to_be_flashed*(context.number+1-context.flashing_iteration)}, Actual Vehicle Count - {len(vehicles_flash_status)}"
            else:
                assert len(vehicles_flash_status) == vehicle_to_be_flashed*flashing_repeat, f"Simultaneous Flashing for Wrong count of vehicle. Expected vehicle count- {vehicle_to_be_flashed*flashing_repeat}, Actual Vehicle Count - {len(vehicles_flash_status)}"

        return vehicles_flash_status


    def get_vehicle_ota_status(self, campaign_id, index, exp_ota_status, timer):
        status_list = []
        vehicle_flash_status = {}

        time_out = time.time() + int(timer)
        while ((time.time() < time_out) and ("UPDATE_FAILURE" not in status_list) and ("UPDATE_SUCCESS" not in status_list) and ("DOWNLOAD_FAILURE" not in status_list)):
            vehicles_detail = self.get_campaign_vehicles_details(campaign_id)
            connected_device = vehicles_detail[index]["deviceId"]
            if "assignment" in vehicles_detail[index]:
                state = vehicles_detail[index]["assignment"]["state"]
                if state not in status_list:
                    logging.info(f"New flash status - %s for vehicle - %s appears."%(state, vehicles_detail[index]["vehicleId"]))
                    status_list.append(state)
                    if state == exp_ota_status:
                        logging.info(f"Expected assignment flash status appears for vehicle - {(index+1)}")
                        break
                else:
                    time.sleep(1)
            else:
                logging.info("Assignment status for vehicle - %s. %s doesn't exist."%(index+1, vehicles_detail[index]["vehicleId"]))
                break
        
        if ((time.time() > time_out) or (exp_ota_status in status_list) or ("UPDATE_FAILURE" in status_list) or ("UPDATE_SUCCESS" in status_list) or ("DOWNLOAD_FAILURE" in status_list)):
            vehicle_flash_status[connected_device] = status_list
            return vehicle_flash_status


    def get_campaign_stats(self, campaign_id):
        r = self.api_requests.get_request(constants.RFC_OTA_ID_STATISTICS.format(campaign_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r.json()

    def get_campaign_target_statistics(self, campaign_id):
        """Gets the Target statistics of a campaign

        Args:
            campaign_id (str): UUID of campaign

        Returns:
            dict: Campaign target statistics
        """
        r = self.api_requests.get_request(constants.CAMPAIGN_TARGET_STATISTICS.format(campaign_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r.json()
    
    def validate_campaign_flash_status(self, campaign_id, flash_status, vehicle_to_be_flashed, timer, context):
        count = 0

        campaign_ota_status = self.verify_campaign_flash_status(campaign_id, flash_status, vehicle_to_be_flashed, timer, context)
        logging.info(f"Flashing status list for all the vehicles in Campaign - {campaign_id} are - {campaign_ota_status} ")

        for all_vehicles_ota_status in campaign_ota_status:
            for device_name, each_flash_status in all_vehicles_ota_status.items():
                if flash_status in each_flash_status:
                    count += 1
                    context.device_for_fota.append(device_name)
        
        campaign_stats = self.get_campaign_stats(campaign_id)
        logging.info("Campaign current flashing Statistics (After flashing Iteration - %s) - "%(context.number+1-context.flashing_iteration))
        logging.info(campaign_stats["overview"])

        assert count >= 1, f"None of the vehicles flashing status reached expected status - {flash_status}"

        if (context.flashing_iteration == 1 and flash_status == "UPDATE_SUCCESS"):
            for each_device_status in all_vehicles_ota_status.values():
                assert "UPDATE_SUCCESS" in each_device_status, "Not all the RF vehicle status reached UPDATE_SUCCESS"

    
    def check_vehicle_count(self, campaign_id, context):
        logging.info(f"Checking vehicle count whose flash assigments are not triggered owing to Maximum Parallel Job limit in Campaign - {campaign_id}")
        exp_vehicle_no_rf = len(context.all_vehicle_id) - context.vehicle_to_be_flashed
        campaign_stats = self.get_campaign_stats(campaign_id)
        act_vehicle_no_rf = campaign_stats.json()["overview"]["notStarted"]
        assert exp_vehicle_no_rf == act_vehicle_no_rf, "Unexpected. Additional vehicle's Remote flashing is triggered. Actual vehicle RF halt - %s, Expected vehicle RF halt - %s"%(act_vehicle_no_rf, exp_vehicle_no_rf)
        logging.info("Expected count of vehicle's RF is triggered as per Maximum Parallel job condition in Campaign.")

    def add_vehicle_to_ota_campaign(self, count, data, campaign_ids):
        if count is None :
            for campaign_id in campaign_ids:
                self.add_content_vehicles(campaign_id, data)
        else:
            self.add_content_vehicles(campaign_ids[count-1], data)

    def add_vehicle_to_rm_rd_campaign(self, count, data, vehicle_list, vehicle_data, campaign_ids):
        vehicles = vehicle_list.split(",")
        if count is None:
            for campaign_id in campaign_ids:
                campaign_slot_name = self.add_slot_to_campaign(campaign_id, vehicle_data, vehicles)
                self.add_content_vehicles(campaign_id, data)
        else:
            campaign_slot_name = self.add_slot_to_campaign(campaign_ids[count-1], vehicle_data, vehicles)
            self.add_content_vehicles(campaign_ids[count-1], data)

        return campaign_slot_name

    def get_campaign_vehicles_id(self, campaign_id):
        campaign_vehicles = self.get_campaign_vehicles_details(campaign_id)
        """ Created a list to store all the vehicle id for each campaign using list comprehension """
        return [campaign_vehicles[index]["vehicleId"] for index in range(len(campaign_vehicles))]

    def get_status_campaign_vehicles(self, campaign_id):
        r = self.api_requests.get_request(constants.RFC_CAMPAIGNS_ID_VEHICLE.format(campaign_id))
        assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
        return r

    def get_campaign_vehicles_name(self, campaign_id):
        campaign_vehicles = self.get_campaign_vehicles_details(campaign_id)
        campaign_vehicles_name = []
        for index in range(0,len(campaign_vehicles)):
            vehicle_id = campaign_vehicles[index]["vehicleId"]
            r = self.api_requests.get_request(constantsfm.FM_VEHICLES_ID.format(vehicle_id))
            assert r.status_code == requests.codes.ok, self.api_gen_obj.assert_message(r)
            campaign_vehicles_name.append(r.json()["name"])
        return campaign_vehicles_name

    def get_campaign_vehicle_state(self, campaign_id, index):
        campaign_vehicles = self.get_campaign_vehicles_details(campaign_id)
        campaign_vehicle_state = campaign_vehicles[index]["assignment"]["state"]
        return campaign_vehicle_state

    def verify_campaign_vehicles_status(self, campaign_vehicles, vehicle_status, campaign_id, timer):
        self.api_gen_obj.update_timeout_time(timer)
        self.api_gen_obj.start_timer()
        while (self.api_gen_obj.check_timer() == True):
            actual_vehicle_status = set()
            for index in range(len(campaign_vehicles)):
                campaign_vehicle_state = self.get_campaign_vehicle_state(campaign_id, index)
                actual_vehicle_status.add(campaign_vehicle_state)
            time.sleep(10)
            if len(actual_vehicle_status) == 1 and next(iter(actual_vehicle_status)) == vehicle_status:
                self.api_gen_obj.stop_timer()
                break

        if self.api_gen_obj.check_timer() == False:
            if len(actual_vehicle_status) > 1 and len(campaign_vehicles) >=2 :
                assert False, f"One or more vehicles assignment status mismatch. Actual: {actual_vehicle_status}, Expected: {vehicle_status}"
            elif len(actual_vehicle_status) == 1 and next(iter(actual_vehicle_status)) != vehicle_status:
                assert False, f"Vehicle assignment status mismatch. Actual: {actual_vehicle_status}, Expected: {vehicle_status}"

    def verify_campaign_specific_vehicle_status(self, vehicle_status, count, actual_count, index_value, campaign_vehicles):
        for index in range(0,len(campaign_vehicles)):
            if "assignment" in campaign_vehicles[index]:
                vehicle_status_act = campaign_vehicles[index]["assignment"]["state"]
                if vehicle_status_act == vehicle_status and int(count) != actual_count and index not in index_value:
                    actual_count += 1
                    index_value.append(index)
            else:
                if " " == vehicle_status and int(count) != actual_count and index not in index_value:
                    actual_count += 1
                    index_value.append(index)

        return actual_count
    
    def create_multiple_device_ota_campaign(self, campaign_name, device_list, package_id):
        """Creates a Device Campaign with the provided details and Distribution package.
            The campaign will be auto scheduled
        Args:
            campaign_name (str): Name of the campaign
            device_list (list): list of devices that will be added in the campaign
            package_id (str): uuid of the distribution package

        Returns:
            str: UUID of campaign
        """
        campaign_data ={
            "name":campaign_name,
            "type":"OTA_ASSIGNMENT",
            "maxRunningAssignments":"100",
            "assignableItem":{"id":package_id},
            "targetType": "DEVICE",
            "targetIds": device_list,
            "autoSchedule": True
        }
        return self.add_campaign(campaign_data)
    
    def check_campaign_completion_with_timeout(self, campaign_id, timer_sec: int):
        """Checks the campaign finished status with timeout for a specific campaign

        Args:
            campaign_id (str): uuid of campaign
            timer_sec (int): time in seconds

        Returns:
            Bool: True if campaign is completed within the specified time, else false
        """
        self.api_gen_obj.update_timeout_time(timer_sec)
        self.api_gen_obj.start_timer()
        finished_flag = False
        while (self.api_gen_obj.check_timer() == True):
            statistic = self.get_campaign_target_statistics(campaign_id)
            if statistic["overview"]["totalTargets"] == statistic["overview"]["finished"]:
                if(statistic["overview"]["finished"] != statistic["overview"]["successful"]):
                    logging.error(f"Not all assignment for the campaign were successful stat: {statistic['overview']}")
                self.api_gen_obj.stop_timer()
                finished_flag = True
                break
        if not finished_flag:
            logging.error(f"Campaign with id {campaign_id} wasn't finished by end of provided time")
            logging.info(f"Current statistics: {statistic['overview']} ")
        return finished_flag