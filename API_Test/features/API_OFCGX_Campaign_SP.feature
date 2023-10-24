Feature: Enable Campaign Management for RM and RD in OTA Service UI
    @E2E-API @E2E-CCU @E2E-SP @E2E-RD @E2E-Regression @E2E-HINO
    Scenario Outline:RD_CM_CCU_API_SP - Create two activation campaign for same RD config with different version
        Given device <device> is "ONLINE"
        And create <vehicle> if it is not available
        And create device slot <device_slot> for <vehicle> vehicle
        And map device to <device_slot> slot of vehicles
        | vehicle_name           | device|
        | AUT_CM_TEST_Vehicle_10 | CCU   |

        When "2" new Campaigns <RD_Activation_Campaign_Detail> are "add"ed
        And RD activation campaign "1" status "CREATED" is verified
        And Diagnostic configuration <diagConfigName> is added to the activation campaign "1"
        And vehicles <vehicle> are added to the "RD activation" campaign "1" using static list
        And verify that "1" vehicles should be listed for the campaign "1"
        And "RD activation" campaign "1" is "schedule"ed
        And RD activation campaign "1" status "RUNNING" is verified
        And diagnostic configuration state of <vehicle> is "ACTIVE" for "RD activation" campaign
        And test is executed for "0.5" minutes
        And vehicle status inside campaign "1" is "ACTIVATION_CONFIRMED"
        And RD activation campaign "1" status "FINISHED" is verified
        And campaign "1" statistics are verified as per campaign <RD_Activation_Campaign_Detail>

        And editing diagnostic configuration is triggered
        And state of diagnostic configuration is "Draft"
        And release diagnostic configuration, if not in RELEASED state

        And RD activation campaign "2" status "CREATED" is verified
        And Diagnostic configuration <diagConfigName> is added to the activation campaign "2"
        And vehicles <vehicle> are added to the "RD activation" campaign "2" using static list
        And verify that "1" vehicles should be listed for the campaign "2"
        And "RD activation" campaign "2" is "schedule"ed
        And RD activation campaign "2" status "RUNNING" is verified
        And diagnostic configuration state of <vehicle> is "ACTIVE" for "RD deactivation" campaign
        And test is executed for "0.5" minutes
        And vehicle status inside campaign "2" is "ACTIVATION_FAILED"
        And campaign "2" statistics are verified as per campaign <RD_Activation_Campaign_Detail_1>

        Examples: 
		| vehicle                      | device | device_slot  | diagConfigName          | RD_Activation_Campaign_Detail | RD_Activation_Campaign_Detail_1 |
		| "AUT_CM_TEST_Vehicle_10"     | "CCU"  | "CCU"        | "SYS-I-001-job_success" | "RD_Activation_campaign_3"    | "RD_Activation_campaign_4"      |