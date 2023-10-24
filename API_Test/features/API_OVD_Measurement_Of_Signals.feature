Feature:  Measurement of CAN raw  and J1939 Signals
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Measurement of CAN raw with complete measurement validation
      Given device <device> is "ONLINE"
      And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
      And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
      When Remote measurement is activated
      And measurement status is "ACTIVE"
      And reference system <Protocol> with Identifier <Identifier> is started
      And test is executed for "1.5" minutes
      And reference system is stopped
      Then Remote measurement is deactivated
      And measurement status is "INACTIVE"
      And measurement test results are stored
      And measurement test step duration is validated
      And measurement data integrity test is performed

      Examples:
          | vehicle    | device |meas_config_name          | Protocol   | Identifier       | 
          | " "        | "CCU"  |"E2E_CAN_RAW_MON_500K"   | "MONonCAN" | "MONonCAN_500k_highloadidents"  |


    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Re-prepare and download of Measurement of CAN raw
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        #And reference system <Protocol> with Identifier <Identifier> is started
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        And measurement status is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And test is executed for "1" minutes
        And measurement test results are stored
        And test is executed for "1" minutes
        And reference system is stopped
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE"
        When measurement test result downloads are reprepared
        And measurement test results are stored
        And measurement test step duration is validated
        And measurement test results having newer measured data is validated
        #And measurement data integrity test is performed
        # This is not needed as above step downloads and varifies the test results
        #And size of the file is validated
        #And data integrity test is performed on consecutive frames
        #   | Variable           | Increment | Timestamp | Threshould |
        #   | S_STD_0x201_S8     | 1         | 0.01      | 800        |
        #   | S_EXT_0x2000005_S8 | 1         | 0.01      | 800        |
        #And reference system is stopped

        Examples:
            | vehicle | device | meas_config_name        | Protocol   | Identifier      |
            | " "     | "CCU"  | "E2E_CAN_RAW_MON_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" |


    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Measurement of J1939 Signals with complete measurement validation
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And reference system <Protocol> with Identifier <Identifier> is started
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        And measurement status is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And test is executed for "1" minutes
        And reference system is stopped
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE"
        And measurement test results are stored
        And measurement data integrity test is performed

        Examples:
            | vehicle | device | meas_config_name            | Protocol       | Identifier                  |
            | " "     | "CCU"  | "E2E_J1939_SIGNALS_CONFIG" | "CANalization" | "J1939_Measurement_Signals_100ms" |


