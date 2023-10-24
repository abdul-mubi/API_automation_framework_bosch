Feature:VIN implantation using UDS Seed & Key
@E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-PACCAR @F-UC_Vehicle_Provision
Scenario Outline: FM_CCU_API_HP - Read VIN Mismatch event when PairOnlyTrustedvin is enabled
Given device <device> is "ONLINE"
        When set <device_mapping> functionality as "ENABLED" in fleet settings
        And vin is erased from device <device>
        Then verify VIN Mismatch event is "false" by reading DTC using <Protocol>
        When performing seed and Key in device using <Protocol>
        And vin "1" is implanted with protocol <Protocol> in device via "UDS"
        Then backend vehicle pairing status of the device is validated to be "Mapped"
        And it is validated that <device> is mapped to vin "1" vehicle
        When vin "1" is implanted with protocol <Protocol> in device via "CAN"
        Then backend vehicle pairing status of the device is validated to be "Mapped"
        When vin "2" is implanted with protocol <Protocol> in device via "CAN"
        Then it is validated that <device> is mapped to "none"
        And backend vehicle pairing status of the device is validated to be "Failure"
        And validate vin "2" is implanted currently in device
        And verify VIN Mismatch event is "true" by reading DTC using <Protocol>

      Examples:
          | device     |   device_mapping     | Protocol     |
          | "CCU"     | "pairOnlyTrustedVin" |"CANalization" |


@E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-PACCAR @F-UC_Vehicle_Provision
Scenario Outline: FM_CCU_API_HP - VIN mismatch retains and confirmed VIN can be modified after mismatch
Given device <device> is "ONLINE"
        When set <device_mapping> functionality as "ENABLED" in fleet settings
        And vin is erased from device <device>
        Then verify VIN Mismatch event is "false" by reading DTC using <Protocol>
        When performing seed and Key in device using <Protocol>
        And vin "1" is implanted with protocol <Protocol> in device via "UDS"
        Then backend vehicle pairing status of the device is validated to be "Mapped"
        And it is validated that <device> is mapped to vin "1" vehicle
        And vin "1" is implanted with protocol <Protocol> in device via "CAN"
        Then backend vehicle pairing status of the device is validated to be "Mapped"
        When vin "2" is implanted with protocol <Protocol> in device via "CAN"
        Then it is validated that <device> is mapped to "none"
        And backend vehicle pairing status of the device is validated to be "Failure"
        When vin "1" is implanted with protocol <Protocol> in device via "UDS"
        Then backend vehicle pairing status of the device is validated to be "Failure"
        And validate vin "2" is implanted currently in device
        And verify VIN Mismatch event is "true" by reading DTC using <Protocol>
        When vin "2" is implanted with protocol <Protocol> in device via "UDS"
        Then backend vehicle pairing status of the device is validated to be "Mapped"
        And it is validated that <device> is mapped to vin "2" vehicle
        
    Examples:
          | device   |   device_mapping     | Protocol      |
          | "CCU"    | "pairOnlyTrustedVin" |"CANalization" |

@E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-PACCAR @E2E-Regression @F-UC_Vehicle_Provision
Scenario Outline: FM_CCU_API_HP - Reinstall CCU on different vehicle and verify VIN mismatch status
Given device <device> is "ONLINE"
        When set <device_mapping> functionality as "ENABLED" in fleet settings
        And vin is erased from device <device>
        #Then verify VIN Mismatch event is "false" by reading DTC using <Protocol>
        When performing seed and Key in device using <Protocol>
        And vin "1" is implanted with protocol <Protocol> in device via "UDS"
        Then backend vehicle pairing status of the device is validated to be "Mapped"
        And it is validated that <device> is mapped to vin "1" vehicle
        When vin "1" is implanted with protocol <Protocol> in device via "CAN"
        Then backend vehicle pairing status of the device is validated to be "Mapped"
        And it is validated that <device> is mapped to <vehicle1>
        When reference system is stopped
        And vin "2" is implanted with protocol <Protocol> in device via "CAN"
        Then it is validated that <device> is mapped to "none"
        And backend vehicle pairing status of the device is validated to be "Failure"
        When performing seed and Key in device using <Protocol>
        And vin "2" is implanted with protocol <Protocol> in device via "UDS"
        Then backend vehicle pairing status of the device is validated to be "Mapped"
        #And verify VIN Mismatch event is "false" by reading DTC using <Protocol>
        And it is validated that <device> is mapped to <vehicle2>

      Examples:
          | device    | vehicle1                  | vehicle2                    |  device_mapping      | Protocol      |
          | "CCU"     |"E2EYDL1H4D9000001_Vehicle"| "E2EYDL1H4D9000002_Vehicle" | "pairOnlyTrustedVin" |"CANalization" |

@E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-PACCAR @E2E-Smoke @F-UC_Vehicle_Provision
Scenario Outline: FM_CCU_API_HP - Auto Pairing via CAN J1939: Reinstall CCU after Resetting the VIN and verify trusted VIN
Given device <device> is "ONLINE"
        When set <device_mapping> functionality as "ENABLED" in fleet settings
        And vin is erased from device <device>
        #Then verify VIN Mismatch event is "false" by reading DTC using <Protocol>
        When vin "1" is implanted with protocol <Protocol> in device via "CAN"
        Then backend vehicle pairing status of the device is validated to be "Mapped"
        And it is validated that <device> is mapped to <vehicle1>
        When performing seed and Key in device using <Protocol>
        And vin "Reset" is implanted with protocol <Protocol> in device via "UDS"
        Then backend vehicle pairing status of the device is validated to be "BACKEND_VIN_RECEIVED"
        When vin "2" is implanted with protocol <Protocol> in device via "CAN"
        Then backend vehicle pairing status of the device is validated to be "Mapped"
        And it is validated that <device> is mapped to <vehicle2>

      Examples:
          | device    | vehicle1                  | vehicle2                    |  device_mapping      | Protocol      |
          | "CCU"     |"E2EYDL1H4D9000001_Vehicle"| "E2EYDL1H4D9000002_Vehicle" | "pairOnlyTrustedVin" |"CANalization" |