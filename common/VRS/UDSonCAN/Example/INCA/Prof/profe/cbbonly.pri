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
    case FPA_ACK : prog5
    default : $return
  [erase2_END]

  [prog5]
    DISPLAY_MESSAGE ("program cbb",FALSE)
    UDSX_PROGRAM_MEMORY ("%1."EXT, 3, 3, 0, "")
    case FPA_ACK : verify5
    default : $return
  [prog5_END]

  [verify5]
    EXTENDED_MESSAGE (TRUE)
    DISPLAY_MESSAGE ("verify checksum cbb",FALSE)
    UDSX_VERIFY_MEMORY ("%1."EXT, 3, 3, MAX_BLOCK_LEN, M_16_BIT_BY_ADD8, TIMEOUT_MSEC)
    case FPA_ACK : verify_ok
    default : $return
  [verify5_END]

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

