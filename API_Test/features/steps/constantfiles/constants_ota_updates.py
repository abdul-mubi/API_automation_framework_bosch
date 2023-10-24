from steps.constantfiles.constants import * # NOSONAR
# OtaUpdatesClass
# EndPoints

OTA_PACKAGE_NAME = "/ota/core/distributionPackages?search=name=={}&sort=creationStartDate,DESC"
OTA_SELFUPDATE = "/ota/core/selfupdate/"      #This EP change is not yet validated
OTA_DISTRIBUTION_ASSIGNMENT = "/ota/core/assignments"
OTA_DISTRIBUTION_ASSIGNMENT_ID = OTA_DISTRIBUTION_ASSIGNMENT + "/"
OTA_CREATE_UPDATE_PACKAGE = "/ota/core/updatePackages"
OTA_CREATE_DISTRIBUTION_PACKAGE = "/ota/core/distributionPackages"
OTA_CREATE_CONTAINER = "/ota/core/distributionPackages/{}/downloadableContainer"
OTA_CORE_ASSIGNMENT = "/ota/core/assignments/"
STATUS_HISTORY = "/statusHistory"
OTA_CORE_ASSIGNMENT_ID_REVOKE = OTA_CORE_ASSIGNMENT + "{}/revoke"
OTA_CORE_ASSIGNMENT_ID_RETRY = OTA_CORE_ASSIGNMENT + "{}/retry"
API_BASE_URL = "/api/applications"
OTA_JOB_RESULT_CONTENT = ["index.xml","MetaData.xml","results","results/.*/log_stdout.txt"]
OTA_ETTDRLOG_CONTENT = ["index.xml","MetaData.xml","LOGS","LOGS/ETTDRLOG_.*_SYS"]
ARTIFACTORY_DOWNLOAD_FILE_PATH   = "/../../../../temp/SU/DP"
ARTIFACTORY_IMAGE_PATH   = "/../../../../temp/SU/images"

DESIRED_STATE = "/ota/desiredStates"
DS_PACKAGE_NAME = DESIRED_STATE + "/{}"
DESIRED_STATE_JSON = "common\\TestData\\OTAUpdates\\Desired_states.json"
DESIRED_STATE_PAYLOAD_JSON = "common\\TestData\\OTAUpdates\\Desired_state_assignment_payload.json"
DESIRED_STATE_ASSIGNMENT = "/ota/desiredStateAssignments"
DESIRED_STATE_ASSIGNMENT_ID = DESIRED_STATE_ASSIGNMENT + "/{}"

REGEX_TCU1_FOLDER = "{update_to_version}/$"
REGEX_TCU2_FOLDER = "^.*CCU-M_{env}_{update_to_version}/$"

DELTA_UPDATE_TCU1_REGEX = "^.*{update_from_version}.*to_{update_to_version}.*.{firmware_type}.*"
FULL_UPDATE_TCU1_REGEX = "^Full.*_{update_to_version}.*.{firmware_type}.*"

DELTA_UPDATE_TCU2_REGEX =" "
FULL_UPDATE_TCU2_REGEX ="^update-bundle-.*"

USB_IMAGE_FILE = "images.zip"

TCU_GZ_FILE = "{file_name}.tar.gz"
TCU2_GZ_FILE = "bundle.raucb"

REGEX_ENVIRONMENT_URL= r'https(.*)bosch-mobility-cloud.com'