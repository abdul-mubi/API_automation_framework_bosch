procedure programECUFlash
{

  [INFO]
    EXTENDED_MESSAGE(TRUE)
    SHOW_PROGRAMMING_INFO (2 ,"%1."EXT,1)
    SHOW_PROGRAMMING_INFO (1 ,"%1."EXT,1)
    case TRUE : start
    default : $return
  [INFO_END]

#include "flash.pri"       ; common routines

  [erase]
    DISPLAY_MESSAGE ("erase internal program Flash-EPROM",FALSE)
    UDSX_ERASE_MEMORY (1, TIMEOUT_MSEC_LONG)
    case FPA_ACK : erase2
    default : $return
  [erase_END]

  [erase2]
    DISPLAY_MESSAGE ("erase external program and data Flash-EPROM ",FALSE)
    UDSX_ERASE_MEMORY (4, TIMEOUT_MSEC_LONG)
    case FPA_ACK : timing2    
    default : $return
  [erase2_END]

  [timing2]
    DISPLAY_MESSAGE("Change Prof Timings (fast)... ",FALSE)
    DISPLAY_MESSAGE("call new prof command UDSB_SET_TIMING(2)",FALSE)
    UDSB_SET_TIMING(2)
    case FPA_ACK : prog
    default: $return
  [timing2_END]

  [prog]
    DISPLAY_MESSAGE ("program ECU code internal",FALSE)
    UDSX_PROGRAM_MEMORY ("%1."EXT, 1, 1, 0, "")
    case FPA_ACK : prog2
    default : $return
  [prog_END]

  [prog2]
    DISPLAY_MESSAGE ("program ECU code external 0x020000 - 0x07FFF0 ",FALSE)
    UDSX_PROGRAM_MEMORY ("%1."EXT, 2, 2, 0, "")
    case FPA_ACK : prog3
    default : $return
  [prog2_END]

  
  [prog3]
    DISPLAY_MESSAGE ("program ECU code external 0x0A0000 - 0x1BFFF0",FALSE)
    UDSX_PROGRAM_MEMORY ("%1."EXT, 4, 4, 0, "")
    case FPA_ACK : prog4
    default : $return
  [prog3_END]

  [prog4]
    DISPLAY_MESSAGE ("program ECU code external 0x1E0000 - 0x1FFFF0",FALSE)
    UDSX_PROGRAM_MEMORY ("%1."EXT, 6, 6, 0, "")
    case FPA_ACK : verify
    default : $return
  [prog4_END]

  [verify]
    EXTENDED_MESSAGE (TRUE)
    DISPLAY_MESSAGE ("verify checksum internal",FALSE)
    UDSX_VERIFY_MEMORY ("%1."EXT, 1, 1, MAX_BLOCK_LEN, M_16_BIT_BY_ADD8, TIMEOUT_MSEC)
    case FPA_ACK : verify2
    default : verify2
  [verify_END]

  [verify2]
    EXTENDED_MESSAGE (TRUE)
    DISPLAY_MESSAGE ("verify checksum external 0x020000 - 0x07FFF0",FALSE)
    UDSX_VERIFY_MEMORY ("%1."EXT, 2, 2, MAX_BLOCK_LEN, M_16_BIT_BY_ADD8, TIMEOUT_MSEC)
    case FPA_ACK : verify3
    default : verify3
  [verify2_END]

  [verify3]
    EXTENDED_MESSAGE (TRUE)
    DISPLAY_MESSAGE ("verify checksum external 0x0A0000 - 0x1BFFF0",FALSE)
    UDSX_VERIFY_MEMORY ("%1."EXT, 4, 4, MAX_BLOCK_LEN, M_16_BIT_BY_ADD8, TIMEOUT_MSEC)
    case FPA_ACK : verify4
    default : verify4
  [verify3_END]

  [verify4]
    EXTENDED_MESSAGE (TRUE)
    DISPLAY_MESSAGE ("verify checksum external 0x1E0000 - 0x1FFFF0",FALSE)
    UDSX_VERIFY_MEMORY ("%1."EXT, 6, 6, MAX_BLOCK_LEN, M_16_BIT_BY_ADD8, TIMEOUT_MSEC)
    case FPA_ACK : prog6
    default : $return
  [verify4_END]

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

