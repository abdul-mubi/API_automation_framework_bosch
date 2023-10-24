Feature:Remote wake up by SMS

    @E2E-API @E2E-CCU @E2E-HINO @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement
    Scenario Outline:RM_CCU_API_HP:- Triggering measurement after device wakes up by the SMS trigger event

        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        When set remote wakeup SMS state as "ENABLED" for duration <sms_duration> is configured
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger",create if not present
        And Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And device wake-up with SMS is triggered
        And wait for device to be "ONLINE"
        And test is executed for "3" minutes
        And measurement test results are stored
        Then validate measurement data is recorded
        And test waited till device remote wakeup configuration <sms_duration> is met
        And wait for device to be "OFFLINE"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        
        Examples:
                |vehicle| device  | sms_duration  | meas_config_name  |Trigger           |Trigger_type      | Cond1              |
                |" "    | "CCU"   | "00:05:00"    |   "POWER_CTPG"   |"E2E_Test_Trigger"|"CONDITION_WAKEUP"| "wakeup_sms_config"|
    

    @E2E-API @E2E-CCU @E2E-FM @E2E-HINO @E2E-HP
    Scenario Outline:FM_CCU_API_HP :- Remote wakeup on SMS

        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        When set remote wakeup SMS state as "ENABLED" for duration <sms_duration> is configured
        And switch "CL15" is turned "Off" 
        And wait for device to be "OFFLINE"
        And device wake-up with SMS is triggered
        And wait for device to be "ONLINE"
        And test waited till device remote wakeup configuration <sms_duration> is met
        And wait for device to be "OFFLINE"
        Then verify device status stayed in "OFFLINE" for "000:00:05"
        
        Examples:
                |vehicle| device | sms_duration|  duration  |
                |" "    | "CCU" | "00:05:00"  | "000:00:05"| 

    
    @E2E-API @E2E-CCU @E2E-FM @E2E-HINO @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement
    Scenario Outline:RM_CCU_API_HP:- Activate RM before device wakes up via SMS 

        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        When set remote wakeup SMS state as "ENABLED" for duration <sms_duration> is configured 
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        And Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        Then device wake-up with SMS is triggered
        And wait for device to be "ONLINE"
        And test is executed for "1" minutes
        And measurement test results are stored
        And validate measurement data is recorded
        And test waited till device remote wakeup configuration <sms_duration> is met
        And wait for device to be "OFFLINE"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes

        Examples:
            |vehicle| device | sms_duration| meas_config_name |duration   | 
            |" "    | "CCU"  | "00:05:00"    |   "POWER_CTPG"  |"000:00:05"| 

    
    @E2E-API @E2E-CCU @E2E-FM @E2E-HINO @E2E-SP
    Scenario Outline:FM_CCU_API_SP:- Device wakes up via Timer instead of SMS

        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle> 
        When time <moment> for device wake up is set and device should be online for <duration>
        When set remote wakeup SMS state as "ENABLED" for duration <sms_duration> is configured
        And switch "CL15" is turned "Off" 
        And wait for device to be "OFFLINE"
        And test waited till device wakeup configuration time <moment> is met
        And device wake-up with SMS is triggered
        And wait for device to be "ONLINE"
        And test waited till device remote wakeup configuration <sms_duration> is met
        And wait for device to be "ONLINE"
        And test waited till device wakeup configuration time <duration>  is met  
        And wait for device to be "OFFLINE"
        Then verify device status stayed in "OFFLINE" for "000:00:05"

        Examples:
            |vehicle| device | sms_duration|  duration  |moment     |
            |" "    | "CCU" | "00:05:00"  | "000:00:10"| "000:00:05"|

    
    @E2E-API @E2E-CCU @E2E-FM @E2E-HINO @E2E-HP
    Scenario Outline:FM_CCU_API_HP:- Shutdown prolonged by turning on CL15 when device wakes up with SMS

        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        When set remote wakeup SMS state as "ENABLED" for duration <sms_duration> is configured
        And switch "CL15" is turned "Off" 
        And wait for device to be "OFFLINE"
        And device wake-up with SMS is triggered
        And wait for device to be "ONLINE"
        And switch "CL15" is turned "On"
        And test waited till device remote wakeup configuration <sms_duration> is met
        And wait for device to be "ONLINE"
        Then verify device status stayed in "ONLINE" for "000:00:05"
        
        Examples:
            |vehicle| device | sms_duration|duration  | 
            |" "    | "CCU" | "00:05:00"  |"000:00:05"|


    @E2E-API @E2E-CCU @E2E-HINO @E2E-HP
    Scenario Outline:FM_CCU_API_HP:- Shutdown of device is prolonged as device in non-sleep mode when it wakes up via SMS

        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        When set remote wakeup SMS state as "ENABLED" for duration <sms_duration> is configured
        And switch "CL15" is turned "Off"
        And switch "CL30" is turned "Off"
        And switch "CL30" is turned "On"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And device wake-up with SMS is triggered
        And wait for device to be "ONLINE"
        And test waited till device remote wakeup configuration <sms_duration> is met
        And wait for device to be "ONLINE"
        Then verify device status stayed in "ONLINE" for "000:00:05"
        
        Examples:
            |vehicle| device | sms_duration| duration   | 
            |" "    | "CCU" | "00:05:00"  | "000:00:05"| 


    @E2E-API @E2E-CCU @E2E-HINO @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement
    Scenario Outline:RM_CCU_API_HP:- Shutdown of device is prolonged by RM when device wakes up via SMS

        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        When set remote wakeup SMS state as "ENABLED" for duration <sms_duration> is configured
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
            
        And switch "CL15" is turned "Off" 
        And wait for device to be "OFFLINE"
        And device wake-up with SMS is triggered
        And wait for device to be "ONLINE"
        And Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And test is executed for "1.5" minutes
        And measurement test results are stored
        And validate measurement data is recorded

        And test waited till device remote wakeup configuration <sms_duration> is met
        And wait for device to be "OFFLINE"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
           
        Examples:
            |vehicle| device  | sms_duration  | meas_config_name |duration   |
            |" "    | "CCU"   | "00:05:00"    |   "POWER_CTPG"   |"000:00:05"|


    @E2E-API @E2E-CCU @E2E-HINO @E2E-RM @BV-UC_RemoteMeasurement @E2E-SP
    Scenario Outline:RM_CCU_API_SP:- Remote Measurement on Trigger on Wakeup "Remote" Device Wakeup by Timer 

        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>      

        When time <moment> for device wake up is set and device should be online for <duration> 
        When set remote wakeup SMS state as "ENABLED" for duration <sms_duration> is configured
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger,stopTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And switch "CL15" is turned "Off" 
        And wait for device to be "OFFLINE"
        And test waited till device wakeup configuration time <moment> is met
        And test waits for "2" minutes
        And device wake-up with SMS is triggered
        And wait for device to be "ONLINE"
        And test is executed for "4" minutes        
        And measurement test results are stored
        #And test result is "False"
        And measurement test results are stored
        And measurement test result is "False"
        And test waited till device remote wakeup configuration <sms_duration> is met
        And wait for device to be "ONLINE"
        And test waited till device wakeup configuration time <moment> is met 
        And wait for device to be "OFFLINE"
        And switch "CL15" is turned "On" 
        And wait for device to be "ONLINE"
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes

        Examples:
            |vehicle| device  | sms_duration | meas_config_name      |moment     | duration  |Trigger           |Trigger_type      | Cond1                    |
            |" "    | "CCU"   | "000:06:00"  |  "wakeup_SMS_config" |"000:00:05"|"000:00:10"|"E2E_Test_Trigger"|"CONDITION_WAKEUP"| "timer_wakeup_sms_config"|



      





 
     