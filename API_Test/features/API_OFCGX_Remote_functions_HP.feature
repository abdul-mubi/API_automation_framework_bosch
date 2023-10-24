Feature:Remote Functions
    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression
    Scenario Outline: RD_CCU_API_HP : Remote Function - RD with capability of remote functions
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending diagnostic jobs
        And deactivate ACTIVE diagnostic configuration if present
        And delete DTC if present
        When diagnostic configuration <diagConfigName> is activated on vehicle
        And diagnostic configuration state is "ACTIVE" for <capability>
        And trigger <capability> on the vehicle
        Then <capability> is executed within "3" minutes
        When deactivate ACTIVE diagnostic configuration if present
        Then diagnostic configuration state is "DEACTIVATION_PENDING" for <capability>
        And diagnostic configuration state is "INACTIVE" for <capability>

        Examples:
            | vehicle | device | diagConfigName                | capability        |
            | " "     | "CCU"  | "Remote_function_config_test" | "REMOTE_FUNCTION" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression
    Scenario Outline: RD_CCU_API_HP : Remote Function - RD with capability of remote functions and make device online after remote function timeout
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending diagnostic jobs
        And deactivate ACTIVE diagnostic configuration if present
        And delete DTC if present
        When diagnostic configuration <diagConfigName> is activated on vehicle
        Then diagnostic configuration state is "ACTIVE" for <capability>
        When switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And trigger <capability> on the vehicle
        And test waits for "3" minutes
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        Then <capability> "fails" within "3" minutes
        When deactivate ACTIVE diagnostic configuration if present
        Then diagnostic configuration state is "DEACTIVATION_PENDING" for <capability>
        And diagnostic configuration state is "INACTIVE" for <capability>

        Examples:
            | vehicle | device | diagConfigName                | capability        |
            | " "     | "CCU"  | "Remote_function_config_test" | "REMOTE_FUNCTION" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression @E2E-HINO
    Scenario Outline: RD_CCU_API_HP : Remote Function - RD with capability of remote functions and make device online by remote wakeup
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending diagnostic jobs
        When set remote wakeup SMS state as "ENABLED" for duration <SMS_duration> is configured
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And device wake-up with SMS is triggered
        And wait for device to be "ONLINE"
        And deactivate ACTIVE diagnostic configuration if present
        And delete DTC if present
        And diagnostic configuration <diagConfigName> is activated on vehicle
        And diagnostic configuration state is "ACTIVE" for <capability>
        And trigger <capability> on the vehicle
        Then <capability> is executed within "3" minutes
        And wait for device to be "OFFLINE"
        And verify device status stayed in "OFFLINE" for "000:00:05"
        When switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And deactivate ACTIVE diagnostic configuration if present
        Then diagnostic configuration state is "DEACTIVATION_PENDING" for <capability>
        And diagnostic configuration state is "INACTIVE" for <capability>

        Examples:
            | vehicle | device | diagConfigName                | capability        | SMS_duration |
            | " "     | "CCU"  | "Remote_function_config_test" | "REMOTE_FUNCTION" | "00:05:00"   |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression
    Scenario Outline: RD_CCU_API_HP : Remote Function - RD with capabilities of remote functions and read all DTC
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending diagnostic jobs
        And reference system <Protocol> with Identifier <Identifier> is started
        And deactivate ACTIVE diagnostic configuration if present
        And delete DTC if present
        When diagnostic configuration <diagConfigName> is activated on vehicle
        And diagnostic configuration state is "ACTIVE" for <capability>
        And trigger <capability> on the vehicle
        And <capability> is executed within "3" minutes
        And adhoc Read All DTCs is triggered
        And adhoc Read All DTCs is generated within "10" minutes
        When deactivate ACTIVE diagnostic configuration if present
        And diagnostic configuration state is "DEACTIVATION_PENDING" for <capability>
        And diagnostic configuration state is "INACTIVE" for <capability>
        And reference system is stopped
        Then latest DTC status is verified
            | Status | Code  |
            | AC     | A9B17 |
            | AC     | 80511 |

        Examples:
            | vehicle | device | diagConfigName                      | capability       |Protocol    | Identifier      |
            | " "     | "CCU"  | "Remote_Function_with_read_all_dtc" |"REMOTE_FUNCTION" | "UDSonCAN" | "UDS_Resp_2DTCs" |