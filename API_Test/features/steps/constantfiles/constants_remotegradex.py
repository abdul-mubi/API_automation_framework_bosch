from steps.constantfiles.constants import * # NOSONAR
# RemoteGradeX_Class
# EndPoints
RGX_RDA_TASK_EXE = "/remote-gradex/rdaTaskExecutions"
RGX_RDA_TASK_EXE_DEVICE_ID = RGX_RDA_TASK_EXE + "?search=deviceId=={}"
RGX_RDA_JOB_RESULT = "/remote-gradex/rdaJobResults"
RGX_RDA_JOB_RESULT_DEVICE_ID = RGX_RDA_JOB_RESULT + "?search=deviceId=={}"
RGX_RDA_JOB_RESULT_ID = RGX_RDA_JOB_RESULT + "/{}"
RGX_RDA_JOB_RESULT_ZIP_ID = RGX_RDA_JOB_RESULT + "/zip/{}"
GRADEX_ZIP_FILE_PATH = "\\..\\..\\..\\common\\TestData\\GradeX_zipFiles\\"

GRADEX_TASK_ID = "/remote-gradex/rdaTaskExecutions/{}"

# Messages
RGX_JOB_RESULT = "RDA Job result is not available"