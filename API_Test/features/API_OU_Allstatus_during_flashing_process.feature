Feature: Remote flashing API-based test
    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CCU_API_HP - All status during Flashing process
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        And check ECU flashing DP <distribution_package> is available
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        Then flashing status of OTA package is changed to "UPDATE_SUCCESS" within "120" seconds
        And reference system is stopped
        And all the flashing status <ota_assignment_status> is verified
        And verify the hex content for <Identifier>

        Examples:
            | vehicle | device | distribution_package                  | Protocol   | Identifier     | Identifier1      | ota_assignment_status                                                                                        |
            | " "     | "CCU"  | "E2E_RF_Standard_Job_Run_Immediately" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | "UPDATE_ASSIGNED,NOTIFIED,DOWNLOADING,DOWNLOAD_SUCCESS,WAITING_FOR_UPDATE_CONDITION,UPDATING,UPDATE_SUCCESS" |


    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CCU_API_HP - Reboot device while flashing is in-progress
        Given device <device> is "ONLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier1> is started
        And check ECU flashing DP <distribution_package> is available
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "80" seconds
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        Then flashing status of OTA package is changed to "UPDATE_SUCCESS" within "120" seconds
        And reference system is stopped
        And verify the hex content for <Identifier>

        Examples:
            | vehicle | device | distribution_package            | Protocol   | Identifier     | Identifier1      | Fota_Identifier        | Fota           |
            | " "     | "CCU"  | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | "DriverApp_Break_True" | "CANalization" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CCU_API_HP - Device status change [ offline - online ] during flashing
        Given device <device> is "ONLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier1> is started
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And check ECU flashing DP <distribution_package> is available
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        Then flashing status of OTA package is changed to "UPDATE_ASSIGNED" within "200" seconds
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "80" seconds
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        Then flashing status of OTA package is changed to "UPDATE_SUCCESS" within "120" seconds
        And reference system is stopped

        Examples:
            | vehicle | device | distribution_package            | Protocol   | Identifier     | Identifier1      | Fota_Identifier        | Fota           |
            | " "     | "CCU"  | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | "DriverApp_Break_True" | "CANalization" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:FM_CCU_API_HP - Multiple Auto Device Log Generation when performing RF
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier> is started
        And device log count is fetched
        And reference system <Protocol> with Identifier <Identifier1> is started
        And check ECU flashing DP <distribution_package> is available
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "80" seconds
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        And flashing status of OTA package is changed to "UPDATING" within "100" seconds
        And reference system is stopped
        And flashing status of OTA package is changed to "UPDATE_FAILURE" within "80" seconds
        And verify logs for "FAILED" OTA assignments within "100" seconds
        And triggering new log file generation for device
        And "3" new log entries are generated for the device


        Examples:
            | vehicle | device | distribution_package            | Protocol   | Identifier     | Identifier1      | Fota_Identifier        | Fota           |
            | " "     | "CCU"  | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | "DriverApp_Break_True" | "CANalization" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CCU_API_HP :Turn on/off the GSM connection when remote flashing is ongoing
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        And check ECU flashing DP <distribution_package> is available
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "80" seconds
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        And flashing status of OTA package is changed to "UPDATING" within "15" seconds
        And command to "stopGSMConnection" GSM mode of the device
        And wait for device to be "OFFLINE"
        And test waits for "5" minutes
        And command to "startGSMConnection" GSM mode of the device
        And wait for device to be "ONLINE"
        Then flashing status of OTA package is changed to "UPDATE_SUCCESS" within "120" seconds
        And verify logs for "SUCCESSFUL" OTA assignments within "100" seconds
        And reference system is stopped


        Examples:
            | vehicle | device | distribution_package            | Protocol   | Identifier     | Identifier1      | Fota_Identifier        | Fota           |
            | " "     | "CCU"  | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | "DriverApp_Break_True" | "CANalization" |

    @E2E-API @E2E-BE @E2E-CCU @E2E-FM @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression @E2E-ValidateTest
    Scenario Outline:RF_CCU_API_HP - Flashing using Lean Package
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And check ECU flashing DP <distribution_package> is available
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        Then flashing status of OTA package is changed to "UPDATE_SUCCESS" within "300" seconds

        Examples:
            | vehicle | device | distribution_package           |
            | " "     | "CCU"  | "DP_lean_package_01_Encrypted" |