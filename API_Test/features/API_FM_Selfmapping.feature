Feature: Self mapping API-based test
@E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-HINO @E2E-Regression @F-UC_Vehicle_Provision
Scenario Outline:FM_CCU_API_HP - Self mapping of device with existing vehicle via CAN
Given device <device> is "ONLINE"
    And unmap device from the vehicle
    And vin is erased from device <device>
    And backend vehicle pairing status of the device is validated to be "Unmapped"
    And it is validated that <device> is mapped to "none"
    When reference system <protocol> with Identifier <identifier> and vehicle <vehicle> is started for self-mapping
    Then backend vehicle pairing status of the device is validated to be "Mapped"
    And it is validated that <device> is mapped to <vehicle>

    Examples:
        | vehicle                   | device | protocol          | identifier   |
        | "INT_VEH_CTPG_AUTOPAIR"   | "CCU" | "CANalization"    | "CAN_UDS_VIN" |


@E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-HINO @E2E-Regression @F-UC_Vehicle_Provision
Scenario Outline:FM_CCU_API_HP - Self mapping of device to an existing vehicle by unmapping from an already mapped existing vehicle via CAN
Given device <device> is "ONLINE"
    And unmap device from the vehicle
    And vin is erased from device <device>
    And backend vehicle pairing status of the device is validated to be "Unmapped"
    And it is validated that <device> is mapped to "none"
    When reference system <protocol> with Identifier <identifier> and vehicle <vehicle> is started for self-mapping
    Then backend vehicle pairing status of the device is validated to be "Mapped"
    And it is validated that <device> is mapped to <vehicle>
    When reference system <protocol> with Identifier <identifier> and vehicle <vehicle_another> is started for self-mapping
    Then backend vehicle pairing status of the device is validated to be "Mapped"
    And it is validated that <device> is mapped to <vehicle_another>

    Examples:
        | vehicle                   | device | vehicle_another                  | protocol          | identifier   |
        | "INT_VEH_CTPG_AUTOPAIR"   | "CCU" | "INT_VEH_CTPG_AUTOPAIR_ANOTHER"  | "CANalization"    | "CAN_UDS_VIN" |

@E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Regression @F-UC_Vehicle_Provision
Scenario Outline:FM_CCU_API_HP : Automatic device mapping with different WMI codes
    Given device <device> is "ONLINE"
        And vin is erased from device <device>
        And it is validated that <device> is mapped to "none"
        And backend vehicle pairing status of the device is validated to be "Unmapped"
        When new VIN with <WMI_Code> is implanted in the device <device>
        And backend vehicle pairing status of the device is validated to be "Mapped"
        And test waits for "1" minutes
        And backend vehicle pairing status of the device is validated to be "Mapped"
        Then auto creation of new vehicle is of status "True"
        And it is validated that <device> is mapped to " "

        Examples:
            | device |WMI_Code|
            | "CCU"  |"XLR"   |
            | "CCU"  |"2AY"   |