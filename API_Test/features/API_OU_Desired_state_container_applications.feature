Feature: Desired state for container application
    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX
    Scenario Outline:DS_TCU2_API_HP - Desired state update of container applications
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>    
        And check desired state package <desired_state_package> is available, create if not present
        And desired package is assigned to vehicle <vehicle>
        And desired state package assignment is changed to <status> with sub status <sub_status> within "300" seconds
        When desired state assignment message changed to <message> 
        Then switch "CL15" is turned "Off"
        And wait for device to be "OFFLINE"
        And switch "CL15" is turned "On"
        And wait for device to be "ONLINE"
        And desired state package assignment is changed to <final_status> with sub status <final_sub_status> within "120" seconds
        And triggering new log file generation for container <container_id>
        And "2" new log entries are generated for the container
        And containers logs are downloaded and stored

        Examples:
            | vehicle | device | desired_state_package              | status   |sub_status                                                 | message          |final_status   | final_sub_status                                     | container_id  |                                   
            | " "     | "CCU"  | "Desired_state_update_to_version_1"| "RUNNING"|{"trimble":"DOWNLOAD_SUCCESS","atos":"DOWNLOAD_SUCCESS"}   | "Pending reboot" |"COMPLETED"    |{"trimble":"UPDATE_SUCCESS", "atos":"UPDATE_SUCCESS"} |"atos,trimble" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX
    Scenario Outline:DS_TCU2_API_SP - Desired state update of wrong container application
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>    
        And check desired state package <desired_state_package> is available, create if not present
        When desired package is assigned to vehicle <vehicle>
        Then desired state package assignment is changed to <status> with sub status <sub_status> within "300" seconds
        
        Examples:
            | vehicle | device | desired_state_package                          | Status   |sub_status                      |                                   
            | " "     | "CCU"  | "invalid_container_application_update"         | "FAILED" |{"internet_check":"IDENTIFIED_FAILED"}   |
            | " "     | "CCU"  | "invalid_container_application_version_update" | "FAILED" |{"trimble":"DOWNLOAD_FAILED"}   |
