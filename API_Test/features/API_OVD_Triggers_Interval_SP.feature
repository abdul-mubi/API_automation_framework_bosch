Feature: Trigger condition based on time or value interval
    @E2E-API @E2E-CCU @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression @E2E-SP
    Scenario Outline:RM_CCU_API_SP - Trigger on Signal value interval for Single shot configuration for wrong start trigger configuration
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "2" minutes
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test steps are not generated

        Examples:
            | vehicle | device | meas_config_name                       | can_protocol   | can_identifier               | Trigger            | Cond1                                    |
            | " "     | "CCU"  | "E2ECanrawValueInterval_SingleShot_SP" | "CANalization" | "RM_mine_incr_vcu_HVBattSOC" | "E2E_Test_Trigger" | "Wrong_Value_interval_config_Singleshot" |