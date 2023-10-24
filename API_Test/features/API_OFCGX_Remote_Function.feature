Feature:perform remote function capability on a vehicle
@E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression
Scenario Outline:RD_CCU_API_HP : Remote Function - RD with capability of remote functions and make device online within remote function timeout
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending diagnostic jobs
        And deactivate ACTIVE diagnostic configuration if present
        And delete DTC if present
        When diagnostic configuration <diagConfigName> is activated on vehicle
        Then diagnostic configuration state is "ACTIVE" for <capability>
        And command to "stopGSMConnection" GSM mode of the device
        And wait for device to be "OFFLINE"
        And trigger <capability> on the vehicle
        And command to "startGSMConnection" GSM mode of the device
        And wait for device to be "ONLINE"
        Then <capability> is executed within "3" minutes
        When deactivate ACTIVE diagnostic configuration if present
        Then diagnostic configuration state is "DEACTIVATION_PENDING" for <capability>
        And diagnostic configuration state is "INACTIVE" for <capability>

        Examples:
            | vehicle | device | diagConfigName                | capability       |
            | " "     | "CCU"  | "Remote_function_config_test" |"REMOTE_FUNCTION" |