Feature:Perform Multiple Device update via Campaign
    @E2E-API @E2E-CCU @E2E-HP @E2E-RF
    Scenario Outline:SU_CCU_API_HP: - Perform multiple device ota update via campaign
        Given prepare data for multiple device ota update via campaign
        When perform campaign for multiple device update
        
    Examples:
            |device|
            |"CCU" |