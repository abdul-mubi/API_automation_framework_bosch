Feature: Trigger on VehiclePropertySignals
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP- Trigger on Vehicle property signal with configuration start trigger as Ignition on and stop trigger as Ignition off when initial state of vehicle is Ignition on
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Trigger_Condition> for "startTrigger,stopTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And test is executed for "30" seconds
        And ignition is turned "Off"
        And test is executed for "10" seconds
        And measurement test results are stored
        Then data integrity test is performed on measured data as per trigger <Trigger> trigger condition <Trigger_Condition> for trigger type <Trigger_type>
        And ignition is turned "On"
        And wait for device to be "ONLINE"
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        
    Examples:
        |vehicle  |device    |meas_config_name                             |can_protocol   |can_identifier                 |Trigger             |Trigger_type       | Trigger_Condition           |
        |" "      |"CCU"     |"E2E_Trigger_Vehicle_property_Signals_01"   |"MONonCAN"     |"MONonCAN_500k_highloadidents" |"E2E_Test_Trigger"  |"VEHICLE_PROPERTY" | "vehicle_property_triggers_01"|

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP- Trigger on Vehicle property signal with configuration start trigger as Ignition on and stop trigger as Ignition off when initial state of vehicle is Ignition off or normal KL15 boot scenario
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Trigger_Condition> for "startTrigger,stopTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And test is executed for "1.5" minutes
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And ignition is turned "On"
        And wait for device to be "ONLINE"
        And test is executed for "30" seconds
        And ignition is turned "Off"
        And test is executed for "10" seconds
        And measurement test results are stored
        Then measurement test result for latest step is "available"
        And ignition is turned "On"
        And wait for device to be "ONLINE"
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        
    Examples:
        |vehicle  |device    |meas_config_name                             |can_protocol   |can_identifier                 |Trigger             |Trigger_type       | Trigger_Condition           |
        |" "      |"CCU"     |"E2E_Trigger_Vehicle_property_Signals_01"   |"MONonCAN"     |"MONonCAN_500k_highloadidents" |"E2E_Test_Trigger"  |"VEHICLE_PROPERTY" | "vehicle_property_triggers_01"|

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP- Trigger on Vehicle property signal with configuration start trigger as Ignition on and stop trigger as Ignition off when device is booted with cold start and Ignition on with some delay
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Trigger_Condition> for "startTrigger,stopTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And switch "CL30" is turned "Off"
        And wait for device to be "OFFLINE"
        And switch "CL30" is turned "On"
        And test is executed for "60" seconds
        And ignition is turned "On"
        And wait for device to be "ONLINE"
        And test is executed for "30" seconds
        And ignition is turned "Off"
        And test is executed for "10" seconds
        And measurement test results are stored
        And measurement test result for latest step is "available"
        And ignition is turned "On"
        And wait for device to be "ONLINE"
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        
    Examples:
        |vehicle  |device    |meas_config_name                             |can_protocol   |can_identifier                 |Trigger             |Trigger_type       | Trigger_Condition           |
        |" "      |"CCU"     |"E2E_Trigger_Vehicle_property_Signals_01"   |"MONonCAN"     |"MONonCAN_500k_highloadidents" |"E2E_Test_Trigger"  |"VEHICLE_PROPERTY" | "vehicle_property_triggers_01"|

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP- Trigger on Vehicle property signal with configuration start trigger as Ignition on and stop trigger as Ignition off with pre and post trigger time
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Trigger_Condition> for "startTrigger,stopTrigger" with "{"preTrigger":5,"postTrigger":5}" seconds,create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And test is executed for "10" seconds
        And ignition is turned "Off"
        And test is executed for "10" seconds
        And ignition is turned "On"
        And test is executed for "30" seconds
        And ignition is turned "Off"
        And test is executed for "15" seconds
        And measurement test results are stored
        Then data integrity test is performed on measured data as per trigger <Trigger> trigger condition <Trigger_Condition> for trigger type <Trigger_type>
        And ignition is turned "On"
        And wait for device to be "ONLINE"
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        
    Examples:
        |vehicle  |device    |meas_config_name                              |Trigger             |Trigger_type       | Trigger_Condition           |
        |" "      |"CCU"     |"E2E_Trigger_Vehicle_property_Signals_02"    |"E2E_Test_Trigger"  |"VEHICLE_PROPERTY" | "vehicle_property_triggers_02"|


    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP- Trigger on Vehicle property signal with configuration start trigger as Ignition off and stop trigger as Ignition on to measure Supply voltage during Ignition off state
   Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Trigger_Condition> for "startTrigger,stopTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And test is executed for "10" seconds
        And ignition is turned "Off"
        And test is executed for "30" seconds
        And ignition is turned "On"
        And wait for device to be "ONLINE"
        And test is executed for "10" seconds
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        Then data integrity test is performed on measured data as per trigger <Trigger> trigger condition <Trigger_Condition> for trigger type <Trigger_type>
        
        
    Examples:
        |vehicle  |device    |meas_config_name                              |Trigger             |Trigger_type       | Trigger_Condition           |
        |" "      |"CCU"     |"E2E_Trigger_Vehicle_property_Signals_03"    |"E2E_Test_Trigger"  |"VEHICLE_PROPERTY" | "vehicle_property_triggers_03"|

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP- Trigger on Vehicle property signal with configuration start trigger as Ignition on for Single shot type configuration
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Trigger_Condition> for "startTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And test is executed for "10" seconds
        And ignition is turned "Off"
        And test is executed for "10" seconds
        And ignition is turned "On"
        And wait for device to be "ONLINE"
        And test is executed for "10" seconds
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        Then data integrity test is performed on measured data as per trigger <Trigger> trigger condition <Trigger_Condition> for trigger type <Trigger_type>
        
        
    Examples:
        |vehicle  |device    |meas_config_name                              |Trigger             |Trigger_type       | Trigger_Condition           |
        |" "      |"CCU"     |"E2E_Trigger_Vehicle_property_Signals_04"    |"E2E_Test_Trigger"  |"VEHICLE_PROPERTY" | "vehicle_property_triggers_01"|

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP- Trigger on Vehicle property signal with configuration start trigger as mobile network unavailable and mobile network available as stop trigger
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Trigger_Condition> for "startTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And test is executed for "1.5" minutes
        And command to "stopGSMConnection" GSM mode of the device
        And wait for device to be "OFFLINE"
        And command to "startGSMConnection" GSM mode of the device
        And wait for device to be "ONLINE"
        And test is executed for "10" seconds
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        Then measurement test result for latest step is "available"
        
    Examples:
        |vehicle  |device    |meas_config_name                              |Trigger             |Trigger_type       | Trigger_Condition           |
        |" "      |"CCU"     |"E2E_Trigger_Vehicle_property_Signals_05"    |"E2E_Test_Trigger"  |"VEHICLE_PROPERTY" | "vehicle_property_triggers_04"|

   