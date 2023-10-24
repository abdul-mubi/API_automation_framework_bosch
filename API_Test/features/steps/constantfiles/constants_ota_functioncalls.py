from steps.constantfiles.constants import * # NOSONAR
#OTA Function Call Class
#Endpoints
OTA_FUNCTION_CALL = "/ota-function-calls/api/v1"
VSC_DEF = OTA_FUNCTION_CALL + "/definitions"
CALL_FUNCTION = OTA_FUNCTION_CALL + "/function-calls"
GET_STATUS_FUNCTION_CALL = CALL_FUNCTION + "/{}"
OTA_FUNCTION_CALL_FILES_PATH = "common\\TestData\\FunctionCall\\"
PROPERTY_JSON_PATH = OTA_FUNCTION_CALL_FILES_PATH + "property.json"
ARTIFACT_URL_PATTERN = r'^https(.*)bosch-mobility-cloud.com(.*)blobs(.*)$'
