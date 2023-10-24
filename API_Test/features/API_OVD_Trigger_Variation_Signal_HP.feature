Feature: Measuring Trigger on variation of signal
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP- Remote measurement config with Trigger on variation of signal for Multiplexed signals
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "5" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Trigger_Condition> for "startTrigger,stopTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "20" seconds
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        Then data integrity test is performed on measured data as per trigger <Trigger> trigger condition <Trigger_Condition> for trigger type <Trigger_type>
        
    Examples:
        |vehicle  |device    |meas_config_name                             |can_protocol   |can_identifier                              |Trigger             |Trigger_type        | Trigger_Condition           |
        |" "      |"CCU"     |"E2E_MULTIPLEXED_SIGNALS_Trigger_ON_Signal" |"CANalization" |"run_CAN_Multiplex_signal_variation_4000ms" |"E2E_Test_Trigger"  |"Signal_Variation"  | "multiplexedsignalVariationconfig"|


    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP- Remote measurement config with Trigger on variation of signal with Start and stop trigger for different signals
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Trigger_Condition> for "startTrigger,stopTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "2" minutes
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        Then data integrity test is performed on measured data as per trigger <Trigger> trigger condition <Trigger_Condition> for trigger type <Trigger_type>
        # Then data integrity test is performed on measured data for "START" trigger as per trigger <Trigger> trigger condition <Trigger_Condition> for trigger type <Trigger_type>
        # And data integrity test is performed on measured data for "STOP" trigger as per trigger <Trigger> trigger condition <Trigger_Condition> for trigger type <Trigger_type>
        
    Examples:
        |vehicle  |device    |meas_config_name                                       |can_protocol   |can_identifier                         |Trigger               |Trigger_type       | Trigger_Condition                |
        |" "      |"CCU"     |"E2E_trigger_signal_variation_on_different_signals"   |"CANalization" |"Signal_variation_identifier_5000ms"   |"E2E_Test_Trigger"    |"Signal_Variation" | "Signal_variation_config_2signals"|


    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP- Remote measurement config with Trigger on variation of signal with only start trigger for Singleshot type RM config
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Trigger_Condition> for "startTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "1" minutes
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        Then data integrity test is performed on measured data for "START" trigger as per trigger <Trigger> trigger condition <Trigger_Condition> for trigger type <Trigger_type>
        
    Examples:
        |vehicle  |device  |meas_config_name                               |can_protocol   |can_identifier        |Trigger             |Trigger_type        | Trigger_Condition               |
        |" "      |"CCU"  |"E2E_trigger_on_signal_variation_Singleshot"  |"CANalization" |"Signal_variation_identifier_5000ms"   |"E2E_Test_Trigger"   |"Signal_Variation" | "signalVariationconfig"|
 

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP- Remote measurement config with Trigger on variation of signal with only stop trigger
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Trigger_Condition> for "stopTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "2" minutes
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        Then data integrity test is performed on measured data for "STOP" trigger as per trigger <Trigger> trigger condition <Trigger_Condition> for trigger type <Trigger_type>
        
    Examples:
        |vehicle  |device   |meas_config_name                      |can_protocol   |can_identifier                         |Trigger             |Trigger_type        | Trigger_Condition              |
        |" "      |"CCU"    |"E2E_trigger_on_signal_variation"     |"CANalization" |"Signal_variation_identifier_5000ms"   |"E2E_Test_Trigger"   |"Signal_Variation" | "signalVariationconfig"|

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP- Remote measurement config with trigger on variation of signal with start and stop trigger
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Trigger_Condition> for "startTrigger,stopTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "2" minutes
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        Then data integrity test is performed on measured data as per trigger <Trigger> trigger condition <Trigger_Condition> for trigger type <Trigger_type>
        
    Examples:
        |vehicle  |device  |meas_config_name                       |can_protocol   |can_identifier        |Trigger             |         Trigger_type        | Trigger_Condition                    |
        |" "      |"CCU"  |"E2E_trigger_on_signal_variation"    |"CANalization" |"Signal_variation_identifier_5000ms"   |"E2E_Test_Trigger"   |"Signal_Variation" | "signalVariationconfig"|
