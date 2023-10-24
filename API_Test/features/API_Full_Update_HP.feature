Feature:Execute device full update
        @E2E-API @E2E-CCU @E2E-HP @E2E-Installation @F-UC_Self_Update
        Scenario Outline:FU_CCU_API_HP - Execute device full update with CL15
                Given device <device> is "ONLINE"
                And check CCU Full update <package> distribution package to "to_version" available, create if not present
                When OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
                Then full update assignment status "UPDATING" is verified in "600" seconds
                And full update device status "VERIFY_SUCCESSFUL" is verified within "600" seconds
                And switch "CL15" is turned "Off"
                And wait for device to be "OFFLINE"
                And switch "CL15" is turned "On"
                And full update device status "UPDATE_SUCCESSFUL" is verified within "600" seconds
                And wait for device to be "ONLINE"
                Then full update assignment status "UPDATE_SUCCESS" is verified in "60" seconds
                And device FW version is verified

                Examples:
                        | device | package       |
                        | "CCU"  | "full_update" |

        @E2E-API @E2E-CCU @E2E-HP @E2E-Installation @F-UC_Self_Update
        Scenario Outline:FU_CCU_API_HP - Execute device full update with CL30
                Given device <device> is "ONLINE"
                And check CCU Full update <package> distribution package to "to_version" available, create if not present
                When OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
                Then full update assignment status "UPDATING" is verified in "600" seconds
                And full update device status "VERIFY_SUCCESSFUL" is verified within "600" seconds
                When switch "CL15" is turned "Off"
                And switch "CL30" is turned "Off"
                Then wait for device to be "OFFLINE"
                When switch "CL30" is turned "On"
                And switch "CL15" is turned "On"
                When test waits for "1" minutes
                When switch "CL15" is turned "Off"
                And switch "CL30" is turned "Off"
                Then wait for device to be "OFFLINE"
                When switch "CL30" is turned "On"
                And switch "CL15" is turned "On"
                And full update device status "UPDATE_SUCCESSFUL" is verified within "600" seconds
                And wait for device to be "ONLINE"
                Then full update assignment status "UPDATE_SUCCESS" is verified in "60" seconds
                And device FW version is verified

                Examples:
                        | device | package       |
                        | "CCU"  | "full_update" |

        @E2E-API @E2E-CCU @E2E-HP @E2E-Installation @F-UC_Self_Update
        Scenario Outline:FU_CCU_API_HP - Execute device full update with CL15 [offline-online]
                Given device <device> is "ONLINE"
                And check CCU Full update <package> distribution package to "to_version" available, create if not present
                When switch "CL15" is turned "Off"
                And wait for device to be "OFFLINE"
                When OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
                And switch "CL15" is turned "On"
                And wait for device to be "ONLINE"
                Then full update assignment status "UPDATING" is verified in "600" seconds
                And full update device status "VERIFY_SUCCESSFUL" is verified within "600" seconds
                And switch "CL15" is turned "Off"
                Then wait for device to be "OFFLINE"
                When test waits for "1" minutes
                And switch "CL15" is turned "On"
                When test waits for "1" minutes
                And switch "CL15" is turned "Off"
                Then wait for device to be "OFFLINE"
                When test waits for "1" minutes
                And switch "CL15" is turned "On"
                And full update device status "UPDATE_SUCCESSFUL" is verified within "600" seconds
                Then wait for device to be "ONLINE" within "3" minutes
                And full update assignment status "UPDATE_SUCCESS" is verified in "60" seconds
                And device FW version is verified

                Examples:
                        | device | package       |
                        | "CCU"  | "full_update" |