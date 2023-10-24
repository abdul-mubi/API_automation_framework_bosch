Feature:  Daf Warnings measurement list
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Continuous RM config with APPEARED and DISAPPEARED warnings list
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,calculatedListSignals" are "2,2" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "2" minutes
        And  Remote measurement is deactivated
        Then measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And measurement data integrity test is performed for calculated list signals

        Examples:
            | vehicle | device | meas_config_name                     | can_protocol   | can_identifier                                 | 
            | " "     | "CCU"  | "Automation_Continuous_Daf_Warnings" | "CANalization" | "Warning_Frames_with_two_trigger_point_1000ms" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Singleshot RM config with APPEARED and DISAPPEARED warnings list
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,calculatedListSignals" are "2,2" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "3" minutes
        And Remote measurement is deactivated
        Then measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And measurement data integrity test is performed for calculated list signals

        Examples:
            | vehicle | device | meas_config_name                     | can_protocol   | can_identifier                                 | 
            | " "     | "CCU"  | "Automation_Singleshot_Daf_Warnings" | "CANalization" | "Warning_Frames_with_two_trigger_point_1000ms" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Only start trigger with pre-trigger time for continuous RM config with DISAPPEARED warnings list
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,calculatedListSignals" are "4,1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger,stopTrigger" with "{"preTrigger":5,"postTrigger":5}" seconds,create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "2" minutes
        And Remote measurement is deactivated
        Then measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And data integrity test is performed on measured data as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>

        Examples:
            | vehicle | device | meas_config_name                             | can_protocol   | can_identifier                                 | Trigger            | Trigger_type      | Cond1                  |
            | " "     | "CCU"  | "Automation_Continuous_Daf_Warnings_trigger" | "CANalization" | "Warning_Frames_with_two_trigger_point_1000ms" | "E2E_Test_Trigger" | "Daf_Warnings"    | "dafWarningContinuous" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - start trigger with pre-trigger time for singleshot RM config DISAPPEARED warnings list
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,calculatedListSignals" are "2,1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger" with "{"preTrigger":5}" seconds,create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "2" minutes
        And Remote measurement is deactivated
        Then measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        Then data integrity test is performed on measured data for "START" trigger as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>

        Examples:
            | vehicle | device | meas_config_name                             | can_protocol   | can_identifier                                 | Trigger            | Trigger_type      | Cond1                  |
            | " "     | "CCU"  | "Automation_Singleshot_Daf_Warnings_trigger" | "CANalization" | "Warning_Frames_with_two_trigger_point_1000ms" | "E2E_Test_Trigger" | "Daf_Warnings"    | "dafWarningSingleShot" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Multiple start trigger condition for singleshot RM config DISAPPEARED warnings list
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,calculatedListSignals" are "4,2" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "2" minutes
        And Remote measurement is deactivated
        Then measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And "Start,Stop" of measurement details are requested for "all" measurements
        And validate "START_TRIGGER,NOT_AVAILABLE" reason as per trigger condition <Cond1>
        Then data integrity test is performed on measured data for "START" trigger as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>

        Examples:
            | vehicle | device | meas_config_name                          | can_protocol   | can_identifier                                 | Trigger            | Trigger_type      | Cond1                       |
            | " "     | "CCU"  | "Automation_Singleshot_multiple_triggers" | "CANalization" | "Warning_Frames_with_one_trigger_point_1000ms" | "E2E_Test_Trigger" | "Daf_Warnings"    | "dafWarningMultiConditions" |
