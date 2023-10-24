Feature: Prevent lifecycle inconsistencies in Remote Measurement Workflow
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP : Make device OFFLINE/ONLINE by GSM off/on before activating/deactivating RM config and try "RETRY" option
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        When "stopGSMConnection" and "activate" remote measurement
        And re-activate remote measurement for "3" times using retry option
        And command to "startGSMConnection" GSM mode of the device
        And wait for device to be "ONLINE"
        And measurement status is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And test is executed for "0.5" minutes
        And "stopGSMConnection" and "deactivate" remote measurement
        And re-deactivate remote measurement for "3" times using retry option
        And command to "startGSMConnection" GSM mode of the device
        And wait for device to be "ONLINE"
        And reference system is stopped
        And measurement status is "INACTIVE"
        Then measurement test results are stored
        And measurement data integrity test is performed
        Examples: 
            | vehicle | device | meas_config_name       | Protocol   | Identifier                | 
            | " "     | "CCU"  | "E2E_CAN_RAW_MON_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" | 

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP : Update RM config when previous config is in IN_ACTIVATION status and try "RETRY" option
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        When "stopGSMConnection" and "activate" remote measurement
        And Measurement job <meas_config_name> is in "draft" state
        And Verify Measurement job <meas_config_name> can be set to "Release" state
        And re-activate remote measurement for "3" times using retry option
        And command to "startGSMConnection" GSM mode of the device
        And wait for device to be "ONLINE"
        And measurement status of older version measurement configuration is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And test is executed for "0.5" minutes
        And reference system is stopped
        And Remote measurement is deactivated
        And measurement status is "INACTIVE"
        Then measurement test results are stored
        And measurement data integrity test is performed including configuration "version" validation

        Examples: 
            | vehicle | device | meas_config_name       | Protocol   | Identifier                     | 
            | " "     | "CCU"  | "E2E_CAN_RAW_MON_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" | 

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP : Retry both activate and deactivate when device is OFFLINE
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        When "stopGSMConnection" and "activate" remote measurement
        And re-activate remote measurement for "3" times using retry option
        And test is executed for "0.2" minutes
        And Remote measurement is deactivated
        And re-deactivate remote measurement for "1" times using retry option
        And command to "startGSMConnection" GSM mode of the device
        And wait for device to be "ONLINE"
        Then measurement status is "INACTIVE"
        
        Examples: 
            | vehicle | device | meas_config_name       | Protocol   | Identifier                     | 
            | " "     | "CCU"  | "E2E_CAN_RAW_MON_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" |