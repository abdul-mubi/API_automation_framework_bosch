Feature:Fetch firmware version of Device
    @E2E-API @E2E-CCU @E2E-HP @E2E-IM @E2E-Regression
    Scenario Outline:IM_CCU_API_HP - Fetch firmware version of Device
    Given device <device> is "ONLINE"
      Then fetch the firmware version of the device from inventory
      
    Examples:
    |device|
    |"CCU"|