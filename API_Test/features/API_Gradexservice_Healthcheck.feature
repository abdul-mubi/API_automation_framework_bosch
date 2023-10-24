Feature: gradex service health monitoring 
@E2E-API @E2E-Smoke @E2E-CCU
Scenario Outline: HealthCheck_API - verify the Gradex services are available and its expected response

    Given Authorization response is verified for gradex services
    Then gradex service health check is verified with expected response

Examples:
             | device |                   
             | "CCU"  |