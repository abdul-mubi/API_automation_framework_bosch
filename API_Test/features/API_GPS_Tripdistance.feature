Feature: [RM][Device Signals] - GPS Trip Distance

    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement
    Scenario Outline:RM_CCU_API_HP: Measurement of GPSTripDistance by Enabling GPS after assigning the Measurement Job

        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        When geo positioning in <vehicle> is "Disabled"
        And measurement configuration <meas_config_name> is assigned
        Then measurement status is "ACTIVE"
        When test is executed for "3" minutes
        And geo positioning in <vehicle> is enabled
        Then positioning data is verified within "600" seconds
        When test is executed for "3" minutes
        And Remote measurement is deactivated
        Then measurement status is "INACTIVE"
        When measurement test results are stored
        Then gps along with trip distance details are verified for the geo positioning enabled duration

Examples:
        | vehicle  | device  | meas_config_name                    |
        | " "      | "CCU"  | "GPS_Device_Signals_10s_Automation" |
    

    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement
    Scenario Outline:RM_CCU_API_HP: Verification of GPSTripDistance Measurement

        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And geo position data of <vehicle> is deleted if available
        When geo positioning in <vehicle> is enabled
        Then positioning data is verified within "600" seconds
        When create measurment configuration <meas_config_name> if it not is available
        And add sources <signal_collection> to <meas_config_name>
        And add signals <signal_details> of source <signal_collection> to measurement configuration <meas_config_name>
        And release measurement configuration <meas_config_name>
        And measurement configuration <meas_config_name> is assigned
        Then measurement status is "ACTIVE"
        When test is executed for "5" minutes
        And Remote measurement is deactivated
        Then measurement status is "INACTIVE"
        When measurement test results are stored
        Then vehicle gps along with trip distance details are verified

Examples:
        | vehicle  | device  |signal_collection     | meas_config_name                      |signal_details                                                                                                                      |
        | " "      | "CCU"  |"System Signals - CTP"| "GPS_Device_Signals_10s_Automation"  |"GPS:10000,GPSTripDistance:10000,GPSAltitude:10000,GPSFix:10000,GPSHeading:10000,GPSLatitude:10000,GPSLongitude:10000,GPSSpeed:10000"|
        | " "      | "CCU"  |"System Signals - CTP"| "GPS_Device_Signals_60s_Automation"  |"GPS:60000,GPSTripDistance:60000,GPSAltitude:60000,GPSFix:60000,GPSLatitude:60000,GPSLongitude:60000"                                |
    

    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-OnRequest
    Scenario Outline:FM_CCU_API_HP - Activation of Geo-positioning and clean-up of Geo-positions for one vehicle

        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And geo position data of <vehicle> is deleted if available        
        When geo positioning in <vehicle> is enabled
        Then test is executed for "7" minutes
        # verifies the latest position and that with current time
        And geo positioning data is verified
        And geo positioning data of <vehicle> is deleted

Examples:
        | vehicle   | device | 
        | " "       | "CCU" |

    
    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement
    Scenario Outline:RM_CCU_API_HP: Measurement of GPS Trip distance with CL15 off and On

        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And geo position data of <vehicle> is deleted if available
        When geo positioning in <vehicle> is enabled
        Then positioning data is verified within "600" seconds
        When measurement configuration <meas_config_name> is assigned
        Then measurement status is "ACTIVE"
        When test is executed for "3" minutes
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And test is executed for "3" minutes
        And Remote measurement is deactivated
        Then measurement status is "INACTIVE"
        When measurement test results are stored
        Then gps along with trip distance is verified for "New Trip"

        Examples:
            | vehicle  | device  |signal_collection     | meas_config_name                     |
            | " "      | "CCU"  |"System Signals - CTP"| "GPS_Device_Signals_10s_Automation" |

    
    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement
    Scenario Outline:RM_CCU_API_HP: Verification of GPSTripDistance measurement while changing the GPS setting

        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And geo position data of <vehicle> is deleted if available
        When geo positioning in <vehicle> is enabled
        Then positioning data is verified within "600" seconds
        When measurement configuration <meas_config_name> is assigned
        Then measurement status is "ACTIVE"
        When test is executed for "3" minutes
        And geo positioning in <vehicle> is "Disabled"
        And test is executed for "3" minutes
        And geo positioning in <vehicle> is enabled
        And test is executed for "3" minutes
        And Remote measurement is deactivated
        Then measurement status is "INACTIVE"
        When measurement test results are stored
        Then gps along with trip distance details are verified for the geo positioning enabled duration

        Examples:
            | vehicle  | device  | meas_config_name                     |
            | " "      | "CCU"  | "GPS_Device_Signals_10s_Automation" |

    




