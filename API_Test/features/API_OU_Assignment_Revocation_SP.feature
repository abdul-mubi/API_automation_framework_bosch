Feature: [OTA][Assignments] - Assignment Revocation - SP
    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression @E2E-SP
    Scenario Outline:RF_CCU_API_SP: Revoke the RF-Assignment after Download is completed after turning off GSM
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        And check ECU flashing DP <distribution_package> is available
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "80" seconds
        And command to "stopGSMConnection" GSM mode of the device
        And wait for device to be "OFFLINE"
        And revoke the OTA assignment
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        And command to "startGSMConnection" GSM mode of the device
        And wait for device to be "ONLINE"
        Then flashing status of OTA package is changed to "UPDATE_REVOKED" within "120" seconds

        Examples:
            | vehicle | device | distribution_package       | Protocol   | Identifier     | Identifier1      | Fota_Identifier        | Fota           |
            | " "     | "CCU"  | "E2E_RF_Standard_Job_Slow" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | "DriverApp_Break_True" | "CANalization" |