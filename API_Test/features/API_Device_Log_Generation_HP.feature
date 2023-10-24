Feature:Device Log Generation using Generate log link trigger
    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Smoke @limit-log
    Scenario Outline:FM_CCU_API_HP - Device Log Generation using Generate log link trigger
    Given device <device> is "ONLINE"
        When device log count is fetched
        Then triggering new log file generation for device
        And new log entry is generated for the device
        And device logs can be downloaded containing file <files>

        Examples:
            | device  | files                 |
            | "CCU"   | index.xml,MetaData.xml|


    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Regression
    Scenario Outline:FM_CCU_API_HP - Multiple Device Log Generation using RM and Generate log link trigger
    Given Perform Remote Measurement 1 times with the data <vehicle>, <device>, <meas_config_name>, <Protocol>, <Identifier>, <Measurement_entity>, <Count>
        When device log count is fetched
        Then triggering "2" new log file generation for device
        And "2" new log entries are generated for the device
        And device logs can be downloaded containing file <files>
        And delete generated log files from device log entries

        Examples:
            | vehicle | device  | Measurement_entity  | Count | meas_config_name        | Protocol   | Identifier                     | files                                |
            | " "     | "CCU"   | "signals"           |  "2"  | "E2E_CAN_RAW_MON_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" | index.xml,MetaData.xml,LOGS/syslog.txt |

    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Regression
    Scenario Outline:FM_CCU_API_HP - Device Log Generation check when CL15 turned [ off - on ] during log generation
    Given device <device> is "ONLINE"
        Then switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And device log count is fetched
        When triggering new log file generation for "OFFLINE" device under test
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And new log entry is generated for the device
        Then device logs can be downloaded containing file <files>
        And delete generated log files from device log entries
        

        Examples:
            | device  | files                                |
            | "CCU" |  index.xml,MetaData.xml,LOGS/syslog.txt  |


    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Regression
    Scenario Outline:FM_CCU_API_HP - Multiple device log generation when GSM ON/OFF during log generation
    Given device <device> is "ONLINE"
        When device log count is fetched
        Then triggering "4" new log file generation for device
        And command to "stopGSMConnection" GSM mode of the device
        And wait for device to be "OFFLINE"
        When command to "startGSMConnection" GSM mode of the device
        And wait for device to be "ONLINE"
        And "4" new log entries are generated for the device
        Then device logs can be downloaded containing file <files>
            
        Examples:
            | device  |  files                               |
            | "CCU" |  index.xml,MetaData.xml,LOGS/syslog.txt  |
