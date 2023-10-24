Feature: Enable Campaign Management for RM and RD in OTA Service UI
    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Smoke @E2E-HINO
    Scenario Outline:RD_CM_CCU_API_HP - Create campaign for RD configuration
        Given device <device> is "ONLINE"
        And device <device2> is "ONLINE"
        And create <vehicles> if it is not available
        And create device slot <device_slot> for "AUT_CM_TEST_Vehicle_10" vehicle
        And create device slot <device_slot> for "AUT_CM_TEST_Vehicle_11" vehicle
        And map device to <device_slot> slot of vehicles
        | vehicle_name           | device|
        | AUT_CM_TEST_Vehicle_10 | CCU   |
        | AUT_CM_TEST_Vehicle_11 | CCU2  |
        And reference system <Protocol> with Identifier <Identifier> is started for <device> device
        And reference system <Protocol> with Identifier <Identifier> is started for <device2> device
        
        When a new campaign <RD_Activation_Campaign_Detail> is "add"ed
        And RD activation campaign status "CREATED" is verified
        And Diagnostic configuration <diagConfigName> is added to the activation campaign
        And vehicles <vehicles> are added to the "RD activation" campaign using static list
        And verify that "2" vehicles should be listed for the campaign
        And "RD activation" campaign is "schedule"ed
        And RD activation campaign status "RUNNING" is verified
        And diagnostic configuration state of <vehicles> is "ACTIVE" for "RD activation" campaign
        And RD activation campaign status "FINISHED" is verified
        And campaign statistics are verified as per campaign <RD_Activation_Campaign_Detail>
        And adhoc Read All DTCs is triggered for <vehicles>
        Then adhoc Read All DTCs is generated within "10" minutes

        When a new campaign <RD_Deactivation_Campaign_Detail> is "add"ed
        And RD deactivation campaign status "CREATED" is verified
        And Diagnostic configuration <diagConfigName> is added to the deactivation campaign
        And vehicles <vehicles> are added to the "RD deactivation" campaign using static list
        And verify that "2" vehicles should be listed for the campaign
        And "RD deactivation" campaign is "schedule"ed
        And RD deactivation campaign status "RUNNING" is verified
        And diagnostic configuration state of <vehicles> is "INACTIVE" for "RD deactivation" campaign
        And RD deactivation campaign status "FINISHED" is verified
        And campaign statistics are verified as per campaign <RD_Deactivation_Campaign_Detail>
        
        And reference system is stopped
        And latest DTC status for <vehicles> is verified
		    | Status | Code  | 
		    | AC     | A9C17 | 
		    | AC     | 80522 |

        Examples: 
		| vehicles                                             | device | device2 | device_slot | diagConfigName          | Protocol   | Identifier          | RD_Activation_Campaign_Detail   | RD_Deactivation_Campaign_Detail   |
		| "AUT_CM_TEST_Vehicle_10,AUT_CM_TEST_Vehicle_11"      | "CCU"  | "CCU2"  | "CCU"       | "SYS-I-001-job_success" | "UDSonCAN" | "UDS_Resp_2DTCs_RD" | "RD_Activation_campaign_1"      | "RD_Deactivation_campaign_1"      |



    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression @E2E-HINO
    Scenario Outline:RD_CM_CCU_API_HP - Validate timeout while creating Activation campaign for RD config with 'maxRunningAssignments' as 1
        Given device <device> is "ONLINE"
        And device <device2> is "ONLINE"
        And create <vehicles> if it is not available
        And create device slot <device_slot> for "AUT_CM_TEST_Vehicle_10" vehicle
        And delete DTC if present
        And create device slot <device_slot> for "AUT_CM_TEST_Vehicle_11" vehicle
        And delete DTC if present
        And map device to <device_slot> slot of vehicles
            | vehicle_name           | device|
            | AUT_CM_TEST_Vehicle_10 | CCU   |
            | AUT_CM_TEST_Vehicle_11 | CCU2  |
        And reference system <Protocol> with Identifier <Identifier> is started for <device> device
        And reference system <Protocol> with Identifier <Identifier> is started for <device2> device
        
        When a new campaign <RD_Activation_Campaign_Detail> is "add"ed
        And RD activation campaign status "CREATED" is verified
        And Diagnostic configuration <diagConfigName> is added to the activation campaign
        And vehicles <vehicles> are added to the "RD activation" campaign using static list
        And verify that "2" vehicles should be listed for the campaign
        And command to "stopGSMConnection" GSM mode for "all" the device
        And wait for device <device> to be "OFFLINE"
        And wait for device <device2> to be "OFFLINE"
        And "RD activation" campaign is "schedule"ed
        And RD activation campaign status "RUNNING" is verified
        And verify vehicle status inside campaign is "IN_ACTIVATION:1, :1"
        And command to "startGSMConnection" GSM mode for <device> the device
        And wait for device <device> to be "ONLINE"
        And verify vehicle status inside campaign is "IN_ACTIVATION:1,ACTIVATION_CONFIRMED:1"
        And command to "startGSMConnection" GSM mode for <device2> the device
        And wait for device <device2> to be "ONLINE"
        
        And diagnostic configuration state of <vehicles> is "ACTIVE" for "RD activation" campaign
        And RD activation campaign status "FINISHED" is verified
        And campaign statistics are verified as per campaign <RD_Activation_Campaign_Detail>
        And adhoc Read All DTCs is triggered for <vehicles>
        Then adhoc Read All DTCs is generated within "10" minutes

        And deactivate ACTIVE diagnostic configuration if present for <vehicles>
        And diagnostic configuration state of <vehicles> is "INACTIVE"
        And reference system is stopped
        And latest DTC status for <vehicles> is verified
            | Status | Code  |
            | AC     | A9C17 |
            | AC     | 80522 |

        Examples: 
		| vehicles                                            | device | device2 | device_slot | diagConfigName          | Protocol   | Identifier          | RD_Activation_Campaign_Detail |
		| "AUT_CM_TEST_Vehicle_10,AUT_CM_TEST_Vehicle_11"     | "CCU"  | "CCU2"  | "CCU"       |"SYS-I-001-job_success"  | "UDSonCAN" | "UDS_Resp_2DTCs_RD" | "RD_Activation_campaign_2"    |
        