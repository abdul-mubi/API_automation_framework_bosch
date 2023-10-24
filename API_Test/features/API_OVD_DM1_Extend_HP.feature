Feature:  DM1 Extend Implementation
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Triggering DM1 Extended Measurement Job with RM config type as Continuous
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,calculatedListSignals" are "7,12" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Condition> for "startTrigger,stopTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "2" minutes
        And Remote measurement is deactivated
        Then measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And data integrity test is performed on measured data as per trigger <Trigger> trigger condition <Condition> for trigger type <Trigger_type>

        Examples:
            | vehicle | device | meas_config_name                      | can_protocol   | can_identifier      |  Trigger            | Trigger_type            | Condition                  |
            | " "     | "CCU"  | "DM1_Extended_Config_Continuous_v1.0" | "CANalization" | "DM1_Extend_1000ms" | "E2E_Test_Trigger"  | "DM1_Extend_Message"    | "DM1_Extend_Continuous_First_ECU_Appeared_Second_ECU_Disappeared" |
            | " "     | "CCU"  | "DM1_Extended_Config_Continuous_v1.0" | "CANalization" | "DM1_Extend_1000ms" | "E2E_Test_Trigger"  | "DM1_Extend_Message"    | "DM1_Extend_Continuous_Multiple_ECU_AppearedDisappeared_Second_ECU_Appeared" |

    
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Triggering DM1 Extended Measurement Job with RM config type as Single shot
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,calculatedListSignals" are "7,12" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Condition> for "startTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "2" minutes
        And Remote measurement is deactivated
        Then measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And data integrity test is performed on measured data for "START" trigger as per trigger <Trigger> trigger condition <Condition> for trigger type <Trigger_type>

        Examples:
            | vehicle | device | meas_config_name                      | can_protocol   | can_identifier      |  Trigger            | Trigger_type            | Condition                  |
            | " "     | "CCU"  | "DM1_Extended_Config_SingleShot_v1.0" | "CANalization" | "DM1_Extend_1000ms" | "E2E_Test_Trigger"  | "DM1_Extend_Message"    | "DM1_Extend_SingleShot_Single_ECU_AppearedDisappeared" |
            | " "     | "CCU"  | "DM1_Extended_Config_SingleShot_v1.0" | "CANalization" | "DM1_Extend_1000ms" | "E2E_Test_Trigger"  | "DM1_Extend_Message"    | "DM1_Extend_SingleShot_Multiple_ECU_Disappeared" |