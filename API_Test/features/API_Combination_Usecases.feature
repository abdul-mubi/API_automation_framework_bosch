Feature: Combination Usecses of RD,RF,RM and GradeX
    @E2E-HP @E2E-CCU @E2E-RF @BV-UC_OTA_Updates_GX @E2E-RM @BV-UC_RemoteMeasurement @E2E-RD @E2E-Regression @BV-UC_DTC_GX
    Scenario Outline: RM_RF_RD_CCU_API_HP: Execute RF and RD When RM job is already activated
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        And create measurment configuration <meas_config_name> if it not is available
        And check ECU flashing DP <distribution_package> is available
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And test is executed for "1" minutes
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        When OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        Then flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "80" seconds
        When trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        Then flashing status of OTA package is changed to "UPDATE_SUCCESS" within "120" seconds
        When diagnostic function <diagConfigName> with "test1" having capability "READ_DTC" using "activate-fix.zip" is created, if not present
        And release diagnostic function, if not in RELEASED state
        And diagnostic configuration <diagConfigName> with description "test1" using function <diagConfigName> is created, if not present
        And release diagnostic configuration, if not in RELEASED state
        And the "2"nd reference system <Protocol_RD> with Identifier <Identifier_RD> is started
        And deactivate ACTIVE diagnostic configuration if present
        And delete DTC if present
        And diagnostic configuration <diagConfigName> is activated on vehicle
        Then diagnostic configuration state is "ACTIVE" 
        And adhoc Read All DTCs is triggered
        Then adhoc Read All DTCs is generated within "2" minutes
        When deactivate ACTIVE diagnostic configuration if present
        Then diagnostic configuration state is "INACTIVE"
        When reference system is stopped
        And Remote measurement is deactivated
        Then measurement status is "INACTIVE" within "10" minutes
        When measurement test results are stored
        Then measurement test results are verified
 	    And latest DTC status is verified
            | Status | Code  |
            | AC     | A9C17 |
            | AC     | 80522 |

        Examples:
            | vehicle| device| diagConfigName           | Protocol_RD | Identifier_RD         |meas_config_name| distribution_package            | Protocol   | Identifier     | Identifier1      | Fota_Identifier        | Fota           |  
            | " "    |"CCU"  | "SYS-I-001-job_success"  | "UDSonCAN"  | "UDS_Resp_2DTCs_RD"   |"POWER_CTPG_new"|"E2E_RF_Standard_Job_encrypted"  | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | "DriverApp_Break_True" | "CANalization" | 