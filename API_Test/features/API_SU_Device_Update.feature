Feature: Device Self-Update
    @E2E-API @E2E-CCU @E2E-HP @E2E-Installation @F-UC_Self_Update
    Scenario Outline:SU_CCU_API_HP - Device Self-Update while RF is in progress
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And check ECU flashing DP <distribution_package> is available
        And check CCU Self update <package> distribution package from "from_version" to "to_version" available, create if not present
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        When <first> OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of <first> OTA assignment is changed to "WAITING_FOR_UPDATE_CONDITION" within "120" seconds
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        And flashing status of <first> OTA assignment is changed to "UPDATING" within "80" seconds
        When <second> OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of <second> OTA assignment is changed to "UPDATING" within "300" seconds
        And flashing status of <first> OTA assignment is changed to "UPDATE_SUCCESS" within "500" seconds
        And wait for self update of device <device> to complete
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE" within "30" minutes
        And flashing status of <second> OTA assignment is changed to "UPDATE_SUCCESS" within "300" seconds
        Then device FW version is verified
        And reference system is stopped

        Examples:
            | device | package           | vehicle | distribution_package          | Protocol   | Identifier     | Identifier1     | Fota_Identifier       | Fota           | first | second |
            | "CCU"  | "downgrade_delta" | " "     | "E2E_RF_Standard_Job_Slow"    | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1"|"DriverApp_Break_True" | "CANalization" |   1   |   2    |
            | "CCU"  | "upgrade_delta"   | " "     | "E2E_RF_Standard_Job_Slow"    | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1"|"DriverApp_Break_True" | "CANalization" |   1   |   2    |


    @E2E-API @E2E-CCU @E2E-HP @E2E-Installation @F-UC_Self_Update @E2E-RD
    Scenario Outline:SU_CCU_API_HP: Device Self-Update while RD is progress
        Given device <device> is "ONLINE"
        And check CCU Self update <package> distribution package from "from_version" to "to_version" available, create if not present
        And map device to the <vehicle> if there are no pending diagnostic jobs
        And reference system <Protocol> with Identifier <Identifier> is started
        And deactivate ACTIVE diagnostic configuration if present
        And delete DTC if present
        When diagnostic configuration <diagConfigName> is activated on vehicle
        And diagnostic configuration state is "ACTIVE"
        And adhoc Read All DTCs is triggered
        And DTC is generated for "2" minutes
        And latest DTC status is verified
            | Status | Code  |
            | AC     | A9B17 |
            | AC     | 80511 |
        Then OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And Self update assignment status "UPDATING" is verified in "300" seconds
        And wait for self update of device <device> to complete
        And diagnostic configuration state is "ACTIVE"
        And DTC is generated for "2" minutes
        And latest DTC status is verified
            | Status | Code  |
            | AC     | A9B17 |
            | AC     | 80511 |
        And VRS with protocol <Protocol> and identifier <Identifier> is stopped
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And Self update assignment status "UPDATE_SUCCESS" is verified in "300" seconds
        Then device FW version is verified
        And diagnostic configuration state is "ACTIVE"
        And DTC is generated for "4" minutes
        And latest DTC status is verified
            | Status | Code  |
            | AC     | A9B17 |
            | AC     | 80511 |
        And deactivate ACTIVE diagnostic configuration if present
        And reference system is stopped

        Examples:
            | device | package           | vehicle | diagConfigName          | Protocol   | Identifier       |
            | "CCU"  | "downgrade_delta" | " "     | "SYS-I-001-job_success" | "UDSonCAN" | "UDS_Resp_2DTCs" |
            | "CCU"  | "upgrade_delta"   | " "     | "SYS-I-001-job_success" | "UDSonCAN" | "UDS_Resp_2DTCs" |

   
   
    @E2E-API @E2E-CCU @E2E-HP @E2E-Installation @F-UC_Self_Update @E2E-RM
    Scenario Outline:SU_CCU_API_HP - Device Self-Update while RM is in progress
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        And measurement status is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And test is executed for "3" minutes
        #And test results are verified and 1 in number
        And measurement test results are stored
        And measurement test results are present and 1 in number
        #And measurement job having "1" measurement receives measured results
        And check CCU Self update <package> distribution package from "from_version" to "to_version" available, create if not present
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        Then Self update assignment status "UPDATING" is verified in "300" seconds
        And wait for self update of device <device> to complete
        And measurement status is "ACTIVE"
        #And test results are verified and 1 in number
        And measurement test results are stored
        And measurement test results are present and 1 in number
        #And measurement job having "1" measurement receives newer measured results
        And VRS with protocol <Protocol> and identifier <Identifier> is stopped
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And Self update assignment status "UPDATE_SUCCESS" is verified in "300" seconds
        Then device FW version is verified
        And test is executed for "3" minutes
        And measurement status is "ACTIVE"
        And measurement test results are stored
        And measurement test results are present and 2 in number
        #And measurement job having "2" measurement receives newer measured results
        And Remote measurement is deactivated
        And measurement status is "INACTIVE"
        And reference system is stopped

        Examples:
            | device | package            | vehicle | meas_config_name        | Protocol   | Identifier                     |
            | "CCU"  | "downgrade_delta"  | " "     | "E2E_CAN_RAW_MON_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" |
            | "CCU"  | "upgrade_delta"    | " "     | "E2E_CAN_RAW_MON_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" |

   
   
    @E2E-API @E2E-CCU @E2E-SP @E2E-Installation @F-UC_Self_Update
    Scenario Outline:SU_CCU_API_SP: Device Self-Update based on wrong static deltas
        Given device <device> is "ONLINE"
        And check ECU flashing DP <package> is available
        When OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        Then Self update assignment status "UPDATE_FAILURE" is verified in "700" seconds
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"

        Examples:
            | device | package                               |
            | "CCU"  | "CCU_DELTA_WRONG_VERSION_UNENCRYPTED" |
            | "CCU"  | "CCU_DELTA_PROD_UNENCRYPTED"          |
    
    @E2E-API @E2E-CCU @E2E-HP @E2E-Installation @F-UC_Self_Update
    Scenario Outline:SU_CCU_API_HP - Self update with device [offline-online]
        Given device <device> is "ONLINE"
        And check CCU Self update <package> distribution package from "from_version" to "to_version" available, create if not present
        When switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        When OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        When switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        Then Self update assignment status "UPDATING" is verified in "300" seconds
		When test waits for "3" minutes
		And switch "CL15" is turned "Off"
		Then wait for device to be "OFFLINE"
		When test waits for "1" minutes
		And switch "CL15" is turned "On"
		Then test waits for "3" minutes
		When switch "CL15" is turned "Off"
		And test waits for "5" minutes
		And switch "CL15" is turned "On"
        Then wait for device to be "ONLINE" within "30" minutes
        And Self update assignment status "UPDATE_SUCCESS" is verified in "300" seconds
        Then device FW version is verified
    
        Examples:
            | device | package          |
            | "CCU" | "downgrade_delta" |
            | "CCU" | "upgrade_delta"   |

        
    @E2E-API @E2E-CCU @E2E-HP @E2E-Installation @F-UC_Self_Update
    Scenario Outline:SU_CCU_API_HP - Self update with CL 30 off/on after complete update
        Given device <device> is "ONLINE"
        And check CCU Self update <package> distribution package from "from_version" to "to_version" available, create if not present
        When OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        Then Self update assignment status "UPDATING" is verified in "300" seconds
        And test waits for "3" minutes
		When switch "CL15" is turned "Off"
        And switch "CL30" is turned "Off"
		Then wait for device to be "OFFLINE"
		When switch "CL30" is turned "On"
		And switch "CL15" is turned "On"
		Then test waits for "3" minutes
		When switch "CL15" is turned "Off"
        And switch "CL30" is turned "Off"
        Then test waits for "1" minutes
        When switch "CL30" is turned "On"
		And switch "CL15" is turned "On"
		Then wait for device to be "ONLINE" within "30" minutes
        And Self update assignment status "UPDATE_SUCCESS" is verified in "300" seconds
        Then device FW version is verified
    
        Examples:
            | device | package           |
            | "CCU"  | "downgrade_delta" |
            | "CCU"  | "upgrade_delta"   |