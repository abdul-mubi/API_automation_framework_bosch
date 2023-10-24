Feature: sad path Enrich measurement results
@E2E-API @E2E-CCU @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression @E2E-SP
Scenario Outline:RM_CCU_API_SP : Enrich measurement results - Continuous - Job Installation/Uninstallation with CL30 reboot
        Given device <device> is "ONLINE"
        When map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And reference system <Protocol> with Identifier <Identifier> is started
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        Then Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        When test is executed for "2" minutes
        And reference system is stopped
        And measurement test results are stored
        When switch "CL30" is turned "Off"
        Then wait for device to be "OFFLINE"
        When switch "CL30" is turned "On"
        Then wait for device to be "ONLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And "Start,Stop" of measurement details are requested
        And validate "JOB_INSTALLATION,DRIVE_CYCLE_END" as measurement reason
        When test is executed for "1" minutes
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        Then "Start,Stop" of measurement details are requested
        And validate "DRIVE_CYCLE_START,JOB_UNINSTALLATION" as measurement reason
        And reference system is stopped

        Examples: 
            | vehicle | device | signal_collection      | meas_config_name       | Protocol   | Identifier                     | 
            | " "     | "CCU"  | "E2E_CAN_RAW_MON_500K" | "E2E_CAN_RAW_MON_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" | 