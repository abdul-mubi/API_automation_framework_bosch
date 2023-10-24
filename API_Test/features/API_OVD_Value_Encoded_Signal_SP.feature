Feature: Remote Measurement of signals with value encoding
    @E2E-API @E2E-CCU @E2E-SP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_SP - Remote Measurement of signals with value encoding when a different reference system is running
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        And release measurement configuration <meas_config_name>
        #And delete the previous data if it is available
        When Remote measurement is activated
        And measurement status is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And test is executed for "1.5" minutes
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE"
        And reference system is stopped
        #And test result is "False"
        And measurement test results are stored
        And measurement test result is "False"

        Examples:
            | vehicle | device | meas_config_name               | Protocol   | Identifier      |
            | " "     | "CCU"  | "E2E_CAN_VALUE_ENCODING_500K" | "MONonCAN" | "MONonCAN_500k_highloadidents" |

