Feature:Inventory of all ECUs in a vehicle
    @E2E-API @E2E-CCU @E2E-HP @E2E-Regression @E2E-RF @BV-UC_Inventory
    Scenario Outline:Complete Inventory of all ECUs in a Vehicle
    Given device <device> is "ONLINE"
    And map device to the vehicle <vehicle>
    And check ECU flashing DP <distribution_package> is available
    When OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"        
    And flashing status of OTA package is changed to "UPDATE_SUCCESS" within "60" seconds
    And command to "stopGSM_MBS_Connection" GSM mode of the device
    And test waits for "0.5" minutes
    And command to "startGSM_MBS_Connection" GSM mode of the device
    And test waits for "1" minutes
    Then vehicle inventory details are verified for <inventory_type>

    Examples:
    |vehicle|device|distribution_package   |inventory_type     |
    |" "    |"CCU" |"New_ECU_Inventory_Job"|"SOFTWARE,HARDWARE"|