Feature:Perform RD when device wakes up via timer wakeup event
    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression @E2E-FM @E2E-HINO
    Scenario Outline: PM_CCU_API_HP - Timer wakeup : Device remains Online if RD is active
        Given device <device> is "ONLINE"
        And diagnostic function <diagConfigName> with "test1" having capability "READ_DTC" using "activate-fix.zip" is created, if not present
        And release diagnostic function, if not in RELEASED state
        And diagnostic configuration <diagConfigName> with description "test1" using function <diagConfigName> is created, if not present
        And release diagnostic configuration, if not in RELEASED state
        And map device to the <vehicle> if there are no pending diagnostic jobs

        And deactivate ACTIVE diagnostic configuration if present
        And delete DTC if present
        When time <moment> for device wake up is set and device should be online for <duration>
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And test waited till device wakeup configuration time <moment> is met
        And wait for device to be "ONLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        When diagnostic configuration <diagConfigName> is activated on vehicle
        And diagnostic configuration state is "ACTIVE"
        And adhoc Read All DTCs is triggered
        Then adhoc Read All DTCs is generated within "4" minutes
        And verify device status stayed in "ONLINE" for <duration>
        And latest DTC status is verified
            | Status | Code  |
            | AC     | A9C17 |
            | AC     | 80522 |
        And deactivate ACTIVE diagnostic configuration if present
        And diagnostic configuration state is "INACTIVE"
        And test waited till device wakeup configuration time <duration> is met
        And wait for device to be "OFFLINE"
        And reference system is stopped
        And verify device status stayed in "OFFLINE" for "000:00:05"

        Examples:
            | vehicle | device | moment      | duration    | Protocol   | Identifier          | diagConfigName          | operation       |
            | " "     | "CCU"  | "000:00:10" | "000:00:07" | "UDSonCAN" | "UDS_Resp_2DTCs_RD" | "SYS-I-001-job_success" | "deleteAllJobs" |