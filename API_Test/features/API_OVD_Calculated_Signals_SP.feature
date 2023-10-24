Feature: Remote measurement of Calculated Signals
    @E2E-API @E2E-CCU @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression @E2E-SP
    Scenario Outline:RM_CCU_API_SP - Remote Measurement of Calculated signals when input signal data for calculated signal formula is empty
     Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,calculatedSignals" are "1,1" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And test is executed for "0.5" minutes
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And measurement test result for latest step is "not available"

        Examples:
            | vehicle | device | meas_config_name                    |
            | " "     | "CCU" | "Calculated_Signals_SP_Automation1" |

    @E2E-API @E2E-CCU @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression @E2E-SP
    Scenario Outline:RM_CCU_API_SP - Remote measurement of Calculated signals by dividing them with zero
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,calculatedSignals" are "1,1" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "0.5" minutes
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And reference system is stopped
        And measurement test results are stored
        And measurement test result for latest step is "not available"

        Examples:
            | vehicle | device | meas_config_name                   | can_protocol   | can_identifier      |
            | " "     | "CCU"  | "Calculated_Signals_SP_Automation" | "CANalization" | "RM_Onetime_Message_5000ms" |