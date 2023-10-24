Feature: Paccar OTA vehicle data with OTA Updates
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @E2E-Load @E2E-Paccar
    Scenario Outline:RM_RF_CCU_API_HP - Perform 30 times ECU flashing parallelly when RM is running
        Given device <device> is "ONLINE"
        And create <vehicles> if it is not available
        And create a vehicle setup group <vsg1>
        And create device slots <device_slot> to vehicle setup group <vsg1>
        And add vehicles <vehicles> to vehicle setup group <vsg1>
        And verify vehicles <vehicles> have same "DEVICE_SLOTS" as vehicle setup group <vsg1>
        And map device to <device_slot> slot of vehicles
            | vehicle_name             | device |
            | AUT_VSG_TEST_Vehicle_002 | CCU    |
        When Remote measurement <measurement_configurations> is activated for vehicle setup group <vsg1> 
        And the "2"nd reference system <Protocol1> with Identifier <Identifier1> is started  
        And measurement status on vehicle <vehicles> device slot <device_slot> is "ACTIVE" with substatus "ACTIVATION_CONFIRMED" and target status is "ACTIVE"

        Then perform remote flashing while RM is in progress for 30 times with the data <vehicles>, <device>, <distribution_package>, <Protocol2>, <Identifier2>, <Identifier3>
        And remote measurement is deactivated for vehicle setup group <vsg1>
        And measurement status on vehicle <vehicles> device slot <device_slot> is "INACTIVE" with substatus "DEACTIVATION_CONFIRMED" and target status is "INACTIVE"
        
        
        Examples:
            | vehicles                  | device | device_slot | vsg1              | measurement_configurations                                                                                                | Protocol1      | Identifier1   | distribution_package                         |  Protocol2    | Identifier2    | Identifier3       |   
            | "AUT_VSG_TEST_Vehicle_002" | "CCU"  | "CCU"      | "VSG_RM_Test_02"  | "Index_DM1_EWP,Index_TellTales,Index_Warnings,Index_Basic_KeyCycleEnd,Index_Basic,Monitor_All,Status_Basic_Continuous_2"  |"CANalization"  | "Paccar_RM"   | "VECU_Slow_runImmediately_InstallRdaJob_New" |  "UDSonCAN"   | "DemoFlashSim" | "DemoFlashSim_1" |

