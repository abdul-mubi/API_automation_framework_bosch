Feature: Self mapping API-based test
    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Smoke
    Scenario Outline:FM_CCU_API_HP : Auto Pairing device to vehicle Enabled with mode "Create new vehicle"
        Given device <device> is "ONLINE"
        And set <device_mapping> functionality as "ENABLED" with mode <vehicle_creation_strategy>
        And vin is erased from device <device>
        And it is validated that <device> is mapped to "none"
        And backend vehicle pairing status of the device is validated to be "Unmapped"
        When new VIN is implanted in the device <device>
        Then auto creation of new vehicle is of status "True"
        And backend vehicle pairing status of the device is validated to be "Mapped" 
        And it is validated that <device> is mapped to " "  

        Examples:
            | device | vehicle_creation_strategy |    device_mapping   |
            | "CCU"  | "CREATE"                  | "enableSelfMapping" |

  

 
    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Regression
    Scenario Outline:FM_CCU_API_HP : Automatic device mapping Enabled with mode "Wait for new vehicle"
    Given device <device> is "ONLINE"
        And set <device_mapping> functionality as "ENABLED" with mode <vehicle_creation_strategy>
        And vin is erased from device <device>
        And it is validated that <device> is mapped to "none"
        And backend vehicle pairing status of the device is validated to be "Unmapped"
        When new VIN is implanted in the device <device>
        And a vehicle <vehicle> using Manufacturer "BMW" and Model "X5" is created with VIN " "
        And backend vehicle pairing status of the device is validated to be "Mapped"
        Then it is validated that <device> is mapped to " "  

        Examples:
            | vehicle | device | vehicle_creation_strategy |    device_mapping   |
            | " "     | "CCU" | "WAIT"                    | "enableSelfMapping" |

  

    
    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Regression
    Scenario Outline:FM_CCU_API_HP : Automatic device mapping Enabled with mode "ignore"
     Given device <device> is "ONLINE"
        And set <device_mapping> functionality as "ENABLED" with mode <vehicle_creation_strategy>
        And vin is erased from device <device>
        And it is validated that <device> is mapped to "none"
        And backend vehicle pairing status of the device is validated to be "Unmapped"
        When new VIN is implanted in the device <device>
        Then auto creation of new vehicle is of status "False"
        And it is validated that <device> is mapped to "none"
        When VIN of vehicle <vehicle> is implanted in the device <device>
        And backend vehicle pairing status of the device is validated to be "Mapped"
        Then it is validated that <device> is mapped to <vehicle>

        Examples:
            | vehicle                 | device |vehicle_creation_strategy |    device_mapping   |
            | "INT_VEH_CTPG_AUTOPAIR" | "CCU" |"IGNORE"                  | "enableSelfMapping" |
  

    
    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Regression
    Scenario Outline:FM_CCU_API_HP : Automatic device mapping Enabled with mode "wait for new vehicle" by manually mapping to another vehicle before new vehicle is created
    Given device <device> is "ONLINE"
        And set <device_mapping> functionality as "ENABLED" with mode <vehicle_creation_strategy>
        And vin is erased from device <device>
        And it is validated that <device> is mapped to "none"
        And backend vehicle pairing status of the device is validated to be "Unmapped"
        When new VIN is implanted in the device <device>
        And map device to the vehicle <vehicle_another>
        And a vehicle <vehicle> using Manufacturer "BMW" and Model "X5" is created with VIN " "
        And backend vehicle pairing status of the device is validated to be "Mapped"
        Then it is validated that <device> is mapped to <vehicle>

        Examples:
            | vehicle | device | vehicle_another                 | vehicle_creation_strategy |    device_mapping   |
            | " "     | "CCU" | "INT_VEH_CTPG_AUTOPAIR_ANOTHER" | "WAIT"                    | "enableSelfMapping" |
  
    

    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Regression
    Scenario Outline:FM_CCU_API_HP : Automatic device mapping Disabled
    Given device <device> is "ONLINE"
        And vin is erased from device <device>
        And it is validated that <device> is mapped to "none"
        And backend vehicle pairing status of the device is validated to be "Unmapped"
        When VIN of vehicle <vehicle> is implanted in the device <device>
        Then it is validated that <device> is mapped to <vehicle>
        And backend vehicle pairing status of the device is validated to be "Mapped"
        And vin is erased from device <device>
        And backend vehicle pairing status of the device is validated to be "Unmapped"
        And it is validated that <device> is mapped to "none"
        And set <device_mapping> functionality as "DISABLED" in fleet settings
        When VIN of vehicle <vehicle> is implanted in the device <device>
        And it is validated that <device> is mapped to "none"
        And map device to the vehicle <vehicle>
        Then it is validated that <device> is mapped to <vehicle>
        
        Examples:
            | vehicle                 | device |    device_mapping   |
            | "INT_VEH_CTPG_AUTOPAIR" | "CCU" | "enableSelfMapping" |
  

    
    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Regression
    Scenario Outline:FM_CCU_API_HP : Automatic device mapping Enabled with "wait for new vehicle" when CL15 is turned off
     Given device <device> is "ONLINE"
        And set <device_mapping> functionality as "ENABLED" with mode <vehicle_creation_strategy>
        And vin is erased from device <device>
        And it is validated that <device> is mapped to "none"
        And backend vehicle pairing status of the device is validated to be "Unmapped"
        When new VIN is implanted in the device <device>
        And switch "CL15" is turned "Off"
        Then wait for device to be "OFFLINE"
        And a vehicle <vehicle> using Manufacturer "BMW" and Model "X5" is created with VIN " "
        And test waits for "2" minutes
        Then it is validated that <device> is mapped to " "

        Examples:
            | vehicle | device | vehicle_creation_strategy |    device_mapping   |
            | " "     | "CCU" | "WAIT"                    | "enableSelfMapping" |
  
  
  
  

    

  

  

  
