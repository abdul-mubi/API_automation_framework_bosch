Feature: verify that the remote diagnostic gets activated when its assigned to device slot first and device is mapped to device slot at later point in time
    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression @E2E-ERASE_VIN
    Scenario Outline: RD_CCU_API_HP - Assign Remote Diagnostic and activate using Device Slot
        Given device <device> is "ONLINE"
        And prepare vehicle <vehicle> by clearing all pending jobs
        And create device slot <device_slot> for <vehicle> vehicle
        And delete DTC if present
        And assign diagnostic config <diagConfigName> to <device_slot> of vehicle <vehicle>
        And remote diagnostic configuration state on vehicle <vehicle> is "ASSIGNED"
        When map devices to device slot of <vehicle> vehicle
            | slot_name | device |
            | CCU       | CCU    |
        And remote diagnostic configuration state on vehicle <vehicle> is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And DTC is generated for "2" minutes
        Then VRS with protocol <Protocol> and identifier <Identifier> is stopped
        And latest DTC status is verified
            | Status | Code  |
            | AC     | A9B17 |
            | AC     | 80511 |
        And unmap device <device> from vehicle
        And remote diagnostic configuration state on vehicle <vehicle> is "INACTIVE"
        And deactivate diagnostic assignment on vehicle <vehicle> from "INACTIVE" state
        And verify remote diagnostic configuration on vehicle <vehicle> is removed

        Examples:
            | vehicle | device | device_slot | diagConfigName          | Protocol   | Identifier       |
            | " "     | "CCU"  | "CCU"       | "SYS-I-001-job_success" | "UDSonCAN" | "UDS_Resp_2DTCs" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression @E2E-ERASE_VIN
    Scenario Outline: RD_CCU_API_HP - Assign Remote Diagnostic and activate using Device Slot for Multiple devices sequentially
        Given device <device> is "ONLINE"
        And prepare vehicle <vehicle> by clearing all pending jobs
        And create device slot <device_slot> for <vehicle> vehicle
        And delete DTC if present
        And assign diagnostic config <diagConfigName> to <device_slot> of vehicle <vehicle>
        And remote diagnostic configuration state on vehicle <vehicle> is "ASSIGNED"
        When map devices to device slot of <vehicle> vehicle
            | slot_name | device |
            | CCU       | CCU    |
        And remote diagnostic configuration state on vehicle <vehicle> is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And adhoc Read All DTCs is triggered
        And DTC is generated for "2" minutes
        Then VRS with protocol <Protocol> and identifier <Identifier> is stopped
        And latest DTC status is verified
            | Status | Code  |
            | AC     | A9B17 |
            | AC     | 80511 |
        And unmap device <device> from vehicle
        And remote diagnostic configuration state on vehicle <vehicle> is "INACTIVE"
        And delete DTC if present
        Given device <device2> is "ONLINE"
        When map devices to device slot of <vehicle> vehicle
            | slot_name | device |
            | CCU       | CCU2   |
        And remote diagnostic configuration state on vehicle <vehicle> is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And adhoc Read All DTCs is triggered
        And test is executed for "3" minutes
        Then VRS with protocol <Protocol> and identifier <Identifier> is stopped
        And latest DTC status is verified
            | Status | Code  |
            | AC     | A9B17 |
            | AC     | 80511 |
        And unmap device <device2> from vehicle
        And remote diagnostic configuration state on vehicle <vehicle> is "INACTIVE"
        And deactivate diagnostic assignment on vehicle <vehicle> from "INACTIVE" state
        And verify remote diagnostic configuration on vehicle <vehicle> is removed


        Examples:
            | vehicle | device | device2 | device_slot | diagConfigName          | Protocol   | Identifier       |
            | " "     | "CCU"  | "CCU2"  | "CCU"       | "SYS-I-001-job_success" | "UDSonCAN" | "UDS_Resp_2DTCs" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression @E2E-ERASE_VIN
    Scenario Outline: RD_CCU_API_HP - Assign Remote Diagnostic and activate on Device Slot using Self Mapping
        Given device <device> is "ONLINE"
        And prepare vehicle <vehicle> by clearing all pending jobs
        And create device slot <device_slot> for <vehicle> vehicle
        And delete DTC if present
        And assign diagnostic config <diagConfigName> to <device_slot> of vehicle <vehicle>
        And remote diagnostic configuration state on vehicle <vehicle> is "ASSIGNED"
        When VIN of vehicle <vehicle> is implanted in the device <device>
        And it is validated that <device> is mapped to <vehicle>
        And remote diagnostic configuration state on vehicle <vehicle> is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And adhoc Read All DTCs is triggered
        And DTC is generated for "2" minutes
        Then VRS with protocol <Protocol> and identifier <Identifier> is stopped
        And latest DTC status is verified
            | Status | Code  |
            | AC     | A9B17 |
            | AC     | 80511 |
        And vin is erased from device <device>
        And it is validated that <device> is mapped to "none"
        And remote diagnostic configuration state on vehicle <vehicle> is "INACTIVE"
        When device <device2> is "ONLINE"
        And delete DTC if present
        And VIN of vehicle <vehicle> is implanted in the device <device2>
        And it is validated that <device2> is mapped to <vehicle>
        And remote diagnostic configuration state on vehicle <vehicle> is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And adhoc Read All DTCs is triggered
        And test is executed for "3" minutes
        Then VRS with protocol <Protocol> and identifier <Identifier> is stopped
        And latest DTC status is verified
            | Status | Code  |
            | AC     | A9B17 |
            | AC     | 80511 |
        And vin is erased from device <device2>
        And it is validated that <device2> is mapped to "none"
        And remote diagnostic configuration state on vehicle <vehicle> is "INACTIVE"
        And deactivate diagnostic assignment on vehicle <vehicle> from "INACTIVE" state
        And verify remote diagnostic configuration on vehicle <vehicle> is removed


        Examples:
            | vehicle                 | device | device2 | device_slot | diagConfigName          | Protocol   | Identifier       |
            | "INT_DeviceSlot_RD_001" | "CCU"  | "CCU2"  | "CCU"       | "SYS-I-001-job_success" | "UDSonCAN" | "UDS_Resp_2DTCs" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression
    Scenario Outline: FM_CCU_API_HP - Assign same device to multiple device slots for a vehicle
        Given device <device> is "ONLINE"
        And create <vehicle> if it is not available
        And create device slot <device_slot_list> for <vehicle> vehicle
        When map devices to device slot of <vehicle> vehicle
            | slot_name | device |
            | CCU       | CCU    |
        Then device not being mapped to vehicle <vehicle> is verified
            | slot_name | device |
            | CCU2      | CCU    |

        Examples:
            | vehicle | device | device_slot_list |
            | " "     | "CCU"  | "CCU,CCU2"       |

