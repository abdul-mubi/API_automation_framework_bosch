Feature:  Remote Measurement with Value encoded Signal
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Smoke
    Scenario Outline:RM_CCU_API_HP - Remote Measurement with Value encoded Signal
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        And release measurement configuration <meas_config_name>
        #And delete the previous data if it is available
        When Remote measurement is activated
        And measurement status is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And test is executed for "3" minutes
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE"
        And reference system is stopped
        And measurement test results are stored
        And measurement data integrity test is performed for encoded measurement
            | vcu_IcMileage | vcu_ParkLockState |
            | 0-20050       | unlocked          |
            | 20051-40000   | locked            |
            | 40001-60000   | Error             |

        Examples:
            | vehicle | device | meas_config_name         | Protocol       | Identifier      |
            | " "     | "CCU"  | "E2E_CAN_VALUE_ENCODING" | "CANalization" | "Value_Encoded" |

