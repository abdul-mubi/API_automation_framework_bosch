from steps.constantfiles.constants import * # NOSONAR
# RF_Campaign_Class
# EndPoints
RFC_CAMPAIGNS = "/campaign/campaigns"
RFC_CAMPAIGNS_SEARCH_NAME = RFC_CAMPAIGNS + "?search=name=={}"
RFC_CAMPAIGNS_ID = RFC_CAMPAIGNS + "/{}"
RFC_CAMPAIGNS_ID_ACTION = RFC_CAMPAIGNS_ID + "/{}"
RFC_CAMPAIGNS_ID_VEHICLE = RFC_CAMPAIGNS_ID + "/vehicles"
RFC_OTA_ID = "/ota/core/assignments/{}"
RFC_OTA_ID_EP = RFC_OTA_ID + "/{}"
RFC_OTA_ID_STATISTICS = RFC_CAMPAIGNS_ID + "/statistics"
CAMPAIGN_TARGET_STATISTICS = RFC_CAMPAIGNS_ID + "/targetStatistics"
RM_CONFIG_NAME = "/remote-measurement/measurementConfigurations?search=name=={}&sort=lastUpdatedOn,DESC"
RD_CONFIG_NAME = "/remote-diagnostics/diagnosticConfigurations?size=10&search=state==RELEASED;name=={}&sort=lastUpdatedOn,DESC"
CAMPAIGN_JSON_PATH = "common\\TestData\\OTAUpdates\\Campaign.json"
