Feature: Campaign HP API test
    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CM_CCU_API_HP - Campaign with static vehicle list with maximum parallel job set to 1
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        When a new campaign <Campaign_Detail> is "add"ed
        And campaign status "CREATED" is verified
        And content <content_DP> is added to the Campaign
        And vehicles are added to the Campaign using static list
        And verify that "1" vehicles should be listed for the campaign
        And campaign is "schedule"ed
        And campaign status "RUNNING" is verified
        Then flashing is verified for the vehicles in Campaign using <Fota> and <Fota_Identifier> as per maximum parallel job configuration
        And campaign status "FINISHED" is verified

	    Examples: 
		    | vehicle | device | Campaign_Detail             | content_DP                       | Protocol   |Identifier     |Identifier1      | Fota_Identifier        | Fota           | 
		    | " "      | "CCU"  | "campaignWithMaxParallel_1" | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN" |"DemoFlashSim" |"DemoFlashSim_1" | "DriverApp_Break_True" | "CANalization" | 


    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CM_CCU_API_HP - Campaign with dynamic vehicle list by adding new vehicle after campaign is running
        Given device <device> is "ONLINE"
        When a vehicle <vehicle> using Manufacturer <Manufacturer> and Model <Model> is created with VIN "AUT20210701124621"
        And map "newly" created vehicle <vehicle> to the device
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        And a new campaign <Campaign_Detail> is "add"ed
        Then campaign status "CREATED" is verified
        When content <content_DP> is added to the Campaign
        And vehicles are added to the Campaign using dynamic filter <vehicle_filter>
        Then verify that "1" vehicles should be listed for the campaign
        When campaign is "schedule"ed
        Then campaign status "RUNNING" is verified
        #When a vehicle <vehicle2> using Manufacturer <Manufacturer> and Model <Model> is created
        #And device <device2> is "ONLINE"
        #And map "newly" created vehicle <vehicle2> to the device
        #Then verify that "2" vehicles should be listed for the campaign
        #When reference system <Protocol> with Identifier <Identifier2> is started
        And flashing assignment status "WAITING_FOR_UPDATE_CONDITION" is verified for the vehicles within "600" seconds
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier> for "Campaign" process
        And flashing assignment completing with "UPDATE_SUCCESS" is verified for the vehicles within "600" seconds
        When campaign is "finish"ed
        Then campaign status "FINISHED" is verified

        Examples:
            | vehicle                | device | Manufacturer | Model    | Campaign_Detail     | vehicle_filter       | content_DP                      | Protocol   |Identifier     | Identifier1      | Fota_Identifier        | Fota           |
            | "E2E_CampaignAuto_001" | "CCU"  | "Maserati"   | "Ghibli" | "vehicleDynamicAdd" | "Model_Manufacturer" | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" |"DriverApp_Break_True" | "CANalization" |
       
    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CM_CCU_API_HP - Campaign with dynamic vehicle list by adding new vehicle after campaign is ready
        Given device <device> is "ONLINE"
        When a vehicle <vehicle> using Manufacturer <Manufacturer> and Model <Model> is created with VIN "AUT20210701124621"
        And map "newly" created vehicle <vehicle> to the device
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        And a new campaign <Campaign_Detail> is "add"ed
        Then campaign status "CREATED" is verified
        When content <content_DP> is added to the Campaign
        And vehicles are added to the Campaign using dynamic filter <vehicle_filter>
        Then verify that "1" vehicles should be listed for the campaign
        #When a vehicle <vehicle2> using Manufacturer <Manufacturer> and Model <Model> is created
        #And device <device2> is "ONLINE"
        #And map "newly" created vehicle <vehicle2> to the device
        #And reference system <Protocol> with Identifier <Identifier2> is started
        #Then verify that "2" vehicles should be listed for the campaign
        And campaign is "schedule"ed
        Then campaign status "RUNNING" is verified
        And flashing assignment status "WAITING_FOR_UPDATE_CONDITION" is verified for the vehicles within "600" seconds
        When trigger flashing using protocol <Fota> Identifier <Fota_Identifier> for "Campaign" process
        And flashing assignment completing with "UPDATE_SUCCESS" is verified for the vehicles within "600" seconds
        And campaign is "finish"ed
        Then campaign status "FINISHED" is verified
        And campaign statistics are verified as per campaign <Campaign_Detail>

        Examples:
            | vehicle               | device | Manufacturer | Model    | Campaign_Detail     | content_DP                      | vehicle_filter       | Protocol   | Identifier     |Identifier1       | Fota_Identifier        | Fota           |
            | "E2E_CampaignAuto_001" | "CCU"  | "Maserati"   | "Ghibli" | "vehicleDynamicAdd" | "E2E_RF_Standard_Job_encrypted" | "Model_Manufacturer" | "UDSonCAN" | "DemoFlashSim" |"DemoFlashSim_1"  | "DriverApp_Break_True" | "CANalization" |
        

    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CM_CCU_API_HP - Campaign with dynamic vehicle list
        Given device <device> is "ONLINE"
        When a vehicle <vehicle> using Manufacturer <Manufacturer> and Model <Model> is created with VIN "AUT20210701124621"
        And map "newly" created vehicle <vehicle> to the device
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        And a new campaign <Campaign_Detail> is "add"ed
        Then campaign status "CREATED" is verified
        When content <content_DP> is added to the Campaign
        And vehicles are added to the Campaign using dynamic filter <vehicle_filter>
        Then verify that "1" vehicles should be listed for the campaign
        And campaign is "schedule"ed
        Then campaign status "RUNNING" is verified
        And flashing assignment status "WAITING_FOR_UPDATE_CONDITION" is verified for the vehicles within "300" seconds
        When trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        And flashing assignment completing with "UPDATE_SUCCESS" is verified for the vehicles within "300" seconds
        Then campaign status "FINISHED" is verified
        And campaign statistics are verified as per campaign <Campaign_Detail>

	    Examples: 
		    | vehicle                | device | Manufacturer | Model    | Campaign_Detail        | vehicle_filter       | content_DP                       | Protocol   |Identifier      | Identifier1    | Fota_Identifier        | Fota           | 
		    | "E2E_CampaignAuto_001" | "CCU"  | "Maserati"   | "Ghibli" | "vehicleDynamicFilter" | "Model_Manufacturer" | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN"  | "DemoFlashSim" |"DemoFlashSim_1"| "DriverApp_Break_True" | "CANalization" |


    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CM_CCU_API_HP - Campaign with specifically scheduled Start/End Campaign time
        Given device <device> is "ONLINE"
        When map device to the vehicle <vehicle1>
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        And a new campaign <Campaign_Detail> is "add"ed
        Then campaign status "CREATED" is verified
        When a existing campaign is "edit"ed with <Campaign_Detail>
        When content <content_DP> is added to the Campaign
        And vehicles are added to the Campaign using static list
        And campaign is "schedule"ed
        Then campaign status "RUNNING" is verified after scheduled duration
        And flashing assignment status "WAITING_FOR_UPDATE_CONDITION" is verified for the vehicles within "300" seconds
        When trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        And flashing assignment completing with "UPDATE_SUCCESS" is verified for the vehicles within "300" seconds
        Then campaign status "FINISHED" is verified after scheduled duration
        And campaign statistics are verified as per campaign <Campaign_Detail>

	    Examples: 
		    | vehicle1 | device | Campaign_Detail        | content_DP                      | Protocol   | Identifier    |Identifier1      | Fota_Identifier        | Fota           | 
		    | " "      | "CCU"  | "campaignWithSchedule" | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN" |"DemoFlashSim" |"DemoFlashSim_1" | "DriverApp_Break_True" | "CANalization" | 
       
    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Smoke
    Scenario Outline:RF_CM_CCU_API_HP - Campaign using Static vehicle list
        Given device <device> is "ONLINE"
        When map device to the vehicle <vehicle1>
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        And a new campaign <Campaign_Detail> is "add"ed
        Then campaign status "CREATED" is verified
        When content <content_DP> is added to the Campaign
        And vehicles are added to the Campaign using static list
        And campaign is "schedule"ed
        Then campaign status "RUNNING" is verified
        And flashing assignment status "WAITING_FOR_UPDATE_CONDITION" is verified for the vehicles within "600" seconds
        When trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        Then flashing assignment completing with "UPDATE_SUCCESS" is verified for the vehicles within "600" seconds
        And campaign status "FINISHED" is verified
        And campaign statistics are verified as per campaign <Campaign_Detail>

        Examples: 
            | vehicle1 | device | Campaign_Detail      | content_DP                      | Protocol   | Identifier   | Identifier1       | Fota_Identifier        | Fota           | 
            | " "      | "CCU"  | "campaign_with_name" | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN" |"DemoFlashSim"| "DemoFlashSim_1"  | "DriverApp_Break_True" | "CANalization" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CM_CCU_API_HP - Campaigns creation with backend approval
        Given device <device> is "ONLINE"
        And a vehicle <vehicle> using Manufacturer <Manufacturer> and Model <Model> is created with VIN "AUT20210701124621"
        And map "newly" created vehicle <vehicle> to the device
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        #And device <device2> is "ONLINE"
        #And a vehicle <vehicle2> using Manufacturer <Manufacturer> and Model <Model> is created
        #And map "newly" created vehicle <vehicle2> to the device
        #And reference system <Protocol> with Identifier <Identifier2> is started
        And a new campaign <Campaign_Detail_Backend_Approval> is "add"ed
        And campaign status "CREATED" is verified
        And content <content_DP> is added to the Campaign
        And vehicles are added to the Campaign using dynamic filter <vehicle_filter>
        And verify that "1" vehicles should be listed for the campaign
        When campaign is "schedule"ed
        And campaign status "RUNNING" is verified
        And flashing assignment status "WAITING_FOR_BACKEND_SIGNOFF" is verified for the vehicles within "100" seconds
        And the assignment in pending "Backend Approval" is "Approved"
        And flashing assignment status "WAITING_FOR_UPDATE_CONDITION" is verified for the vehicles within "600" seconds
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier> for "Campaign" process
        And flashing assignment completing with "UPDATE_SUCCESS" is verified for the vehicles within "600" seconds
        Then campaign status "FINISHED" is verified
        And campaign statistics are verified as per campaign <Campaign_Detail_Backend_Approval>

        Examples:
            | vehicle                | device | Manufacturer | Model    | Campaign_Detail_Backend_Approval | vehicle_filter       | content_DP                      | Protocol   | Identifier     | Identifier1      | Fota_Identifier        | Fota           |
            | "E2E_CampaignAuto_001" | "CCU"  | "Maserati"   | "Ghibli" | "campaign_with_backend_approval" | "Model_Manufacturer" | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | "DriverApp_Break_True" | "CANalization" |
       

    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CM_CCU_API_HP - Trigger CM with backend approval while RF on-going on same vehicle
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        And check ECU flashing DP <distribution_package> is available  
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "300" seconds
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        And flashing status of OTA package is changed to "UPDATING" within "300" seconds
        And a new campaign <Campaign_Detail_Backend_Approval> is "add"ed
        Then campaign status "CREATED" is verified
        When content <content_DP> is added to the Campaign
        And vehicles are added to the Campaign using static list
        And campaign is "schedule"ed
        Then campaign status "RUNNING" is verified
        And flashing assignment status "WAITING_FOR_BACKEND_SIGNOFF" is verified for the vehicles within "100" seconds
        And the assignment in pending "Backend Approval" is "Approved"
        And flashing assignment status "WAITING_FOR_UPDATE_CONDITION" is verified for the vehicles within "600" seconds
        Then flashing status of OTA package is changed to "UPDATE_SUCCESS" within "120" seconds
        And reference system with protocol <Fota> and Identifier <Fota_Identifier> and number "0" is stopped
        And test waits for "1" minutes
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        Then flashing assignment completing with "UPDATE_SUCCESS" is verified for the vehicles within "300" seconds
        Then campaign status "FINISHED" is verified
        And campaign statistics are verified as per campaign <Campaign_Detail_Backend_Approval>

        Examples:
            | vehicle | device | Campaign_Detail_Backend_Approval | distribution_package            |content_DP                       | Protocol   | Identifier     | Identifier1      |Fota_Identifier        | Fota           |
            | " "     | "CCU"  | "campaign_with_backend_approval" | "E2E_RF_Standard_Job_encrypted" |"E2E_RF_Standard_Job_encrypted"  | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" |"DriverApp_Break_True" | "CANalization" |


    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CM_CCU_API_HP - Reject CM with backend approval
        Given device <device> is "ONLINE"
        When a vehicle <vehicle> using Manufacturer <Manufacturer> and Model <Model> is created with VIN "AUT20210701124621"
        And map "newly" created vehicle <vehicle> to the device
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        And a new campaign <Campaign_Detail_Backend_Approval> is "add"ed
        Then campaign status "CREATED" is verified
        When content <content_DP> is added to the Campaign
        And vehicles are added to the Campaign using dynamic filter <vehicle_filter>
        Then verify that "1" vehicles should be listed for the campaign
        And campaign is "schedule"ed
        Then campaign status "RUNNING" is verified
        And flashing assignment status "WAITING_FOR_BACKEND_SIGNOFF" is verified for the vehicles within "100" seconds
        And the assignment in pending "Backend Approval" is "Rejected"
        And flashing assignment status "UPDATE_REJECTED" is verified for the vehicles within "100" seconds
        Then campaign status "FINISHED" is verified
        And campaign statistics are verified as per campaign <Campaign_Detail_Backend_Approval>

        Examples:
            | vehicle                | device | Manufacturer | Model    | Campaign_Detail_Backend_Approval        | vehicle_filter       | content_DP                      | Protocol   | Identifier     | Identifier1      |
            | "E2E_CampaignAuto_001" | "CCU"  | "Maserati"   | "Ghibli" | "reject_campaign_with_backend_approval" | "Model_Manufacturer" | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" |
        
    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CM_CCU_API_HP - RF and CM with backend approval on same vehicle
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        And check ECU flashing DP <distribution_package> is available  
        And OTA package is assigned to device <device> with status "UPDATE_ASSIGNED"
        And flashing status of OTA package is changed to "WAITING_FOR_UPDATE_CONDITION" within "300" seconds
        And a new campaign <Campaign_Detail_Backend_Approval> is "add"ed
        Then campaign status "CREATED" is verified
        When content <content_DP> is added to the Campaign
        And vehicles are added to the Campaign using static list
        And campaign is "schedule"ed
        Then campaign status "RUNNING" is verified
        And flashing assignment status "WAITING_FOR_BACKEND_SIGNOFF" is verified for the vehicles within "100" seconds
        And the assignment in pending "Backend Approval" is "Approved"
        And flashing assignment status "WAITING_FOR_UPDATE_CONDITION" is verified for the vehicles within "300" seconds
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        Then flashing status of OTA package is changed to "UPDATE_SUCCESS" within "600" seconds
        And flashing assignment completing with "UPDATE_SUCCESS" is verified for the vehicles within "300" seconds
        Then campaign status "FINISHED" is verified
        And campaign statistics are verified as per campaign <Campaign_Detail_Backend_Approval>

        Examples:
            | vehicle | device | Campaign_Detail_Backend_Approval | distribution_package            |content_DP           | Protocol   | Identifier     | Identifier1   |Fota_Identifier        | Fota           |
            | " "     | "CCU"  | "campaign_with_backend_approval" | "E2E_RF_Standard_Job_encrypted" |"RF_Campaign_DP"  | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" |"DriverApp_Break_True" | "CANalization" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CM_CCU_API_HP - Finish campaign with backend approval before campaign is completed
        Given device <device> is "ONLINE"
        And a vehicle <vehicle> using Manufacturer <Manufacturer> and Model <Model> is created with VIN "AUT20210701124621"
        And map "newly" created vehicle <vehicle> to the device
        And a new campaign <Campaign_Detail_Backend_Approval_1> is "add"ed
        And campaign status "CREATED" is verified
        And content <content_DP> is added to the Campaign
        And vehicles are added to the Campaign using dynamic filter <vehicle_filter>
        And verify that "1" vehicles should be listed for the campaign
        When campaign is "schedule"ed
        And campaign status "RUNNING" is verified
        And flashing assignment status "WAITING_FOR_BACKEND_SIGNOFF" is verified for the vehicles within "100" seconds
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        And the assignment in pending "Backend Approval" is "Approved"
        And flashing assignment status "WAITING_FOR_UPDATE_CONDITION" is verified for the vehicles within "600" seconds
        And campaign is "finish"ed
        And campaign status "FINISHED" is verified
        And campaign statistics are verified as per campaign <Campaign_Detail_Backend_Approval_1>
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier>
        Then flashing assignment status "UPDATE_SUCCESS" is verified for the vehicles within "300" seconds
        And campaign statistics are verified as per campaign <Campaign_Detail_Backend_Approval_2>

	    Examples: 
		    | vehicle                | device | Manufacturer | Model    | Campaign_Detail_Backend_Approval_1       | Campaign_Detail_Backend_Approval_2 | vehicle_filter       | content_DP                      | Protocol   | Identifier     | Identifier1      | Fota_Identifier        | Fota           | 
		    | "E2E_CampaignAuto_001" | "CCU"  | "Maserati"   | "Ghibli" | "running_campaign_with_backend_approval" | "campaign_with_backend_approval"   | "Model_Manufacturer" | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | "DriverApp_Break_True" | "CANalization" | 



    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CM_CCU_API_HP - Campaign with VMA having Approved as response
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        When a new campaign <Campaign_Detail> is "add"ed
        Then campaign status "CREATED" is verified
        When content <content_DP> is added to the Campaign
        And vehicles are added to the Campaign using static list
        And campaign is "schedule"ed
        Then campaign status "RUNNING" is verified
        And flashing assignment status "WAITING_FOR_MANAGER_APPROVAL" is verified for the vehicles within "600" seconds
        And the assignment in pending "Vehicle Manager Approval" is "Approved"
        And flashing assignment status "WAITING_FOR_UPDATE_CONDITION" is verified for the vehicles within "600" seconds
        When trigger flashing using protocol <Fota> Identifier <Fota_Identifier> for "Campaign" process
        And flashing assignment completing with "UPDATE_SUCCESS" is verified for the vehicles within "300" seconds
        And campaign status "FINISHED" is verified

        Examples: 
            | vehicle | device | Campaign_Detail              | content_DP                      | Protocol   | Identifier     | Identifier1      | Fota_Identifier        | Fota           | 
            | " "     | "CCU"  | "campaign_with_mgr_approval" | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | "DriverApp_Break_True" | "CANalization" | 



    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Smoke
    Scenario Outline:RF_CM_CCU_API_HP - Campaign with VMA having Scheduled Approval as response
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        When a new campaign <Campaign_Detail> is "add"ed
        Then campaign status "CREATED" is verified
        When content <content_DP> is added to the Campaign
        And vehicles are added to the Campaign using static list
        And campaign is "schedule"ed
        Then campaign status "RUNNING" is verified
        And flashing assignment status "WAITING_FOR_MANAGER_APPROVAL" is verified for the vehicles within "600" seconds
        When the assignment with pending "Vehicle Manager Approval" is "Approved" at scheduled time after "000:00:03"
        Then flashing assignment status "UPDATE_SCHEDULED" is verified for the vehicles within "60" seconds
        And flashing assignment status "WAITING_FOR_UPDATE_CONDITION" is verified for the vehicles within "600" seconds
        When trigger flashing using protocol <Fota> Identifier <Fota_Identifier> for "Campaign" process
        And flashing assignment completing with "UPDATE_SUCCESS" is verified for the vehicles within "600" seconds
        And campaign status "FINISHED" is verified

        Examples:
            | vehicle | device | Campaign_Detail              | content_DP                      | Protocol   | Identifier     | Identifier1      | Fota_Identifier        | Fota           |
            | " "     | "CCU"  | "campaign_with_mgr_approval" | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | "DriverApp_Break_True" | "CANalization" |



    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CM_CCU_API_HP - Campaign with VMA having rejection as response
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        When a new campaign <Campaign_Detail> is "add"ed
        Then campaign status "CREATED" is verified
        When content <content_DP> is added to the Campaign
        And vehicles are added to the Campaign using static list
        And campaign is "schedule"ed
        Then campaign status "RUNNING" is verified
        And flashing assignment status "WAITING_FOR_MANAGER_APPROVAL" is verified for the vehicles within "600" seconds
        When the assignment in pending "Vehicle Manager Approval" is "Rejected"
        Then flashing assignment completing with "UPDATE_REJECTED" is verified for the vehicles within "600" seconds
        And campaign status "FINISHED" is verified

        Examples:
            | vehicle | device | Campaign_Detail              | content_DP                      |
            | " "     | "CCU"  | "campaign_with_mgr_approval" | "E2E_RF_Standard_Job_encrypted" |



    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CM_CCU_API_HP - Campaign with VMA and revoking assignment at 'Pending Manager Approval' status
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        When a new campaign <Campaign_Detail> is "add"ed
        Then campaign status "CREATED" is verified
        When content <content_DP> is added to the Campaign
        And vehicles are added to the Campaign using static list
        And campaign is "schedule"ed
        Then campaign status "RUNNING" is verified
        And flashing assignment status "WAITING_FOR_MANAGER_APPROVAL" is verified for the vehicles within "600" seconds
        When "Campaign" OTA assignment is revoked
        Then flashing assignment completing with "UPDATE_REVOKED" is verified for the vehicles within "600" seconds
        And campaign status "FINISHED" is verified

        Examples:
            | vehicle | device | Campaign_Detail              | content_DP                      |
            | " "     | "CCU"  | "campaign_with_mgr_approval" | "E2E_RF_Standard_Job_encrypted" |



    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CM_CCU_API_HP - 2 Campaigns with VMA on same vehicle
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        When "2" new Campaigns <Campaign_Detail_Manager_Approval> are "add"ed
        Then campaign status "CREATED" is verified
        When content <content_DP> is added to the Campaign
        And vehicles are added to the Campaign using static list
        And campaign "1" is "schedule"ed
        And test is executed for "1" minutes
        And campaign "2" is "schedule"ed
        Then campaign status "RUNNING" is verified
        And flashing assignment status "WAITING_FOR_MANAGER_APPROVAL" is verified for the vehicles within "1200" seconds
        When the assignment of Campaign "1" in pending "Vehicle Manager Approval" is "Approved" with scheduled time after "000:00:08"
        And the assignment from Campaign "2" in pending "Vehicle Manager Approval" is "Approved"
        Then flashing assignment status "WAITING_FOR_UPDATE_CONDITION" is verified for the vehicles in Campaign "2" within "600" seconds
        When trigger flashing using protocol <Fota> Identifier <Fota_Identifier> for "Campaign" process
        And flashing assignment status "UPDATE_SUCCESS" is verified for the vehicles in Campaign "2" within "600" seconds
        And flashing assignment status "WAITING_FOR_UPDATE_CONDITION" is verified for the vehicles in Campaign "1" within "600" seconds
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier> for "Campaign" process
        And flashing assignment status "UPDATE_SUCCESS" is verified for the vehicles in Campaign "1" within "600" seconds
        And campaign status "FINISHED" is verified

        Examples: 
            | vehicle | device | Campaign_Detail_Manager_Approval | content_DP                      | Protocol   | Identifier     | Identifier1      | Fota_Identifier        | Fota           | 
            | " "     | "CCU"  | "campaign_with_mgr_approval"     | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | "DriverApp_Break_True" | "CANalization" | 

    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CM_CCU_API_HP - Campaign with VMA having GSM interruption while approving
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        And a new campaign <Campaign_Detail> is "add"ed
        Then campaign status "CREATED" is verified
        When content <content_DP> is added to the Campaign
        And vehicles are added to the Campaign using static list
        And campaign is "schedule"ed
        Then campaign status "RUNNING" is verified
        And flashing assignment status "WAITING_FOR_MANAGER_APPROVAL" is verified for the vehicles within "600" seconds
        And command to "stopGSMConnection" GSM mode of the device
        And wait for device to be "OFFLINE"
        When the assignment in pending "Vehicle Manager Approval" is "Approved"
        And flashing assignment status "MANAGER_APPROVAL_DECISION_MADE" is verified for the vehicles within "600" seconds
        And command to "startGSMConnection" GSM mode of the device
        And wait for device to be "ONLINE"
        And flashing assignment status "WAITING_FOR_UPDATE_CONDITION" is verified for the vehicles within "600" seconds
        When trigger flashing using protocol <Fota> Identifier <Fota_Identifier> for "Campaign" process
        And flashing assignment completing with "UPDATE_SUCCESS" is verified for the vehicles within "600" seconds
        And campaign status "FINISHED" is verified

        Examples:
            | vehicle | device | Campaign_Detail              | content_DP                      | Protocol   | Identifier     | Identifier1      | Fota_Identifier        | Fota           |
            | " "     | "CCU"  | "campaign_with_mgr_approval" | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | "DriverApp_Break_True" | "CANalization" |



    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CM_CCU_API_HP - Campaign with VMA on 2 vehicles and verifying SUCCESS status
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle1>
        And device <device2> is "ONLINE"
        And map device to the vehicle <vehicle2>
        And reference system <Protocol> with Identifier <Identifier1> is started
        And reference system <Protocol> with Identifier <Identifier2> is started
	Given device <device> is "ONLINE"
        And reference system <Protocol> with Identifier <Identifier1> is started
        And reference system <Protocol> with Identifier <Identifier2> is started
        When a new campaign <Campaign_Detail_Manager_Approval> is "add"ed
        And campaign status "CREATED" is verified
        And content <content_DP> is added to the Campaign
        And vehicles are added to the Campaign using static list
        And campaign is "schedule"ed
        And campaign status "RUNNING" is verified
        Then flashing assignment status "WAITING_FOR_MANAGER_APPROVAL" is verified for the vehicles within "600" seconds
        When the assignment in pending "Vehicle Manager Approval" is "Approved"
        And flashing assignment status "WAITING_FOR_UPDATE_CONDITION" is verified for the vehicles within "600" seconds
        And trigger flashing using protocol <Fota> Identifier <Fota_Identifier> for "Campaign" process
        And flashing assignment completing with "UPDATE_SUCCESS" is verified for the vehicles within "600" seconds
        And campaign status "FINISHED" is verified

        Examples:
            | vehicle1                 | device | vehicle2                 | device2 | Campaign_Detail_Manager_Approval | content_DP                      | Protocol   | Identifier1    | Identifier2      | Fota_Identifier        | Fota           |
            | "VMA_Campaign_Vehicle_1" | "CCU"  | "VMA_Campaign_Vehicle_2" | "CCU2"  | "campaign_with_mgr_approval"     | "E2E_RF_Standard_Job_encrypted" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | "DriverApp_Break_True" | "CANalization" |

    @E2E-API @E2E-CCU @E2E-HP @E2E-RF @BV-UC_OTA_Updates_GX @E2E-Regression
    Scenario Outline:RF_CM_CCU_API_HP - Campaign with VMA and BE having Approved as response
        Given device <device> is "ONLINE"
        And map device to the vehicle <vehicle>
        And reference system <Protocol> with Identifier <Identifier> is started
        And reference system <Protocol> with Identifier <Identifier1> is started
        When a new campaign <Campaign_Detail> is "add"ed
        Then campaign status "CREATED" is verified
        When content <content_DP> is added to the Campaign
        And vehicles are added to the Campaign using static list
        And campaign is "schedule"ed
        Then campaign status "RUNNING" is verified
        And flashing assignment status "WAITING_FOR_BACKEND_SIGNOFF" is verified for the vehicles within "100" seconds
        And the assignment in pending "Backend Approval" is "Approved"
        And flashing assignment status "WAITING_FOR_MANAGER_APPROVAL" is verified for the vehicles within "600" seconds
        And the assignment in pending "Vehicle Manager Approval" is "Approved"
        And flashing assignment status "WAITING_FOR_UPDATE_CONDITION" is verified for the vehicles within "600" seconds
        When trigger flashing using protocol <Fota> Identifier <Fota_Identifier> for "Campaign" process
        And flashing assignment completing with "UPDATING" is verified for the vehicles within "300" seconds
        When "Campaign" OTA assignment is revoked
        Then flashing assignment completing with "UPDATE_REVOKED" is verified for the vehicles within "600" seconds
        And campaign status "FINISHED" is verified
        And campaign statistics are verified as per campaign <Campaign_Detail>

        Examples: 
            | vehicle | device | Campaign_Detail                     | content_DP                 | Protocol   | Identifier     | Identifier1      | Fota_Identifier        | Fota           | 
            | " "     | "CCU"  | "campaign_with_mgr_and_be_approval" | "E2E_RF_Standard_Job_Slow" | "UDSonCAN" | "DemoFlashSim" | "DemoFlashSim_1" | "DriverApp_Break_True" | "CANalization" | 
