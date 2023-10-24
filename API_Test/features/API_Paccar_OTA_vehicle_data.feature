Feature: Paccar OTA vehicle data for Vehicle Setup Group
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression @E2E-Paccar
    Scenario Outline:RM_CCU_API_HP - OTA vehicle data Trip measurement validation
        Given device <device> is "ONLINE"
        And create <vehicles> if it is not available
        And create a vehicle setup group <vsg1>
        And create device slots <device_slot> to vehicle setup group <vsg1>
        And add vehicles <vehicles> to vehicle setup group <vsg1>
        And verify vehicles <vehicles> have same "DEVICE_SLOTS" as vehicle setup group <vsg1>
        And map device to <device_slot> slot of vehicles
            | vehicle_name         | device |
            | AUT_Paccar_VSG_Test_9| CCU    |
        When Remote measurement <measurement_configurations> is activated for vehicle setup group <vsg1> 
        And reference system <Protocol> with Identifier <Identifier> is started  
        Then validate sync progress bar with <statistics_value>
        And measurement status on vehicle <vehicles> device slot <device_slot> is "ACTIVE" with substatus "ACTIVATION_CONFIRMED" and target status is "ACTIVE"
        When test is executed for "28" minutes
        And measurement test results are stored for vehicle setup group <vsg1>
        And reference system is stopped
        Then measurement test results are present and 13 in number
        And validate data for <signals_to_check> for measurement configuration "Status_Basic_Continuous_2"
        And validate preview data for VTripDuration for the measurement configuration
        When remove vehicles <vehicles> from vehicle setup group <vsg1>
        Then measurement status on vehicle <vehicles> device slot <device_slot> is "INACTIVE" with substatus "DEACTIVATION_CONFIRMED" and target status is "INACTIVE"
        When create a vehicle setup group <vsg2>
        And create device slots <device_slot> to vehicle setup group <vsg2>
        And add vehicles <vehicles> to vehicle setup group <vsg2>
        Then check "no active" measurement configuration in <vsg2> and generate logs if active measurement configuration found
        When remove vehicles <vehicles> from vehicle setup group <vsg2>
        And remote measurement is deactivated for vehicle setup group <vsg1>
        And validate sync progress bar with <deactivation_statistics> for <vsg1>
        And target status as "INACTIVE" for vehicle setup group <vsg1> is validated
        And delete the vehicle setup group

        Examples:
            | vehicles                | device | device_slot | vsg1    | vsg2    | measurement_configurations                                                                                               | statistics_value                         | deactivation_statistics                     | Protocol       | Identifier  | signals_to_check                  |              
            | "AUT_Paccar_VSG_Test_9" | "CCU"  | "CCU"       | "VSG_A" | "VSG_B" | "Index_DM1_EWP,Index_TellTales,Index_Warnings,Index_Basic_KeyCycleEnd,Index_Basic,Monitor_All,Status_Basic_Continuous_2" | "vsg_paccar_OTA_vehicle_data_activation" |  "vsg_paccar_OTA_vehicle_data_deactivation" |"CANalization" | "Paccar_RM" | "VUsedFuel:1244.0,Distance:5180.0"|

