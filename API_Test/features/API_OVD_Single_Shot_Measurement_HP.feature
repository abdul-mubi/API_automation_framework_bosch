Feature: Single shot measurement
    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Single shot measurement of CAN raw and J1939
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        #And delete the previous data if it is available
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        When Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And measurement data integrity test is performed

        Examples:
            | vehicle | device | meas_config_name                  | can_protocol   | can_identifier      |
            | " "     | "CCU"  | "E2E_CAN_RAW_MON_500K_SingleShot" | "MONonCAN"     | "MONonCAN_500k_highloadidents"     |
            | " "     | "CCU"  | "E2E_J1939_SingleShot"            | "CANalization" | "J1939_Measurement_200ms" |



    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Smoke
    Scenario Outline: RM_CCU_API_HP - Single shot measurement of CCU Voltage signal
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        #And create measurement configuration <meas_config_name> of type "SINGLE_SHOT" if it is not available
        #And add sources <signal_collection> to <meas_config_name>
        #And add signals "SupplyVoltage:" of source <signal_collection> to measurement configuration <meas_config_name>
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        And release measurement configuration <meas_config_name>
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        When Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And measurement data integrity test is performed

        Examples: 
            | vehicle | device | meas_config_name         | 
            | " "     | "CCU"  | "CCU_Voltage_SingleShot" | 


    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Single shot measurement of CAN raw signal by turning OFF and ON CL15 after activation
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        #And delete the previous data if it is available
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And test is executed for "30" seconds
        And measurement test results are stored
        And reference system is stopped
        And measurement data integrity test is performed
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And test is executed for "2" minutes
        
        #And test is executed for "10" seconds
        When Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        Then measurement test results are stored
        And measurement data integrity test is performed

        Examples:
            | vehicle    | device  | meas_config_name                    | can_protocol    | can_identifier              |
            | " "        | "CCU"   | "E2E_CAN_RAW_MON_500K_SingleShot"   | "MONonCAN"      | "MONonCAN_500k_endurance"   |


    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline: RM_CCU_API_HP - Single shot measurement and Continuous measurement in parallel
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name_continous> measurement jobs
        And device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name_singleshot> measurement jobs
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name_continous>
        #And delete the previous data if it is available
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "30" seconds
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name_singleshot>
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        Then Remote measurement <meas_config_name_continous> is deactivated
        And measurement status for configuration <meas_config_name_continous> is "INACTIVE" within "10" minutes
        Then Remote measurement <meas_config_name_singleshot> is deactivated
        And measurement status for configuration <meas_config_name_singleshot> is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And measurement data integrity test is performed
        And reference system is stopped


        Examples:
            | vehicle | device | meas_config_name_singleshot               | meas_config_name_continous | can_protocol   | can_identifier       |
            | " "     | "CCU"  | "E2E_CAN_RAW_MON_500K_SingleShot_Timeout" | "E2E_CAN_RAW_MON_500K"     | "CANalization" | "Remote_Measurement_350ms" |



    @E2E-API @E2E-CCU @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Regression
    Scenario Outline:RM_CCU_API_HP - Single shot measurement with custom timeout
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        #And delete the previous data if it is available
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "5" minutes
        And test is executed for "2" seconds
        And reference system <can_protocol> with Identifier <can_identifier> is started
        And test is executed for "10" seconds
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        And measurement data integrity test is performed
        And VRS with protocol <can_protocol> and identifier <can_identifier> is stopped

        When Remote measurement is activated
        And measurement status is "ACTIVE" within "5" minutes
        And test is executed for "70" seconds
        And reference system <can_protocol> with Identifier <can_identifier> is started
        Then Remote measurement is deactivated
        And measurement status is "INACTIVE" within "10" minutes
        And measurement test results are stored
        Then measurement test result for latest step is "not available"
        And reference system is stopped


        Examples:
            | vehicle | device | meas_config_name                                 | can_protocol | can_identifier                 |
            | " "     | "CCU"  | "E2E_CAN_RAW_MON_500K_SingleShot_Custom_Timeout" | "MONonCAN"   | "MONonCAN_500k_highloadidents" |
