Feature: Execute measurement and Diagnostics SP in parallel
    @E2E-API @E2E-CCU @E2E-SP @E2E-RD @E2E-RM @BV-UC_RemoteMeasurement @E2E-Load
    Scenario Outline:RM_RD_CCU_API_SP - Execute measurement and Diagnostics SP in parallel - 5 Iteration of RD
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending diagnostic jobs
        And device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And reference system <meas_protocol> with Identifier <meas_identifier> is started
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        #And delete the previous data if it is available
        When Remote measurement is activated
        And measurement status is "ACTIVE"

        And Perform Remote Diagnostics SadPath 5 times with the data <diag_config_name>, <diag_protocol> and <diag_identifier_name>

        And Remote measurement is deactivated
        And measurement status is "INACTIVE"
        And measurement test results are stored
        And measurement data integrity smoke test is performed
        And reference system is stopped

        Examples:
            | vehicle | device | meas_config_name       | meas_protocol | meas_identifier                | diag_config_name        | diag_protocol | diag_identifier_name |
            | " "     | "CCU"  | "E2E_CAN_RAW_MON_500K" | "MONonCAN"    | "MONonCAN_500k_highloadidents" | "SYS-I-001-job_success" | "UDSonCAN"    | "UDS_Resp_2DTCs_RD"  |


    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-RM @BV-UC_RemoteMeasurement @E2E-Load
    Scenario Outline:RM_RD_CCU_API_HP - Execute measurement and Diagnostics in parallel - 10 Iteration of RD
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending diagnostic jobs
        And device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <measConfigName> measurement jobs
        And reference system <measProtocol> with Identifier <measIdentifier> is started
        And verify number of "signals" are "2" respectively is present in measurement configuration <measConfigName>
        #And delete the previous data if it is available
        When Remote measurement is activated
        And measurement status is "ACTIVE"
        And reference system <diagProtocol> with Identifier <diagIdentifier> is started

        Then Perform Remote Diagnostics 10 times with the data <diagConfigName>

        And Remote measurement is deactivated
        And measurement status is "INACTIVE"
        And measurement test results are stored
        And measurement data integrity smoke test is performed
        And reference system is stopped

        Examples:
            | vehicle | device | measConfigName         | measProtocol | measIdentifier                 | diagConfigName          | diagProtocol | diagIdentifier      |
            | " "     | "CCU"  | "E2E_CAN_RAW_MON_500K" | "MONonCAN"   | "MONonCAN_500k_highloadidents" | "SYS-I-001-job_success" | "UDSonCAN"   | "UDS_Resp_2DTCs_RD" |



