Feature:  Handling of device data
    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression @BV-UC_DTC_GX
    Scenario Outline: RD_CCU_API_HP: Turn on/off CL15 while RD is ongoing
        Given device <device> is "ONLINE"
        And device operation "rebootDevice" is performed
        And wait for device to be "ONLINE"
        And map device to the <vehicle> if there are no pending diagnostic jobs
        And diagnostic function <diagConfigName> with "test1" having capability "READ_DTC" using "activate-fix.zip" is created, if not present
        And release diagnostic function, if not in RELEASED state
        And diagnostic configuration <diagConfigName> with description "test1" using function <diagConfigName> is created, if not present
        And release diagnostic configuration, if not in RELEASED state
        And deactivate ACTIVE diagnostic configuration if present
        And delete DTC if present
        And reference system <Protocol> with Identifier <Identifier> is started
        When diagnostic configuration <diagConfigName> is activated on vehicle
        And diagnostic configuration state is "ACTIVE"
        And switch "CL15" is turned "Off"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And adhoc Read All DTCs is triggered
        And adhoc Read All DTCs is generated within "2" minutes
        And deactivate ACTIVE diagnostic configuration if present
        And diagnostic configuration state is "INACTIVE"
        Then reference system is stopped
        And latest DTC status is verified
            | Status | Code  |
            | AC     | A9C17 |
            | AC     | 80522 |

        Examples:
            | vehicle | device | diagConfigName          | Protocol   | Identifier          | operation       |
            | " "     | "CCU"  | "SYS-I-001-job_success" | "UDSonCAN" | "UDS_Resp_2DTCs_RD" | "deleteAllJobs" |


    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression
    Scenario Outline: Turn on/off CL15 before remote diagnostics has started
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending diagnostic jobs
        And deactivate ACTIVE diagnostic configuration if present
        And delete DTC if present
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        When diagnostic configuration <diagConfigName> is activated on vehicle
        And diagnostic configuration state is "ACTIVATION_PENDING" and sub_status is "IN_ACTIVATION"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And diagnostic configuration state is "ACTIVE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And adhoc Read All DTCs is triggered
        Then adhoc Read All DTCs is generated within "2" minutes
        And deactivate ACTIVE diagnostic configuration if present
        And diagnostic configuration state is "INACTIVE"
        And reference system is stopped
        And latest DTC status is verified
            | Status | Code  |
            | AC     | A9C17 |
            | AC     | 80522 |

        Examples:
            | vehicle | device | diagConfigName          | Protocol   | Identifier          | operation       |
            | " "     | "CCU"  | "SYS-I-001-job_success" | "UDSonCAN" | "UDS_Resp_2DTCs_RD" | "deleteAllJobs" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression
    Scenario Outline: RD_CCU_API_HP - Handling of device data - RD data when CL15 is turned ON/OFF
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending diagnostic jobs
        And reference system <Protocol> with Identifier <Identifier> is started
        And deactivate ACTIVE diagnostic configuration if present
        And delete DTC if present
        When diagnostic configuration <diagConfigName> is activated on vehicle
        And diagnostic configuration state is "ACTIVE"
        And test waits for "2" minutes
        And VRS with protocol <Protocol> and identifier <Identifier> is stopped
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And deactivate ACTIVE diagnostic configuration if present
        And diagnostic configuration state is "DEACTIVATION_PENDING" within "1" minutes
        Then DTC is generated for "1" minutes
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And reference system <Protocol> with Identifier <Identifier> is started
        And test waits for "2" minutes
        And diagnostic configuration state is "INACTIVE"
        Then "No" newer DTCs are generated
        And reference system is stopped

        Examples:
            | vehicle | device | diagConfigName          | Protocol   | Identifier       |
            | " "     | "CCU"  | "SYS-I-001-job_success" | "UDSonCAN" | "UDS_Resp_2DTCs" |


    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression @BV-UC_DTC_GX
    Scenario Outline: RD_CCU_API_HP : Turn on/off the GSM connection when remote diagnostics is ongoing
        Given device <device> is "ONLINE"
        And diagnostic function <diagConfigName> with "test1" having capability "READ_DTC" using "activate-fix.zip" is created, if not present
        And release diagnostic function, if not in RELEASED state
        And diagnostic configuration <diagConfigName> with description "test1" using function <diagConfigName> is created, if not present
        And release diagnostic configuration, if not in RELEASED state
        And map device to the <vehicle> if there are no pending diagnostic jobs
        And reference system <Protocol> with Identifier <Identifier> is started
        And deactivate ACTIVE diagnostic configuration if present
        And delete DTC if present
        When diagnostic configuration <diagConfigName> is activated on vehicle
        And diagnostic configuration state is "ACTIVE"
        And adhoc Read All DTCs is triggered
        And adhoc Read All DTCs is generated within "2" minutes
        And command to "stopGSMConnection" GSM mode of the device
        And wait for device to be "OFFLINE"
        And adhoc Read All DTCs is triggered
        And "No" newer DTCs are generated
        Then reference system is stopped
        And command to "startGSMConnection" GSM mode of the device
        And wait for device to be "ONLINE"
        And deactivate ACTIVE diagnostic configuration if present
        And diagnostic configuration state is "INACTIVE"
        Examples:
            | vehicle | device | diagConfigName          | Protocol   | Identifier          | operation       |
            | " "     | "CCU"  | "SYS-I-001-job_success" | "UDSonCAN" | "UDS_Resp_2DTCs_RD" | "deleteAllJobs" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression @E2E-ERASE_VIN
    Scenario Outline: RD_CCU_API_HP - Handling of device data - RD when changing the VIN of the device to a new vehicle and then back to the original
        Given device <device> is "ONLINE"
        And prepare vehicle <vehicle> by clearing all pending jobs
        And create device slot <device_slot> for <vehicle> vehicle
        When VIN of vehicle <vehicle> is implanted in the device <device>
        Then auto creation of new vehicle is of status "True"
        And deactivate ACTIVE diagnostic configuration if present
        And delete DTC if present
        And the "7"nd reference system <Protocol> with Identifier <Identifier> is started
        And assign diagnostic config <diagConfigName> to <device_slot> of vehicle <vehicle>
        And diagnostic configuration state is "ACTIVE"
        And DTC is generated for "2" minutes
        # And reference system is stopped
        And VIN of vehicle <New_vehicle> is implanted in the device <device>
        And test waits for "2" minutes
        And VIN of vehicle <vehicle> is implanted in the device <device>
        # And reference system <Protocol> with Identifier <Identifier> is started
        And diagnostic configuration state is "ACTIVE"
        Then "No" newer DTCs are generated
        And test waits for "2" minutes
        And newer DTCs are generated
        And deactivate diagnostic assignment on vehicle <vehicle> from "ACTIVE" state
        And reference system is stopped
        And unmap device <device> from vehicle
        And remove device slot from vehicle

        Examples: 
            | vehicle                     | device | New_vehicle                 | device_slot | diagConfigName          | Protocol   | Identifier       | 
            | "AUT15072021130520_Vehicle" | "CCU"  | "AUT15072021130510_Vehicle" | "CCU"       | "SYS-I-001-job_success" | "UDSonCAN" | "UDS_Resp_2DTCs" | 


    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression @E2E-ERASE_VIN
    Scenario Outline: RD_CCU_API_HP - Handling of device data - RD data when GSM is turned ON/OFF and changing the VIN of device
        Given device <device> is "ONLINE"
        And prepare vehicle <vehicle> by clearing all pending jobs
        And create device slot <device_slot> for <vehicle> vehicle
        When VIN of vehicle <vehicle> is implanted in the device <device>
        Then auto creation of new vehicle is of status "True"
        And deactivate ACTIVE diagnostic configuration if present
        And delete DTC if present
        And assign diagnostic config <diagConfigName> to <device_slot> of vehicle <vehicle>
        And the "7"nd reference system <Protocol> with Identifier <Identifier> is started
        And diagnostic configuration state is "ACTIVE"
        And DTC is generated for "2" minutes
        And test waits for "1" minutes
        And command to "stopGSMConnection" GSM mode of the device
        And wait for device to be "OFFLINE"
        And DTC is generated for "1" minutes
        # And reference system is stopped
        And VIN of vehicle <New_vehicle> is implanted in the device <device>
        And command to "startGSMConnection" GSM mode of the device
        And wait for device to be "ONLINE"
        And test waits for "2" minutes
        And VIN of vehicle <vehicle> is implanted in the device <device>
        # And reference system <Protocol> with Identifier <Identifier> is started
        And diagnostic configuration state is "ACTIVE"
        Then "No" newer DTCs are generated
        And test waits for "2" minutes
        And newer DTCs are generated
        And deactivate diagnostic assignment on vehicle <vehicle> from "ACTIVE" state
        And reference system is stopped
        And unmap device <device> from vehicle
        And remove device slot from vehicle

        Examples:
            | vehicle                     | device | New_vehicle                 | device_slot | diagConfigName          | Protocol   | Identifier       |
            | "AUT15072021130515_Vehicle" | "CCU"  | "AUT15072021130513_Vehicle" | "CCU"       | "SYS-I-001-job_success" | "UDSonCAN" | "UDS_Resp_2DTCs" |


    
    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression
    Scenario Outline:RD_CCU_API_HP - Handling of device data - RD data when GSM is turned ON/OFF
    Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending diagnostic jobs
        And reference system <Protocol> with Identifier <Identifier> is started
        And deactivate ACTIVE diagnostic configuration if present
        And delete DTC if present
        When diagnostic configuration <diagConfigName> is activated on vehicle
        And diagnostic configuration state is "ACTIVE"
        And DTC is generated for "2" minutes
        And command to "stopGSMConnection" GSM mode of the device
        And wait for device to be "OFFLINE"
        And test waits for "2" minutes
        And deactivate ACTIVE diagnostic configuration if present
        And diagnostic configuration state is "DEACTIVATION_PENDING" within "1" minutes
        And command to "startGSMConnection" GSM mode of the device
        And wait for device to be "ONLINE"
        And diagnostic configuration state is "INACTIVE"
        Then verify no dtcs are generated after deactivation
        And latest DTC status is verified
            | Status | Code  |
            | AC     | A9B17 |
            | AC     | 80511 |
        And reference system is stopped

        Examples:
            | vehicle | device | diagConfigName          | Protocol   | Identifier       |
            | " "     | "CCU" | "SYS-I-001-job_success" | "UDSonCAN" | "UDS_Resp_2DTCs"  |