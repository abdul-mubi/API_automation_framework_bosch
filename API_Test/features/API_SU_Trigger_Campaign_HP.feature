Feature:Trigger campaign on devices using static vehicle list
        @E2E-API @E2E-CCU @E2E-HP @E2E-Installation @F-UC_Self_Update
        Scenario Outline:SU_CM_CCU_API_HP - Campaign for Self-update with CTP distribution package as content
        Given device <device> is "ONLINE"
        When map device to the vehicle <vehicle1>
        And device <device2> is "ONLINE"
        And map device to the vehicle <vehicle2>
        And a new campaign <Campaign_Detail> is "add"ed
        Then campaign status "CREATED" is verified
        When content <package> is added to the Campaign
        And vehicles are added to the Campaign using static list
        And campaign is "schedule"ed
        Then campaign status "RUNNING" is verified
        And flashing assignment status "UPDATING" is verified for the vehicles within "600" seconds
        And wait for self update of device <devices> to complete
        And device <device> is "ONLINE"
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And device <device2> is "ONLINE"
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        Then flashing assignment status "UPDATE_SUCCESS" is verified for the vehicles within "600" seconds
        Then device FW version is verified
        And campaign status "FINISHED" is verified
        #And campaign statistics are verified as per campaign <Campaign_Detail>

        Examples:
            | vehicle1            | device | vehicle2            | device2 |devices    | Campaign_Detail        | package            |
            | "Campaign_Test_001" | "CCU"  | "Campaign_Test_002" | "CCU2"  |"CCU,CCU2" | "campaign_self_update" | "downgrade_delta"  |
            | "Campaign_Test_001" | "CCU"  | "Campaign_Test_002" | "CCU2"  |"CCU,CCU2" | "campaign_self_update" | "upgrade_delta"  |
