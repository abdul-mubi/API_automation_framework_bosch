Feature: Measuring Trigger on variation of signal Sad Path
    @E2E-API @E2E-CCU @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression @E2E-SP
    Scenario Outline:RM_CCU_API_SP- Trigger on variation of signal on a multiplexed signal with no CAN traces present
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "5" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Trigger_Condition> for "startTrigger,stopTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "1" minutes
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test steps are not generated

Examples:
        |vehicle  |device   |meas_config_name                             |can_protocol   |can_identifier                |Trigger             |Trigger_type        | Trigger_Condition               |
        |" "      |"CCU"    |"E2E_MULTIPLEXED_SIGNALS_Trigger_ON_Signal" |"CANalization" |"run_CAN_multiplex_SP_4000ms" |"E2E_Test_Trigger"  |"Signal_Variation" | "multiplexedsignalVariationconfig"|


    @E2E-API @E2E-CCU @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression @E2E-SP
    Scenario Outline:RM_CCU_API_SP- Wrong configuration of mask for start trigger on variation of signal
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Trigger_Condition> for "startTrigger,stopTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "1" minutes
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        Then measurement test steps are not generated

Examples:
        |vehicle  |device  |signal_collection       |meas_config_name                       |can_protocol   |can_identifier                |Trigger             |Trigger_type       | Trigger_Condition          |
        |" "      |"CCU"  |"E2E_CAN_RAW_MON_500K"   |"E2E_trigger_on_signal_variation_SP"  |"CANalization" |"Signal_variation_identifier_5000ms" |"E2E_Test_Trigger"  |"Signal_Variation" | "wrongsignalVariationconfig"|


