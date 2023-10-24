Feature: Power-management Timer wakeup
    @E2E-API @E2E-CCU @E2E-FM @E2E-Regression @E2E-SP
    Scenario Outline:PM_CCU_API_SP - Timer wakeup : Device remains Online when CL15 is turned on and off
    Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        When time <moment> for device wake up is set and device should be online for <duration>
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And verify device status stayed in "ONLINE" for <moment>  
        And verify device status stayed in "ONLINE" for <duration>
        And verify device status stayed in "ONLINE" for "000:00:05"
                
        Examples:
            | vehicle  | device  | moment       | duration |
            |" "       | "CCU"   | "000:00:05"  |"000:00:05"|

    @E2E-API @E2E-CCU @E2E-FM @E2E-Regression @E2E-SP
    Scenario Outline:PM_CCU_API_SP -Timer wakeup : CL30 turned on during wakeup config device should be offline
    Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        When time <moment> for device wake up is set and device should be online for <duration>
        And switch "CL15" is turned "Off"
        And switch "CL30" is turned "Off"
        Then wait for device to be "OFFLINE"
        And verify device status stayed in "OFFLINE" for <moment>
        And verify device status stayed in "OFFLINE" for "000:00:02"
        And switch "CL30" is turned "On"
        And verify device status stayed in "OFFLINE" for "000:00:05"
            
        Examples:
            | vehicle  | device  | moment        | duration  |
            |" "       | "CCU"  | "000:00:05"   |"000:00:05" |

     