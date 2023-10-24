@REQ_ARTMC-10626
Feature: Smoke Test
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Smoke
    Scenario Outline:RM_CCU_API_HP - Measurement of CAN raw
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        And measurement status is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And test is executed for "3" minutes
        And reference system is stopped
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE"
        And measurement test results are stored
        And measurement data integrity smoke test is performed

        Examples: 
            | vehicle | device | meas_config_name  | Protocol   | Identifier                | 
            | " "     | "CCU"  | "E2E_CAN_RAW_MON" | "MONonCAN" | "MONonCAN_highloadidents" | 

    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Smoke
    Scenario Outline:RF_CCU_API_HP - Flashing using UDSonCAN
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        And check ECU flashing DP <distribution_package> is available  
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "80" seconds
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        Then flashing status of OTA package is changed to "UPDATE_SUCCESS" within "120" seconds
        And verify logs for "SUCCESSFUL" OTA assignments within "100" seconds
        And reference system is stopped
        And verify the hex content for <Identifier>
        

            Examples:
            | vehicle| device   | distribution_package              | Protocol   | Identifier     |  Identifier1       |   Fota_Identifier      | Fota            |
            | " "    | "CCU"   | "E2E_RF_Standard_Job_encrypted"   | "UDSonCAN" | "DemoFlashSim" |  "DemoFlashSim_1"  | "DriverApp_Break_True" | "CANalization"  |



    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Smoke @BV-UC_DTC_GX
    Scenario Outline:RD_CCU_API_HP - Ad hoc read of DTCs
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending diagnostic jobs
        And diagnostic function <diagConfigName> with "test1" having capability "READ_DTC" using "activate-fix.zip" is created, if not present
        And release diagnostic function, if not in RELEASED state
        And diagnostic configuration <diagConfigName> with description "test1" using function <diagConfigName> is created, if not present
        And release diagnostic configuration, if not in RELEASED state
        And reference system <Protocol> with Identifier <Identifier> is started
        And deactivate ACTIVE diagnostic configuration if present
        And delete DTC if present
        When diagnostic configuration <diagConfigName> is activated on vehicle
        And diagnostic configuration state is "ACTIVE"
        And adhoc Read All DTCs is triggered
        Then adhoc Read All DTCs is generated within "10" minutes
        And deactivate ACTIVE diagnostic configuration if present
        And diagnostic configuration state is "INACTIVE"
        Then reference system is stopped
        And latest DTC status is verified
            | Status | Code  |
            | AC     | A9C17 |
            | AC     | 80522 |

        Examples:
            | vehicle | device | diagConfigName          | Protocol   | Identifier          | operation       |
            | " "     | "CCU"  | "SYS-I-001-job_success" | "UDSonCAN" | "UDS_Resp_2DTCs_RD" | "deleteAllJobs" |


    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Smoke
    Scenario Outline:RM_CCU_API_HP - Measurement of J1939 Signals
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And reference system <Protocol> with Identifier <Identifier> is started
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        And measurement status is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And test is executed for "2" minutes
        And reference system is stopped
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE"
        And measurement test results are stored
        And measurement data integrity smoke test is performed

        Examples: 
            | vehicle | device | meas_config_name            | Protocol       | Identifier                        | 
            | " "     | "CCU"  | "E2E_J1939_SIGNALS_CONFIG" | "CANalization" | "J1939_Measurement_Signals_100ms" |