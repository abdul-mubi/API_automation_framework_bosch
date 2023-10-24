Feature: Enrich measurement results with trigger details
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP : Enrich measurement results - Continuous with start trigger of multiple groups and conditions and stop triggers
            Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger,stopTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "2" minutes
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And "Start,Stop" of measurement details are requested
        And validate "START_TRIGGER,STOP_TRIGGER" reason as per trigger condition <Cond1> 

Examples:
        |vehicle  |device |meas_config_name             |can_protocol   |can_identifier               |Trigger              |Trigger_type       | Cond1                                    |
        |" "      |"CCU"  |"E2E_RM_ENHANCE_TRIGGER"    |"CANalization" |"Remote_Measurement_350ms"   |"E2E_Test_Trigger"   |"COMPARE_CONSTANT" | "enrich_RM_Continuous_4levels8conditions"| 
        |" "      |"CCU"  |"E2E_RM_ENHANCE_TRIGGER"    |"CANalization" |"Remote_Measurement_350ms"   |"E2E_Test_Trigger"   |"COMPARE_CONSTANT" | "enrich_RM_Continuous_2levels3conditions"|  

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP : Enrich measurement results - Singleshot with start triggers with 1 group and 2 condition
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "2" minutes
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And "Start,Stop" of measurement details are requested
        And validate "START_TRIGGER,NOT_AVAILABLE" reason as per trigger condition <Cond1>

        Examples: 
            | vehicle | device | signal_collection      | meas_config_name                            | can_protocol   | can_identifier             | Trigger            | Trigger_type       | Cond1                                     | 
            | " "     | "CCU"  | "E2E_CAN_RAW_MON_500K" | "E2E_CAN_RAW_MON_500K_SingleShot_Triggers" | "CANalization" | "Remote_Measurement_350ms" | "E2E_Test_Trigger" | "COMPARE_CONSTANT" | "enrich_RM_Singleshot_1levels2conditions" | 
            
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP : Enrich measurement results - Continuous - Job Installation/Uninstallation with GSM and CL15 reboot
    Given device <device> is "ONLINE"
        When map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And reference system <Protocol> with Identifier <Identifier> is started
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        Then Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        When test is executed for "1" minutes
        And measurement test results are stored
        And command to "stopGSMConnection" GSM mode of the device
        When switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And Remote measurement is deactivated
        When switch "CL15" is turned "On"
        And command to "startGSMConnection" GSM mode of the device
        And wait for device to be "ONLINE"
        And measurement status is "INACTIVE" within "10" minutes
        Then "Start,Stop" of measurement details are requested
        And validate "JOB_INSTALLATION,JOB_UNINSTALLATION" as measurement reason
        And reference system is stopped
        
        Examples: 
            | vehicle | device|  meas_config_name     | Protocol   | Identifier      |
            | " "     | "CCU" | "E2E_CAN_RAW_MON_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP : Enrich measurement results - Continuous - Job Installation/Uninstallation with CL15 reboot
    Given device <device> is "ONLINE"
        When map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And reference system <Protocol> with Identifier <Identifier> is started
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        Then Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        When test is executed for "1" minutes
		And reference system is stopped
        And measurement test results are stored
        When switch "CL15" is turned "Off"
        Then wait for device to be "OFFLINE"
        When switch "CL15" is turned "On"
        Then wait for device to be "ONLINE"
		And reference system <Protocol> with Identifier <Identifier> is started
        And "Start,Stop" of measurement details are requested
        And validate "JOB_INSTALLATION,DRIVE_CYCLE_END" as measurement reason
        When test is executed for "1" minutes
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        Then "Start,Stop" of measurement details are requested
        And validate "DRIVE_CYCLE_START,JOB_UNINSTALLATION" as measurement reason
        And reference system is stopped
        
        Examples: 
            | vehicle | device|  meas_config_name     | Protocol   | Identifier      |
            | " "     | "CCU" | "E2E_CAN_RAW_MON_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" |
