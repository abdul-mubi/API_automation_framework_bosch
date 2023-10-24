Feature: Remote measurement of Calculated Signals
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Remote measurement of Calculated signals with Triggers
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,calculatedSignals" are "1,1" respectively is present in measurement configuration <meas_config_name> 
        And verify <Trigger> as per <Cond1> for "startTrigger,stopTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "2" minutes
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And data integrity test is performed on measured data as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>
        And measurement data integrity test is performed for calculated signals

        Examples:
            | vehicle | device  | meas_config_name                                   | can_protocol   | can_identifier                      | Trigger            | Trigger_type      | Cond1                   |
            | " "     | "CCU"  | "E2E_CALCULATED_SIGNALS_with_TRIGGERS_Automation" | "CANalization" | "Signal_variation_identifier_5000ms" | "E2E_Test_Trigger" | "Signal_Variation" | "signalVariationconfig" |
    

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Smoke
    Scenario Outline:RM_CCU_API_HP - Remote measurement of Calculated signals created using system signals
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,calculatedSignals" are "1,1" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And test is executed for "1" minutes
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And measurement test result for latest step is "available"

        Examples:
        |vehicle  |device    |meas_config_name                             |
        |" "      |"CCU"     |"E2E_CALCULATED_SYSTEM_SIGNALS_Automation"   |


    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Remote measurement of Single shot type with Calculated signals
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And verify number of "signals,calculatedSignals" are "1,1" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And reference system is stopped
        And measurement test results are stored
        And measurement test result for latest step is "available"

        Examples:
        |vehicle  |device  |meas_config_name                                 |can_protocol   |can_identifier    |
        |" "      |"CCU"  |"E2E_SINGLESHOT_CALCULATED_SIGNALS_Automation"  |"MONonCAN"     |"MONonCAN_500k_highloadidents"   | 


    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Remote measurement of Calculated signals created using CANRaw and J1939 protocol signals
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,calculatedSignals" are "1,2" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "0.5" minutes
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And reference system is stopped
        And measurement test results are stored
        And measurement data integrity test is performed for calculated signals

    Examples:
        |vehicle  |device     |meas_config_name                              |can_protocol   |can_identifier               |
        |" "      |"CCU"     |"E2E_CAN_RAW_CALCULATED_SIGNALS_Automation"  |"CANalization" |"Remote_Measurement_350ms"          |
        |" "      |"CCU"     |"E2E_J1939_CALCULATED_SIGNALS_Automation"    |"CANalization" |"J1939_Measurement_Signals_100ms"   |
    

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Smoke
    Scenario Outline:RM_CCU_API_HP - Remote measurement of calculated signals and messages
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
        And measurement test results are stored
        And measurement data integrity test is performed

    Examples:
            |vehicle  |device    |meas_config_name                             |can_protocol   |can_identifier                |
            |" "      |"CCU"     |"E2E_CALCULATED_SIGNALS_MESSAGE_Automation"  |"CANalization" |"Remote_Measurement_350ms"    |
            
