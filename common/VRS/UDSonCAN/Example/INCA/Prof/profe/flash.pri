; History :
; Mle 2008-07-15 : WAIT(2000) might be required for ES590 and ES690 not tested yet

;#define SA_SEND_KEY        02
;#define SA_KEY             "0x60 0xB0" ;fix key (seed==0x5FAF with EcuSimulator)
;#define SEED_PROG         "..\Security\SEED_DEV.DLL"

#define SA_SECURITY_DLL        "..\Security\SEED_DEV.DLL"
#define SA_ACCESS_IDX          1 ; idx of .. in *.cnf
#define SA_ACCESS_MODE         $10

#define ATP_SET_TIMING_PARAMETER_SET              04 ; setTimingParameterSetToGivenValues
#define ATP_NEW_TIMING_PARAMETER_SET              "0x07 0xD1 0x13 0x99" ; dummy when not setTimingParameterSetToGivenValues



  [start]
    EXTENDED_MESSAGE(FALSE)
    DISPLAY_MESSAGE("Start communication",POPUP_FALSE)
    UDSB_INIT_COMMUNICATION
    case FALSE : wait_on
    default : ssctime
  [start_END]

  [wait_on]
    DISPLAY_MESSAGE("activating communication with ECU ",POPUP_FALSE)
    DISPLAY_MESSAGE("Please switch ignition on ...  ",POPUP_FALSE)
    DISPLAY_MESSAGE("(press <CANCEL> to cancel waiting)  ",POPUP_FALSE)
    default : ssctime
  [wait_on_END]

  [ssctime]
    DISPLAY_MESSAGE("ECU startup mode,start programming",FALSE)
    DISPLAY_MESSAGE("Change Prof Timings (fast)... ",FALSE)
    DISPLAY_MESSAGE("call new prof command UDSB_SET_TIMING(2)",FALSE)
    UDSB_SET_TIMING(2)
    case FPA_ACK : seed2key
    default : $return
  [ssctime_END]


  [seed2key]
    DISPLAY_MESSAGE("check Seed&Key",FALSE)
    UDSX_SECURITY_ACCESS(SA_ACCESS_IDX, SA_ACCESS_MODE, SA_SECURITY_DLL)
    case FPA_ACK : start_diag
    default : seederror
  [seed2key_END]

  [start_diag]
    DISPLAY_MESSAGE("start diagnostic mode",FALSE)
    UDS_DIAGNOSTIC_SESSION_CONTROL(2)
    case FPA_ACK : waitshrt
    default : $return
  [start_diag_END]

  [waitshrt]
    DISPLAY_MESSAGE("   ",FALSE)
    default: fcu_id
  [waitshrt_END]

  [fcu_id]
   DISPLAY_MESSAGE("Create ID", FALSE)
   RUN_DLL(FCU_ID_DLL,fcu_id,FCU_ID_TMP)
   case TRUE : fcu_id_write
   default : $return FALSE
  [fcu_id_END]

  [fcu_id_write]
   DISPLAY_MESSAGE("Write ID", FALSE)
   UDS_WRITE_DATA_BY_IDENTIFIER_FILE(FCU_LOCAL_ID,FCU_ID_TMP2)
   case FPA_ACK : erase
   default : $return FALSE
  [fcu_id_write_END]

  
  [seederror]
    DISPLAY_MESSAGE ("Security access (SEED&KEY) denied !",FALSE)
    DISPLAY_MESSAGE ("PROGRAMMING NOT POSSIBLE !",FALSE)
    default : $return FALSE
  [seederror_END]


  [stopC]
    DISPLAY_MESSAGE ("UDS Reset ECU !!!!!!",FALSE)
    UDSX_SUSPEND_TESTER_PRESENT(1)
    UDS_ECU_RESET(4)
    DISPLAY_MESSAGE ("wait for 2sec might be required for ES590 ",FALSE)
    CLEAR_ERROR_INFO
    EXTENDED_MESSAGE (FALSE)
    DISPLAY_MESSAGE ("Reset ECU done!!!!!!",FALSE)
    default : $return TRUE
  [stopC_END]

