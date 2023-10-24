[DSP_ERROR]
   SET_UPROG(0)
   DISPLAY_MESSAGE (" ERROR-ERROR-ERROR-ERROR-ERROR-ERROR-ERROR-ERROR", POPUP_FALSE)
   DISPLAY_MESSAGE ("         session aborted by error", POPUP_FALSE)
   DISPLAY_MESSAGE (" CAUTION: flash file e.g. temp_dbg.s19 has to be local on this PC ", POPUP_FALSE)
   DISPLAY_MESSAGE ("  If you can't solve your problem, please contact the support line  ", POPUP_FALSE)
   DISPLAY_MESSAGE ("  and have the files FPSTAT.PRT and INCAPROT.LOG ready  ", POPUP_FALSE)
   EXTENDED_MESSAGE(FALSE)
   default : success
[DSP_ERROR_END]

[DSP_break]
   DISPLAY_MESSAGE ("", FALSE);
   DISPLAY_MESSAGE (" session aborted by user", FALSE)
   DISPLAY_MESSAGE ("", FALSE);
  default : EXIT
[DSP_break_END]

;-----------------------------------------------------------------------------
; Unterprogramm zur allgemeinen fehleranzeige
;-----------------------------------------------------------------------------
procedure err_m
{
[e_message]
   SET_UPROG(0)
   DISPLAY_MESSAGE (" ERROR-ERROR-ERROR-ERROR-ERROR-ERROR-ERROR-ERROR", POPUP_FALSE)
   DISPLAY_MESSAGE (" ADVICE :", POPUP_FALSE)
  default : $return
[e_message_END]
}
