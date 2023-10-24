Feature:  Remote Measurement on Trigger on variation of message HP
   @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Triggering measurement when there is variation of message with masking in start trigger and stop trigger
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
        And measurement data integrity test is performed
        And data integrity test is performed on measured data as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>

Examples:
        |vehicle  |device |meas_config_name                       |can_protocol   |can_identifier               |Trigger              |Trigger_type        | Cond1                   |
        |" "      |"CCU"  |"E2E_TRIGGER_ON_VARIATION_MESSAGE"    |"CANalization" |"Remote_Measurement_350ms"   |"E2E_Test_Trigger"   |"Message_Variation" | "messageVariationconfig"|


   @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Triggering measurement when there is variation of message with masking only with start trigger
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
        And measurement data integrity test is performed
        And data integrity test is performed on measured data for "START" trigger as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>

Examples:
        |vehicle  |device |meas_config_name                       |can_protocol   |can_identifier                |Trigger             |Trigger_type        | Cond1                    |
        |" "      |"CCU"  |"E2E_TRIGGER_ON_VARIATION_MESSAGE"    |"CANalization" |"Remote_Measurement_350ms"   |"E2E_Test_Trigger"   |"Message_Variation" | "messageVariationconfig"| 

@E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Triggering measurement when there is variation of message with masking only with stop trigger
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
        And measurement data integrity test is performed
        And data integrity test is performed on measured data for "STOP" trigger as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>

Examples:
        |vehicle  |device |meas_config_name                       |can_protocol   |can_identifier               |Trigger             |Trigger_type        | Cond1                    |
        |" "      |"CCU"  |"E2E_TRIGGER_ON_VARIATION_MESSAGE"    |"CANalization" |"Remote_Measurement_350ms"   |"E2E_Test_Trigger"   |"Message_Variation" | "messageVariationconfig"|   

 