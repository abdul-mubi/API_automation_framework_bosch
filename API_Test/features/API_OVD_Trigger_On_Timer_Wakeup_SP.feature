Feature:  Remote Measurement on Trigger on Wakeup Timer device
    @E2E-API @E2E-CCU @E2E-HINO @E2E-SP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_SP - Remote Measurement on Trigger on Wakeup Timer device Wakeup by CAN Traffic
        Given device <device> is "ONLINE"
        And device operation "rebootDevice" is performed
        And wait for device to be "ONLINE"
        And map device to the vehicle <vehicle>
        When time <time> for device wake up is set and device should be online for <duration>
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And switch "CL15" is turned "Off"
        Then wait for device to be "OFFLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And wait for device to be "ONLINE"
        And test is executed for "3" minutes
        And VRS with protocol <Protocol> and identifier <Identifier> is stopped
        And measurement test steps are not generated


        Examples:
            | vehicle | device | time        | duration    | Trigger            | Cond1                      | Protocol   | Identifier                     | meas_config_name                      |
            | " "     | "CCU"  | "000:00:12" | "000:00:05" | "E2E_Test_Trigger" | "TimerTriggerWithoutDelay" | "MONonCAN" | "MONonCAN_500k_highloadidents" | "E2E_CAN_RAW_MON_500K_Trigger_Timer" |


    @E2E-API @E2E-CCU @E2E-HINO @E2E-SP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_SP - Remote Measurement on Trigger on Wakeup Timer Device Wakeup by T15
        Given device <device> is "ONLINE"
        And device operation "rebootDevice" is performed
        And wait for device to be "ONLINE"
        And map device to the vehicle <vehicle>
        When time <time> for device wake up is set and device should be online for <duration>
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And switch "CL15" is turned "Off"
        Then wait for device to be "OFFLINE"
        And switch "CL15" is turned "On"
        Then wait for device to be "ONLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And test is executed for "3" minutes
        And VRS with protocol <Protocol> and identifier <Identifier> is stopped
        And measurement test steps are not generated


        Examples:
            | vehicle | device | time        | duration    | Trigger            | Cond1                      | Protocol   | Identifier                     | meas_config_name                      |
            | " "     | "CCU"  | "000:00:07" | "000:00:05" | "E2E_Test_Trigger" | "TimerTriggerWithoutDelay" | "MONonCAN" | "MONonCAN_500k_highloadidents" | "E2E_CAN_RAW_MON_500K_Trigger_Timer" |


    @E2E-API @E2E-CCU @E2E-HINO @E2E-SP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_SP - Remote Measurement on Trigger on Wakeup TL15 Device Wakeup by Timer
        Given device <device> is "ONLINE"
        And device operation "rebootDevice" is performed
        And wait for device to be "ONLINE"
        And map device to the vehicle <vehicle>
        When time <time> for device wake up is set and device should be online for <duration>
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And switch "CL15" is turned "Off"
        Then wait for device to be "OFFLINE"
        And test waited till device wakeup configuration time <time> is met
        And wait for device to be "ONLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And test is executed for "3" minutes
        And VRS with protocol <Protocol> and identifier <Identifier> is stopped
        And measurement test steps are not generated


        Examples:
            | vehicle | device | time        | duration    | Trigger            | Cond1                     | Protocol   | Identifier                     | meas_config_name                     |
            | " "     | "CCU"  | "000:00:07" | "000:00:05" | "E2E_Test_Trigger" | "TL15TriggerWithoutDelay" | "MONonCAN" | "MONonCAN_500k_highloadidents" | "E2E_CAN_RAW_MON_500K_Trigger_TL15" |

    @E2E-API @E2E-CCU @E2E-HINO @E2E-SP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_SP - Remote Measurement on Trigger on Wakeup TL15 Device Wakeup by CAN Traffic
        Given device <device> is "ONLINE"
        And device operation "rebootDevice" is performed
        And wait for device to be "ONLINE"
        And map device to the vehicle <vehicle>
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger",create if not present
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And switch "CL15" is turned "Off"
        Then wait for device to be "OFFLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And wait for device to be "ONLINE"
        And test is executed for "3" minutes
        And VRS with protocol <Protocol> and identifier <Identifier> is stopped
        And measurement test steps are not generated


        Examples:
            | vehicle | device | Trigger            | Cond1                     | Protocol   | Identifier                     | meas_config_name                     |
            | " "     | "CCU"  | "E2E_Test_Trigger" | "TL15TriggerWithoutDelay" | "MONonCAN" | "MONonCAN_500k_highloadidents" | "E2E_CAN_RAW_MON_500K_Trigger_TL15" |