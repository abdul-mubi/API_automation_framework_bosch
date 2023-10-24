#All Generic constants should be listed here, all the other constants will import this file



#TOKEN RELATED




#PATH RELATED
GC_VRS = "\\..\\..\\..\\..\\common\\VRS\\"
GC_VRS_STEPS = "\\..\\..\\..\\common\\VRS\\"
GC_TEST_DATA = "\\..\\..\\..\\common\\TestData\\"





GC_UDS_DATA_PATH = "\\..\\..\\..\\common\\VRS\\UDSonCAN\\Data\\"
TEST_DATA_TOKEN = "\\.." + GC_TEST_DATA + "token.json"
TEST_DATA_TOKEN_JSON = "common\\TestData\\token.json"
TEST_CONFIG_JSON = "common\\TestData\\testConfig.json"
DEVICEMAP_JSON = "common\\TestData\\DeviceMap.json"
DEVICE_CONFIG_JSON = "common\\TestData\\config.json"
DESIRED_FW_FILE = "common/Desired_Sw_Version.json"
INITIAL_DEFAULT_VERSION = "0.0.0"

DEFAULT_TIMEOUT_TIME_SEC = 600



#UPDATE PACKAGE RELATED
DELTA_UPDATE_DP_FORMAT = "Delta_DP_{}_{}_{}_{}"
FULL_UPDATE_DP_FORMAT = "Full_Update_DP_{}_{}_{}"


#Device
DEVICE_FW_VALUE_REGEX = '\"Short_Version\": \"(.+?)\"'


#PEA UPDATE PACKAGE

PEA_UPDATE_PACKAGE = "pea_config_safe_states_TT"