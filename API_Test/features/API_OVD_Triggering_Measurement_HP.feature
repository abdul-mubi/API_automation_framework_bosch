Feature: Triggering measurement
    @E2E-API @E2E-CCU @E2E-HINO @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Triggering measurement after device is started by the timer trigger event
    Given device <device> is "ONLINE"
        And device operation "rebootDevice" is performed
        And wait for device to be "ONLINE"
        And map device to the vehicle <vehicle>
        When time <time> for device wake up is set and device should be online for <duration>
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger",create if not present
        And reference system <Protocol> with Identifier <Identifier> is started
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And test is executed for "2" minutes
        And measurement test steps are not generated
        And VRS with protocol <Protocol> and identifier <Identifier> is stopped
        When switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And test waited till device wakeup configuration time <time> is met
        And wait for device to be "ONLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And test is executed for "5" minutes
        And VRS with protocol <Protocol> and identifier <Identifier> is stopped
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And validate measurement data is recorded
    
        Examples:
            | vehicle | device  | time        | duration   |  Trigger            | Cond1                      |  Protocol  | Identifier                     | meas_config_name                      |
            | " "     | "CCU"  | "000:00:12" | "000:00:20" | "E2E_Test_Trigger"  | "TimerTriggerWithoutDelay" | "MONonCAN" | "MONonCAN_500k_highloadidents" | "E2E_CAN_RAW_MON_500K_Trigger_Timer" |

   
    @E2E-API @E2E-CCU @E2E-HINO @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Triggering measurement after the delay time when the device is started by a timer trigger event
    Given device <device> is "ONLINE"
        And device operation "rebootDevice" is performed
        And wait for device to be "ONLINE"
        And map device to the vehicle <vehicle>
        When time <time> for device wake up is set and device should be online for <duration>
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And switch "CL15" is turned "Off"
        Then wait for device to be "OFFLINE"
        And test waited till device wakeup configuration time <time> is met
        And wait for device to be "ONLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And test is executed for "5" minutes
        And VRS with protocol <Protocol> and identifier <Identifier> is stopped
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And validate measurement data is recorded
    
        Examples:
            | vehicle   | device  | time        | duration   |  Trigger            | Cond1                   |  Protocol  | Identifier                     | meas_config_name                      |
            |  " "      | "CCU"  | "000:00:08"  | "000:00:05" | "E2E_Test_Trigger" | "TimerTriggerWithDelay" | "MONonCAN" | "MONonCAN_500k_highloadidents" | "E2E_CAN_RAW_MON_500K_Trigger_Timer" |

 
 @E2E-API @E2E-CCU @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Triggering measurement after device is started by the TL15 trigger event
    Given device <device> is "ONLINE"
        And device operation "rebootDevice" is performed
        And wait for device to be "ONLINE"
        And map device to the vehicle <vehicle>
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger",create if not present
        And reference system <Protocol> with Identifier <Identifier> is started
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And test is executed for "2" minutes
        And measurement test steps are not generated
        And VRS with protocol <Protocol> and identifier <Identifier> is stopped
        And switch "CL15" is turned "Off"
        Then wait for device to be "OFFLINE"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And test is executed for "4" minutes
        And VRS with protocol <Protocol> and identifier <Identifier> is stopped
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And validate measurement data is recorded
    
        Examples:
            | vehicle | device  | duration    |  Trigger            | Cond1                     |  Protocol   | Identifier                     | meas_config_name                     |
			| " "     | "CCU"  | "000:00:05"  |  "E2E_Test_Trigger" | "TL15TriggerWithoutDelay" |  "MONonCAN" | "MONonCAN_500k_highloadidents" | "E2E_CAN_RAW_MON_500K_Trigger_TL15" |
 
 
 @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Triggering measurement after the delay time when the device is started by a TL15 trigger event
    Given device <device> is "ONLINE"
        And switch "CL15" is turned "Off"
        Then wait for device to be "OFFLINE"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And map device to the vehicle <vehicle>
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger",create if not present
        And reference system <Protocol> with Identifier <Identifier> is started
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And test is executed for "4" minutes
        And VRS with protocol <Protocol> and identifier <Identifier> is stopped
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And validate measurement data is recorded
    
        Examples:
            | vehicle  | device |  Trigger           | Cond1                  |  Protocol  | Identifier                     | meas_config_name                     |
            | " "      | "CCU"  | "E2E_Test_Trigger" | "TL15TriggerWithDelay" | "MONonCAN" | "MONonCAN_500k_highloadidents" | "E2E_CAN_RAW_MON_500K_Trigger_TL15" |


     @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP : Triggering RM while device is in sleep mode[CL15]
         Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        #And delete the previous data if it is available
        When Remote measurement is activated
        And measurement status "INACTIVE" and substatus "IN_ACTIVATION"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And measurement status is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And test is executed for "2" minutes
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "15" minutes
        And measurement test results are stored
        And measurement data integrity smoke test is performed 
        And reference system is stopped
       
        Examples: 
            | vehicle | device | meas_config_name      | Protocol   | Identifier      |
            | " "     | "CCU"  | "E2E_CAN_RAW_MON_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" |  

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Triggering measurement after device is started by the TL15 trigger event along with CL30 Off and On 
        Given device <device> is "ONLINE"
        And device operation "rebootDevice" is performed
        And wait for device to be "ONLINE"
        And map device to the vehicle <vehicle>
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger",create if not present
        And reference system <Protocol> with Identifier <Identifier> is started
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And test is executed for "2" minutes
        And measurement test steps are not generated
        And VRS with protocol <Protocol> and identifier <Identifier> is stopped
        And switch "CL15" is turned "Off"
        And switch "CL30" is turned "Off"
        Then wait for device to be "OFFLINE"
        And switch "CL30" is turned "On"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And test is executed for "4" minutes
        And VRS with protocol <Protocol> and identifier <Identifier> is stopped
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And validate measurement data is recorded
    
        Examples:
            | vehicle   | device |  Trigger            | Cond1                     |  Protocol  | Identifier                      | meas_config_name                                 |
            | " "       | "CCU"  | "E2E_Test_Trigger"  | "TL15TriggerWithoutDelay" | "MONonCAN" | "MONonCAN_500k_highloadidents"  | "E2E_CAN_RAW_MON_500K_Trigger_TL15_CL30_OFF_ON" | 