Feature: [OTA][Assignments] - Assignment Revocation and Retry
@E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CCU_API_HP: Assignment Revocation Retry once Update is started
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        And check ECU flashing DP <distribution_package> is available
        When OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "80" seconds
        And revoke the OTA assignment
        Then flashing status of OTA package is changed to "UPDATE_REVOKED" within "120" seconds
        When retry revoked Ota assignment using retry mechanism 
        Then flashing status of OTA package is changed to "UPDATE_ASSIGNED" within "60" seconds
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "80" seconds
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        And flashing status of OTA package is changed to "UPDATE_SUCCESS" within "120" seconds
        And reference system is stopped

        Examples:
            | vehicle | device | distribution_package       | Protocol   | Identifier     | Identifier1      | Fota_Identifier        | Fota           |
            | " "     | "CCU"  | "E2E_RF_Standard_Job_Slow" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | "DriverApp_Break_True" | "CANalization" |