procedure programECUFlash
{

  [INFO]
    EXTENDED_MESSAGE(TRUE)
    SHOW_PROGRAMMING_INFO (3 ,"%1."EXT,1)
    case TRUE : start
    default : $return
  [INFO_END]

#include "flash.pri"       ; common routines

  [erase]
    DISPLAY_MESSAGE ("erase data",FALSE)
    UDSX_ERASE_MEMORY (5, TIMEOUT_MSEC_LONG)
    case FPA_ACK : timing2
    default : $return
  [erase_END]


  [timing2]
    DISPLAY_MESSAGE("Change Prof Timings (fast)... ",FALSE)
    DISPLAY_MESSAGE("call new prof command UDSB_SET_TIMING(2)",FALSE)
    UDSB_SET_TIMING(2)
    case FPA_ACK : prog6
    default: $return
  [timing2_END]

  [prog6]
    DISPLAY_MESSAGE ("program ECU data",FALSE)
    UDSX_PROGRAM_MEMORY ("%1."EXT, 5, 5, 0, "")
    case FPA_ACK : verify6
    default : $return
  [prog6_END]
  
  [verify6]
    EXTENDED_MESSAGE (TRUE)
    DISPLAY_MESSAGE ("verify ECU data",FALSE)
    UDSX_VERIFY_MEMORY ("%1."EXT, 5, 5, MAX_BLOCK_LEN, M_16_BIT_BY_ADD8, TIMEOUT_MSEC)
    case FPA_ACK : verify_ok
    default : $return
  [verify6_END]

  [verify_ok]
    DISPLAY_MESSAGE("Verify successful !", FALSE)
    default : success
  [verify_ok_END]

  [success]
   DISPLAY_MESSAGE ("Programming finished successfully !",FALSE);
   DISPLAY_MESSAGE ("ECU is programmed with a new version of data,",FALSE);
   DISPLAY_MESSAGE ("ECU resetting",FALSE);
   default : stopC
  [success_END]
}

