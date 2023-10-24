Feature:Data Preprocessing Onboard - SUM for nD-statistics
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Data Preprocessing of SUM for nD-statistics using Matrix 1D operator
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,calculatedSignals,messages" are "2,2,1" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        Then measurement status is "ACTIVE" within "10" minutes
        When reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "1" minutes
        And Remote measurement is deactivated
        Then measurement status is "INACTIVE" within "10" minutes
        When reference system is stopped
        And measurement test results are stored including "preview_data"
        Then validate "calculated_signal" matrix for the measurement configuration <meas_config_name> in preview data

        Examples:
            | vehicle | device | meas_config_name                                 | can_protocol | can_identifier                 |
            | " "     | "CCU"  | "E2E_CALCULATED_SIGNAL_MATRIX_SUM1D_Automation" | "MONonCAN"   | "MONonCAN_500k_highloadidents" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Data Preprocessing of SUM for nD-statistics using Matrix 2D operator
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,calculatedSignals" are "2,3" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        Then measurement status is "ACTIVE" within "10" minutes
        When reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "1" minutes
        And Remote measurement is deactivated
        Then measurement status is "INACTIVE" within "10" minutes
        When reference system is stopped
        And measurement test results are stored including "preview_data"
        Then validate "calculated_signal" matrix for the measurement configuration <meas_config_name> in preview data


        Examples:
            | vehicle | device | meas_config_name                                 | can_protocol | can_identifier                 |
            | " "     | "CCU"  | "E2E_CALCULATED_SIGNAL_MATRIX_SUM2D_Automation" | "MONonCAN"   | "MONonCAN_500k_highloadidents" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Data Preprocessing of SUM for nD-statistics using Matrix 3D operator
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,calculatedSignals" are "3,2" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        Then measurement status is "ACTIVE" within "10" minutes
        When reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "1" minutes
        And Remote measurement is deactivated
        Then measurement status is "INACTIVE" within "10" minutes
        When reference system is stopped
        And measurement test results are stored including "preview_data"
        Then validate "calculated_signal" matrix for the measurement configuration <meas_config_name> in preview data


        Examples:
            | vehicle | device | meas_config_name                                 | can_protocol | can_identifier                 |
            | " "     | "CCU"  | "E2E_CALCULATED_SIGNAL_MATRIX_SUM3D_Automation" | "MONonCAN"   | "MONonCAN_500k_highloadidents" |


    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Data Preprocessing of SUM for nD-statistics using SUM,COUNT and TIME methods
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals,calculatedSignals,messages" are "4,3,1" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        Then measurement status is "ACTIVE" within "10" minutes
        When reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "1" minutes
        And Remote measurement is deactivated
        Then measurement status is "INACTIVE" within "10" minutes
        When reference system is stopped
        And measurement test results are stored including "preview_data"
        Then validate "calculated_signal" matrix for the measurement configuration <meas_config_name> in preview data


        Examples:
            | vehicle | device | meas_config_name                                         | can_protocol | can_identifier                 |
            | " "     | "CCU"  | "E2E_CALCULATED_SIGNAL_MATRIX_COMBINATION3D_Automation" | "MONonCAN"   | "MONonCAN_500k_highloadidents" |
