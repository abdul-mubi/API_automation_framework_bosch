Feature:Timer wakeup
    @E2E-API @E2E-CCU @E2E-FM @E2E-HINO @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: PM_CCU_API_HP - Timer wakeup : Perform RM after device timer wake-up
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        When time <moment> for device wake up is set and device should be online for <duration>
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And test waited till device wakeup configuration time <moment> is met
        And wait for device to be "ONLINE"
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "15" minutes
        And reference system <Protocol> with Identifier <Identifier> is started
        And test is executed for "1" minutes
        And reference system is stopped
        #Then test results are verified
        And measurement test results are stored
        And measurement test results are verified
        And wait for device to be "OFFLINE"
        And verify device status stayed in "OFFLINE" for "000:00:05"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And Remote measurement is deactivated
        And measurement status is "INACTIVE" within "15" minutes


        Examples:
            | vehicle | device | moment      | duration    | Protocol      | Identifier                      | meas_config_name        |
            | " "     | "CCU"  | "000:00:05" | "000:00:05" | "MONonCAN"    | "MONonCAN_500k_highloadidents " | "E2E_CAN_RAW_MON_500K" |