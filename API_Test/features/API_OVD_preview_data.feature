Feature: Validate Remote measurement preview data

    @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-API @E2E-Regression @E2E-CCU
    Scenario Outline: RM_CCU_API_HP - Preview RM data for both numeric and other series

        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,calculatedSignals,messages" are "1,1,1" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "0.5" minutes
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And reference system is stopped
        And measurement test results are stored including "preview_data"
        And validate preview data for the measurement configuration <meas_config_name>

Examples:
        |vehicle  |device    |meas_config_name                              |can_protocol   |can_identifier      |
        |" "      |"CCU"     |"E2E_CALCULATED_SIGNALS_MESSAGE_Automation"  |"CANalization" |"Remote_Measurement_350ms"|

    @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-API @E2E-Regression @E2E-CCU
    Scenario Outline: RM_CCU_API_HP - Preview RM data for only numeric series

        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <Protocol> with Identifier <Identifier> is started
        And test is executed for "0.5" minutes
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And reference system is stopped
        And measurement test results are stored including "preview_data"
        And validate preview data for the measurement configuration <meas_config_name>

Examples:
        | vehicle | device | meas_config_name        | Protocol   | Identifier      |
        | " "     | "CCU"  | "Preview_Test1"        | "MONonCAN" | "MONonCAN_500k_endurance" |

    @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-API @E2E-Regression @E2E-CCU
    Scenario Outline: RM_CCU_API_HP - Preview RM data for multiple single-shot signals with triggers

        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,calculatedSignals,messages" are "3,0,0" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "1" minutes
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And reference system is stopped
        And measurement test results are stored including "preview_data"
        And validate preview data for the measurement configuration <meas_config_name>

Examples:
        |vehicle  |device    |meas_config_name                 |can_protocol   |can_identifier             |
        |" "      |"CCU"     |"E2E_SingleShot_Last_CAN_data"  |"CANalization" |"Remote_Measurement_350ms" |