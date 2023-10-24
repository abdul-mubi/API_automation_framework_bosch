Feature:Map and unmap device from slot during measurement 10 iterations
    @E2E-API @E2E-CCU @E2E-ERASE_VIN @E2E-HP @E2E-RM @BV-UC_RemoteMeasurement @E2E-Load
    Scenario Outline:RM_CCU_API_HP - Map and unmap device from slot during measurement 10 iterations
        Given device <device> is "ONLINE"
        And prepare vehicle <vehicle> by clearing all pending jobs
        And verify number of "signals" are "2" respectively is present in measurement configuration <meas_config_name>
        And create device slot <device_slot> for <vehicle> vehicle
        And create measurment configuration <meas_config_name> if it not is available
        And release measurement configuration <meas_config_name>
        When assign remote measurement to <device_slot> of vehicle <vehicle>
        Then perform device mapping and unmaping from device slot "10" times on <vehicle> for remote measurement
        And deactivate remote measurement <meas_config_name> from <device_slot> of vehicle <vehicle>
        And measurement status on vehicle <vehicle> device slot <device_slot> is "INACTIVE" with target status as "INACTIVE"

        Examples:
            | vehicle | device | device_slot | signal_collection      | signal_collection_details | meas_config_name       |
            | " "     | "CCU"  | "CCU1"      | "E2E_CAN_RAW_MON_500K" | "transmissionRate:500000" | "E2E_CAN_RAW_MON_500K" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @BV-UC_DTC_GX @E2E-Load @E2E-ERASE_VIN
    Scenario Outline: RD_CCU_API_HP - Map and unmap device from slot during diagnostics 10 iterations
        Given device <device> is "ONLINE"
        And prepare vehicle <vehicle> by clearing all pending jobs
        And create device slot <device_slot> for <vehicle> vehicle
        When assign diagnostic config <diagConfigName> to <device_slot> of vehicle <vehicle>
        And remote diagnostic configuration state on vehicle <vehicle> is "ASSIGNED"
        Then perform device mapping and unmaping from device slot "10" times on <vehicle> for remote diagnostics
        And deactivate diagnostic assignment on vehicle <vehicle> from "INACTIVE" state
        And verify remote diagnostic configuration on vehicle <vehicle> is removed

        Examples:
            | vehicle               | device | device_slot | diagConfigName          |
            | "INT_Device_Slot_050" | "CCU"  | "CCU1"      | "SYS-I-001-job_success" |