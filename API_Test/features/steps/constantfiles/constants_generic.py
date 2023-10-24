from steps.constantfiles.constants import * # NOSONAR
# Generic
# Messages
GS_TEST_DATA_PATH = "common\\TestData\\Path.json"
GS_CONFIG_LINK = "http://bosch.de/AA_AS/Telediag/Configuration"
GC_DEVICECLEANUP = "\\..\\..\\..\\..\\common\\DeviceCleanUp\\"
SSH_PKEY = GC_DEVICECLEANUP + "Data\\{ssh_key}"
GC_DATE_AND_TIME = "%d-%m-%Y, %H:%M"
GC_BAUDRATE_250K = "Baudrate = 250000"
GC_USER_GUIDE_URL = "https://ota.eu.bosch-mobility-cloud.com/userguide/content/en-gb/{}.html"
GC_UDS_DATA_PATH = "\\..\\..\\..\\common\\VRS\\UDSonCAN\\Data\\"
VRS_ISSUE = {"0x80002004": "BOA device Interface is not available in the Test PC", 
                "Another controller associated with the same hardware port": "CAN port is busy/in-use, might be by BusMaster",
                "is probably not available": "CAN port is not available/connection Issue", 
                "0x80002008": "Generic BOA VRS error",
                "0x80004000": "Specified VRS config is incompatible with Active config"}
DATA_PATH = GC_VRS_STEPS + "CANalization\\Data"
ASC_ZIP_FILE_PATH =DATA_PATH +"\\Master_Test_Data_RaspberryPi_Teststand_Blue_20220707_shortend.zip"


VERSION_JSON_PATH = "\\..\\..\\..\\version.json"
ENVIRONMENT_PATH = GC_TEST_DATA + "Environment"
TEMP_PATH = "\\..\\..\\..\\temp\\"
GC_VRS_RESPONSE_ASC_PATH = TEMP_PATH + "vrs_response.asc"
GC_VRS_UDS_SEND_KEY_ASC_PATH = GC_VRS_STEPS + "CANalization\\Data\\UDS_SendKey.asc"
GC_VRS_RESET_BAT_PATH = GC_VRS_STEPS + "reset.bat"
GC_VRS_DELETE_BAT_PATH = GC_VRS_STEPS + "del_VRS_Residual.bat"
GC_DEVICECLEANUP_PS = GC_DEVICECLEANUP + "deviceCleanUp.ps1"
TEST_DATA_GENERATOR = "\\..\\..\\..\\..\\test-data-generator"
CLEWARE_SWITCH = "\\..\\..\\..\\..\\common\\Cleware"
CLEWARE_USBSWITCH_EXE = CLEWARE_SWITCH + "\\USBswitchCmd.exe"
GC_DEVICECLEANUP_DATA_KEY = "\\..\\..\\..\\..\\common\\DeviceCleanUp\\Data\\developerKey{}"

GC_SEED_AND_KEY_CALCULATOR_EXE = "\\..\\..\\..\\..\\common\\Seed_Key_Calculator\\seed_key_cli.exe"
GC_KEY_GENERATOR_PY = "\\..\\..\\..\\..\\common\\Seed_Key_Calculator\\seed_key_generator.py"
GC_TEST_SUITE_EXECUTOR_YAML = "\\..\\..\\..\\..\\.github\\workflows\\test_suite_executor.yaml"
GC_GIT = "\\..\\..\\..\\..\\.git"
EXECUTION_ID = []
CAN_DATA_JSON_PATH = "\\common\\TestData\\Generic\\can_data.json"

SSH_USERNAME = "root"
SSH_PASSWORD = ""

STUTTGART_LATITUDE_RANGE = [47.7, 49.7]
STUTTGART_LONGITUDE_RANGE = [8.4, 10.4]