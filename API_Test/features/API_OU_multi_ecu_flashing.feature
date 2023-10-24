Feature: Multi ECU Flashing
    @E2E-API @E2E-CCU @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression @E2E-HP
    Scenario Outline:RF_CCU_API_HP - Multiple (>5) Distribution Packages to the same vehicle in parallel
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier> is started
        And the "7"nd reference system <Protocol> with Identifier <Identifier1> is started
        And check ECU flashing DP <distribution_package> is available
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "180" seconds
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        Then flashing status of OTA package is changed to "UPDATE_SUCCESS" within "120" seconds
        And verify logs for "SUCCESSFUL" OTA assignments within "100" seconds
        And reference system is stopped

        Examples:
            | vehicle | device | distribution_package                                                                                                                                                                                                                                                                                                                                    | Protocol   | Identifier                                                                                  | Fota_Identifier        | Identifier1           | Fota           |
            | " "     | "CCU"  | "VECU_Fast_driverApprovalAndPreconditions_InstallRdaJob21,VECU_Fast_driverApprovalAndPreconditions_InstallRdaJob31,VECU_Fast_driverApprovalAndPreconditions_InstallRdaJob29,VECU_Fast_driverApprovalAndPreconditions_InstallRdaJob27,VECU_Fast_driverApprovalAndPreconditions_InstallRdaJob25,VECU_Fast_driverApprovalAndPreconditions_InstallRdaJob23" | "UDSonCAN" | "DemoFlashSim21,DemoFlashSim31,DemoFlashSim29,DemoFlashSim27,DemoFlashSim25,DemoFlashSim23" | "DriverApp_Break_True" | "DemoFlashSim_Getway" | "CANalization" |