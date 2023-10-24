Feature: Undispatch device to target space and dispatch it back again

@E2E-API @E2E-CCU @E2E-HP @E2E-OnRequest @E2E-Team_BEts
Scenario Outline:DP_CCU_API_HP - Undispatching of device from targetspace

        Given device <device> is "ONLINE"
        And verify the provisioning status "REGISTERED" in target space
        And remove paired vehicle
        And undispatch device in targetspace
        And test waits for "1" minutes
        And verify the provisioning status "UNDISPATCHED" in target space
        When switch to "device-provisioning"
        And verify the device provisioning state "UNDISPATCHED" in provisioning space
        And dispatch device to <targetspace> in provisioning space
        And test waits for "1" minutes
        And verify the device provisioning state "DISPATCHED" in provisioning space
        And switch to <targetspace>
        And verify the provisioning status "REGISTERED" in target space
        And wait for device to be "OFFLINE"
        Then switch "CL15" is turned "Off"
        And test waits for "1" minutes
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"

        Examples:
                | device |  targetspace |  
                | "CCU" |      " "      |
