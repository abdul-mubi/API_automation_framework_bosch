Feature:Assignment Revocation
        @E2E-API @E2E-CCU @E2E-HP @E2E-Installation @F-UC_Self_Update
        Scenario Outline:SU_CCU_API_HP: - Assignment Revocation once self Update is started
                Given device <device> is "ONLINE"
                And check CCU Self update <package> distribution package from "from_version" to "to_version" available, create if not present
                When OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
                And Self update assignment status "UPDATING" is verified in "300" seconds
                And revoke the OTA assignment
                And wait for self update of device <device> to complete
                Then switch "CL15" is turned "Off"
                And wait for device to be "OFFLINE"
                And switch "CL15" is turned "On"
                And wait for device to be "ONLINE"
                And Self update assignment status "UPDATE_SUCCESS" is verified in "600" seconds
                Then device FW version is verified
                And verify that assignment revocation is failed

                Examples:
                        | device | package           |
                        | "CCU"  | "downgrade_delta" |
                        | "CCU"  | "upgrade_delta"   |

       
        @E2E-API @E2E-CCU @E2E-HP @E2E-Installation @F-UC_Self_Update
        Scenario Outline:SU_CCU_API_HP: - Assignment Revocation of self Update before Update is started
                Given device <device> is "ONLINE"
                And check ECU flashing DP <package> is available
                When OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
                Then Self update assignment status <assignment_status> is verified in "100" seconds
                And revoke the OTA assignment
                And Self update assignment status "UPDATE_REVOKED" is verified in "300" seconds

                Examples:
                        | device | package                            | assignment_status |
                        | "CCU"  | "Delta_DP_4.11.1_5.0.0_ENCRYPTION" | "UPDATE_ASSIGNED" |