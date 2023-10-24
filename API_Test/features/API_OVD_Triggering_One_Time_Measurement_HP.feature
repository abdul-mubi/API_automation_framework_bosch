Feature:  Triggering one-time measurement
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Triggering one-time measurement when there is new message with masking and less timeout in start trigger and stop trigger
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs

        And verify number of "signals,messages" are "1,1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger,stopTrigger",create if not present
        #And delete the previous data if it is available
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "4" minutes
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And data integrity test is performed on measured data as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>

        Examples:
            | vehicle | device | meas_config_name                | can_protocol   | can_identifier       | Trigger            | Trigger_type      | Cond1                  |
            | " "     | "CCU"  | "E2E_TRIGGER_ONE_TIME_MESSAGE" | "CANalization" | "RM_Onetime_Message_5000ms" | "E2E_Test_Trigger" | "OneTime_Message" | "oneTimeMessageconfig" |



    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Triggering one-time measurement when there is new message with masking and timeout with only start trigger and pre trigger time
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs

        And verify number of "signals,messages" are "1,1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger" with "{"preTrigger":20}" seconds,create if not present
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
            | vehicle | device | meas_config_name                | can_protocol   | can_identifier       | Trigger            | Trigger_type      | Cond1                  |
            | " "     | "CCU"  | "E2E_TRIGGER_ONE_TIME_MESSAGE" | "CANalization" | "RM_Onetime_Message_5000ms" | "E2E_Test_Trigger" | "OneTime_Message" | "oneTimeMessageconfig" |



    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Triggering one-time measurement when there is new message with masking and timeout with only stop trigger and post trigger time
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs

        And verify number of "signals,messages" are "1,1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "stopTrigger" with "{"preTrigger":0,"postTrigger":10}" seconds,create if not present
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
            | vehicle | device | meas_config_name                | can_protocol   | can_identifier       | Trigger            | Trigger_type      | Cond1                  |
            | " "     | "CCU"  | "E2E_TRIGGER_ONE_TIME_MESSAGE" | "CANalization" | "RM_Onetime_Message_5000ms" | "E2E_Test_Trigger" | "OneTime_Message" | "oneTimeMessageconfig" |



    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Triggering one-time measurement when there is new message with masking and high timeout in start trigger and stop trigger
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs

        And verify number of "signals,messages" are "1,1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger,stopTrigger",create if not present
        #And delete the previous data if it is available
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "4" minutes
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And data integrity test is performed on measured data as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>

        Examples:
            | vehicle | device | meas_config_name                | can_protocol   | can_identifier       | Trigger            | Trigger_type      | Cond1                                 |
            | " "     | "CCU"  | "E2E_TRIGGER_ONE_TIME_MESSAGE" | "CANalization" | "RM_Onetime_Message_5000ms" | "E2E_Test_Trigger" | "OneTime_Message" | "oneTimeMessageWithHighTimeoutconfig" |

    
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Triggering one-time measurement when there is new message with masking and timeout with only start trigger and post trigger time
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,messages" are "1,1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger" with "{"preTrigger":0,"postTrigger":40}" seconds,create if not present     
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
        |vehicle  |device |meas_config_name                       |can_protocol   |can_identifier        |Trigger             |Trigger_type        | Cond1                    |
        |" "      |"CCU"  |"E2E_TRIGGER_ONE_TIME_MESSAGE"         |"CANalization" |"RM_Onetime_Message_5000ms"   |"E2E_Test_Trigger"   |"OneTime_Message" | "oneTimeMessageWithHighTimeoutconfig"| 

