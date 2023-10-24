Feature: Fleet management Geotrack API-based test
    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Regression
    Scenario Outline:FM_CCU_API_HP - Activation of Geo-positioning and clean-up of Geo-positions for all vehicles
            Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And geo positioning in <vehicle> is enabled
        When geo position data of all vehicles are deleted
        Then verify that vehicle map is "empty"
        When geo position of all vehicles is "disabled"
        Then verify geo positioning in <vehicle> is "Disabled"
        When geo position of all vehicles is "enabled"
        Then verify geo positioning in <vehicle> is "disabled"

        Examples:
            | vehicle                | device | 
            | "GPS_vehicle_setting"  | "CCU" |
