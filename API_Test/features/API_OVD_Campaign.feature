Feature: Enable Campaign Management for RM and RD in OTA Service UI
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CM_CCU_API_HP - Re-adding and revoking the vehicles in RM Campaign
        Given device <device> is "ONLINE"
        And device <device2> is "ONLINE"
        And create <vehicles> if it is not available
        And create device slot <device_slot> for <first_vehicle> vehicle
        And create device slot <device_slot> for <second_vehicle> vehicle
        And map device to <device_slot> slot of vehicles
                | vehicle_name              | device | 
                | AUT_RM_CM_TEST_Vehicle_15 | CCU    | 
                | AUT_RM_CM_TEST_Vehicle_16 | CCU2   |
        And geo positioning in <vehicles> is enabled        
        And reference system <Protocol> with Identifier <Identifier> is started for <device> device
        And reference system <Protocol> with Identifier <Identifier> is started for <device2> device
        And a new campaign <RM_Campaign_Detail_1> is "add"ed
        And Measurement configuration <meas_config_name> is added to the measurement campaign
        And vehicles <vehicles> are added to the "REMOTE_MEASUREMENT" campaign using dynamic filter <vehicle_filter>
        And verify that "2" vehicles should be listed for the campaign
        And "REMOTE_MEASUREMENT" campaign is "schedule"ed
        And measurement campaign status "RUNNING" is verified
        And vehicle status inside campaign is "ACTIVATION_CONFIRMED"
        And campaign statistics are verified as per campaign <RM_Campaign_Detail_1>
        And revoking the vehicle <second_vehicle> from campaign by altering the vehicle <vehicle_attribute2>
        And verify that "2" vehicles should be listed for the campaign
        And verify vehicle status inside campaign is "ACTIVATION_CONFIRMED:1,DEACTIVATION_CONFIRMED:1"
        And campaign statistics are verified as per campaign <RM_Campaign_Detail_2>
        And re-adding the vehicle <second_vehicle> to campaign by altering the vehicle <vehicle_attribute1>
        And verify that "2" vehicles should be listed for the campaign
        And vehicle status inside campaign is "ACTIVATION_CONFIRMED"
        And campaign statistics are verified as per campaign <RM_Campaign_Detail_1>
        When "REMOTE_MEASUREMENT" campaign is "abort"ed
        And measurement campaign status "ABORTED" is verified
        And vehicle status inside campaign is "DEACTIVATION_CONFIRMED"
        And campaign statistics are verified as per campaign <RM_Campaign_Detail_3>
        And reference system is stopped
        And measurement test results are stored for RM campaign <RM_Campaign_Detail_1>
        And measurement data integrity smoke test is performed for RM campaign

            Examples: 
                | vehicles                                              | first_vehicle               | second_vehicle              | device | device2 | RM_Campaign_Detail_1 | RM_Campaign_Detail_2 | RM_Campaign_Detail_3 | device_slot | meas_config_name       | Protocol   | Identifier                     | vehicle_filter           | vehicle_attribute1 | vehicle_attribute2 | 
                | "AUT_RM_CM_TEST_Vehicle_15,AUT_RM_CM_TEST_Vehicle_16" | "AUT_RM_CM_TEST_Vehicle_15" | "AUT_RM_CM_TEST_Vehicle_16" | "CCU"  | "CCU2"  | "RM_campaign_1"      | "RM_campaign_2"      | "RM_campaign_3"      | "CAMPAIGN6"  | "E2E_CAN_RAW_MON_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" | "geoPositioning_Enabled" | "GPS_ENABLED"      | "GPS_DISABLED"     |
    
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CM_CCU_API_HP - Performing RM on multiple Campaign with same vehicles and different configuration
        Given device <device> is "ONLINE"
        And create <vehicles> if it is not available
        And create device slot <device_slot> for <vehicles> vehicle
        And map device to <device_slot> slot of vehicles
        | vehicle_name               | device  |
        | AUT_RM_CM_TEST_Vehicle_15  | CCU     |
        And geo positioning in <vehicles> is enabled
        And reference system <Protocol> with Identifier <Identifier> is started for <device> device

        When "2" new Campaigns <RM_Campaign_Detail_4> are "add"ed
        And measurement campaign "1" status "CREATED" is verified
        And measurement campaign "2" status "CREATED" is verified
        And Measurement configuration <meas_config_name_1> is added to the measurement campaign "1"
        And vehicles <vehicles> are added to the "REMOTE_MEASUREMENT" campaign "1" using dynamic filter <vehicle_filter>
        And verify that "1" vehicles should be listed for the campaign "1"
        And vehicles <vehicles> are added to the "REMOTE_MEASUREMENT" campaign "2" using dynamic filter <vehicle_filter>
        And verify that "1" vehicles should be listed for the campaign "2"
        And "REMOTE_MEASUREMENT" campaign "1" is "schedule"ed
        And Measurement configuration <meas_config_name_2> is added to the measurement campaign "2"
        And "REMOTE_MEASUREMENT" campaign "2" is "schedule"ed
        And measurement campaign "1" status "RUNNING" is verified
        And vehicle status inside campaign "1" is "ACTIVATION_CONFIRMED"
        And measurement status on campaign <RM_Campaign_Detail_4> vehicle <vehicles> device slot <device_slot> is "ACTIVE" with substatus "ACTIVATION_CONFIRMED" and target status is "ACTIVE"
        And campaign "1" statistics are verified as per campaign <RM_Campaign_Detail_4>
        And measurement campaign "2" status "RUNNING" is verified
        And vehicle status inside campaign "2" is "ACTIVATION_CONFIRMED"
        And campaign "2" statistics are verified as per campaign <RM_Campaign_Detail_4>
        And measurement status for configuration <meas_config_name_1> is "ACTIVE" within "10" minutes
        And measurement status for configuration <meas_config_name_2> is "ACTIVE" within "10" minutes

        When "REMOTE_MEASUREMENT" campaign "2" is "abort"ed
        And measurement campaign "2" status "ABORTED" is verified
        And vehicle status inside campaign "2" is "DEACTIVATION_CONFIRMED"
        And measurement status for configuration <meas_config_name_2> is "INACTIVE" within "10" minutes
        And measurement status for configuration <meas_config_name_1> is "ACTIVE" within "10" minutes
        And campaign "2" statistics are verified as per campaign <RM_Campaign_Detail_5>

        When "REMOTE_MEASUREMENT" campaign "1" is "abort"ed
        And measurement campaign "1" status "ABORTED" is verified
        And vehicle status inside campaign "1" is "DEACTIVATION_CONFIRMED"
        And measurement status for configuration <meas_config_name_1> is "INACTIVE" within "10" minutes
        And measurement status for configuration <meas_config_name_2> is "INACTIVE" within "10" minutes
        And campaign "1" statistics are verified as per campaign <RM_Campaign_Detail_5>

        And reference system is stopped
        And measurement test results are stored for RM campaign <RM_Campaign_Detail_4>
        And measurement data integrity smoke test is performed for RM campaign

        Examples: 
            | vehicles                    | device   | RM_Campaign_Detail_4 | RM_Campaign_Detail_5 |  device_slot  | meas_config_name_1       | meas_config_name_2                  | Protocol   | Identifier                       | vehicle_filter           |
            | "AUT_RM_CM_TEST_Vehicle_15" |  "CCU"   | "RM_campaign_4"      | "RM_campaign_5"      |  "CAMPAIGN6"  |"E2E_CAN_RAW_MON_500K"    |"E2E_RM_ENHANCE_TRIGGER_DEMO_500K"   | "MONonCAN" | "MONonCAN_500k_highloadidents"   | "geoPositioning_Enabled" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CM_CCU_API_HP - Perform Campaign with setting the max parallel job as 1
        Given device <device> is "ONLINE"
        And device <device2> is "ONLINE"
        And create <vehicles> if it is not available
        And create device slot <device_slot> for <first_vehicle> vehicle
        And create device slot <device_slot> for <second_vehicle> vehicle
        And map device to <device_slot> slot of vehicles
        | vehicle_name            | device |
        | AUT_CM_TEST_Vehicle_05  | CCU    |
        | AUT_CM_TEST_Vehicle_06  | CCU2   |
        And geo positioning in <vehicles> is enabled
        And reference system <Protocol> with Identifier <Identifier> is started for <device> device
        And reference system <Protocol> with Identifier <Identifier> is started for <device2> device

        And a new campaign <RM_Campaign_Detail_7> is "add"ed
        And measurement campaign status "CREATED" is verified
        And Measurement configuration <meas_config_name> is added to the measurement campaign
        And vehicles <vehicles> are added to the "REMOTE_MEASUREMENT" campaign using dynamic filter <vehicle_filter>
        And verify that "2" vehicles should be listed for the campaign

        And command to "stopGSMConnection" GSM mode for "all" the device
        And wait for device <device> to be "OFFLINE"
        And wait for device <device2> to be "OFFLINE"
        And "REMOTE_MEASUREMENT" campaign is "schedule"ed
        And measurement campaign status "RUNNING" is verified
        And verify vehicle status inside campaign is "IN_ACTIVATION:1, :1"
        And command to "startGSMConnection" GSM mode for <device> the device
        And wait for device <device> to be "ONLINE"
        And verify vehicle status inside campaign is "ACTIVATION_CONFIRMED:1, :1"
        And campaign statistics are verified as per campaign <RM_Campaign_Detail_8>
        And command to "startGSMConnection" GSM mode for <device2> the device
        And wait for device <device2> to be "ONLINE"
        And vehicle status inside campaign "1" is "ACTIVATION_CONFIRMED"
        And campaign statistics are verified as per campaign <RM_Campaign_Detail_1>
        And measurement status on vehicle <vehicles> device slot <device_slot> is "ACTIVE" with substatus "ACTIVATION_CONFIRMED" and target status is "ACTIVE"

        And command to "stopGSMConnection" GSM mode for "all" the device
        And wait for device <device> to be "OFFLINE"
        And wait for device <device2> to be "OFFLINE"
        When "REMOTE_MEASUREMENT" campaign is "abort"ed
        And measurement campaign status "ABORTED" is verified
        And verify vehicle status inside campaign is "IN_DEACTIVATION:1, :1"
        And command to "startGSMConnection" GSM mode for <device> the device
        And wait for device <device> to be "ONLINE"
        And verify vehicle status inside campaign is "DEACTIVATION_CONFIRMED:1, :1"
        And campaign statistics are verified as per campaign <RM_Campaign_Detail_8>
        And command to "startGSMConnection" GSM mode for <device2> the device
        And wait for device <device2> to be "ONLINE"
        And vehicle status inside campaign "1" is "DEACTIVATION_CONFIRMED"
        And campaign statistics are verified as per campaign <RM_Campaign_Detail_3>
        And measurement status on vehicle <vehicles> device slot <device_slot> is "INACTIVE" with substatus "DEACTIVATION_CONFIRMED" and target status is "INACTIVE"

        And reference system is stopped
        And measurement test results are stored for RM campaign <RM_Campaign_Detail_7>
        And measurement data integrity smoke test is performed for RM campaign   

        Examples: 
            | vehicles                                        | first_vehicle            | second_vehicle           | device   | device2 | RM_Campaign_Detail_1 | RM_Campaign_Detail_3 | RM_Campaign_Detail_7 | RM_Campaign_Detail_8 | RM_Campaign_Detail_9 | device_slot | meas_config_name       | Protocol   | Identifier                     | vehicle_filter         |
            | "AUT_CM_TEST_Vehicle_05,AUT_CM_TEST_Vehicle_06" | "AUT_CM_TEST_Vehicle_05" | "AUT_CM_TEST_Vehicle_06" |  "CCU"   | "CCU2"  | "RM_campaign_1"      | "RM_campaign_3"      | "RM_campaign_7"      |  "RM_campaign_8"     |  "RM_campaign_9"     | "CAMPAIGN"  |"E2E_CAN_RAW_MON_500K"  | "MONonCAN" | "MONonCAN_500k_highloadidents" | "Model_Manufacturer"   |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CM_CCU_API_HP - Performing RM on multiple Campaign with different vehicles and same configuration with different version
        Given device <device> is "ONLINE"
        And device <device2> is "ONLINE"
        And create <vehicles> if it is not available
        And create device slot <device_slot> for <first_vehicle> vehicle
        And create device slot <device_slot> for <second_vehicle> vehicle
        And map device to <device_slot> slot of vehicles
        | vehicle_name              | device|
        | AUT_RM_CM_TEST_Vehicle_15 | CCU   |
        | AUT_RM_CM_TEST_Vehicle_16 | CCU2  |
        And geo positioning in <first_vehicle> is enabled
        And geo positioning in <second_vehicle> is "DISABLED"
        And reference system <Protocol> with Identifier <Identifier> is started for <device> device
        And reference system <Protocol> with Identifier <Identifier> is started for <device2> device

        When "2" new Campaigns <RM_Campaign_Detail_4> are "add"ed
        And measurement campaign "1" status "CREATED" is verified
        And measurement campaign "2" status "CREATED" is verified
        And Measurement configuration <meas_config_name> is added to the measurement campaign "1"
        And vehicles <vehicles> are added to the "REMOTE_MEASUREMENT" campaign "1" using dynamic filter <vehicle_filter_1>
        And verify that "1" vehicles should be listed for the campaign "1"
        And vehicles <vehicles> are added to the "REMOTE_MEASUREMENT" campaign "2" using dynamic filter <vehicle_filter_2>
        And verify that "1" vehicles should be listed for the campaign "2"
        And "REMOTE_MEASUREMENT" campaign "1" is "schedule"ed
        And measurement campaign "1" status "RUNNING" is verified
        And vehicle status inside campaign "1" is "ACTIVATION_CONFIRMED"
        And campaign "1" statistics are verified as per campaign <RM_Campaign_Detail_4>

        And Measurement job <meas_config_name> is in "draft" state
        And release measurement configuration <meas_config_name>
        
        And Measurement configuration <meas_config_name> is added to the measurement campaign "2"
        And "REMOTE_MEASUREMENT" campaign "2" is "schedule"ed
        And measurement campaign "2" status "RUNNING" is verified
        And vehicle status inside campaign "2" is "ACTIVATION_CONFIRMED"
        And campaign "2" statistics are verified as per campaign <RM_Campaign_Detail_4>
        And measurement status on campaign <RM_Campaign_Detail_4> vehicle <vehicles> device slot <device_slot> is "ACTIVE" with substatus "ACTIVATION_CONFIRMED" and target status is "ACTIVE"

        When "REMOTE_MEASUREMENT" campaign "1" is "abort"ed
        And measurement campaign "1" status "ABORTED" is verified
        And vehicle status inside campaign "1" is "DEACTIVATION_CONFIRMED"
        And measurement status on campaign <RM_Campaign_Detail_4> vehicle <first_vehicle> device slot <device_slot> is "INACTIVE" with substatus "DEACTIVATION_CONFIRMED" and target status is "INACTIVE"
        And campaign "1" statistics are verified as per campaign <RM_Campaign_Detail_5>

        When "REMOTE_MEASUREMENT" campaign "2" is "abort"ed
        And measurement campaign "2" status "ABORTED" is verified
        And vehicle status inside campaign "2" is "DEACTIVATION_CONFIRMED"
        And measurement status on campaign <RM_Campaign_Detail_4> vehicle <second_vehicle> device slot <device_slot> is "INACTIVE" with substatus "DEACTIVATION_CONFIRMED" and target status is "INACTIVE"
        And campaign "2" statistics are verified as per campaign <RM_Campaign_Detail_5>

        And reference system is stopped
        And measurement test results are stored for RM campaign <RM_Campaign_Detail_4>
        And measurement data integrity smoke test is performed for RM campaign

        Examples: 
            | vehicles                                              | first_vehicle               | second_vehicle              | device   | device2 | RM_Campaign_Detail_4  | RM_Campaign_Detail_10  | RM_Campaign_Detail_5 |  device_slot  | meas_config_name       | Protocol   | Identifier                     | vehicle_filter_1          | vehicle_filter_2          |
            | "AUT_RM_CM_TEST_Vehicle_15,AUT_RM_CM_TEST_Vehicle_16" | "AUT_RM_CM_TEST_Vehicle_15" | "AUT_RM_CM_TEST_Vehicle_16" |  "CCU"   | "CCU2"  | "RM_campaign_4"       |"RM_campaign_10"        | "RM_campaign_5"      |  "CAMPAIGN6"  |"E2E_CAN_RAW_MON_500K"  | "MONonCAN" | "MONonCAN_500k_highloadidents" | "geoPositioning_Enabled"  | "geoPositioning_Disabled" |
            