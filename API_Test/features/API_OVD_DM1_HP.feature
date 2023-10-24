Feature:  [RM][J1939] DM1-message - SPN-signals
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP -  Triggering DM1 with RM config type as continuous and only start trigger with source filter as All
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,messages" are "3,2" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger",create if not present
        And Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "1.5" minutes
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        Then data integrity test is performed on measured data for "START" trigger as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>

        Examples:
            | vehicle | device | meas_config_name                        | can_protocol   | can_identifier          | Trigger            | Trigger_type  | Cond1                  |
            | " "     | "CCU"  | "Automation_J1939_DM1_Continuous_Plus" | "CANalization" | "DM1_Continuous_1000ms" | "E2E_Test_Trigger" | "DM1_Message" | "DM1_All_Source_addresses" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP -  Triggering DM1 with RM config type as singleshot with proper reset DTC
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,messages" are "5,2" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger",create if not present
        And Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "1" minutes
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        Then data integrity test is performed on measured data for "START" trigger as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>

        Examples:
            | vehicle | device | meas_config_name                          | can_protocol   | can_identifier    | Trigger            | Trigger_type  | Cond1                  |
            | " "     | "CCU"  | "Automation_J1939_DM1_SingleShot_Plus_1" | "CANalization" | "DM1_Singleshot" | "E2E_Test_Trigger" | "DM1_Message" | "DM1_Singleshot_ResetDTC" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP -  Triggering DM1 with RM config type as singleshot with inactive force retrigger
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,messages" are "5,2" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger",create if not present
        And Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "1" minutes
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        Then data integrity test is performed on measured data for "START" trigger as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>

        Examples:
            | vehicle | device | meas_config_name                          | can_protocol   | can_identifier          | Trigger            | Trigger_type  | Cond1                  |
            | " "     | "CCU"  | "Automation_J1939_DM1_SingleShot_Plus_1" | "CANalization" | "DM1_Continuous_1000ms" | "E2E_Test_Trigger" | "DM1_Message" | "DM1_Singleshot_Force_Retrigger_Inactive" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP -  Triggering DM1 with RM config type as continuous with active force retrigger and reset DTC
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,messages" are "3,2" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger,stopTrigger",create if not present
        And Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "1" minutes
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        Then data integrity test is performed on measured data as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>

        Examples:
            | vehicle | device | meas_config_name                        | can_protocol   | can_identifier          | Trigger            | Trigger_type  | Cond1                  |
            | " "     | "CCU"  | "Automation_J1939_DM1_Continuous_Plus1" | "CANalization" | "DM1_Continuous_1000ms" | "E2E_Test_Trigger" | "DM1_Message" | "DM1_Active_Force_Retrigger_and_ResetDTC" |
