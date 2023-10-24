Feature:SP for VIN implantation using UDS Seed & Key
@E2E-API @E2E-CCU @E2E-FM @E2E-PACCAR @E2E-SP @F-UC_Vehicle_Provision
Scenario Outline: FM_CCU_API_SP - No VIN Mismatch event when "PairOnlyTrustedvin" is disabled after performing seed and key
Given device <device> is "ONLINE"
        When set <device_mapping> functionality as "ENABLED" in fleet settings
        And vin is erased from device <device>
        Then verify VIN Mismatch event is "false" by reading DTC using <Protocol>
        When performing seed and Key in device using <Protocol>
        And set <device_mapping> functionality as "DISABLED" in fleet settings
        And vin "1" is implanted with protocol <Protocol> in device via "UDS"
        And backend vehicle pairing status of the device is validated to be "Mapped"
        And vin "1" is implanted with protocol <Protocol> in device via "CAN"
        And backend vehicle pairing status of the device is validated to be "Mapped"
        When vin "2" is implanted with protocol <Protocol> in device via "CAN"
        Then backend vehicle pairing status of the device is validated to be "Mapped"
        And validate vin "2" is implanted currently in device
        And verify VIN Mismatch event is "true" by reading DTC using <Protocol>

    Examples:
          | device     |   device_mapping     | Protocol     |
          | "CCU"     | "pairOnlyTrustedVin" |"CANalization" |


@E2E-API @E2E-CCU @E2E-FM @E2E-PACCAR @E2E-SP @F-UC_Vehicle_Provision
Scenario Outline: FM_CCU_API_SP - No VIN Mismatch event while performing seed and key when "PairOnlyTrustedvin" is disabled
Given device <device> is "ONLINE"
        When set <device_mapping> functionality as "DISABLED" in fleet settings
        And vin is erased from device <device>
        Then verify VIN Mismatch event is "false" by reading DTC using <Protocol>
        When performing seed and Key in device using <Protocol>
        And vin "1" is implanted with protocol <Protocol> in device via "UDS"
        Then backend vehicle pairing status of the device is validated to be "Mapped"
        When vin "2" is implanted with protocol <Protocol> in device via "CAN"
        Then backend vehicle pairing status of the device is validated to be "Mapped"
        And validate vin "1" is implanted currently in device
        And verify VIN Mismatch event is "false" by reading DTC using <Protocol>

    Examples:
          | device     |   device_mapping     | Protocol      |
          | "CCU"     | "pairOnlyTrustedVin" |"CANalization" |
