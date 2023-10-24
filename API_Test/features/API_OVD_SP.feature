Feature:Remote Measurement   
@E2E-API @E2E-CCU @E2E-SP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_SP : Turn on/off CL30 before remote measurement has started
            Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
       
        And switch "CL15" is turned "Off"
        And switch "CL30" is turned "Off"
        And wait for device to be "OFFLINE"
        #And delete the previous data if it is available
        When Remote measurement is activated
        And measurement status "INACTIVE" and substatus "IN_ACTIVATION"
        And switch "CL30" is turned "On"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And measurement status is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And test is executed for "1" minutes
        And measurement test results are stored
        And measurement data integrity smoke test is performed 
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And reference system is stopped
       
        Examples: 
            | vehicle | device |  meas_config_name      | Protocol   | Identifier                     |
            | " "     | "CCU"  | "E2E_CAN_RAW_MON_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" | 
    
 @E2E-API @E2E-CCU @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_SP : Turn off ECU while RM is ongoing
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And reference system <Protocol> with Identifier <Identifier> is started
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        #And delete the previous data if it is available
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And test is executed for "1" minutes
        And reference system is stopped
        And measurement test results are stored 
        And test is executed for "1" minutes
        And measurement test result downloads are reprepared 
        And measurement test results are stored 
        And measurement test results having "No" newer measured data is validated 
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
       

        Examples: 
            | vehicle | device |meas_config_name        | Protocol   | Identifier                     |
            | " "     | "CCU"  | "E2E_CAN_RAW_MON_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" |  