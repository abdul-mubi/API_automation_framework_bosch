Feature: Assign Remote measurement and activate using Device Slot
    @E2E-API @E2E-CCU @E2E-ERASE_VIN @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Assign Remote measurement and activate using Device Slot
        Given device <device> is "ONLINE"
        And prepare vehicle <vehicle> by clearing all pending jobs
        And create device slot <device_slot> for <vehicle> vehicle
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        When assign remote measurement to <device_slot> of vehicle <vehicle>
        Then measurement status on vehicle <vehicle> device slot <device_slot> is "ASSIGNED" with substatus "ASSIGNED" and target status is "ACTIVE"
        When map devices to device slot of <vehicle> vehicle
            | slot_name | device |
            | CCU       | CCU    |
        And measurement status on vehicle <vehicle> device slot <device_slot> is "ACTIVE" with substatus "ACTIVATION_CONFIRMED" and target status is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started
        Then test is executed for "1.5" minutes
        And VRS with protocol <Protocol> and identifier <Identifier> is stopped
        And unmap device <device> from vehicle
        And measurement status on vehicle <vehicle> device slot <device_slot> is "ASSIGNED" with substatus "ASSIGNED" and target status is "ACTIVE"
        And test is executed for "10" seconds
        And deactivate remote measurement <meas_config_name> from <device_slot> of vehicle <vehicle>
        And measurement status on vehicle <vehicle> device slot <device_slot> is "INACTIVE" with target status as "INACTIVE"
        #And test results are verified
        And measurement test results are stored
        And measurement test results are verified

        Examples:
            | vehicle | device | device_slot | meas_config_name        | Protocol   | Identifier                     |
            | " "     | "CCU"  | "CCU"       | "E2E_CAN_RAW_MON_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" |


    @E2E-API @E2E-CCU @E2E-ERASE_VIN @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Assign Remote measurement and activate using Device Slot for Multiple devices sequentially
        Given device <device> is "ONLINE"
        And prepare vehicle <vehicle> by clearing all pending jobs
        And create device slot <device_slot> for <vehicle> vehicle
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        When assign remote measurement to <device_slot> of vehicle <vehicle>
        Then measurement status on vehicle <vehicle> device slot <device_slot> is "ASSIGNED" with substatus "ASSIGNED" and target status is "ACTIVE"
        When map devices to device slot of <vehicle> vehicle
            | slot_name | device |
            | CCU       | CCU    |
        And measurement status on vehicle <vehicle> device slot <device_slot> is "ACTIVE" with substatus "ACTIVATION_CONFIRMED" and target status is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started
        Then test is executed for "1.5" minutes
        And VRS with protocol <Protocol> and identifier <Identifier> is stopped
        And unmap device <device> from vehicle
        And measurement status on vehicle <vehicle> device slot <device_slot> is "ASSIGNED" with substatus "ASSIGNED" and target status is "ACTIVE"
        And measurement test results are stored
        And measurement test results are verified
        Given device <device2> is "ONLINE"
        When map devices to device slot of <vehicle> vehicle
            | slot_name | device |
            | CCU       | CCU2   |
        And measurement status on vehicle <vehicle> device slot <device_slot> is "ACTIVE" with substatus "ACTIVATION_CONFIRMED" and target status is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started
        Then test is executed for "1.5" minutes
        And VRS with protocol <Protocol> and identifier <Identifier> is stopped
        And unmap device <device2> from vehicle
        And measurement status on vehicle <vehicle> device slot <device_slot> is "ASSIGNED" with substatus "ASSIGNED" and target status is "ACTIVE"
        And deactivate remote measurement <meas_config_name> from <device_slot> of vehicle <vehicle>
        And measurement status on vehicle <vehicle> device slot <device_slot> is "INACTIVE" with target status as "INACTIVE"
        And measurement test results are stored
        And measurement test results are present and 2 in number

        Examples:
            | vehicle | device | device2 | device_slot | meas_config_name        | Protocol   | Identifier      |
            | " "     | "CCU"  | "CCU2"  | "CCU"       | "E2E_CAN_RAW_MON_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" |


    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Assign Remote measurement on two device slots and activate
        Given device <device> is "ONLINE"
        And device <device2> is "ONLINE"
        And prepare vehicle <vehicle> by clearing all pending jobs
        And create device slot <device_slot_list> for <vehicle> vehicle
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        When map devices to device slot of <vehicle> vehicle
            | slot_name | device |
            | CCU       | CCU    |
            | CCU2      | CCU2   |
        And assign remote measurement to <first_device_slot> of vehicle <vehicle>
        And assign remote measurement to <second_device_slot> of vehicle <vehicle>
        And measurement status on vehicle <vehicle> device slot <first_device_slot> is "ACTIVE" with substatus "ACTIVATION_CONFIRMED" and target status is "ACTIVE"
        And measurement status on vehicle <vehicle> device slot <second_device_slot> is "ACTIVE" with substatus "ACTIVATION_CONFIRMED" and target status is "ACTIVE"
        Then test is executed for "1" minutes
        And deactivate remote measurement <meas_config_name> from <first_device_slot> of vehicle <vehicle>
        And measurement status on vehicle <vehicle> device slot <first_device_slot> is "INACTIVE" with target status as "INACTIVE"
        And deactivate remote measurement <meas_config_name> from <second_device_slot> of vehicle <vehicle>
        And measurement status on vehicle <vehicle> device slot <second_device_slot> is "INACTIVE" with target status as "INACTIVE"

        Examples:
            | vehicle | device | device2 | device_slot_list | first_device_slot | second_device_slot | meas_config_name        | Protocol   | Identifier                     |
            | " "     | "CCU"  | "CCU2"  | "CCU,CCU2"       | "CCU"             | "CCU2"             | "E2E_CAN_RAW_MON_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" |


    @E2E-API @E2E-CCU @E2E-ERASE_VIN @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Assign Remote measurement and activate on Device Slot for using Self Mapping
        Given device <device> is "ONLINE"
        And prepare vehicle <vehicle> by clearing all pending jobs
        And create device slot <device_slot> for <vehicle> vehicle
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        When assign remote measurement to <device_slot> of vehicle <vehicle>
        And measurement status on vehicle <vehicle> device slot <device_slot> is "ASSIGNED" with substatus "ASSIGNED" and target status is "ACTIVE"
        And VIN of vehicle <vehicle> is implanted in the device <device>
        And it is validated that <device> is mapped to <vehicle>
        And measurement status on vehicle <vehicle> device slot <device_slot> is "ACTIVE" with substatus "ACTIVATION_CONFIRMED" and target status is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started
        Then test is executed for "1.5" minutes
        And VRS with protocol <Protocol> and identifier <Identifier> is stopped
        And vin is erased from device <device>
        And it is validated that <device> is mapped to "none"
        And measurement status on vehicle <vehicle> device slot <device_slot> is "ASSIGNED" with substatus "ASSIGNED" and target status is "ACTIVE"
        #And test results are verified and 1 in number
        And measurement test results are stored
        And measurement test results are present and 1 in number

        When device <device2> is "ONLINE"
        And VIN of vehicle <vehicle> is implanted in the device <device2>
        And it is validated that <device2> is mapped to <vehicle>
        And measurement status on vehicle <vehicle> device slot <device_slot> is "ACTIVE" with substatus "ACTIVATION_CONFIRMED" and target status is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started
        Then test is executed for "2.5" minutes
        And VRS with protocol <Protocol> and identifier <Identifier> is stopped
        And vin is erased from device <device2>
        And it is validated that <device2> is mapped to "none"
        And measurement status on vehicle <vehicle> device slot <device_slot> is "ASSIGNED" with substatus "ASSIGNED" and target status is "ACTIVE"
        And deactivate remote measurement <meas_config_name> from <device_slot> of vehicle <vehicle>
        And measurement status on vehicle <vehicle> device slot <device_slot> is "INACTIVE" with target status as "INACTIVE"
        #And test results are verified
        And measurement test results are stored
        And measurement test results are present and 2 in number

        Examples:
            | vehicle                   | device | device2 | device_slot | meas_config_name        | Protocol   | Identifier      |
            | "INT_DeviceSlot_Test_035" | "CCU"  | "CCU2"  | "CCU"       | "E2E_CAN_RAW_MON_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" |
