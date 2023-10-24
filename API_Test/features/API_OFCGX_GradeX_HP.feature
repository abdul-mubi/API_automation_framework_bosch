Feature:Perform RD when device wakes up via timer wakeup event
    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression @E2E-Gradex
    Scenario Outline:RD_RGRADEX_RD_CCU_API_HP : Execute GradeX RD when Remote Diagnostic Job is activated
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending diagnostic jobs
        And reference system <Protocol> with Identifier <Identifier> is started
        And deactivate ACTIVE diagnostic configuration if present
        And delete DTC if present
        When diagnostic configuration <diagConfigName> is activated on vehicle
        And diagnostic configuration state is "ACTIVE"
        And adhoc Read All DTCs is triggered
        Then adhoc Read All DTCs is generated within "2" minutes
        And task <RDTask> is executed
        Then verify "EXECUTED" for "Task" is available within "5" minutes
        And test is executed for "2" minutes
        And verify "JOB_SUCCESS" for "Job Result" is available within "1" minutes
        And verify RD GradeX <dtc_code_result> is as expected
        And task <RDCleanUpTask> is executed
        Then verify "EXECUTED" for "Task" is available within "1" minutes
        And deactivate ACTIVE diagnostic configuration if present
        And diagnostic configuration state is "INACTIVE"
        And reference system is stopped
        And latest DTC status is verified
            | Status | Code  |
            | AC     | A9C17 |
            | AC     | 80522 |


        Examples:
            | vehicle | device | diagConfigName          | Protocol   | Identifier          |  RDTask                | RDCleanUpTask   | dtc_code_result      |
            | " "     | "CCU"  | "SYS-I-001-job_success" | "UDSonCAN" | "UDS_Resp_2DTCs_RD" |  "remotediagpatch.zip" | "deletejob.zip" | "AC0A9C17AC080522AC" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-Regression @E2E-Gradex
    Scenario Outline:RGRADEX_RD_CCU_API_HP :Turn off CL30 while GradeX-RD is in progress
        Given device <device> is "ONLINE"
        And device operation "rebootDevice" is performed
        And wait for device to be "ONLINE"
        And reference system <Protocol_xRD> with Identifier <Identifier_xRD> is started
        And task <RDTask> is executed
        And verify "EXECUTED" for "Task" is available within "5" minutes
        And switch "CL15" is turned "Off"
        And switch "CL30" is turned "Off"
        And wait for device to be "OFFLINE"
        And switch "CL30" is turned "On"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And test is executed for "2" minutes
        And verify "JOB_SUCCESS" for "Job Result" is available within "1" minutes
        And verify RD GradeX <dtc_code_result> is as expected
        #And task <CleanUpTask> is executed
        #Then verify "EXECUTED" for "Task" is available within "1" minutes
        And reference system is stopped


        Examples:
            | vehicle | device | Protocol_xRD | Identifier_xRD      | RDTask                | CleanUpTask     | Status             | dtc_code_result      |
            | " "     | "CCU"  | "UDSonCAN"   | "UDS_Resp_2DTCs_RD" | "remotediagpatch.zip" | "deletejob.zip" | "PENDING,EXECUTED" | "AC0A9C17AC080522AC" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-Regression @E2E-Gradex
    Scenario Outline:RGRADEX_RD_CCU_API_HP : GSM on/off during GradeX RD in progress
        Given device <device> is "ONLINE"
        And reference system <Protocol_xRD> with Identifier <Identifier_xRD> is started
        When task <RDTask> is executed
        And command to "stopGSMConnection" GSM mode of the device
        And wait for device to be "OFFLINE"
        And command to "startGSMConnection" GSM mode of the device
        And wait for device to be "ONLINE"
        Then verify "EXECUTED" for "Task" is available within "5" minutes
        And test is executed for "2" minutes
        And verify "JOB_SUCCESS" for "Job Result" is available within "1" minutes
        And verify RD GradeX <dtc_code_result> is as expected
        And task <CleanUpTask> is executed
        And verify "EXECUTED" for "Task" is available within "1" minutes
        And reference system is stopped


        Examples:
            | vehicle | device | Protocol_xRD | Identifier  | Identifier_xRD      | RDTask                | CleanUpTask     | Status             | dtc_code_result      |
            | " "     | "CCU"  | "UDSonCAN"   | "RD_GradeX" | "UDS_Resp_2DTCs_RD" | "remotediagpatch.zip" | "deletejob.zip" | "PENDING,EXECUTED" | "AC0A9C17AC080522AC" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-Regression @E2E-Gradex
    Scenario Outline:RGRADEX_RD_CCU_API_HP : Turn on/off the CL15 while GX-RD is ongoing
        Given device <device> is "ONLINE"
        And device operation "rebootDevice" is performed
        And wait for device to be "ONLINE"
        When reference system <Protocol_xRD> with Identifier <Identifier_xRD> is started
        And task <RDTask> is executed
        Then verify "EXECUTED" for "Task" is available within "5" minutes
        And switch "CL15" is turned "Off"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And test is executed for "2" minutes
        And verify "JOB_SUCCESS" for "Job Result" is available within "1" minutes
        And verify RD GradeX <dtc_code_result> is as expected
        And task <CleanUpTask> is executed
        Then verify "EXECUTED" for "Task" is available within "1" minutes
        And reference system is stopped



        Examples:
            | vehicle | device | Protocol_xRD | Identifier_xRD      | RDTask                | CleanUpTask     | Status             | dtc_code_result      |
            | " "     | "CCU"  | "UDSonCAN"   | "UDS_Resp_2DTCs_RD" | "remotediagpatch.zip" | "deletejob.zip" | "PENDING,EXECUTED" | "AC0A9C17AC080522AC" |

