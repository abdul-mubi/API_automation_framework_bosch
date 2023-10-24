Feature:Pause measurement jobs during ECU Updates
    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @E2E-Regression @E2E-Paccar
    Scenario Outline:RM_RF_CCU_API_HP - Pause measurement jobs during ECU Update
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        And create measurment configuration <meas_config_name> if it not is available
        And check ECU flashing DP <distribution_package> is available
        When Remote measurement is activated
        Then measurement status is "ACTIVE" within "10" minutes
        And test is executed for "1" minutes
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        When OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        Then flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "200" seconds
        And flashing status of OTA package is changed to "UPDATE_SUCCESS" within "200" seconds
        When reference system is stopped
        Then test is executed for "1" minutes
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And measurement test results are present and 2 in number
 	    
        Examples:
            | vehicle| device |meas_config_name| distribution_package                                                   | Protocol   | Identifier     | Identifier1      | 
            | " "    |"CCU"   |"POWER_CTPG_new"|"VECU_Slow_runImmediately_InstallRdaJob_measurement_paused_capability"  | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | 


    @E2E-API @E2E-CCU @E2E-HP @E2E-Regression @E2E-Paccar @E2E-RF
    Scenario Outline:RM_RF_CCU_API_HP - Activate measurement jobs when ECU Update is ongoing with measurement stop trigger
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        And create measurment configuration <meas_config_name> if it not is available
        And check ECU flashing DP <distribution_package> is available
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        When OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        Then flashing status of OTA package is changed to "UPDATING" within "200" seconds
        And Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And test is executed for "40" seconds
        And measurement test steps are not generated
        And flashing status of OTA package is changed to "UPDATE_SUCCESS" within "200" seconds
        When reference system is stopped
        Then test is executed for "1" minutes
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And measurement test results are present and 1 in number
 	    
        Examples:
            | vehicle| device |meas_config_name| distribution_package                                                   | Protocol   | Identifier     | Identifier1      | 
            | " "    |"CCU"   |"POWER_CTPG_new"|"VECU_Slow_runImmediately_InstallRdaJob_measurement_paused_capability"  | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | 