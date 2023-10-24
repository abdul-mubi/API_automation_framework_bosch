Feature:Remote Measurement on Trigger on CANRaw and J1939 message
        @E2E-API @E2E-CCU @E2E-SP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
        Scenario Outline: RM_CCU_API_SP - Trigger on CANRaw or J1939 message with Start trigger as mode APPEARS and logic Inverting
                Given device <device> is "ONLINE"
                And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
                And verify number of "messages" are "2" respectively is present in measurement configuration <meas_config_name>
                And verify <Trigger> as per <Cond1> for "startTrigger",create if not present
                #And delete the previous data if it is available
                When Remote measurement is activated
                And measurement status is "ACTIVE" within "10" minutes
                And reference system <can_protocol> with Identifier <can_identifier> is started
                And test is executed for "2" minutes
                Then Remote measurement is deactivated
                And measurement status is "INACTIVE" within "10" minutes
                And measurement test steps are not generated

                Examples:
                        | vehicle | device | meas_config_name    | can_protocol   | can_identifier            | Trigger            | Cond1                         |
                        | " "     | "CCU"  | "E2E_CAN_RAW_DEMO" | "CANalization" | "J1939_Measurement_200ms" | "E2E_Test_Trigger" | "wrong_Canraw_appears_config" |
