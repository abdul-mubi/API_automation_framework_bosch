Feature: Rework transfer of measurements
    @E2E-CCU @E2E-API @E2E-HP @E2E-RM @E2E-Regression @BV-UC_RemoteMeasurement 
    Scenario Outline:RM_CCU_API_HP - Rework transfer of measurement via cloudstore
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,messages" are "8,3" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        And measurement status is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And test is executed for "3" minutes
        And reference system is stopped
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE"
        And measurement test results are stored
        And measurement test result for latest step is available

        Examples: 
            | vehicle | device | meas_config_name         | Protocol   | Identifier                | 
            | " "     | "CCU"  | "E2E_CAN_RAW_CLOUDSTORE" | "MONonCAN" | "MONonCAN_highloadidents" |