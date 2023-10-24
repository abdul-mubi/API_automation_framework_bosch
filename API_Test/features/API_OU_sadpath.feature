Feature: Remote flashing Sad Path API-based test
    @E2E-API @E2E-CCU @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression @E2E-SP
    Scenario Outline:RF_CCU_API_SP - Flashing with wrong binaries [ interchanged ]
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier> is started
        And check ECU flashing DP <distribution_package> is available
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "80" seconds
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        Then flashing status of OTA package is changed to "UPDATE_FAILURE" within "120" seconds
        And reference system is stopped
        And verify the hex content for <Identifier>

        Examples:
            | vehicle | device | distribution_package | Protocol   | Identifier        | Identifier1      | Fota_Identifier   | Fota           |
            | " "     | "CCU"  | "DP_wrongBinaries"   | "UDSonCAN" | "CCU_FlashSim_CC" | "DemoFlashSim_1" | "Flash_Start_CCU" | "CANalization" |

    @E2E-API @E2E-CCU @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression @E2E-SP
    Scenario Outline:RF_CCU_API_SP - Wrong UDS response during Flashing
        Given device <device> is "ONLINE"
        And reference system <ProtocolErrorUDS> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        And map device to the vehicle <vehicle>
        And check ECU flashing DP <distribution_package> is available
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "80" seconds
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        Then flashing status of OTA package is changed to "UPDATE_FAILURE" within "120" seconds
        And reference system is stopped

        Examples:
            | vehicle | device | distribution_package            | ProtocolErrorUDS | Protocol   | Identifier                 | Identifier1      | Fota_Identifier        | Fota           |
            | " "     | "CCU"  | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN"       | "UDSonCAN" | "CCU_FlashSim_CC-UDSError" | "DemoFlashSim_1" | "DriverApp_Break_True" | "CANalization" |

    @E2E-API @E2E-CCU @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression @E2E-SP
    Scenario Outline:RF_CCU_API_SP - Flashing using corrupted container
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And check ECU flashing DP <distribution_package> is available
        And reference system <Protocol> with Identifier <Identifier> is started
        When OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to "UPDATE_FAILURE" within "600" seconds
        And reference system is stopped

        Examples: 
            | vehicle | device | distribution_package         | Protocol   | Identifier        | Fota_Identifier   | Fota           | 
            | " "     | "CCU"  | "E2E-invalid-encrypted_None" | "UDSonCAN" | "CCU_FlashSim_CC" | "Flash_Start_CCU" | "CANalization" |

    @E2E-API @E2E-CCU @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression @E2E-SP
    Scenario Outline:FM_CCU_API_SP - Device log after RF failure
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        And device log count is fetched
        And check ECU flashing DP <distribution_package> is available
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "80" seconds
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        And flashing status of OTA package is changed to "UPDATING" within "80" seconds
        And reference system is stopped
        And flashing status of OTA package is changed to "UPDATE_FAILURE" within "120" seconds
        Then "2" new log entries are generated for the device

        Examples:
            | vehicle | device | distribution_package            | Protocol   | Identifier     | Identifier1      | Fota_Identifier        | Fota           |
            | " "     | "CCU"  | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | "DriverApp_Break_True" | "CANalization" |


    @E2E-API @E2E-CCU @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression @E2E-SP
    Scenario Outline:RF_CCU_API_SP : Turn off CL30 when flashing is in progress
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        And check ECU flashing DP <distribution_package> is available
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "80" seconds
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        And flashing status of OTA package is changed to "UPDATING" within "100" seconds
        And switch "CL15" is turned "Off"
        And switch "CL30" is turned "Off"
        And wait for device to be "OFFLINE"
        And switch "CL30" is turned "On"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        Then flashing status of OTA package is changed to "UPDATE_FAILURE" within "100" seconds
        And verify logs for "FAILED" OTA assignments within "100" seconds
        And reference system is stopped

        Examples:
            | vehicle | device | distribution_package            | Protocol   | Identifier     | Identifier1      | Fota_Identifier        | Fota           |
            | " "     | "CCU"  | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | "DriverApp_Break_True" | "CANalization" |

    @E2E-API @E2E-CCU @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression @E2E-SP
    Scenario Outline:RF_CCU_API_SP : Turn off ECU when flashing is in progress
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        And check ECU flashing DP <distribution_package> is available
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "80" seconds
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        And flashing status of OTA package is changed to "UPDATING" within "100" seconds
        And reference system is stopped
        Then flashing status of OTA package is changed to "UPDATE_FAILURE" within "500" seconds

        Examples:
            | vehicle | device | distribution_package            | Protocol   | Identifier     | Identifier1      | Fota_Identifier        | Fota           |
            | " "     | "CCU"  | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | "DriverApp_Break_True" | "CANalization" |

    @E2E-API @E2E-CCU @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression @E2E-SP
    Scenario Outline:RF_CCU_API_SP : Compatibility Check with Negative Outcome on Assignment creation
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And check ECU flashing DP <distribution_package> is available
        And verify assignment creation is "Rejected" for device <device> with incompatible distribution package

        Examples:
            | vehicle | device | distribution_package                                   |
            | " "     | "CCU"  | "DP_Verify_Compatibility_Check_Assignment_Creation_SP" |

    @E2E-API @E2E-CCU @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression @E2E-HP
    Scenario Outline:RF_CCU_API_HP : Compatibility Check with Positive Outcome on Assignment creation
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        And check ECU flashing DP <distribution_package> is available
        And verify assignment creation is "Accepted" for device <device> with compatible distribution package
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "300" seconds
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        And flashing status of OTA package is changed to "UPDATING" within "100" seconds
        Then flashing status of OTA package is changed to "UPDATE_SUCCESS" within "600" seconds
        And reference system is stopped

        Examples:
            | vehicle | device | distribution_package                                   | Protocol   | Identifier     | Identifier1      | Fota         |Fota_Identifier       |
            | " "     | "CCU"  | "DP_Verify_Compatibility_Check_Assignment_Creation_New_HP" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" |"CANalization"|"DriverApp_Break_True"|