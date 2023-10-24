Feature: Load test Self mapping of device
    @E2E-API @E2E-CCU @E2E-HP @E2E-FM @E2E-Load
    Scenario Outline: FM_CCU_API_HP - Load test Self mapping of device to an existing vehicle by unmapping from an already mapped existing vehicle
        Given perform 10 times self mapping of <device> with vehicles <vehicle> and <vehicle_another>

        Examples:
            | vehicle                 | device | vehicle_another                 |
            | "INT_VEH_CTPG_AUTOPAIR" | "CCU"  | "INT_VEH_CTPG_AUTOPAIR_ANOTHER" |

    @E2E-API @E2E-CCU @E2E-SP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Load
    Scenario Outline: RF_CCU_API_SP : CAN disconnection during Flashing process - 10 Iteration
        Given perform remote flashing with CAN disconnection 10 times with the data <vehicle>, <device>, <distribution_package>, <Protocol>, <Identifier>, <Identifier1>, <Fota>, <Fota-Identifier>

        Examples:
            | vehicle | device | distribution_package            | Protocol   | Identifier        |Identifier1        | Fota           | Fota-Identifier   |
            | " "     | "CCU"  | "E2E_RF_Standard_Job_Slow" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | "CANalization" | "DriverApp_Break_True" |


    @E2E-API @E2E-CCU @E2E-HP @E2E-PM @E2E-Load
    Scenario Outline:PM_CCU_API_HP - GSM on/off - 10 Iteration
        Given perform 10 times GSM connection on and off for device <device>

        Examples:
            | device |
            | "CCU"  |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Load
    Scenario Outline:RM_CCU_API_HP - Measurement of CAN raw - 10 Iteration
        Given Perform Remote Measurement 10 times with the data <vehicle>, <device>, <meas_config_name>, <Protocol>, <Identifier>, <Measurement_entity>, <Count>

        Examples:
            | vehicle | device | Measurement_entity  | Count   | meas_config_name        | Protocol   | Identifier      |
            | " "     | "CCU"  | "signals"           | "2"     | "E2E_CAN_RAW_MON_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" |


    @E2E-API @E2E-CCU @E2E-HP @E2E-PM @E2E-Load
    Scenario Outline:PM_CCU_API_HP - CL 15 on/off - 20 Iteration
        Given perform CL15 On and Off operation 20 times on device <device> with a time limit of 5 minutes for each iteration

        Examples:
            | device |
            | "CCU"  |


    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Load
    Scenario Outline: PM_CCU_API_HP - Timer wakeup for 10 Iteration
        Given Perform timer wakeup 10 times with the data <vehicle>, <device>, <duration>, <moment>

        Examples:
            | vehicle | device | moment      | duration    |
            | " "     | "CCU"  | "000:00:05" | "000:00:05" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Load
    Scenario Outline:RF_CCU_API_HP - Verify Device log during flashing process for 50 Iteration
        Given perform ECU update with log generation 50 times with the data <vehicle>, <device>, <distribution_package>, <Protocol>, <Identifier>, <Identifier1>, <Fota>, <Fota-Identifier>

        Examples:
            | vehicle | device |  distribution_package           | Protocol   | Identifier     | Identifier1        | Fota           | Fota-Identifier   |
            | " "     | "CCU"  | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | "CANalization" | "DriverApp_Break_True" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Load
    Scenario Outline:RF_CCU_API_HP: Perform OTA ECU update failure and generate logs 50 Iteration
        Given perform ECU update failure with log generation 50 times with the data <vehicle>, <device>, <distribution_package>, <Protocol>, <Identifier>, <Identifier1>, <Fota>, <Fota-Identifier>

        Examples:
            | vehicle | device |  distribution_package  | Protocol   | Identifier        | Identifier1      | Fota           | Fota-Identifier   |
            | " "     | "CCU"  | "DP_wrongBinaries"     | "UDSonCAN" | "CCU_FlashSim_CC" | "DemoFlashSim_1" | "CANalization" | "Flash_Start_CCU" |