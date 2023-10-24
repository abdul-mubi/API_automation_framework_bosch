Feature:Trigger on Time interval for Single shot measurement of CCU voltage
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Trigger on Time interval for Single shot measurement of CCU voltage
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "3" minutes
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And measurement data integrity test is performed
        And data integrity test is performed on measured data for "START" trigger as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>

        Examples:
            | vehicle | device | meas_config_name                         | can_protocol   | can_identifier               | Trigger            | Trigger_type    | Cond1                             |
            | " "     | "CCU"  | "E2E_TimeInterval_Singleshot_CCUVoltage" | "CANalization" | "RM_mine_incr_vcu_HVBattSOC" | "E2E_Test_Trigger" | "TIME_INTERVAL" | "Time_interval_config_CCUVoltage" |


    
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP- Trigger on Time interval for Single shot configuration with Timeout
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "4" minutes
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And measurement data integrity test is performed
        And data integrity test is performed on measured data for "START" trigger as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>

        Examples:
            | vehicle | device | meas_config_name                   | signals          | can_protocol   | can_identifier               | Trigger            | Trigger_type    | Cond1                             |
            | " "     | "CCU"  | "E2ECANrawTimeInterval_SingleShot" | "vcu_HVBattSOC:" | "CANalization" | "RM_mine_incr_vcu_HVBattSOC" | "E2E_Test_Trigger" | "TIME_INTERVAL" | "Time_interval_config_Singleshot" |
