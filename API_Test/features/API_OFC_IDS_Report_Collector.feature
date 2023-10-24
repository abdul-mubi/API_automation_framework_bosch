Feature:IDS report collector
    @E2E-API @E2E-CCU @E2E-OFC @E2E-HP @E2E-Regression @F-UC_IDS @E2E-PACCAR
    Scenario Outline:OFC_CCU_API_HP - Install IDS Report Collector Job and Verify Result
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending diagnostic jobs
        And device log count is fetched
        And check VSC is available for tenant with <property_name>
        When diagnostic configuration <diagConfigName> is activated on vehicle
        Then diagnostic configuration state is "ACTIVE" for <capability>
        When invoke function call to "vehicle" for <action> on <property_name>
        Then check function call status as "SUCCESS"
        And verify artifactUrl for IDS Report function call
        When new log entry is generated for the device
        And device logs are downloaded and stored
        Then verify the IDS report log file  
        When deactivate diagnostic assignment on vehicle <vehicle> from "ACTIVE" state
        Then diagnostic configuration state is "INACTIVE" for <capability>


        Examples:
            | vehicle | device | diagConfigName  | capability        | property_name | action         |
            | " "     | "CCU"  | "TT_IDS_Report" | "REMOTE_FUNCTION" | "security"    | "ids_csg_logs" |


    @E2E-API @E2E-CCU @E2E-OFC @E2E-HP @E2E-Regression @F-UC_IDS @E2E-PACCAR
    Scenario Outline:OFC_CCU_API_HP - Trigger OFC when Device is Turned Off with CL15
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending diagnostic jobs
        And check VSC is available for tenant with <property_name>
        When diagnostic configuration <diagConfigName> is activated on vehicle
        Then diagnostic configuration state is "ACTIVE" for <capability>
        When switch "CL15" is turned "Off"
        Then wait for device to be "OFFLINE"
        When invoke function call to "vehicle" for <action> on <property_name>
        Then check function call status as "Pending/Delivered"
        When switch "CL15" is turned "On"
        Then wait for device to be "ONLINE"
        And check function call status as "SUCCESS"
        And verify artifactUrl for IDS Report function call
        When invoke function call to "vehicle" for <action> on <property_name>
        Then check function call status as "SUCCESS"
        And verify artifactUrl for IDS Report function call
        When deactivate diagnostic assignment on vehicle <vehicle> from "ACTIVE" state
        Then diagnostic configuration state is "INACTIVE" for <capability>


        Examples:
            | vehicle | device | diagConfigName  | capability        | property_name | action         |
            | " "     | "CCU"  | "TT_IDS_Report" | "REMOTE_FUNCTION" | "security"    | "ids_csg_logs" |


    @E2E-API @E2E-CCU @E2E-OFC @E2E-HP @E2E-Regression @F-UC_IDS @E2E-PACCAR
    Scenario Outline:OFC_CCU_API_HP - GSM Disconnection during IDS Report generation
        Given device <device> is "ONLINE"
        And map device to the <vehicle> if there are no pending diagnostic jobs
        And check VSC is available for tenant with <property_name>
        When diagnostic configuration <diagConfigName> is activated on vehicle
        Then diagnostic configuration state is "ACTIVE" for <capability>
        When invoke function call to "vehicle" for <action> on <property_name>
        And test is executed for "2" seconds
        When command to "stopGSMConnection" GSM mode of the device
        Then wait for device to be "OFFLINE"
        And check function call status as "Delivered"
        And test is executed for "5" minutes
        When command to "startGSMConnection" GSM mode of the device
        Then wait for device to be "ONLINE"  
        Then check function call status as "SUCCESS"
        And verify artifactUrl for IDS Report function call
        When deactivate diagnostic assignment on vehicle <vehicle> from "ACTIVE" state
        Then diagnostic configuration state is "INACTIVE" for <capability>

        Examples:
            | vehicle | device | diagConfigName  | capability        | property_name | action         |
            | " "     | "CCU"  | "TT_IDS_Report" | "REMOTE_FUNCTION" | "security"    | "ids_csg_logs" |


    @E2E-API @E2E-CCU @E2E-OFC @E2E-HP @E2E-Regression @F-UC_IDS @E2E-PACCAR
    Scenario Outline:OFC_CCU_API_HP - Install IDS Report Collector via OTA Update Service and Verify Result
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And check VSC is available for tenant with <property_name>  
        And check OTA update DP <distribution_packages> is available
        When <First> OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        Then flashing status of <First> OTA assignment is changed to "UPDATE_SUCCESS" within "120" seconds
        When invoke function call to "vin" for <action> on <property_name>
        Then check function call status as "SUCCESS"
        And verify artifactUrl for IDS Report function call
        When <Second> OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        Then flashing status of <Second> OTA assignment is changed to "UPDATE_SUCCESS" within "120" seconds
        When invoke function call to "vin" for <action> on <property_name>
        Then check function call status as "FAILURE"


        Examples:
            | vehicle | device | distribution_packages               | property_name | action         | First | Second |
            | " "     | "CCU"  | "TT_IDS_Latest,TT_IDS_Latest_Delete"|  "security"   | "ids_csg_logs" | 1     | 2      |

