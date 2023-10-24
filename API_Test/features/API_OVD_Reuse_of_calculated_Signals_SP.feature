Feature: Reuse calculated signals in other calculated signals

    @E2E-SP @E2E-RM @BV-UC_RemoteMeasurement @E2E-API @E2E-Regression @E2E-CCU
    Scenario Outline: RM_CCU_API_SP - Invalid reuse of calculated signals referring itself in a closed loop

        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        When add calculated signals <calculated_signals> with invalid formula <formula> respectively to measurement configuration <meas_config_name>
        Then verify that invalid calculated signal is "True" in measurement configuration <meas_config_name>
        And Verify Measurement job <meas_config_name> can be set to "Release" state returns "Failure"
    
Examples:
        |vehicle  |device    |meas_config_name                               | calculated_signals                       |formula                                              |    
        |" "      |"CCU"     |"E2E_REUSE_CALCULATED_SIGNALS_03_Automation"   |"Calculated_signal_1:,Calculated_Signal_2:"|"Addcalsignal2andconstant,Addcalsignal1andconstant"|

    @E2E-SP @E2E-RM @BV-UC_RemoteMeasurement @E2E-API @E2E-Regression @E2E-CCU
    Scenario Outline: RM_CCU_API_SP - Invalid reuse of calculated signal with a non scalar value

        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "1" respectively is present in measurement configuration <meas_config_name>
        When add calculated signals <calculated_signals> with invalid formula <formula> respectively to measurement configuration <meas_config_name>
        Then verify that invalid calculated signal is "True" in measurement configuration <meas_config_name>
        And Verify Measurement job <meas_config_name> can be set to "Release" state returns "Failure"
    
Examples:
        |vehicle  |device     |meas_config_name                               | calculated_signals     |formula                 |    
        |" "      |"CCU"      |"E2E_REUSE_CALCULATED_SIGNALS_04_Automation"  |"Calculated_Signal_2:"  |"Addscalarandconstant"  |
