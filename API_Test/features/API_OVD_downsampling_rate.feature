Feature: Remote measurement of signals with downsampling rate defined
    @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-CCU @E2E-API @E2E-Regression
    Scenario Outline: Remote Measurement of a signal with downsampling rate defined
    Given device <device> is "ONLINE"
      And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
      And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
      When Remote measurement is activated
      And measurement status is "ACTIVE"
      And reference system <Protocol> with Identifier <Identifier> is started
      And test is executed for "2" minutes
      And reference system is stopped
      Then Remote measurement is deactivated
      And measurement status is "INACTIVE"
      And measurement test results are stored
      And measurement data integrity test is performed

      Examples:
          | vehicle | device   |meas_config_name                          | Protocol   | Identifier                      |
          | " "     | "CCU"    |"E2E_CAN_RAW_MON_500K_Downsampling_rate" | "MONonCAN" | "MONonCAN_500k_highloadidents"  |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Measurement of signals from different source with combination of downsampling
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And create measurment configuration <meas_config_name> if it not is available
        When Measurement job <meas_config_name> is in "draft" state
        And Remove all sources from <meas_config_name>
        And add sources <signal_collection> to <meas_config_name>
        And add signals "S_STD_0x201_S8:" of source <signal_collection_1> to measurement configuration <meas_config_name>
        And add signals "SupplyVoltage:500" of source <signal_collection_2> to measurement configuration <meas_config_name>
        And add signals "Signal_05:2500" of source <signal_collection_3> to measurement configuration <meas_config_name>
        And add signals "S_STD_0x205_S8:1000" of source <signal_collection_1> to measurement configuration <meas_config_name>
        Then release measurement configuration <meas_config_name>
        And verify number of "signals" are "4" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        Then measurement status is "ACTIVE" within "10" minutes
        When reference system <Protocol_1> with Identifier <Identifier_1> is started
        And reference system <Protocol_2> with Identifier <Identifier_2> is started
        And test is executed for "2" minutes
        And Remote measurement is deactivated
        Then measurement status is "INACTIVE" within "10" minutes
        When reference system is stopped
        And measurement test results are stored
        Then measurement data integrity test is performed

        Examples:
            | vehicle | device | signal_collection                                                  | signal_collection_1    | signal_collection_2    | signal_collection_3      | signal_collection_details | meas_config_name        | Protocol_1 | Identifier_1                   | Protocol_2    | Identifier_2                    |
            | " "     | "CCU"  | "E2E_CAN_RAW_MON_500K,System Signals - CTP,SYS-J1939-2021_Signals" | "E2E_CAN_RAW_MON_500K" | "System Signals - CTP" | "SYS-J1939-2021_Signals" | "transmissionRate:500000" | "E2E_MULTI_SRC_JOB"    | "MONonCAN" | "MONonCAN_500k_highloadidents" |"CANalization" |"J1939_Measurement_Signals_200ms"|

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Measurement of signals using different source and downsampling with multiple test steps
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And create measurment configuration <meas_config_name> if it not is available
        When Measurement job <meas_config_name> is in "draft" state
        And Remove all sources from <meas_config_name>
        And add sources <signal_collection> to <meas_config_name>
        And add signals "S_STD_0x201_S8:1000,S_STD_0x205_S8:100" of source <signal_collection_1> to measurement configuration <meas_config_name>
        And add signals "SupplyVoltage:500" of source <signal_collection_2> to measurement configuration <meas_config_name>
        And release measurement configuration <meas_config_name>
        And verify number of "signals" are "3" respectively is present in measurement configuration <meas_config_name>
        And verify <Trigger> as per <Cond1> for "startTrigger,stopTrigger" with "{"preTrigger":20,"postTrigger":20}" seconds,create if not present        
        And Remote measurement is activated
        Then measurement status is "ACTIVE" within "10" minutes
        When reference system <Protocol> with Identifier <Identifier> is started
        And test is executed for "5" minutes
        And Remote measurement is deactivated
        Then measurement status is "INACTIVE" within "10" minutes
        When measurement test results are stored
        Then measurement test results are present and 5 in number
        And measurement data integrity test is performed

        Examples:
            | vehicle | device | signal_collection                               | signal_collection_1    | signal_collection_2    | signal_collection_details | meas_config_name                  | Protocol   | Identifier                     | Trigger            | Trigger_type    | Cond1                             |
            | " "     | "CCU"  | "E2E_CAN_RAW_MON_500K,System Signals - CTP"     | "E2E_CAN_RAW_MON_500K" | "System Signals - CTP" | "transmissionRate:500000" | "E2E_MULTI_SRC_JOB_With_Trigger" | "MONonCAN" | "MONonCAN_500k_highloadidents" |"E2E_Test_Trigger"  | "TIME_INTERVAL" | "Time_interval_config_CCUVoltage" |


    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Measurement of signals from different source with downsampling less than upload interval
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And create measurement configuration <meas_config_name> using upload interval <Upload_Interval> if it is not available
        When Measurement job <meas_config_name> is in "draft" state
        And Remove all sources from <meas_config_name>
        And add sources <signal_collection> to <meas_config_name>
        And add signals "S_STD_0x201_S8:20000,S_STD_0x205_S8:20000" of source <signal_collection_1> to measurement configuration <meas_config_name>
        And add signals "SupplyVoltage:20000" of source <signal_collection_2> to measurement configuration <meas_config_name>
        And add signals "Signal_05:20000" of source <signal_collection_3> to measurement configuration <meas_config_name>
        And release measurement configuration <meas_config_name>
        And verify number of "signals" are "4" respectively is present in measurement configuration <meas_config_name>
        And reference system <Protocol_1> with Identifier <Identifier_1> is started
        And reference system <Protocol_2> with Identifier <Identifier_2> is started
        When Remote measurement is activated
        Then measurement status is "ACTIVE" within "10" minutes
        When test is executed for "80" seconds
        And Remote measurement is deactivated
        Then measurement status is "INACTIVE" within "10" minutes
        When reference system is stopped
        And measurement test results are stored
        Then measurement test step duration is validated with offset <offset_seconds>
        And verify <num_of_samples> samples are present for all signals

        Examples:
            | vehicle | device | signal_collection                                                  | Upload_Interval | signal_collection_1    | signal_collection_2    | signal_collection_3      | signal_collection_details | meas_config_name        | Protocol_1 | Identifier_1                   | Protocol_2    | Identifier_2                    |offset_seconds |num_of_samples|
            | " "     | "CCU"  | "E2E_CAN_RAW_MON_500K,System Signals - CTP,SYS-J1939-2021_Signals" | "60"            | "E2E_CAN_RAW_MON_500K" | "System Signals - CTP" | "SYS-J1939-2021_Signals" | "transmissionRate:500000" | "E2E_MULTI_SRC_JOB"    | "MONonCAN" | "MONonCAN_500k_highloadidents" |"CANalization" |"J1939_Measurement_Signals_200ms"|"10"           |"5"           |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Measurement of signals from different source with downsampling same as upload interval  
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And create measurement configuration <meas_config_name> using upload interval <Upload_Interval> if it is not available
        When Measurement job <meas_config_name> is in "draft" state
        And Remove all sources from <meas_config_name>
        And add sources <signal_collection> to <meas_config_name>
        And add signals "S_STD_0x201_S8:60000,S_STD_0x205_S8:60000" of source <signal_collection_1> to measurement configuration <meas_config_name>
        And add signals "SupplyVoltage:60000" of source <signal_collection_2> to measurement configuration <meas_config_name>
        And add signals "Signal_05:60000" of source <signal_collection_3> to measurement configuration <meas_config_name>
        And release measurement configuration <meas_config_name>
        And verify number of "signals" are "4" respectively is present in measurement configuration <meas_config_name>
        And reference system <Protocol_1> with Identifier <Identifier_1> is started
        And reference system <Protocol_2> with Identifier <Identifier_2> is started
        When Remote measurement is activated
        Then measurement status is "ACTIVE" within "10" minutes
        When test is executed for "1" minutes
        And Remote measurement is deactivated
        Then measurement status is "INACTIVE" within "10" minutes
        When reference system is stopped
        And measurement test results are stored
        Then verify <num_of_samples> samples are present for all signals

        Examples:
            | vehicle | device | signal_collection                                                  | Upload_Interval | signal_collection_1    | signal_collection_2    | signal_collection_3      | signal_collection_details | meas_config_name        | Protocol_1 | Identifier_1                   | Protocol_2    | Identifier_2                     |num_of_samples|
            | " "     | "CCU"  | "E2E_CAN_RAW_MON_500K,System Signals - CTP,SYS-J1939-2021_Signals" | "60"            | "E2E_CAN_RAW_MON_500K" | "System Signals - CTP" | "SYS-J1939-2021_Signals" | "transmissionRate:500000" | "E2E_MULTI_SRC_JOB"    | "MONonCAN" | "MONonCAN_500k_highloadidents" |"CANalization" |"J1939_Measurement_Signals_200ms" |"2"           |


    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Load
    Scenario Outline: RM_CCU_API_HP - Measurement of signals using different source and combination of downsampling for longer duration
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And create measurment configuration <meas_config_name> if it not is available
        When Measurement job <meas_config_name> is in "draft" state
        And Remove all sources from <meas_config_name>
        And add sources <signal_collection> to <meas_config_name>
        And add signals "S_STD_0x201_S8:1000,S_STD_0x205_S8:100" of source <signal_collection_1> to measurement configuration <meas_config_name>
        And add signals "SupplyVoltage:500" of source <signal_collection_2> to measurement configuration <meas_config_name>
        Then release measurement configuration <meas_config_name>
        And verify number of "signals" are "3" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        Then measurement status is "ACTIVE" within "10" minutes
        When reference system <Protocol> with Identifier <Identifier> is started
        And test is executed for "90" minutes
        And Remote measurement is deactivated
        Then measurement status is "INACTIVE" within "10" minutes
        When measurement test results are stored
        Then measurement data integrity test is performed

        Examples:
            | vehicle | device | signal_collection                               | signal_collection_1    | signal_collection_2    | signal_collection_details | meas_config_name     | Protocol   | Identifier                     |
            | " "     | "CCU"  | "E2E_CAN_RAW_MON_500K,System Signals - CTP"     | "E2E_CAN_RAW_MON_500K" | "System Signals - CTP" | "transmissionRate:500000" | "E2E_MULTI_SRC_JOB" | "MONonCAN" | "MONonCAN_500k_highloadidents" |
