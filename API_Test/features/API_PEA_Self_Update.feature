Feature: PEA Self-Update
    @E2E-API @E2E-CTPG @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-OnRequest
    Scenario Outline: Execute PEA self update and validate database.xml file in device
        Given device <device> is "ONLINE"
        And check ECU flashing DP <distribution_package> is available
        When OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And Self update assignment status "UPDATE_SUCCESS" is verified in "300" seconds
        Then validate "RDA.LOGLEVEL" as "TRACE" in database.xml from <device>
        And validate "CDP.LOGLEVEL" as "TRACE" in database.xml from <device>
        
        Examples:
        | device | package                                      |
        | "CTPG" | "cTPG_UpdateProperty_RDA_CDP_Loglevel_TRACE" |
    
    @E2E-API @E2E-CTPG @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-OnRequest
    Scenario Outline: Execute PEA self update and validate config.xml file in device
        Given device <device> is "ONLINE"
        And store a backup file for "config.xml" from device <device>
        And check ECU flashing DP <distribution_package> is available
        When OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And Self update assignment status "UPDATE_SUCCESS" is verified in "300" seconds
        Then validate "config.xml" file in the device <device>
        
        Examples:
        | device | package |
        | "CTPG" | "cTPG_InstallProperty_ConfigTask" |

    @E2E-API @E2E-CTPG @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-OnRequest
    Scenario Outline: Execute PEA self update and validate database.xml file in device
        Given device <device> is "ONLINE"
        And store a backup file for "database.xml" from device <device>
        And check ECU flashing DP <distribution_package> is available
        When OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And Self update assignment status "UPDATE_SUCCESS" is verified in "300" seconds
        Then validate "database.xml" file in the device <device>
        
        Examples:
        | device | package |
        | "CTPG" | "cTPG_InstallProperty_PeaDatabaseTask" |

    @E2E-API @E2E-CTPG @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline: Execute PEA self update and validate assignment status for self-update
        Given device <device> is "ONLINE"
        And check ECU flashing DP <distribution_package> is available
        When OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        Then Self update assignment status "UPDATE_SUCCESS" is verified in "100" seconds
        
        Examples:
        | device | distribution_package |
        | "CCU"  | "pea_config_E2ETest" |