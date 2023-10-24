Feature:Migration of PEA Self Update tests to API regression
    @E2E-API @E2E-CCU @E2E-HP @E2E-OnRequest @E2E-RF @BV-UC_OTA_Updates_GX
    Scenario Outline: RF_PEA_CCU_API_HP - Update Task
    Given device <device> is "ONLINE"
        And check ECU flashing DP <package> is available
        When OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And Self update assignment status "UPDATE_SUCCESS" is verified in "300" seconds
        Then validate "RDA.LOGLEVEL" as "TRACE" in database.xml from <device>
        And validate "CDP.LOGLEVEL" as "TRACE" in database.xml from <device>
                
        Examples:
        | device | package                                      |
        | "CCU"  | "cTPG_UpdateProperty_RDA_CDP_Loglevel_TRACE" |



    @E2E-API @E2E-CCU @E2E-HP @E2E-OnRequest @E2E-RF @BV-UC_OTA_Updates_GX
    Scenario Outline: RF_PEA_CCU_API_HP - Install Database Task
    Given device <device> is "ONLINE"
        And store a backup file for "database.xml" from device <device>
        And check ECU flashing DP <package> is available
        When OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And Self update assignment status "UPDATE_SUCCESS" is verified in "300" seconds
        Then validate "database.xml" file in the device <device>
                
        Examples:
        | device | package                                |
        | "CCU"  | "cTPG_InstallProperty_PeaDatabaseTask" |

    
    @E2E-API @E2E-CCU @E2E-HP @E2E-OnRequest @E2E-RF @BV-UC_OTA_Updates_GX
    Scenario Outline: RF_PEA_CCU_API_HP - Install Config Task
    Given device <device> is "ONLINE"
        And store a backup file for "config.xml" from device <device>
        And check ECU flashing DP <package> is available
        When OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And Self update assignment status "UPDATE_SUCCESS" is verified in "300" seconds
        Then validate "config.xml" file in the device <device>
                
        Examples:
        | device | package                           |
        | "CCU"  | "cTPG_InstallProperty_ConfigTask" |

    

    @E2E-API @E2E-CCU @E2E-HP @E2E-OnRequest @E2E-RF @BV-UC_OTA_Updates_GX
    Scenario Outline: RF_PEA_CCU_API_HP - Install PEA Config
    Given device <device> is "ONLINE"
        And check ECU flashing DP <package> is available
        When OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        Then Self update assignment status "UPDATE_SUCCESS" is verified in "100" seconds
                
        Examples:
        | device| package              |
        | "CCU" | "pea_config_E2ETest" |