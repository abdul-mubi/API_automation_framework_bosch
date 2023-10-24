Feature: Remote measurement of CANRaw/J1939 Multiplexed signals
@E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
Scenario Outline: RM_CCU_API_HP - Remote measurement of CANRaw and J1939 Multiplexed signals
Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,messages" are "4,1" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "1" minutes
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And reference system is stopped
        And measurement test results are stored
        And measurement data integrity test is performed for Multiplexed signals measurement

Examples:
        |vehicle  |device |meas_config_name                           |can_protocol   |can_identifier       |
        |" "      |"CCU"  |"E2E_CAN_RAW_MULTIPLEXED_SIGNALS"         |"CANalization" |"run_CAN_Multiplex_1000ms"   |
        |" "      |"CCU"  |"E2E_J1939_MULTIPLEXED_SIGNALS"           |"CANalization" |"SimpleMultiplexing_J1938_500ms"   |
        |" "      |"CCU"  |"E2E_MULTIPLEXED_SIGNALS"                 |"CANalization" |"run_CAN_Multiplex_1000ms"   |

    

@E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
Scenario Outline: RM_CCU_API_HP - Remote measurement of Multiplexed signals with two multiplexors in Measurement configuration
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,messages" are "4,2" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier_1> is started
        And reference system <can_protocol> with Identifier <can_identifier_2> is started
        And test is executed for "1" minutes
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And reference system is stopped
        And measurement test results are stored
        And measurement data integrity test is performed for Multiplexed signals measurement

Examples:
        |vehicle  |device |meas_config_name               |can_protocol   |can_identifier_1             |can_identifier_2                |
        |" "      |"CCU"  |"E2E_TWO_MULTIPLEXOR_SIGNALS" |"CANalization" |"run_CAN_Multiplex_1000ms"   |"SimpleMultiplexing_J1938_500ms"|	
