Feature:Ad hoc read ECUs
    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression
    Scenario Outline: RD_CCU_API_HP - Ad hoc read ECUs
        Given device <device> is "ONLINE"
        And diagnostic function <diagConfigName> with "test1" having capability "READ_ECU" using "ReadECUsAdhoc_Install.zip" is created, if not present
        And release diagnostic function, if not in RELEASED state
        And diagnostic configuration <diagConfigName> with description "test1" using function <diagConfigName> is created, if not present
        And release diagnostic configuration, if not in RELEASED state
        And map device to the " " if there are no pending diagnostic jobs
        And reference system <Protocol> with Identifier <Identifier> is started
        And deactivate ACTIVE diagnostic configuration if present
        And delete <capability> if present
        When diagnostic configuration <diagConfigName> is activated on vehicle
        And diagnostic configuration state is "ACTIVE" for <capability>
        And trigger adhoc Read All <capability>
        Then adhoc Read All <capability> is generated within "2" minutes
        And deactivate ACTIVE diagnostic configuration if present
        And diagnostic configuration state is "INACTIVE" for <capability>
        Then reference system is stopped
        And verify latest <capability> details

        Examples:
            | vehicle | device | capability | diagConfigName    | Protocol   | Identifier                                |
            | " "     | "CCU"  | "ECU"      | "Read_ECUs_Adhoc" | "UDSonCAN" | "BCM_ECU,ECM_ECU,PS_ECU,TPMS_ECU,VCM_ECU" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression @BV-UC_DTC_GX
    Scenario Outline: RD_CCU_API_HP - Cyclic read of DTCs
        Given device <device> is "ONLINE"
        # And diagnostic function <diagConfigName> with "test1" having capability "READ_DTC" using "activate-fix.zip" is created, if not present
        #And release diagnostic function, if not in RELEASED state
        #And diagnostic configuration <diagConfigName> with description "test1" using function <diagConfigName> is created, if not present
        #And release diagnostic configuration, if not in RELEASED state
        And map device to the <vehicle> if there are no pending diagnostic jobs
        And reference system <Protocol> with Identifier <Identifier> is started
        And deactivate ACTIVE diagnostic configuration if present
        And delete DTC if present
        When diagnostic configuration <diagConfigName> is activated on vehicle
        And diagnostic configuration state is "ACTIVE"
        And DTC is generated for "2" minutes
        And deactivate ACTIVE diagnostic configuration if present
        And diagnostic configuration state is "INACTIVE"
        Then reference system is stopped
        And latest DTC status is verified
            | Status | Code  |
            | AC     | A9B17 |
            | AC     | 80511 |

        Examples:
            | vehicle | device | diagConfigName          | Protocol   | Identifier       |
            | " "     | "CCU"  | "SYS-I-001-job_success" | "UDSonCAN" | "UDS_Resp_2DTCs" |


    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression @BV-UC_DTC_GX
    Scenario Outline: RD_CCU_API_HP - Ad hoc read DTCs of ECU and clear DTCs of ECU
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending diagnostic jobs
        And reference system <Protocol> with Identifier <Identifier> is started
        And deactivate ACTIVE diagnostic configuration if present
        And delete existing DTCs and ECU details for <capability2> if present
        When diagnostic configuration <diagConfigName> is activated on vehicle
        And diagnostic configuration state is "ACTIVE" for <capability>
        And trigger adhoc Read All <capability>
        And adhoc Read All <capability> is generated within "2" minutes
        And test waits for "2" minutes
        Then verify latest <capability> details
        When adhoc <capability2> is triggered for ECU <ECUUnderTest>
        And adhoc <capability2> is generated within "2" minutes
        Then latest DTC status is verified for "ECU"
            | ECU | Status | Code  |
            | BCM | FF     | A9B55 |
            | BCM | FF     | 705A5 |
        When adhoc <capability3> is triggered for ECU <ECUUnderTest>
        And adhoc <capability3> is generated within "2" minutes
        And deactivate ACTIVE diagnostic configuration if present
        And diagnostic configuration state is "INACTIVE" for <capability>
        And reference system is stopped

        Examples:
            | vehicle | device | capability | capability2       | capability3        | diagConfigName | Protocol   | Identifier       | ECUUnderTest |
            | " "     | "CCU"  | "ECU"      | "READ_DTC_OF_ECU" | "CLEAR_DTC_OF_ECU" | "RD_FOR_ECUs"  | "UDSonCAN" | "BCM_ECU,PS_ECU" | "BCM,PS"     |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression @BV-UC_DTC_GX
    Scenario Outline: RD_CCU_API_HP - Ad hoc read DTCs and clear DTCs
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
        And adhoc Read All DTCs is generated within "10" minutes
        Then latest DTC status is verified
            | Status | Code  |
            | AC     | A9C17 |
            | AC     | 80522 |
        When adhoc <capability> is triggered
        And adhoc <capability> is generated within "2" minutes
        And deactivate ACTIVE diagnostic configuration if present
        And diagnostic configuration state is "INACTIVE"
        And reference system is stopped

        Examples:
            | vehicle | device | diagConfigName | Protocol   | Identifier          | capability  |
            | " "     | "CCU"  | "RD_FOR_ECUs"  | "UDSonCAN" | "UDS_Resp_2DTCs_RD" | "CLEAR_DTC" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RD @E2E-Regression @BV-UC_DTC_GX
    Scenario Outline: RD_CCU_API_HP : VRS on/off during diagnostics process
        Given device <device> is "ONLINE"
        And diagnostic function <diagConfigName> with "test1" having capability "READ_DTC" using "activate-fix.zip" is created, if not present
        And diagnostic configuration <diagConfigName> with description "test1" using function <diagConfigName> is created, if not present
        And release diagnostic configuration, if not in RELEASED state
        And map device to the <vehicle> if there are no pending diagnostic jobs
        And reference system <Protocol> with Identifier <Identifier> is started
        And deactivate ACTIVE diagnostic configuration if present
        And delete DTC if present
        When diagnostic configuration <diagConfigName> is activated on vehicle
        And diagnostic configuration state is "ACTIVE"
        And adhoc Read All DTCs is triggered
        And adhoc Read All DTCs is generated within "3" minutes
        And reference system is stopped
        And adhoc Read All DTCs is triggered
        And test waits for "2" minutes
        And "No" newer DTCs are generated
        And deactivate ACTIVE diagnostic configuration if present
        And diagnostic configuration state is "INACTIVE"
        Examples:
            | vehicle | device | diagConfigName          | Protocol   | Identifier          | operation       |
            | " "     | "CCU"  | "SYS-I-001-job_success" | "UDSonCAN" | "UDS_Resp_2DTCs_RD" | "deleteAllJobs" |


