Feature: verify GPS date on CAN
    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Regression
    Scenario Outline:FM_CCU_API_HP - Activation of Geo-positioning and verify GPS data on CAN
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "7" respectively is present in measurement configuration <meas_config_name>
        And geo positioning in <vehicle> is enabled
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <protocol> with Identifier "SM_record_response" is started
        And test waits for "0.5" minutes
        And reference system is stopped
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        Then validate GPS data on CAN
        And geo positioning in <vehicle> is "Disabled"

        Examples:
            | vehicle| device | meas_config_name | protocol       |
            | " "    | "CCU"  | "RM_GPS_TCU2_RM" | "CANalization" |
