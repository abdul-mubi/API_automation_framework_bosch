Feature: Remote Measurement Vehicle Setup Group with vehicle movement
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @E2E-Regression @BV-UC_RemoteMeasurement
    Scenario Outline:RM_CCU_API_HP - Assign RM configuration on vehicle which were added to VSG previously
    Given device <device> is "ONLINE"
        And create <vehicle> if it is not available
        And create a vehicle setup group <vsg>
        And create device slots <device_slot> to vehicle setup group <vsg>
        And add vehicles <vehicle> to vehicle setup group <vsg>
        Then remove vehicles <vehicle> from vehicle setup group <vsg>
        And create measurment configuration <meas_config_name> if it not is available
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        And Remote measurement is activated
        And measurement status is "ACTIVE"
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE"

   Examples:
        | vehicle                   | device | device_slot | vsg                         | meas_config_name        |                                                                                                                
        | "AUT_VSG_TEST_Vehicle_01" | "CCU"  | "CCU"       | "VSG_Test_vehicle_movement" |  "E2E_CAN_RAW_MON_500K" |