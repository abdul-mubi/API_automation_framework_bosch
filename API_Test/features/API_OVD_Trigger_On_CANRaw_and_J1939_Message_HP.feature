Feature:  Remote Measurement on Trigger on CANRaw and J1939 message
        @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
        Scenario Outline: RM_CCU_API_HP - Trigger on CANRaw and J1939 message with Start and stop trigger mode Compare to Bitmask
                Given device <device> is "ONLINE"
                And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
                And verify number of "signals,messages" are "1,1" respectively is present in measurement configuration <meas_config_name>
                And verify <Trigger> as per <Cond1> for "startTrigger,stopTrigger",create if not present
                #And delete the previous data if it is available
                When Remote measurement is activated
                And measurement status is "ACTIVE" within "10" minutes
                And reference system <can_protocol> with Identifier <can_identifier> is started
                And test is executed for "2" minutes
                Then Remote measurement is deactivated
                And measurement status is "INACTIVE" within "10" minutes
                And measurement test results are stored
                And data integrity test is performed on measured data as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>

                Examples:
                        | vehicle | device | meas_config_name               | can_protocol   | can_identifier             | Trigger            | Trigger_type      | Cond1                          |
                        | " "     | "CCU"  | "E2E_CAN_RAW_COMPARE_BITMASK" | "CANalization" | "Remote_Measurement_350ms" | "E2E_Test_Trigger" | "COMPARE_BITMASK" | "Canraw_comparebitmask_config" |
                        | " "     | "CCU"  | "E2E_J1939_COMPARE_BITMASK"   | "CANalization" | "J1939_one_byte_1000ms"    | "E2E_Test_Trigger" | "COMPARE_BITMASK" | "J1939_comparebitmask_config"  |


        @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
        Scenario Outline: RM_CCU_API_HP - Trigger on CANRaw and J1939 with only Start trigger configured with mode Compare to Bitmask
                Given device <device> is "ONLINE"
                And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
                And verify number of "signals,messages" are "1,1" respectively is present in measurement configuration <meas_config_name>
                And verify <Trigger> as per <Cond1> for "startTrigger",create if not present
                #And delete the previous data if it is available
                When Remote measurement is activated
                And measurement status is "ACTIVE" within "10" minutes
                And reference system <can_protocol> with Identifier <can_identifier> is started
                And test is executed for "2" minutes
                Then Remote measurement is deactivated
                And measurement status is "INACTIVE" within "10" minutes
                And measurement test results are stored
                And data integrity test is performed on measured data for "START" trigger as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>

                Examples:
                        | vehicle | device | meas_config_name                        | can_protocol   | can_identifier             | Trigger            | Trigger_type      | Cond1                          |
                        | " "     | "CCU"  | "E2E_CAN_RAW_COMPARE_BITMASK"          | "CANalization" | "Remote_Measurement_350ms" | "E2E_Test_Trigger" | "COMPARE_BITMASK" | "Canraw_comparebitmask_config" |
                        | " "     | "CCU"  | "E2E_J1939_COMPARE_BITMASK"            | "CANalization" | "J1939_one_byte_1000ms"    | "E2E_Test_Trigger" | "COMPARE_BITMASK" | "J1939_comparebitmask_config"  |


        @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
        Scenario Outline: RM_CCU_API_HP - Trigger on CANRaw and J1939 with only Stop trigger configured with mode Compare to Bitmask
                Given device <device> is "ONLINE"
                And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
                And verify number of "signals,messages" are "1,1" respectively is present in measurement configuration <meas_config_name>
                And verify <Trigger> as per <Cond1> for "stopTrigger",create if not present
                #And delete the previous data if it is available
                When Remote measurement is activated
                And measurement status is "ACTIVE" within "10" minutes
                And reference system <can_protocol> with Identifier <can_identifier> is started
                And test is executed for "2" minutes
                Then Remote measurement is deactivated
                And measurement status is "INACTIVE" within "10" minutes
                And measurement test results are stored
                And data integrity test is performed on measured data for "STOP" trigger as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>

                Examples:
                        | vehicle | device | meas_config_name               | can_protocol   | can_identifier             | Trigger            | Trigger_type      | Cond1                          |
                        | " "     | "CCU"  | "E2E_CAN_RAW_COMPARE_BITMASK" | "CANalization" | "Remote_Measurement_350ms" | "E2E_Test_Trigger" | "COMPARE_BITMASK" | "Canraw_comparebitmask_config" |
                        | " "     | "CCU"  | "E2E_J1939_COMPARE_BITMASK"   | "CANalization" | "J1939_one_byte_1000ms"    | "E2E_Test_Trigger" | "COMPARE_BITMASK" | "J1939_comparebitmask_config"  |


        @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
        Scenario Outline:RM_CCU_API_HP - Trigger on CANRaw and J1939 with message with Start trigger on CANRaw message and Stop trigger on J1939 message with modes Compare to Bitmask
                Given device <device> is "ONLINE"
                And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
                And verify number of "messages" are "2" respectively is present in measurement configuration <meas_config_name>
                And verify <Trigger> as per <Cond1> for "startTrigger,stopTrigger",create if not present
                #And delete the previous data if it is available
                When Remote measurement is activated
                And measurement status is "ACTIVE" within "10" minutes
                And reference system <can_protocol> with Identifier <can_identifier_1> is started
                And test is executed for "30" seconds
                And VRS with protocol <can_protocol> and identifier <can_identifier_1> is stopped
                And test is executed for "10" seconds
                And reference system <can_protocol> with Identifier <can_identifier_2> is started
                And test is executed for "2" minutes
                Then Remote measurement is deactivated
                And measurement status is "INACTIVE" within "10" minutes
                And VRS with protocol <can_protocol> and identifier <can_identifier_2> is stopped
                And measurement test results are stored
                And data integrity test is performed on measured data as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>
                #And data integrity test is performed on measured data for "START" trigger as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>
                #And data integrity test is performed on measured data for "STOP" trigger as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>

                Examples:
                        | vehicle | device | meas_config_name                     | can_protocol   | can_identifier_1           | can_identifier_2        | Trigger            | Trigger_type      | Cond1                               | 
                        | " "     | "CCU"  | "E2E_CAN_RAW_J1939_COMPARE_BITMASK" | "CANalization" | "Remote_Measurement_350ms" | "J1939_one_byte_1000ms" | "E2E_Test_Trigger" | "COMPARE_BITMASK" | "Canraw_J1939_Comparebitmask_config" |



        @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
        Scenario Outline:RM_CCU_API_HP - Trigger on CANRaw and J1939 message with Start and stop trigger mode Compare to Bitmask and with Floating values for Pre and Post trigger time configured
                Given device <device> is "ONLINE"
                And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
                And verify number of "signals,messages" are "1,1" respectively is present in measurement configuration <meas_config_name>
                And verify <Trigger> as per <Cond1> for "startTrigger,stopTrigger" with "{"preTrigger":4.5,"postTrigger":5.5}" seconds,create if not present
                #And delete the previous data if it is available
                When Remote measurement is activated
                And measurement status is "ACTIVE" within "10" minutes
                And reference system <can_protocol> with Identifier <can_identifier> is started
                And test is executed for "1" minutes
                Then Remote measurement is deactivated
                And measurement status is "INACTIVE" within "10" minutes
                And measurement test results are stored
                And data integrity test is performed on measured data as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>

                Examples:
                        | vehicle | device | meas_config_name               | can_protocol   | can_identifier             | Trigger            | Trigger_type      | Cond1                          |
                        | " "     | "CCU"  | "E2E_CAN_RAW_COMPARE_BITMASK" | "CANalization" | "Remote_Measurement_350ms" | "E2E_Test_Trigger" | "COMPARE_BITMASK" | "Canraw_comparebitmask_config" |



        @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
        Scenario Outline:RM_CCU_API_HP - Trigger on CANRaw or J1939 message with mode APPEARS
                Given device <device> is "ONLINE"
                And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
                And verify number of "messages" are "2" respectively is present in measurement configuration <meas_config_name>
                And verify <Trigger> as per <Cond1> for "startTrigger,stopTrigger",create if not present
                #And delete the previous data if it is available
                And reference system <can_protocol> with Identifier <can_identifier_1> is started
                When Remote measurement is activated
                And measurement status is "ACTIVE" within "10" minutes
                And test is executed for "30" seconds
                And VRS with protocol <can_protocol> and identifier <can_identifier_1> is stopped
                And test is executed for "10" seconds
                And reference system <can_protocol> with Identifier <can_identifier_2> is started
                And test is executed for "30" seconds
                Then Remote measurement is deactivated
                And measurement status is "INACTIVE" within "10" minutes
                And VRS with protocol <can_protocol> and identifier <can_identifier_2> is stopped
                And measurement test results are stored
                And data integrity test is performed on measured data as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>

                Examples:
                        | vehicle | device | meas_config_name            | can_protocol   | can_identifier_1           | can_identifier_2           | Trigger            | Trigger_type | Cond1                         |
                        | " "     | "CCU"  | "E2E_CAN_RAW_J1939_APPEAR" | "CANalization" | "RM_CANRaw_message1_400ms" | "J1939_8byte_500ms"        | "E2E_Test_Trigger" | "APPEARS"    | "Canraw_J1939_Appears_config" |
                        | " "     | "CCU"  | "E2E_CAN_RAW_APPEAR"       | "CANalization" | "RM_CANRaw_message1_400ms" | "RM_CANRaw_message2_400ms" | "E2E_Test_Trigger" | "APPEARS"    | "Canraw_Appears_config"       |
                        | " "     | "CCU"  | "E2E_J1939_APPEAR"         | "CANalization" | "J1939_8byte_500ms"        | "J1939_Measurement_200ms"  | "E2E_Test_Trigger" | "APPEARS"    | "J1939_Appears_config"        |



        @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
        Scenario Outline:RM_CCU_API_HP - Trigger on CANRaw or J1939 message with Start trigger mode Compare to Bitmask and Stop trigger mode APPEAR
                Given device <device> is "ONLINE"
                And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
                And verify number of "messages" are "2" respectively is present in measurement configuration <meas_config_name>
                And verify <Trigger> as per <Cond1> for "startTrigger,stopTrigger",create if not present
                #And delete the previous data if it is available
                When Remote measurement is activated
                And measurement status is "ACTIVE" within "10" minutes
                And reference system <can_protocol> with Identifier <can_identifier_1> is started
                And test is executed for "30" seconds
                And VRS with protocol <can_protocol> and identifier <can_identifier_1> is stopped
                And test is executed for "10" seconds
                And reference system <can_protocol> with Identifier <can_identifier_2> is started
                And test is executed for "30" seconds
                Then Remote measurement is deactivated
                And measurement status is "INACTIVE" within "10" minutes
                And VRS with protocol <can_protocol> and identifier <can_identifier_2> is stopped
                And measurement test results are stored
                And data integrity test is performed on measured data for "START" trigger as per trigger <Trigger> trigger condition <Cond2> for trigger type <Start_Trigger_type>
                And data integrity test is performed on measured data for "STOP" trigger as per trigger <Trigger> trigger condition <Cond3> for trigger type <Stop_Trigger_type>

                Examples:
                        | vehicle | device | meas_config_name                    | can_protocol   | can_identifier_1           | can_identifier_2       | Trigger           | Start_Trigger_type | Stop_Trigger_type | Cond2                          |Cond3                         |Cond1                                       |
                        | " "     | "CCU"  | "E2E_CAN_RAW_J1939_COMPARE_APPEAR" | "CANalization" | "Remote_Measurement_350ms" | "J1939_8byte_500ms"    | "E2E_Test_Trigger" | "COMPARE_BITMASK"  | "APPEARS"         | "Canraw_comparebitmask_config" |"Canraw_J1939_Appears_config" |"Canraw_comparebitmask_J1939_Appears_config"|



