Feature: Reuse calculated signals in other calculated signals
        # comments for this test
        @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-API @E2E-Regression @E2E-CCU
        Scenario Outline: RM_CCU_API_HP - Remote measurement of reused calculated signals

                Given device <device> is "ONLINE"
                And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
                And verify number of "signals,calculatedSignals" are "1,2" respectively is present in measurement configuration <meas_config_name>
                When Remote measurement is activated
                And measurement status is "ACTIVE" within "10" minutes
                And reference system <can_protocol> with Identifier <can_identifier> is started
                And test is executed for "1" minutes
                And Remote measurement is deactivated
                And measurement status is "INACTIVE" within "10" minutes
                And reference system is stopped
                And measurement test results are stored
                Then measurement data integrity test is performed for reused calculated signals

                Examples:
                        |vehicle  |device     |meas_config_name                               |can_protocol   |can_identifier       |
                        |" "      |"CCU"     |"E2E_REUSE_CALCULATED_SIGNALS_01_Automation"  |"CANalization" |"Remote_Measurement_350ms"  |

        @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-API @E2E-Regression @E2E-CCU
        Scenario Outline: RM_CCU_API_HP - Remote measurement of reused calculated signals ignoring the creation order

                Given device <device> is "ONLINE"
                And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
                And verify number of "signals,calculatedSignals" are "1,2" respectively is present in measurement configuration <meas_config_name>
                When Remote measurement is activated
                And measurement status is "ACTIVE" within "10" minutes
                And reference system <can_protocol> with Identifier <can_identifier> is started
                And test is executed for "1" minutes
                And Remote measurement is deactivated
                And measurement status is "INACTIVE" within "10" minutes
                And reference system is stopped
                And measurement test results are stored
                Then measurement data integrity test is performed for reused calculated signals

                Examples:
                        |vehicle  |device     |meas_config_name                               |can_protocol   |can_identifier       |
                        |" "      |"CCU"     |"E2E_REUSE_CALCULATED_SIGNALS_02_Automation"  |"CANalization" |"Remote_Measurement_350ms"  |

        @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-API @E2E-Regression @E2E-CCU
        Scenario Outline: RM_CCU_API_HP - Remote measurement of reused calculated signals when referenced calculated signal is empty

                Given device <device> is "ONLINE"
                And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
                And verify number of "calculatedSignals" are "2" respectively is present in measurement configuration <meas_config_name>
                When Remote measurement is activated
                And measurement status is "ACTIVE" within "10" minutes
                And reference system <can_protocol> with Identifier <can_identifier> is started
                And test is executed for "2" minutes
                And Remote measurement is deactivated
                And measurement status is "INACTIVE" within "10" minutes
                And reference system is stopped
                And measurement test results are stored
                Then measurement data integrity test is performed for reused calculated signals

                Examples:
                        |vehicle  |device     |meas_config_name                               |can_protocol   |can_identifier       |
                        |" "      |"CCU"     |"E2E_REUSE_CALCULATED_SIGNALS_05_Automation"  |"CANalization" |"Remote_Measurement_350ms"  |

        @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-API @E2E-Regression @E2E-CCU
        Scenario Outline: RM_CCU_API_HP - Remote measurement of reused calculated signals when invalid event occurs for referenced calculated signal

                Given device <device> is "ONLINE"
                And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
                And verify number of "calculatedSignals" are "2" respectively is present in measurement configuration <meas_config_name>
                When Remote measurement is activated
                And measurement status is "ACTIVE" within "10" minutes
                And reference system <can_protocol> with Identifier <can_identifier> is started
                And test is executed for "1" minutes
                And Remote measurement is deactivated
                And measurement status is "INACTIVE" within "10" minutes
                And reference system is stopped
                And measurement test results are stored
                Then measurement data integrity test is performed for reused calculated signals

                Examples:
                        |vehicle  |device     |meas_config_name                               |can_protocol   |can_identifier       |
                        |" "      |"CCU"     |"E2E_REUSE_CALCULATED_SIGNALS_06_Automation"  |"CANalization" |"Remote_Measurement_350ms"  |


        
        # reuse of calc signal
        @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-API @E2E-Regression @E2E-CCU
        Scenario Outline: RM_CCU_API_HP - Remote measurement of reuse calculated signals by refrencing 1st and 2nd calcualted signal in 3rd calculated signal 

                Given device <device> is "ONLINE"
                And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
                And verify number of "signals,calculatedSignals" are "1,3" respectively is present in measurement configuration <meas_config_name>
                When Remote measurement is activated
                And measurement status is "ACTIVE" within "10" minutes
                And reference system <can_protocol> with Identifier <can_identifier> is started
                And test is executed for "3" minutes
                And Remote measurement is deactivated
                And measurement status is "INACTIVE" within "10" minutes
                And reference system is stopped
                And measurement test results are stored
                Then measurement data integrity test is performed for reused calculated signals

                Examples:
                        |vehicle  |device     |meas_config_name                               |can_protocol   |can_identifier       |
                        |" "      |"CCU"     |"E2E_REUSE_CALCULATED_SIGNALS_07_Automation"  |"CANalization" |"Remote_Measurement_350ms"  |
