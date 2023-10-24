Feature: Device provisioning - Handling of device data
@E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Handling of device data - RM data when VIN mismatch
    Given device <device> is "ONLINE"
        And set <device_mapping> functionality as "DISABLED" in fleet settings
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        And assign remote measurement to <device_slot> of vehicle <vehicle>
        And measurement status is "ACTIVE" within "10" minutes
        And test waits for "1" minutes
        And measurement test results are stored
        And measurement test result for latest step is "available"
        When VIN of vehicle <new_vehicle> is implanted in the device <device>
        Then validate no new results are pushed to test step 
        
        Examples:
            |vehicle | new_vehicle                      | device | device_slot | meas_config_name | device_mapping |
            | " "    | "Auto_Pair_Veh_Device_Data"      | "CCU"  | "CCU"       | "POWER_CTPG_new" |"enableSelfMapping" |

    
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Handling of device data - RM data when CL15 is turned ON/OFF
    Given device <device> is "ONLINE" 
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And test waits for "0.5" minutes
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And Remote measurement is deactivated
        And measurement status "ACTIVE" and substatus "IN_DEACTIVATION"
        And test waits for "10" minutes
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And test waits for "1" minutes
        Then measurement test results are stored
        And measurement test results are present and 1 in number

        Examples:
            | vehicle | device | meas_config_name  |
            | " "     | "CCU" | "POWER_CTPG_new"    |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - CL15 off/on during Measurement of J1939 Signals
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        #And delete the previous data if it is available
        And Remote measurement is activated
        And measurement status is "ACTIVE"
        And test is executed for "1.5" minutes
        #And test result is "False"
        And measurement test results are stored
        And measurement test result is "False"
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        When switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And test is executed for "1.5" minutes
        And Remote measurement is deactivated
        And measurement status is "INACTIVE"
        Then reference system is stopped
        #And test results are verified and 2 in number
        And measurement test results are stored
        And measurement test results are present and 2 in number

        Examples:
            | vehicle | device | meas_config_name                | Protocol       | Identifier                |
            | " "     | "CCU"  | "SYS-I-J1939-03-Configuration" | "CANalization" | "J1939_Measurement_200ms" |

   
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Measure CCU supply voltage
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        #And delete the previous data if it is available
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "15" minutes
        And test is executed for "1" minutes
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "15" minutes
        And measurement test results are stored
        And measurement test step duration is validated
        And measurement data integrity test is performed

        Examples:
            | vehicle  | device | meas_config_name  |
            | "      " | "CCU"  | "POWER_CTPG_new" |


    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:Turn on/off GSM connection when remote measurement is in progress
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And reference system <Protocol> with Identifier <Identifier> is started
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        #And delete the previous data if it is available
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And test is executed for "1" minutes
        And command to "stopGSMConnection" GSM mode of the device
        And wait for device to be "OFFLINE"
        And measurement test results are stored
        And command to "startGSMConnection" GSM mode of the device
        And wait for device to be "ONLINE"
        And test waits for "1" minutes where wait is "included" in recording
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test result downloads are reprepared
        And measurement test results are stored
        And measurement test results having no loss of measured data is validated
        And reference system is stopped

        Examples:
            | vehicle | device | meas_config_name       | Protocol   | Identifier      |
            | " "     | "CCU"  | "E2E_CAN_RAW_MON_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" |



    @E2E-API @E2E-CCU @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP : CL15 on/off when remote measurement is in progress
        Given device <device> is "ONLINE"
        And device operation "rebootDevice" is performed
        And wait for device to be "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And reference system <Protocol> with Identifier <Identifier> is started
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        #And delete the previous data if it is available
        And measurement status is "ACTIVE" within "10" minutes
        And test is executed for "1" minutes
        And measurement test results are stored
        And switch "CL15" is turned "Off"
        And wait for device to be "ONLINE"
        And test is executed for "1" minutes
        And measurement test result downloads are reprepared
        And measurement test results are stored
        And measurement test results having newer measured data is validated
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And reference system is stopped

        Examples:
            | vehicle | device  | meas_config_name       | Protocol   | Identifier      |
            | " "     | "CCU"   | "E2E_CAN_RAW_MON_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" |



    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP : Turn on/off CL30 while remote measurement is ongoing

        Given device <device> is "ONLINE"
        And device operation "rebootDevice" is performed
        And wait for device to be "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And reference system <Protocol> with Identifier <Identifier> is started
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        #And delete the previous data if it is available
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And test is executed for "1" minutes
        And measurement test results are stored
        And switch "CL15" is turned "Off"
        And switch "CL30" is turned "Off"
        And wait for device to be "OFFLINE"
        And switch "CL30" is turned "On"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And test is executed for "1.5" minutes
        And measurement test result downloads are reprepared
        And measurement test results are stored
        And measurement test results having newer measured data is validated
        And reference system is stopped
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "15" minutes


        Examples:
            | vehicle | device | meas_config_name       | Protocol   | Identifier      |
            | " "     | "CCU"  | "E2E_CAN_RAW_MON_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" |

    
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Handling of device data - RM data when GSM is turned ON/OFF
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And reference system <Protocol> with Identifier <Identifier> is started
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And test waits for "0.5" minutes
        And command to "stopGSMConnection" GSM mode of the device
        And wait for device to be "OFFLINE"
        And test waits for "0.5" minutes
        And Remote measurement is deactivated
        And measurement status "ACTIVE" and substatus "IN_DEACTIVATION"
        And test waits for "1" minutes
        And command to "startGSMConnection" GSM mode of the device
        And wait for device to be "ONLINE"
        And reference system is stopped
        And measurement test results are stored
        Then measurement test step duration is validated

        Examples:
            | vehicle | device | meas_config_name        | Protocol   | Identifier      |
            | " "     | "CCU"  | "E2E_CAN_RAW_MON_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" |
