Feature: [OTA][Assignments] - Assignment Revocation
    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Smoke
    Scenario Outline:RF_CCU_API_HP: Assignment Revocation from different status before Update is started
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And check ECU flashing DP <distribution_package> is available
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to <assignment_status> within "300" seconds
        And revoke the OTA assignment
        Then flashing status of OTA package is changed to "UPDATE_REVOKED" within "100" seconds

        Examples:
            | vehicle | device | distribution_package            | assignment_status              |
            | " "     | "CCU"  | "E2E_RF_Standard_Job_encrypted" | "UPDATE_ASSIGNED"              |
            | " "     | "CCU"  | "E2E_RF_Standard_Job_encrypted" | "DOWNLOADING"                  |
            | " "     | "CCU"  | "E2E_RF_Standard_Job_encrypted" | "WAITING_FOR_UPDATE_CONDITION" |


    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CCU_API_HP: Assignment Revocation once Update is started
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        And check ECU flashing DP <distribution_package> is available
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "80" seconds
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        Then flashing status of OTA package is changed to "UPDATING" within "1000" seconds
        And revoke the OTA assignment
        Then flashing status of OTA package is changed to "UPDATE_REVOKED" within "120" seconds
        And reference system is stopped

        Examples:
            | vehicle | device | distribution_package       | Protocol   | Identifier     | Identifier1      | Fota_Identifier        | Fota           |
            | " "     | "CCU"  | "E2E_RF_Standard_Job_Slow" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | "DriverApp_Break_True" | "CANalization" |


    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CCU_API_HP: Revoke the RF-Assignment from PENDING UPDATE CONDITION after turning off CL15
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And check ECU flashing DP <distribution_package> is available
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "80" seconds
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And revoke the OTA assignment
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        Then flashing status of OTA package is changed to "UPDATE_REVOKED" within "300" seconds
        And reference system is stopped

        Examples:
            | vehicle | device | distribution_package            | Protocol   | Identifier     | Identifier1      | Fota_Identifier        | Fota           |
            | " "     | "CCU"  | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | "DriverApp_Break_True" | "CANalization" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CCU_API_HP: Rewoke one of Multiple RF-Assignments
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier> is started
        And check ECU flashing DP <distribution_package> is available
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "80" seconds
        And revoke <First> OTA assignment
        And flashing status of <First> OTA assignment is changed to "UPDATE_REVOKED" within "80" seconds
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        And flashing status of <Second> OTA assignment is changed to "UPDATE_SUCCESS" within "120" seconds
        And reference system is stopped
        Examples:
            | vehicle | device | distribution_package                                                                                                | Protocol   | Identifier                      | Fota_Identifier        | Fota           | First | Second |
            | " "     | "CCU"  | "VECU_Fast_driverApprovalAndPreconditions_InstallRdaJob31,VECU_Fast_driverApprovalAndPreconditions_InstallRdaJob29" | "UDSonCAN" | "DemoFlashSim31,DemoFlashSim29" | "DriverApp_Break_True" | "CANalization" | 1     | 2      |