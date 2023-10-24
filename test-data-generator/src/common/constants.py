#Folders
TEMP = "temp/"
DEVICE_SPECIFIC_FOLDER = TEMP + "{device_id}/"
PROTOBUF_OUT_FOLDER = DEVICE_SPECIFIC_FOLDER + "protobuf_out/"
RESULT_TEMPLATE_FOLDER = "src/resources/rm_templates/"
RM_ZIP_PATH = DEVICE_SPECIFIC_FOLDER + "rm_config.zip"
ZIP_EXTRACT_PATH = DEVICE_SPECIFIC_FOLDER + "zip_extract"
RM_FOLDER_PATH = DEVICE_SPECIFIC_FOLDER + "RM_CONFIGS/"
OTA_FOLDER_PATH = DEVICE_SPECIFIC_FOLDER + "OTA_CONFIG/"
OTA_ASSIGNMENT_JSON_PATH = DEVICE_SPECIFIC_FOLDER + "OTA_CONFIG/{assignment_id}.json"
CDP_JOB_INITIAL_PATH = DEVICE_SPECIFIC_FOLDER + "zip_extract/cdpJobConfig.xml"
MEASUREMENT_CSV_PATH = "userdata/measurement/measurement_data.csv"
DEFAULT_INVENTORY = "userdata/default_inventory.json"
DEVICE_INVENTORY_PATH = DEVICE_SPECIFIC_FOLDER + "inventory.json"
DEVICE_CERTIFICATES_PATH = "D:/Device_simulator/certificates/"

#FilePaths
DEVICE_DATA_FILE ="userdata/device_data.json"
ENVIRONMENT_DATA_FILE = "userdata/environment.json"
ROUTE_DATA_FILE= "userdata/route_details.json"
FUNCTION_CALL_FILE= "userdata/function_call_status.json"

#Topics
SUBSCRIBE_TOPICS = [ "devices/{device_id}/bfb/functionCallsGx/v2/protobuf/commands/executeJob",
				"devices/{device_id}/bfb/functionCallsGx/v2/protobuf/commands/executeTask",
				"devices/{device_id}/bfb/deviceManagement/v2/protobuf/commands/requestLogs",
				"devices/{device_id}/bfb/vehicleData/v3/protobuf/commands/activateMeasurement",
				"devices/{device_id}/bfb/vehicleData/v3/protobuf/commands/deactivateMeasurement",
                "devices/{device_id}/bfb/inventory/v3/protobuf/commands/inventory",
                "devices/{device_id}/bfb/softwareUpdate/v2/protobuf/commands/update",
                "devices/{device_id}/bfb/softwareUpdate/v2/protobuf/commands/updateApproval",
                "devices/{device_id}/bfb/softwareUpdate/v2/protobuf/commands/updateRevocation",
                "devices/{device_id}/bfb/deviceManagement/v2/protobuf/commands/setGpsStatus",
                "devices/{device_id}/bfb/deviceVehicleMapping/v2/protobuf/commands/updateMappingStatus",
                "devices/{device_id}/bfb/functionCalls/v2/protobuf/commands/callFunction"
            ]
MEASUREMENT_STATUS_TOPIC = 'devices/{device_id}/bfb/vehicleData/v3/protobuf/events/measurementStatus'
MEASUREMENT_RESULT_TOPIC = 'devices/{device_id}/bfb/vehicleData/v3/protobuf/events/measurementResult'
VIN_UPDATE_TOPIC = 'devices/{device_id}/bfb/deviceVehicleMapping/v2/protobuf/events/vinUpdate'
GPS_REPORT_TOPIC = 'devices/{device_id}/bfb/deviceManagement/v2/protobuf/events/gpsPositionReport'
UPDATE_STATUS_TOPIC = 'devices/{device_id}/bfb/softwareUpdate/v2/protobuf/events/updateStatus'
INVENTORY_REPORT_TOPIC = 'devices/{device_id}/bfb/inventory/v3/protobuf/events/inventoryReport'
CERTIFICATE_REPORT_TOPIC = 'devices/{device_id}/bfb/deviceManagement/v2/protobuf/events/certificateReport'
FUNCTION_CALL_STATUS_TOPIC = 'devices/{device_id}/bfb/functionCalls/v2/protobuf/events/functionCallStatus'

#Cloud store

DEVICE_UPLOAD_BLOB_URL = "https://objectstore.connect.devices.eu.bosch-mobility-cloud.com/v3/device/blobs"
DOWNLOAD_BLOB_URL = "https://api.devices.eu.bosch-mobility-cloud.com/v3/blobs"

#Data_Formats
PROTOBUF = "PROTOBUF"
JSON = "JSON"
PROTO_MESSAGE = "PROTO_MESSAGE"

#Version Info
VERSION="1.0.1"
BFB_SUPPORT={"inventory":"3","datapoints":"2","deviceManagement":"2",
             "functionCallsGx":"2","vehicleData":"3","softwareUpdate":"2",
             "deviceVehicleMapping":"2", "functionCalls":"2"}


#measurement
MEASUREMENT_RESULT_DURATION_SEC = 180
CONTINUOUS_REPORTING = False  #True or False
GPS_SAMPLE_SEC = 10
OTA_STATUS_PUBLISH_TIME_SEC = 10
PERIODIC_RM_PUBLISH_TIME_SEC = 1
MEASUREMENT_RESULT_FILE_SIZE_IN_KBS = 99000

#Other
RAW_RESULT_STORE_TIME_MIN = 2

#Measurement Metadata repeated keys
CONFIG = 'config:config'
CONTENT = 'config:content'
CONFIG_ENTRIES = 'config:dataLoggerResultEntries'