Feature: Validate CAN keep alive when CL15 is turn off in RD
@E2E-HP @E2E-RD @E2E-CCU @E2E-API @E2E-Regression @E2E-PACCAR
Scenario Outline: RD_CCU_API_HP: Validate data using CAN keep alive when CL15 is off in RD
Given device <device> is "ONLINE"
    And map device to the <vehicle> if there are no pending diagnostic jobs
    When diagnostic configuration <diagConfigName> is activated on vehicle
    And diagnostic configuration state is "ACTIVE"
    And switch "CL15" is turned "Off"
    And wait for device to be "OFFLINE"
    And reference system <Protocol> with Identifier <Identifier> is started
    And wait for device to be "ONLINE"
    Then "No" newer DTCs are generated
    And reference system <Protocol1> with Identifier <Identifier1> is started
    And adhoc Read All DTCs is triggered    
    Then adhoc Read All DTCs is generated within "5" minutes
    And deactivate ACTIVE diagnostic configuration if present
    And diagnostic configuration state is "INACTIVE"
    Then reference system is stopped
    And latest DTC status is verified
            | Status | Code  |
            | AC     | A9C17 |
            | AC     | 80522 |
    And wait for device to be "OFFLINE"
    And switch "CL15" is turned "On"
    And wait for device to be "ONLINE"

Examples:
            | vehicle | device | diagConfigName        | Protocol       | Identifier      | Protocol1 | Identifier1       |
            | " "     | "CCU" | "SYS-I-001-job_success" | "CANalization" | "CAN_KeepAlive" |"UDSonCAN" | "UDS_Resp_2DTCs_RD" |