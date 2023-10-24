Feature:API based test for remote measurement with Grade X
    @E2E-API @E2E-CCU @E2E-Gradex @E2E-HP @E2E-Regression
    Scenario Outline:RGRADEX_RM_CCU_API_HP - Execute Measurement job when GSM is turned off/on after 3 minutes
    Given device <device> is "ONLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        When task <TriggerTask> is executed
        Then verify <Status> for "Task" is available within "3" minutes
        When task <MeasurementTask> is executed
        Then verify "PENDING" for "Task" is available within "1" minutes
        And command to "stopGSMConnection" GSM mode of the device
        And wait for device to be "OFFLINE"
        And test is executed for "4" minutes
        When command to "startGSMConnection" GSM mode of the device
        And wait for device to be "ONLINE"
        Then verify "EXECUTED" for "Task" is available within "7" minutes
        And verify "JOB_SUCCESS" for "Job Result" is available within "1" minutes
        And verify Measurement Task executed for more than "3" minutes
        When task <CleanUpTask> is executed
        Then verify <Status> for "Task" is available within "3" minutes
        #And verify the result file that may match with lesser time-stamp entry
        And verify RM GradeX result is as expected
        And verify RM GradeX result can be deleted
        And reference system is stopped
        Examples:
            | device  | Protocol       | Identifier  | TriggerTask      | MeasurementTask     | CleanUpTask     | Status     |
            | "CCU" | "CANalization" | "RM_GradeX" | "container.zip" | "ExecuteRdaJob.zip" | "DeleteRdaJob.zip" | "EXECUTED" |


    @E2E-API @E2E-CCU @E2E-Gradex @E2E-HP @E2E-Regression
    Scenario Outline:RGRADEX_RM_CCU_API_HP - Execute Measurement job when Diagnostic gradex job is already activate
    Given device <device> is "ONLINE"
        When reference system <Protocol_xRD> with Identifier <Identifier_xRD> is started
        And task <RDTask> is executed
        Then verify "EXECUTED" for "Task" is available within "1" minutes
        And test is executed for "2" minutes
        And verify "JOB_SUCCESS" for "Job Result" is available within "1" minutes
        #When reference system is stopped
        And task <RDCleanUpTask> is executed
        Then verify "EXECUTED" for "Task" is available within "1" minutes 
        When reference system <Protocol> with Identifier <Identifier> is started
        And task <TriggerTask> is executed
        Then verify "EXECUTED" for "Task" is available within "1" minutes
        When task <MeasurementTask> is executed
        Then verify <Status> for "Task" is available within "5" minutes
        And verify "JOB_SUCCESS" for "Job Result" is available within "1" minutes
        And verify Measurement Task executed for more than "3" minutes
        When task <CleanUpTask> is executed
        Then verify "EXECUTED" for "Task" is available within "1" minutes
        And verify RM GradeX result is as expected
        And verify RM GradeX result can be deleted
        And reference system is stopped

        Examples:
            | vehicle                | device  | Protocol_xRD | Identifier_xRD      | RDTask                | RDCleanUpTask   | Protocol       | Identifier  | TriggerTask     | MeasurementTask     | CleanUpTask        | Status             |
            | " " | "CCU" | "UDSonCAN"   | "UDS_Resp_2DTCs_RD" | "remotediagpatch.zip" | "deletejob.zip" | "CANalization" | "RM_GradeX" | "container.zip" | "ExecuteRdaJob.zip" | "DeleteRdaJob.zip" | "PENDING,EXECUTED" |



    @E2E-API @E2E-CCU @E2E-Gradex @E2E-HP @E2E-Regression
    Scenario Outline:RGRADEX_RM_CCU_API_HP - Execute Measurement job when GSM is turned off/on within 3 minutes
    Given device <device> is "ONLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        When task <TriggerTask> is executed
        Then verify <Status> for "Task" is available within "3" minutes
        When task <MeasurementTask> is executed
        Then verify "PENDING" for "Task" is available within "1" minutes
        When command to "stopGSMConnection" GSM mode of the device
        And wait for device to be "OFFLINE"
        And test is executed for "1" minutes
        And command to "startGSMConnection" GSM mode of the device
        And wait for device to be "ONLINE"
        Then verify "EXECUTED" for "Task" is available within "7" minutes
        And verify "JOB_SUCCESS" for "Job Result" is available within "1" minutes
        And verify Measurement Task executed for more than "3" minutes
        When task <CleanUpTask> is executed
        Then verify <Status> for "Task" is available within "3" minutes
        #And verify the result file that may match with lesser time-stamp entry
        And verify RM GradeX result is as expected
        And verify RM GradeX result can be deleted
        And reference system is stopped
        Examples:
            | device  | Protocol       | Identifier  | TriggerTask      | MeasurementTask     | CleanUpTask     | Status     |
            | "CCU" | "CANalization" | "RM_GradeX" | "container.zip" | "ExecuteRdaJob.zip" | "DeleteRdaJob.zip" | "EXECUTED" |


    @E2E-API @E2E-CCU @E2E-Gradex @E2E-HP @E2E-Regression
    Scenario Outline:RGRADEX_RM_CCU_API_HP : CL-15 off/on during execution of Measurement job
    Given device <device> is "ONLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        When task <TriggerTask> is executed
        Then verify <Status> for "Task" is available within "1" minutes
        When task <MeasurementTask> is executed
        Then verify "PENDING" for "Task" is available within "1" minutes
        And VRS with protocol <Protocol> and identifier <Identifier> is stopped
        Then switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        Then verify "EXECUTED" for "Task" is available within "5" minutes
        And verify Measurement Task executed for more than "3" minutes
        And verify "JOB_SUCCESS" for "Job Result" is available within "1" minutes
        When task <CleanUpTask> is executed
        Then verify <Status> for "Task" is available within "1" minutes
        And verify RM GradeX result is as expected
        And verify RM GradeX result can be deleted
        And reference system is stopped
        Examples:
            | vehicle   | device | Protocol      | Identifier  | TriggerTask     | MeasurementTask     | CleanUpTask        | Status    |
            | " "       | "CCU" | "CANalization" | "RM_GradeX" | "container.zip" | "ExecuteRdaJob.zip" | "DeleteRdaJob.zip" | "EXECUTED" |


    @E2E-API @E2E-CCU @E2E-Gradex @E2E-HP @E2E-Regression
    Scenario Outline:RGRADEX_RM_CCU_API_HP - Execute measurement without triggering RDA container.zip job
    Given device <device> is "ONLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        When task <MeasurementTask> is executed
        Then verify <Status> for "Task" is available within "5" minutes
        And reference system is stopped
        Examples:
            | device  | Protocol       | Identifier  | MeasurementTask     | Status |
            | "CCU" | "CANalization" | "RM_GradeX" | "ExecuteRdaJob.zip" | "FAILED" |


    @E2E-API @E2E-CCU @E2E-Gradex @E2E-HP @E2E-Regression
    Scenario Outline:RGRADEX_RM_CCU_API_HP - Execute 5 Measurement Jobs
    Given device <device> is "ONLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        When task <TriggerTask> is executed
        Then verify <Status> for "Task" is available within "2" minutes
        When task <MeasurementTask> is executed for "5" times
        Then verify "EXECUTED" for "Task" is available within "5" minutes for all "5" tasks
        And verify Measurement Task executed for more than "3" minutes each for all "5" tasks
        And verify "JOB_SUCCESS" for "Job Result" is available within "2" minutes for all "5" results
        And verify RM GradeX result is as expected for all "5" Job results
        When task <CleanUpTask> is executed
        Then verify <Status> for "Task" is available within "2" minutes
        And verify all "5" RM GradeX result can be deleted
        And reference system is stopped
        Examples:
            | device  | Protocol       | Identifier  | TriggerTask     | MeasurementTask     | CleanUpTask      | Status     |
            | "CCU" | "CANalization" | "RM_GradeX" | "container.zip" | "ExecuteRdaJob.zip" | "DeleteRdaJob.zip" | "EXECUTED" |

    
    @E2E-API @E2E-CCU @E2E-Gradex @E2E-HP @E2E-Regression
    Scenario Outline:RGRADEX_RM_CCU_API_HP : Turn on/off CL30 while GradeX RM is ongoing
    Given device <device> is "ONLINE"
        And device operation "rebootDevice" is performed
        And wait for device to be "ONLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        When task <TriggerTask> is executed
        Then verify <Status> for "Task" is available within "1" minutes
        When task <MeasurementTask> is executed
        Then verify "PENDING" for "Task" is available within "1" minutes
        And switch "CL15" is turned "Off"
        And switch "CL30" is turned "Off"
         And switch "CL30" is turned "On"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        Then verify "EXECUTED" for "Task" is available within "5" minutes
        And verify "JOB_SUCCESS" for "Job Result" is available within "1" minutes
        When task <CleanUpTask> is executed
        Then verify <Status> for "Task" is available within "1" minutes
        And verify RM GradeX result is as expected
        And verify RM GradeX result can be deleted
        And reference system is stopped
        Examples:
            | device | Protocol      | Identifier  | TriggerTask     | MeasurementTask     | CleanUpTask        | Status     |
            | "CCU" | "CANalization" | "RM_GradeX" | "container.zip" | "ExecuteRdaJob.zip" | "DeleteRdaJob.zip" | "EXECUTED" |
