Feature: [RM][Device Signals] - GPS Trip Distance

    @E2E-API @E2E-CCU @E2E-OnRequest @E2E-SP
    Scenario Outline:DP_CCU_API_SP - replacing keystore file by combination of device and environment

        Given device <device> is "ONLINE"
        # And command <command> is executed on device <device>
        And device operation <command> is performed
        And verify <key> path in device
        And copy file <key> to device from <deviceType> deviceType and <environment> space
        And device operation "rebootDevice" is performed
        And wait for device to be "OFFLINE"
        And test waits for "3" minutes
        And device <device> is "OFFLINE"
        And copy device specfic file <key> to device
        And device operation "rebootDevice" is performed
        And wait for device to be "ONLINE"

Examples:
         | vehicle| device |key       |command          |deviceType |environment | 
         | "    " | "CCU" |"keystore"|"getKeystorePath"|  "same"   |  "same"    | 
         | "    " | "CCU" |"keystore"|"getKeystorePath"|  "same"   |"different" | 
         | "    " | "CCU" |"keystore"|"getKeystorePath"|"different"|   "same"   | 
         | "    " | "CCU" |"keystore"|"getKeystorePath"|"different"|"different" |

    
    @E2E-API @E2E-CCU @E2E-FM @E2E-OnRequest @E2E-SP
    Scenario Outline:FM_CCU_API_SP - No device Log entries after replacing corrupted keystore

        Given device <device> is "ONLINE"
        When triggering new log file generation for device
        #And command <command> is executed on device <device>
        And device operation <command> is performed
        And verify <key> path in device
        And <mode> the content of file <key> with <data> and copy to device
        And copy device specfic file <key> to device
        And device operation "rebootDevice" is performed
        And wait for device to be "ONLINE"
        And new log entry is generated for the device
        Then device logs can be downloaded containing file <files>

        Examples:
            | device  | files                                  | key        | command           | mode     | data        |
            | "CCU" | [index.xml,MetaData.xml,LOGS/syslog.txt] | "keystore" | "getKeystorePath" | "append" | "@^$8huhhh" |


    @E2E-API @E2E-CCU @E2E-OnRequest @E2E-SP
    Scenario Outline:DP_CCU_API_SP : replacing empty/corrupted keystore file in device

        Given device <device> is "ONLINE"
        # And command <command> is executed on device <device>
        And device operation <command> is performed
        And verify <key> path in device
        And <mode> the content of file <key> with <data> and copy to device
        And device operation "rebootDevice" is performed
        And wait for device to be "OFFLINE"
        And test waits for "3" minutes
        And device <device> is "OFFLINE"
        And copy device specfic file <key> to device
        And device operation "rebootDevice" is performed
        And wait for device to be "ONLINE"

Examples:
         | vehicle| device  |key       |command          |mode     |data         |
         | "    " | "CCU"  |"keystore"|"getKeystorePath"|"replace"|" "          |
         | "    " | "CCU"  |"keystore"|"getKeystorePath"|"replace"|"@3eE$gg555" |



