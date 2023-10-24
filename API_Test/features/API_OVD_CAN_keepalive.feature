Feature: Validate CAN keep alive when CL15 is turn off
@E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-CCU @E2E-API @E2E-Regression @E2E-PACCAR
Scenario Outline: RM_CCU_API_HP: Validate data using CAN keep alive when CL15 is off in RM
Given device <device> is "ONLINE"
    And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
    And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
    When Remote measurement is activated
    And measurement status is "ACTIVE" within "10" minutes
    And switch "CL15" is turned "Off"
    And wait for device to be "OFFLINE"
    And reference system <Protocol> with Identifier <Identifier> is started
    And wait for device to be "ONLINE"
    And measurement test results are stored
    And measurement test result for latest step is "not available"
    And reference system <Protocol1> with Identifier <Identifier1> is started
    And test waits for "1" minutes
    And measurement test results are stored
    And measurement data integrity test is performed for the 2 numbereth test step 
    Then Remote measurement is deactivated
    And measurement status is "INACTIVE" within "10" minutes
    And reference system is stopped
    And wait for device to be "OFFLINE"
    And switch "CL15" is turned "On"
    And wait for device to be "ONLINE"

    Examples:
            | vehicle | device | meas_config_name        | Protocol       | Identifier      | Protocol1 | Identifier1                   |
            | " "     | "CCU" | "E2E_CAN_RAW_MON_500K" | "CANalization" | "CAN_KeepAlive" |"MONonCAN" | "MONonCAN_500k_highloadidents" |
