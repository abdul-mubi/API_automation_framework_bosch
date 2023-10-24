Feature: Measurement configuration - Configurable upload interval
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Configurable upload interval
    Given device <device> is "ONLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        Then measurement test step is verified with upload interval <Upload_Interval> for upload count <Upload_Count> cycles
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And reference system is stopped

        Examples:
            | vehicle | device  | meas_config_name                   | Protocol   | Identifier                     | Upload_Interval | Upload_Count |
            | " "     | "CCU"   | "E2E_CAN_RAW_UPLOAD_INTERVAL_30"  | "MONonCAN" | "MONonCAN_500k_highloadidents" | "30"            | "4"          |
            | " "     | "CCU"   | "E2E_CAN_RAW_UPLOAD_INTERVAL_60"  | "MONonCAN" | "MONonCAN_500k_highloadidents" | "60"            | "4"          |
            | " "     | "CCU"   | "E2E_CAN_RAW_UPLOAD_INTERVAL_300" | "MONonCAN" | "MONonCAN_500k_highloadidents" | "300"           | "3"          |