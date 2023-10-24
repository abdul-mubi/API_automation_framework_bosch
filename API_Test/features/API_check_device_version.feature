Feature:Check device FW version
        @E2E-API @E2E-CCU @E2E-HP @E2E-RF
        Scenario Outline:SU_CCU_API_HP: - Check and update device if version is not as expected
        Given device operation "deleteDeviceLogs" is performed on "ALL" device
        And device operation "deleteAllJobs" is performed on "ALL" device 
        And Check <device> FW version to update device if version is not as expected
        Examples:
            | device|device2|
            | "CCU" |"CCU2" |
 #device2 is not being used in this feature file but it is required to update 2nd deivce in our setup