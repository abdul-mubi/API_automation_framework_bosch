Feature: Remote Measurement for Vehicle Setup Group
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Activating Remote Measurement for one vehicle in measurement setup group
    Given device <device> is "ONLINE"
        And create <vehicles> if it is not available
        And create a vehicle setup group <vsg>
        And create device slots <device_slot> to vehicle setup group <vsg>
        And add vehicles <vehicles> to vehicle setup group <vsg>
        And verify vehicles <vehicles> have same "DEVICE_SLOTS" as vehicle setup group <vsg>
        And map device to <device_slot> slot of vehicles
        | vehicle_name       | device |
        | AUT_VSG_TEST_Vehicle_01 | CCU  |
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement <meas_config_name> is activated for vehicle setup group <vsg>
        And validate sync progress bar with <statistics_value>
        Then remote measurement deactivated for vehicle setup group
        And validate sync progress bar with <deactivation_statistics>
        And remove vehicles <vehicles> from vehicle setup group <vsg>


      Examples:
          | vehicles                                          | vsg           | device     | device2 | device_slot | Protocol   |Identifier                    | meas_config_name        |         statistics_value       |  deactivation_statistics|
          | "AUT_VSG_TEST_Vehicle_01,AUT_VSG_TEST_Vehicle_02" |"AUT_VSG_TEST_01"| "CCU"     | "CCU2" | "CCU"       | "MONonCAN" |"MONonCAN_500k_highloadidents" | "E2E_CAN_RAW_MON_500K" | "vsg_sp_statistics_activate"   |  "vsg_statistics_validation"|

    
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Performing Remote Measurement activation and reactivation on measurement setup group
    Given device <device> is "ONLINE"
        And create <vehicles> if it is not available
        And create a vehicle setup group <vsg>
        And create device slots <device_slot> to vehicle setup group <vsg>
        And add vehicles <vehicles> to vehicle setup group <vsg>
        And verify vehicles <vehicles> have same "DEVICE_SLOTS" as vehicle setup group <vsg>
        And map device to <device_slot> slot of vehicles
        | vehicle_name       | device |
        | AUT_VSG_TEST_Vehicle_03 | CCU	|
        | AUT_VSG_TEST_Vehicle_04 | CCU2  |
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement <meas_config_name> is activated for vehicle setup group <vsg>
        And validate sync progress bar with <statistics_value>
        And measurement status on vehicle <vehicles> device slot <device_slot> is "ACTIVE" with substatus "ACTIVATION_CONFIRMED" and target status is "ACTIVE"
        Then remote measurement deactivated for vehicle setup group
        And validate sync progress bar with <deactivation_statistics>
        When remote measurement is reactivated for vehicle setup group
        And validate sync progress bar with <statistics_value>
        Then remote measurement deactivated for vehicle setup group
        And validate sync progress bar with <deactivation_statistics>
        And measurement status on vehicle <vehicles> device slot <device_slot> is "INACTIVE" with substatus "DEACTIVATION_CONFIRMED" and target status is "INACTIVE"
        Then remove vehicles <vehicles> from vehicle setup group <vsg>


      Examples:
          | vehicles                                         | vsg           | device     | device2 | device_slot | Protocol   |Identifier                    | meas_config_name        |    statistics_value        |   deactivation_statistics     |
          | "AUT_VSG_TEST_Vehicle_03,AUT_VSG_TEST_Vehicle_04"|"AUT_VSG_TEST_02"| "CCU"     | "CCU2" | "CCU"      | "MONonCAN" |"MONonCAN_500k_highloadidents" | "E2E_CAN_RAW_MON_500K"  | "vsg_activation_statistics"| "vsg_deactivation_statistics" |


    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Smoke
    Scenario Outline:RM_CCU_API_HP - Performing continuous Remote Measurement on measurement setup group
    Given device <device> is "ONLINE"
        And create <vehicles> if it is not available
        And create a vehicle setup group <vsg>
        And create device slots <device_slot> to vehicle setup group <vsg>
        And add vehicles <vehicles> to vehicle setup group <vsg>
        And verify vehicles <vehicles> have same "DEVICE_SLOTS" as vehicle setup group <vsg>
        And map device to <device_slot> slot of vehicles
        | vehicle_name       | device |
        | AUT_VSG_TEST_Vehicle_13 | CCU   |
        | AUT_VSG_TEST_Vehicle_14 | CCU2  |
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement <meas_config_name> is activated for vehicle setup group <vsg>
        And target status as "ACTIVE" for vehicle setup group is validated
        And validate sync progress bar with <statistics_value>
        And measurement status on vehicle <vehicles> device slot <device_slot> is "ACTIVE" with substatus "ACTIVATION_CONFIRMED" and target status is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started for <device> device
        And reference system <Protocol> with Identifier <Identifier> is started for <device2> device
        And test is executed for "1" minutes
        And remote measurement deactivated for vehicle setup group
        And target status as "INACTIVE" for vehicle setup group is validated
        And validate sync progress bar with <deactivation_statistics>
        And measurement status on vehicle <vehicles> device slot <device_slot> is "INACTIVE" with substatus "DEACTIVATION_CONFIRMED" and target status is "INACTIVE"
        And reference system is stopped
        And measurement test results are stored for vehicle setup group <vsg>
        And measurement data integrity smoke test is performed for vehicle setup group
        Then remove vehicles <vehicles> from vehicle setup group <vsg>


      Examples:
          | vehicles                                          | vsg             | device    | device2 | device_slot| Protocol   |Identifier                     | meas_config_name  |     statistics_value       | deactivation_statistics       |
          | "AUT_VSG_TEST_Vehicle_13,AUT_VSG_TEST_Vehicle_14" |"AUT_VSG_TEST_03"| "CCU"     | "CCU2"  | "CCU"      | "MONonCAN" |"MONonCAN_500k_highloadidents" | "E2E_CAN_RAW_MON" | "vsg_activation_statistics"| "vsg_deactivation_statistics" |