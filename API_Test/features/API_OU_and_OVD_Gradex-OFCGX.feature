Feature: Happy path for Remote Measurement when Remote Flashing is activated on same device initially
    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @BV-UC_OTA_Updates_GX @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_RF_CCU_API_HP : Execute Remote Measurement when Remote Flashing is activated
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And the "2"nd reference system <Protocol> with Identifier <Identifier> is started
        And the "2"nd reference system <Protocol> with Identifier <Identifier1> is started
        And check ECU flashing DP <distribution_package> is available  
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "300" seconds
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        And flashing status of OTA package is changed to "UPDATING" within "100" seconds
        And the "3"nd reference system <Protocol_RM> with Identifier <Identifier_RM> is started
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        #And delete the previous data if it is available
        When Remote measurement is activated
        And measurement status is "ACTIVE"
        And test is executed for "2" minutes
        Then flashing status of OTA package is changed to "UPDATE_SUCCESS" within "600" seconds
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        #And test results are verified
        And measurement test results are stored
        And measurement test results are verified
        And reference system is stopped

        Examples:
           | vehicle| device | distribution_package      | Protocol  | Identifier      | Identifier1      | Fota         | Fota_Identifier        |Protocol_RM|Identifier_RM                 |signal_collection     |meas_config_name      |
           | "  "   | "CCU"  | "E2E_RF_Standard_Job_Slow"| "UDSonCAN"| "DemoFlashSim"  | "DemoFlashSim_1" |"CANalization"| "DriverApp_Break_True" |"MONonCAN" |"MONonCAN_500k_highloadidents"|"E2E_CAN_RAW_MON_500K"|"E2E_CAN_RAW_MON_500K"|


    @E2E-API @E2E-CCU @E2E-Gradex @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RF_RM_RGRADEX_RD_CCU_API_HP: Execute RM ,RF via distribution package when GradeX-RD is activated
    Given device <device> is "ONLINE"
        When the "2"nd reference system <Protocol_xRD> with Identifier <Identifier_xRD> is started
        And task <RDTask> is executed
        And verify "EXECUTED" for "Task" is available within "5" minutes
        And test is executed for "2" minutes
        Then verify "JOB_SUCCESS" for "Job Result" is available within "1" minutes
        And verify RD GradeX <dtc_code_result> is as expected
        And VRS with protocol <Protocol_xRD> and identifier <Identifier_xRD> is stopped
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        And check ECU flashing DP <distribution_package> is available  
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "300" seconds
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        And flashing status of OTA package is changed to "UPDATING" within "100" seconds
        And reference system <Protocol_RM> with Identifier <Identifier_RM> is started
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        #And delete the previous data if it is available
        When Remote measurement is activated
        And measurement status is "ACTIVE"
        And test is executed for "2" minutes
        Then flashing status of OTA package is changed to "UPDATE_SUCCESS" within "600" seconds
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And measurement test results are verified
        #Then test results are verified
        And reference system is stopped
        And task <RDCleanUpTask> is executed
        And verify "EXECUTED" for "Task" is available within "1" minutes

        Examples:
            | vehicle | device |  distribution_package           | Protocol   | Identifier    | Identifier1      | Fota         |Fota_Identifier       |Protocol_xRD | Identifier_xRD      | RDTask                | RDCleanUpTask  |Protocol_RM    |Identifier_RM                 |signal_collection     |meas_config_name      | dtc_code_result    | 
            | " "     | "CCU"  | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN" |"DemoFlashSim" | "DemoFlashSim_1" |"CANalization"|"DriverApp_Break_True"|"UDSonCAN"   | "UDS_Resp_2DTCs_RD" | "remotediagpatch.zip" | "deletejob.zip"|"CANalization" |"Remote_Measurement_350ms"|"E2E_CAN_RAW_MON_500K"|"E2E_CAN_RAW_MON_500K"|"AC0A9C17AC080522AC"|