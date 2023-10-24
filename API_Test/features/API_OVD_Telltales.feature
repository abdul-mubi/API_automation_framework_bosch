Feature:  Telltales measurement list
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @E2E-Regression @BV-UC_RemoteMeasurement
    Scenario Outline: RM_CCU_API_HP - Continuous RM config with FULL LIST and CHANGED LIST POSITION list
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,calculatedListSignals" are "2,2" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        Then measurement status is "ACTIVE" within "10" minutes
        When reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "2" minutes
        And Remote measurement is deactivated
        Then measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And measurement data integrity test is performed for calculated list signals

        Examples:
            | vehicle | device | meas_config_name                  | can_protocol   | can_identifier     | 
            | " "     | "CCU"  | "Automation_continuous_telltales" | "CANalization" | "TellTales_1000ms" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @E2E-Regression @BV-UC_RemoteMeasurement
    Scenario Outline: RM_CCU_API_HP - Singleshot RM config with FULL LIST and CHANGED LIST POSITION
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,calculatedListSignals" are "6,2" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        Then measurement status is "ACTIVE" within "10" minutes
        When reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "2" minutes
        And Remote measurement is deactivated
        Then measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And measurement data integrity test is performed for calculated list signals

        Examples:
            | vehicle | device | meas_config_name                         | can_protocol   | can_identifier     |
            | " "     | "CCU"  | "Automation_singleshot_telltales_trigger"| "CANalization" | "TellTales_1000ms" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @E2E-Regression @BV-UC_RemoteMeasurement
    Scenario Outline: RM_CCU_API_HP - Singleshot RM config with WARNINGS and TELLTALES with multiple VARIATION trigger conditions
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,calculatedListSignals" are "6,4" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger",create if not present
        And Remote measurement is activated
        Then measurement status is "ACTIVE" within "10" minutes
        When reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "2" minutes
        And Remote measurement is deactivated
        Then measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And data integrity test is performed on measured data for "START" trigger as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>

        Examples:
            | vehicle | device | meas_config_name                | can_protocol   | can_identifier     | Trigger            | Trigger_type    | Cond1                      |
            | " "     | "CCU"  | "SYSINT_SingleShot_TellTales_01"| "CANalization" | "TellTales_1000ms" | "E2E_Test_Trigger" | "Tell_Tales"    | "tellTalesMultiConditions" |