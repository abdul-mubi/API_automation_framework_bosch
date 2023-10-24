Feature:  Handling of device data
    @E2E-API @E2E-CCU @E2E-SP @E2E-RD @E2E-Regression @BV-UC_DTC_GX
    Scenario Outline: RD_CCU_API_SP : Turn on/off CL30 while remote diagnostics is ongoing
        Given device <device> is "ONLINE"
        And device operation "rebootDevice" is performed
        And wait for device to be "ONLINE"
        And diagnostic function <diagConfigName> with "test1" having capability "READ_DTC" using "activate-fix.zip" is created, if not present
        And release diagnostic function, if not in RELEASED state
        And diagnostic configuration <diagConfigName> with description "test1" using function <diagConfigName> is created, if not present
        And release diagnostic configuration, if not in RELEASED state
        And map device to the <vehicle> if there are no pending diagnostic jobs
        And reference system <Protocol> with Identifier <Identifier> is started
        And deactivate ACTIVE diagnostic configuration if present
        And delete DTC if present
        When diagnostic configuration <diagConfigName> is activated on vehicle
        And diagnostic configuration state is "ACTIVE"
        And adhoc Read All DTCs is triggered
        And adhoc Read All DTCs is generated within "2" minutes
        And switch "CL15" is turned "Off"
        And switch "CL30" is turned "Off"
        And wait for device to be "OFFLINE"
        And adhoc Read All DTCs is triggered
        And test waits for "2" minutes
        And "No" newer DTCs are generated
        And switch "CL30" is turned "On"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
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

