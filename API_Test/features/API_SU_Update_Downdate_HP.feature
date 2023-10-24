Feature:Execute self update and downdate
        @E2E-API @E2E-CCU @E2E-HP @E2E-Installation @F-UC_Self_Update
        Scenario Outline:SU_CCU_API_HP - Execute self update and downdate
        Given device <device> is "ONLINE"
        # And check ECU <package> is available
        And check CCU Self update <package> distribution package from "from_version" to "to_version" available, create if not present
        # And create CCU full update distribution package to "4.11.1", if not present'
        When OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        Then Self update assignment status "UPDATING" is verified in "300" seconds
        And wait for self update of device <device> to complete
        #And test is executed for "30" minutes
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And Device is "OFF" with no SSH connection     
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And Self update assignment status "UPDATE_SUCCESS" is verified in "300" seconds
        Then device FW version is verified

        Examples:
        | device| package           |
        | "CCU" | "downgrade_delta" |
        | "CCU" | "upgrade_delta"   |
