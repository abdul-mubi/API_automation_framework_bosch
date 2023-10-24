Feature: Power-management Timer wakeup
    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Regression
    Scenario Outline:PM_CCU_API_HP - Timer wakeup
    Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        When time <moment> for device wake up is set and device should be online for <duration>
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And test waited till device wakeup configuration time <moment> is met 
        And wait for device to be "ONLINE"
        And test waited till device wakeup configuration time <duration> is met 
        And wait for device to be "OFFLINE"
        And verify device status stayed in "OFFLINE" for "000:00:05"    

        Examples:
            | vehicle  | device  | moment   | duration |
            |" "  | "CCU"  | "000:00:05"   |"000:00:05"|


    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Regression
    Scenario Outline:PM_CCU_API_HP - Timer wakeup : Device must be online when CL15 is on
    Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        When time <moment> for device wake up is set and device should be online for <duration>
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And test waited till device wakeup configuration time <moment> is met
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And test waited till device wakeup configuration time <duration> is met 
        And verify device status stayed in "ONLINE" for "000:00:05"
                
        Examples:
            | vehicle  | device  | moment        | duration |
            |" "       | "CCU"  | "000:00:15"   |"000:00:05"|    


    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Regression
    Scenario Outline:PM_CCU_API_HP -Timer wakeup : Mode wakeup configuration for device
    Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And time mode and duration for device wake up is set <moment> <mode> <duration>
        And switch "CL15" is turned "Off"
        Then wait for device to be "OFFLINE"
        And test waited till device wakeup configuration time <moment> is met 
        And wait for device to be "ONLINE"
        And test waited till device wakeup configuration time <duration> is met 
        And wait for device to be "OFFLINE"

        Examples: 
            | vehicle  | device  | mode    |moment        |duration   |
        #|" "       | "CCU"  |"weekly" |"000:00:05" |"000:00:05"|
        #|" "       | "CCU"  |"monthly"|"000:00:05" |"000:00:05"|
        #|" "       | "CCU"  |"yearly" |"000:00:05" |"000:00:05"|
        #|" "       | "CCU"  |"every_second_day"|"000:00:05" |"000:00:05"|
            |" "       | "CCU"  |"daily"  |"000:00:05" |"000:00:05"|


    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Regression
    Scenario Outline:PM_CCU_API_HP - Timer wakeup : Wakeup timer perform disabled and enabled
    Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        When time <moment> for device wake up is set and device should be online for <duration>
        And set wakeup timer state as "DISABLED"
        And test waits for "1" minutes
        And set wakeup timer state as "ENABLED"
        And switch "CL15" is turned "Off"
        Then wait for device to be "OFFLINE"
        And test waited till device wakeup configuration time <moment> is met
        And wait for device to be "ONLINE"
        And test waited till device wakeup configuration time <duration> is met
        And wait for device to be "OFFLINE"


        Examples:
            | vehicle  | device  | moment      | duration |
            |" "       | "CCU"  | "000:00:07" |"000:00:08"|

    
    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Regression
    Scenario Outline:PM_CCU_API_HP - Timer wakeup : Device should remain offline when CL30 is off
    Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        When time <moment> for device wake up is set and device should be online for <duration>
        And switch "CL30" is turned "Off"
        Then wait for device to be "OFFLINE"
        And test waited till device wakeup configuration time <moment> is met
        And verify device status stayed in "OFFLINE" for "000:00:05" 
        And switch "CL30" is turned "On"        
        Then wait for device to be "ONLINE"    

        Examples:
            | vehicle  | device  | moment     | duration  |
            |" "       | "CCU"  | "000:00:05" |"000:00:05"|


    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Regression
    Scenario Outline:PM_CCU_API_HP - Timer wakeup : making the wakeup timer sate as disabled
    Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        When time <moment> for device wake up is set and device should be online for <duration>
        And set wakeup timer state as "DISABLED"
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        Then verify device status stayed in "OFFLINE" for <moment>  
        And verify device status stayed in "OFFLINE" for <duration>
        And verify device status stayed in "OFFLINE" for "000:00:05"  

            Examples:
                | vehicle  | device  | moment      | duration |
                |" "       | "CCU"  | "000:00:05" |"000:00:05"|      
          
    
    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Regression
    Scenario Outline:PM_CCU_API_HP - Timer wakeup : Wake up setting is not lost with CL30
    Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        When time <moment> for device wake up is set and device should be online for <duration>
        And switch "CL15" is turned "Off" 
        Then wait for device to be "OFFLINE"
        And switch "CL30" is turned "Off" 
        Then wait for device to be "OFFLINE"
        And switch "CL30" is turned "On"
        And test waited till device wakeup configuration time <moment> is met
        Then wait for device to be "ONLINE" 
        And test waited till device wakeup configuration time <duration> is met
        Then wait for device to be "OFFLINE" 
        And verify device status stayed in "OFFLINE" for "000:00:05" 

            Examples:
                | vehicle  | device  | moment       | duration |
                |" "       | "CCU"  | "000:00:10" |"000:00:10" |