Feature:  Remote Measurement on Trigger on variation of message
    @E2E-API @E2E-CCU @E2E-SP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_SP - Wrong configuration of mask for start trigger on variation of message
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs

        And verify number of "signals,messages" are "1,1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger",create if not present
        #And delete the previous data if it is available
        And reference system <can_protocol> with Identifier <can_identifier> is started
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And test is executed for "2" minutes
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test steps are not generated

        Examples:
            | vehicle | device | meas_config_name                    | can_protocol   | can_identifier             | Trigger            | Trigger_type        | Cond1                     |
            | " "     | "CCU"  | "E2E_TRIGGER_ON_VARIATION_MESSAGE" | "CANalization" | "Remote_Measurement_350ms" | "E2E_Test_Trigger" | "Message_Variation" | "WrongstartTriggerconfig" |