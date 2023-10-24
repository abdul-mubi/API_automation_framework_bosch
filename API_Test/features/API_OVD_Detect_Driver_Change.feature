Feature: Remote measurement of drived Id

    @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-API @E2E-Regression
    Scenario Outline: Remote measurement of drived Id
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending <meas_config_name> measurement jobs
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        When Remote measurement is activated
        And measurement status is "ACTIVE" within "10" minutes
        And driver with driver_Id drives for <Drive_Time>minutes
            | driver_Id     |
            | No_Driver     |
            | Driver1_Slot1 |
            | Driver1_Slot2 |
            | Two_Drivers   |
        And Remote measurement is deactivated
        And measurement test results are stored
        And measurement status is "INACTIVE" within "10" minutes
        Then verify the drive time difference of driver change
            | driver_Id     |
            | No_Driver     |
            | Driver1_Slot1 |
            | Driver1_Slot2 |
            | Two_Drivers   |

        Examples:
            | vehicle | device | meas_config_name  | Drive_Time |
            | " "     | "CCU" | "Driver_ID_Info"  | "5"        |