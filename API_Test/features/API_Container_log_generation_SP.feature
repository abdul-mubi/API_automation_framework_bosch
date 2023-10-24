Feature:Container log generation
    @E2E-API @E2E-CCU @E2E-FM @E2E-SP @E2E-Regression
    Scenario Outline:FM_CCU_API_HP - Requesting Container Log which is not available inside TCU2
        Given device <device> is "ONLINE"
        When triggering new log file generation for container <container_id>
        Then "0" new log entries are generated for the container

        Examples:
            | device  | container_id|
            | "CCU"   | "tedtitans" |

    @E2E-API @E2E-CCU @E2E-FM @E2E-SP @E2E-Regression
    Scenario Outline:FM_CCU_API_HP - Requesting Container Logs for both available and unavailable containers
        Given device <device> is "ONLINE"
        When triggering new log file generation for container <container_id>
        Then "1" new log entries are generated for the container
        And containers logs are downloaded and stored

        Examples:
            | device  | container_id|
            | "CCU"   | "atos,tedtitans"|

   