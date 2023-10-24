from steps.constantfiles.constants import * # NOSONAR

RELEASE = "/releases"

# RemoteDiagnostic_Class
# EndPoints
RD = "/remote-diagnostics"
DTC_SNAPSHOT = "/dtcsSnapshots/"
DTC_SNAPSHOT_HISTORY = "/dtcsSnapshots/history?sort=timestamp,DESC"
ECUS = "/ecus"
RD_VEHICLES = RD + "/vehicles"
RD_VEHICLE_ID_ASSIGNMENTS = "{}/{}/assignment"
RD_VEHICLE_ID = RD_VEHICLES + "/{}"
RD_VEHICLE_ID_VDC = RD_VEHICLE_ID + "/vehicleDiagnosticConfigurations"
RD_VEHICLE_ID_DTCSS_HISTORY = RD_VEHICLE_ID + DTC_SNAPSHOT_HISTORY
RD_VEHICLES_ID_DTCSS_ID = RD_VEHICLE_ID + DTC_SNAPSHOT + "{}"
RD_VEHICLES_ID_AC = RD_VEHICLE_ID + "/availableCapabilities"
RD_VEHICLES_ID_CC = RD_VEHICLE_ID + "/capabilityConfigurations"
RD_DIAG_FUNC = RD + "/diagnosticFunctions"
RD_DIAG_FUNC_ID = RD_DIAG_FUNC + "/{}"
RD_DIAG_FUNC_ID_EP = RD_DIAG_FUNC_ID + "/{}"
RD_DIAG_FUNC_NAME = RD_DIAG_FUNC + "?search=name=={}"
RD_DIAG_FUNC_ID_RELEASE = RD_DIAG_FUNC_ID + RELEASE
RD_DIAG_JOB_ID = RD + "/diagnosticJobs/{}"
RD_DIAG_JOB_ID_RELEASE = RD_DIAG_JOB_ID + RELEASE
RD_DIAG_SEARCHNAME_FUNC_ID = RD_DIAG_FUNC + "?search=diagnosticFunctionId=={}"
RD_DIAG_FUNC_ID_DRAFT = RD_DIAG_FUNC_ID + "/draft"
RD_DIAG_CONFIG = RD + "/diagnosticConfigurations"
RD_DIAG_CONFIG_SEARCH_NAME = RD_DIAG_CONFIG + "?search=name=={}"
RD_DIAG_CONFIG_ID = RD_DIAG_CONFIG + "/{}"
RD_DIAG_CONFIG_ID_EP = RD_DIAG_CONFIG_ID + "/{}"
RD_DIAG_CONFIG_SEARCH_NAME_ID = RD_DIAG_CONFIG + "?search=diagnosticConfigurationId=={}"
RD_DIAG_CONFIG_ID_DRAFT = RD_DIAG_CONFIG_ID + "/draft"
RD_DIAG_CONFIG_ID_RELEASE = RD_DIAG_CONFIG_ID + RELEASE
RD_LATEST_VEHICLE_DIAG_CONFIG = "{}/{}/latestVehicleDiagnosticConfiguration"
OTA_FUNCTION_CALL_GX = "\\..\\..\\..\\common\\TestData\\OTAFunctionCallsGX\\"

# Messages
RD_TD_CRUD_JSON = "\\..\\..\\..\\common\\TestData\\testData_RD_CRUD.json"
RD_FUNC_FAILURE = "Retrieving Diagnostic Function information failed"
RD_LOADTEST_FAILURE = "Load test failed in the execution: "
RD_WITH_ERROR = " with the error: "
RD_DATE_AND_TIME = "%Y-%m-%dT%H:%M"