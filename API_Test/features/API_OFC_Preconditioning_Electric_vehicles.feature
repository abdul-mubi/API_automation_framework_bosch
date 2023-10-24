Feature: Remote Preconditioning of Electric Vehicles
    @E2E-API @E2E-CCU @E2E-OFC @E2E-HP @E2E-Smoke @E2E-PACCAR @BV-UC_BEV_Preconditioning 
    Scenario Outline:OFC_CCU_API_HP - Trigger function call using short and long config byte and verify the message in CAN
    Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        When reference system <protocol> with Identifier "SM_record_response" is started
        Then check VSC is available for tenant with <property_name>
        And reference system <protocol> with Identifier <can_identifier> is started
        When invoke function call to "vehicle" <action> on <property_name> for <in_arg_value>
        Then check function call status as "SUCCESS"
        When reference system is stopped
        Then verify the message_id and message data in CAN bus for <message_type>

        Examples:
            | vehicle | device | property_name      | action                        |protocol      |in_arg_value              |message_type        | can_identifier |
            | " "     | "CCU"  | "remotesettings"   | "remotesettings_precondition" |"CANalization"|"config:30A1BB2A"         |"short_message_byte"| "VECU_Reply"   |
            | " "     | "CCU"  | "remotesettings"   | "remotesettings_precondition" |"CANalization"|"config:30A1BB2A30A1BB2A" |"long_message_byte" | "VECU_Reply"   |
    

    @E2E-API @E2E-CCU @E2E-OFC @E2E-HP @E2E-Regression @E2E-PACCAR @BV-UC_BEV_Preconditioning
    Scenario Outline:OFC_CCU_API_HP - wake up TCU from VECU and trigger OTA Function call using longer config byte and verify message in CAN bus
    Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        When switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        Then check VSC is available for tenant with <property_name>
        And reference system <protocol> with Identifier <can_identifier> is started
        When invoke function call to "vehicle" <action> on <property_name> for <in_arg_value>
        Then check function call status as "Pending/Delivered"
        When the "2"nd reference system <protocol> with Identifier "SM_record_response" is started
        And reference system <protocol> with Identifier <Identifier> is started
        And wait for device to be "ONLINE"
        Then check function call status as "SUCCESS"
        When reference system is stopped
        Then verify the message_id and message data in CAN bus for <message_type>
        And wait for device to be "OFFLINE"
        And switch "CL15" is turned "ON"
        And wait for device to be "ONLINE"

        Examples:
            | vehicle | device | property_name      | action                        |protocol      |Identifier              |in_arg_value             |message_type       | can_identifier |
            | " "     | "CCU"  | "remotesettings"   | "remotesettings_precondition" |"CANalization"|"Preconditioning_wakeup"|"config:30A1BB2A30A1BB2A"|"long_message_byte"| "VECU_Reply"   |

    @E2E-API @E2E-CCU @E2E-OFC @E2E-SP @E2E-Regression @E2E-PACCAR @BV-UC_BEV_Preconditioning
    Scenario Outline:OFC_CCU_API_SP - Trigger function call using Invalid config values
    Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        When check VSC is available for tenant with <property_name>
        When invoke function call to "vehicle" <action> on <property_name> for <in_arg_value>
        Then check function call status as "FAILURE"

        Examples:
            | vehicle | device | property_name      | action                        |in_arg_value              |
            | " "     | "CCU"  | "remotesettings"   | "remotesettings_precondition" |"config:20A0B32A,30A1BB2A"|
