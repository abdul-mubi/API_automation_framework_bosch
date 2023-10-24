Feature: Setting the enhance trigger configuration
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP- Enhance trigger configuration with count period
    Given device <device> is "ONLINE"
      And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
      And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
      And verify <Trigger> as per <Cond1> for "startTrigger,stopTrigger",create if not present
      #And delete the previous data if it is available
      When Remote measurement is activated
      And measurement status is "ACTIVE" within "10" minutes
      And reference system <can_protocol> with Identifier <can_identifier> is started
      And test is executed for "5" minutes
      Then Remote measurement is deactivated
      And measurement status is "INACTIVE" within "10" minutes
      And measurement test results are stored
      And data integrity test is performed on measured data as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>
      Then reference system is stopped

      Examples:
         | vehicle | device| meas_config_name              | Trigger           | Cond1                                 | can_protocol   | can_identifier       |Trigger_type|
         | " "     | "CCU" | "E2E_RM_ENHANCE_TRIGGER_DEMO" | "E2E_Test_Trigger"| "group_count_triggercond_count_Config"| "CANalization" | "Remote_Measurement_350ms" |"COMPARE_CONSTANT"|

    
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP -Enhance trigger configuration with Timeout interrupting the start trigger fire
    Given device <device> is "ONLINE"
      And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
      And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
      And verify <Trigger> as per <Cond1> for "startTrigger,stopTrigger",create if not present
      #And delete the previous data if it is available
      When Remote measurement is activated
      And measurement status is "ACTIVE" within "10" minutes
      And reference system <can_protocol> with Identifier <can_identifier> is started
      And test is executed for "0.5" minutes
      Then Remote measurement is deactivated
      And measurement status is "INACTIVE" within "10" minutes
      Then reference system is stopped
      #And test result is "False"
      And measurement test steps are not generated

      Examples:
         | vehicle | device| meas_config_name              | Trigger            | Cond1                     | can_protocol   | can_identifier       |Trigger_type|
         | " "     | "CCU" | "E2E_RM_ENHANCE_TRIGGER_DEMO" | "E2E_Test_Trigger"| "timeout_config"          | "CANalization" | "Remote_Measurement_350ms" |"COMPARE_CONSTANT"|
         | " "     | "CCU" | "E2E_RM_ENHANCE_TRIGGER_DEMO" | "E2E_Test_Trigger"| "grouptriggercondtn_count"| "CANalization" | "Remote_Measurement_350ms" |"COMPARE_CONSTANT"|

      
   @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
   Scenario Outline:RM_CCU_API_HP - Enhance trigger configuration with start condition and debounce time
    Given device <device> is "ONLINE"
      And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
      And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
      And verify <Trigger> as per <Cond1> for "startTrigger,stopTrigger",create if not present
      When Remote measurement is activated
      And measurement status is "ACTIVE" within "10" minutes
      And reference system <can_protocol> with Identifier <can_identifier> is started
      And test is executed for "0.5" minutes
      Then Remote measurement is deactivated
      And measurement status is "INACTIVE" within "10" minutes
      Then reference system is stopped
      And measurement test steps are not generated

         Examples: 
            | vehicle | device | meas_config_name               | Trigger            | Cond1                           | can_protocol   | can_identifier             | Trigger_type       | 
            | " "     | "CCU"  | "E2E_RM_ENHANCE_TRIGGER_DEMO" | "E2E_Test_Trigger" | "trigger_start_debounce_config" | "CANalization" | "Remote_Measurement_350ms" | "COMPARE_CONSTANT" | 
    
   @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Smoke
   Scenario Outline:RM_CCU_API_HP - Enhance trigger configuration with mode as "static"
      Given device <device> is "ONLINE"
      And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
      And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
      And verify <Trigger> as per <Cond1> for "startTrigger,stopTrigger",create if not present
      When Remote measurement is activated
      And measurement status is "ACTIVE" within "10" minutes
      And reference system <can_protocol> with Identifier <can_identifier> is started
      And test is executed for "0.5" minutes
      Then Remote measurement is deactivated
      And measurement status is "INACTIVE" within "10" minutes
      And measurement test results are stored
      And data integrity test is performed on measured data as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>
      Then reference system is stopped

      Examples: 
         | vehicle | device | meas_config_name              | Trigger            | Cond1                        | can_protocol   | can_identifier             | Trigger_type       | 
         | " "     | "CCU"  | "E2E_RM_ENHANCE_TRIGGER_DEMO" | "E2E_Test_Trigger" | "triggercondt_static_config" | "CANalization" | "Remote_Measurement_350ms" | "COMPARE_CONSTANT" | 
            
    
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Enhance trigger configuration with count and count period
    Given device <device> is "ONLINE"
      And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
      And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
      And verify <Trigger> as per <Cond1> for "startTrigger,stopTrigger",create if not present
      #And delete the previous data if it is available
      When Remote measurement is activated
      And measurement status is "ACTIVE" within "10" minutes
      And reference system <can_protocol> with Identifier <can_identifier> is started
      And test is executed for "0.5" minutes
      Then Remote measurement is deactivated
      And measurement status is "INACTIVE" within "10" minutes
      And measurement test results are stored
      And data integrity test is performed on measured data as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>
      Then reference system is stopped

      Examples:
         | vehicle | device | meas_config_name               | Trigger           | Cond1                                 | can_protocol   | can_identifier             |Trigger_type|
         | " "     | "CCU"  | "E2E_RM_ENHANCE_TRIGGER_DEMO" | "E2E_Test_Trigger"| "triggercondtn_count_timeout"         | "CANalization" | "Remote_Measurement_350ms" |"COMPARE_CONSTANT"|
         | " "     | "CCU"  | "E2E_RM_ENHANCE_TRIGGER_DEMO" | "E2E_Test_Trigger"| "group_count_countperiod_config"      | "CANalization" | "Remote_Measurement_350ms" |"COMPARE_CONSTANT"|
      

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP- Enhance trigger configuration with debounce time
    Given device <device> is "ONLINE"
      And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
      And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
      And verify <Trigger> as per <Cond1> for "startTrigger,stopTrigger",create if not present
      #And delete the previous data if it is available
      When Remote measurement is activated
      And measurement status is "ACTIVE" within "10" minutes
      And reference system <can_protocol> with Identifier <can_identifier> is started
      And test is executed for "0.5" minutes
      Then Remote measurement is deactivated
      And measurement status is "INACTIVE" within "10" minutes
      And measurement test results are stored
      And data integrity test is performed on measured data as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>
      Then reference system is stopped

      Examples:
         | vehicle | device | meas_config_name                | Trigger           | Cond1                             | can_protocol   | can_identifier       |Trigger_type|
         #| " "     | "CCU" | "E2E_RM_ENHANCE_TRIGGER_DEMO " | "E2E_Test_Trigger"| "triggercondt_debounce_config"    | "CANalization" | "Remote_Measurement_350ms" |"COMPARE_CONSTANT"|
        # | " "     | "CCU" | "E2E_RM_ENHANCE_TRIGGER_DEMO " | "E2E_Test_Trigger"| "triggercondt_debouncehigh_config"| "CANalization" | "Remote_Measurement_350ms" |"COMPARE_CONSTANT"|
         | " "     | "CCU"  | "E2E_RM_ENHANCE_TRIGGER_DEMO"   | "E2E_Test_Trigger"| "group_count_triggercond_debounce"| "CANalization" | "Remote_Measurement_350ms" |"COMPARE_CONSTANT"|


    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Enhance trigger configuration with Logic as "Inverting"
      Given device <device> is "ONLINE"
      And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
      And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
      And verify <Trigger> as per <Cond1> for "startTrigger,stopTrigger",create if not present
      When Remote measurement is activated
      And measurement status is "ACTIVE" within "10" minutes
      And reference system <can_protocol> with Identifier <can_identifier> is started
      And test is executed for "0.5" minutes
      Then Remote measurement is deactivated
      And measurement status is "INACTIVE" within "10" minutes
      And measurement test results are stored
      And data integrity test is performed on measured data as per trigger <Trigger> trigger condition <Cond1> for trigger type <Trigger_type>
      Then reference system is stopped

         Examples: 
            | vehicle | device | meas_config_name               | Trigger            | Cond1                              | can_protocol   | can_identifier             | Trigger_type       | 
            | " "     | "CCU"  | "E2E_RM_ENHANCE_TRIGGER_DEMO" | "E2E_Test_Trigger" | "triggercondtn_Inv_config"         | "CANalization" | "Remote_Measurement_350ms" | "COMPARE_CONSTANT" | 
            | " "     | "CCU"  | "E2E_RM_ENHANCE_TRIGGER_DEMO" | "E2E_Test_Trigger" | "group_inverting_config"           | "CANalization" | "Remote_Measurement_350ms" | "COMPARE_CONSTANT" | 
            | " "     | "CCU"  | "E2E_RM_ENHANCE_TRIGGER_DEMO" | "E2E_Test_Trigger" | "triggercondt_debounce_inv_config" | "CANalization" | "Remote_Measurement_350ms" | "COMPARE_CONSTANT" | 

          