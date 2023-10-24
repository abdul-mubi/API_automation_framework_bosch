Feature: Self mapping API-based test
@E2E-API @E2E-CCU @E2E-FM @E2E-Regression @E2E-SP
Scenario Outline:FM_CCU_API_SP : Automatic device mapping - Implant VIN before 'Wait for new vehicle' is selected
    Given device <device> is "ONLINE"
        And set <device_mapping> functionality as "ENABLED" with mode <vehicle_creation_strategy>
        And vin is erased from device <device>
        And it is validated that <device> is mapped to "none"
        And backend vehicle pairing status of the device is validated to be "Unmapped"
        When new VIN is implanted in the device <device>
        Then it is validated that <device> is mapped to "none"
        And set <device_mapping> functionality as "ENABLED" with mode "WAIT"
        And a vehicle <vehicle> using Manufacturer "BMW" and Model "X5" is created with VIN " " 
        Then it is validated that <device> is mapped to "none"

        Examples:           
            | vehicle | device | vehicle_creation_strategy |    device_mapping   |
            | " "     | "CCU" | "IGNORE"                  | "enableSelfMapping" |


@E2E-API @E2E-CCU @E2E-FM @E2E-SP @E2E-Regression
Scenario Outline: FM_CCU_API_SP - Auto Pairing unsuccessful via CAN J1939 with RPM less than 450 and HVB signal OFF
Given device <device> is "ONLINE"
        When set <device_mapping> functionality as "ENABLED" with mode <vehicle_creation_strategy>
        And vin is erased from device <device>
        Then vin "1" is implanted with protocol <Protocol> in device via "CAN" returns "Failure"
        And it is validated that <device> is mapped to "none"
    
      Examples:
          | device    |  device_mapping      | Protocol      |
          | "CCU"     | "enableSelfMapping"  |"CANalization" |


  


  