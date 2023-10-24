Feature:Container log generation
    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Regression
    Scenario Outline:FM_CCU_API_HP - Container Log Generation using container id
        Given device <device> is "ONLINE" 
        When triggering new log file generation for container <container_id>
        Then "2" new log entries are generated for the container
        And containers logs are downloaded and stored

        Examples:
            | device  | container_id   |
            | "CCU"   | "atos,trimble" |

    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Regression
    Scenario Outline:FM_CCU_API_HP - Container Log Generation check when CL15 turned [ off - on ] during log generation
        Given device <device> is "ONLINE"
        And switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        When triggering new log file generation for container <container_id> when device is "OFFLINE"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        Then "2" new log entries are generated for the container
        And containers logs are downloaded and stored
        #No changes required as no api ep available for deleting with logTrigger
        And delete generated log files from device log entries

        Examples:
            | device  | container_id   |
            | "CCU"   | "atos,trimble" |

    @E2E-API @E2E-CCU @E2E-FM @E2E-HP @E2E-Regression
    Scenario Outline:FM_CCU_API_HP - Generate Container Log and device log simultaneously
        Given device <device> is "ONLINE" 
        When triggering new log file generation for device <device> and container <container_id>
        Then "3" new log entries are generated for the device and container
        And device and container logs are downloaded and stored

        Examples:
            | device  | container_id   |
            | "CCU"   | "atos,trimble" |