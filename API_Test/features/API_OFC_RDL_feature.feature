Feature:Configure Vehicle-specific Device Settings on API

    Feature:Configure Vehicle-specific Device Settings on API
    @E2E-API @E2E-CCU @E2E-OFC @E2E-HP @E2E-Regression @BV-UC_Tachofresh @E2E-PACCAR
    Scenario Outline:OFC_CCU_API_HP - Function call to get current status enabling and disabling the RDL property
        Given device <device> is "ONLINE"
        And check VSC is available for tenant with <property_name>
        When invoke function call to "device" for "enable" on <property_name>
        Then check function call status as "SUCCESS"
        And verify Remote Tacho download status to be "enabled"
        When invoke function call to "device" for "disable" on <property_name>
        Then check function call status as "SUCCESS"
        And verify Remote Tacho download status to be "disabled"

        Examples:
            | device  |   property_name            |
            | "CCU"   |  "remote_tacho_download"   |

    @E2E-API @E2E-CCU @E2E-OFC @E2E-HP @E2E-Regression @BV-UC_Tachofresh @E2E-PACCAR
    Scenario Outline:OFC_CCU_API_HP - Function call to re-enable RDL property when its enabled
        Given device <device> is "ONLINE"
        And check VSC is available for tenant with <property_name>
        When invoke function call to "device" for "enable" on <property_name>
        Then check function call status as "SUCCESS"
        And verify Remote Tacho download status to be "enabled"
        When invoke function call to "device" for "enable" on <property_name>
        Then check function call status as "SUCCESS"
        And verify Remote Tacho download status to be "enabled"

        Examples:
            | device  |   property_name            |
            | "CCU"   |  "remote_tacho_download"   |

    @E2E-API @E2E-CCU @E2E-OFC @E2E-HP @E2E-Regression @BV-UC_Tachofresh @E2E-PACCAR
    Scenario Outline:OFC_CCU_API_HP - Function call to enable RDL property when cl15 is off
        Given device <device> is "ONLINE"
        And check VSC is available for tenant with <property_name>
        When switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And invoke function call to "device" for "enable" on <property_name>
        And check function call status as "Pending/Delivered"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        Then check function call status as "SUCCESS"
        And verify Remote Tacho download status to be "enabled"

        Examples:
            | device  |   property_name            |
            | "CCU"   |  "remote_tacho_download"   |

    @E2E-API @E2E-CCU @E2E-OFC @E2E-HP @E2E-Regression @BV-UC_Tachofresh @E2E-PACCAR
    Scenario Outline:OFC_CCU_API_HP - Multipe Function call for RDL property when cl15 is off
        Given device <device> is "ONLINE"
        And check VSC is available for tenant with <property_name>
        When switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And invoke function call to "device" for "enable" on <property_name>
        And invoke function call to "device" for "disable" on <property_name>
        And check function call status as "PENDING"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        Then check function call status as "SUCCESS"
        And verify Remote Tacho download status to be "disabled"
        Examples:
            | device  |   property_name            |
            | "CCU"   |  "remote_tacho_download"   |

    @E2E-API @E2E-CCU @E2E-OFC @E2E-SP @E2E-Regression @BV-UC_Tachofresh @E2E-PACCAR
    Scenario Outline:OFC_CCU_API_HP - Function call to enable property which is not present in device
        Given device <device> is "ONLINE"
        And check VSC is available for tenant with <property_name>
        When invoke function call to "device" for "enable" on <property_name>
        Then check function call status as "FAILURE"

        Examples:
            | device  |   property_name      |
            | "CCU"   |  "remote_download"   |