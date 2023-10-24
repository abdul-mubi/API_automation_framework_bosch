
;--------------------------------------------------------------------------------
; Unterprogramm zum Konvertieren der Hex-Datei in eine Binaer-Datei mit 'CONVERT'
;--------------------------------------------------------------------------------


procedure convert
{
[echo]
  DISPLAY_MESSAGE (" checking datafiles...",FALSE)
  DISPLAY_MESSAGE ("   ",FALSE)
  CHECK_CONSISTENCE ("%1")
  case TRUE : nochange
  case -1   : noclf
  case -2   : nocontainer
  case -3   : nobinaer
  case -4   : nocontainer
  case	0   : oldbin
  default   : $return
[echo_END]

[nochange]
  DISPLAY_MESSAGE (" OK ",FALSE)
  default : $return
[nochange_END]

[noclf]
  DISPLAY_MESSAGE (" no converted binary file found,",FALSE)
  default : con
[noclf_END]

[oldbin]
  DISPLAY_MESSAGE (" Binary file found, but not generated from Hex file.",POPUP_FALSE)
  DISPLAY_MESSAGE (" Press <CONTINUE> to start conversion or",POPUP_FALSE)
  DISPLAY_MESSAGE ("       <CANCEL>   to use existing binary file",POPUP_TRUE)
  case TRUE : con
  default : nocontainer
[oldbin_END]

[nocontainer]
  DISPLAY_MESSAGE (" use existing binary file ... ",FALSE)
  default : $return
[nocontainer_END]

[nobinaer]
  DISPLAY_MESSAGE (" binary file doesn't exist, ",FALSE)
  default : con
[nobinaer_END]


[con]
  DISPLAY_MESSAGE (" convert Hex file --> binary file ...",FALSE)
  DISPLAY_MESSAGE (" ",FALSE)
  RUN_DLL ("CONVERT.DLL",convert,-h,-q,-i,ADR_END,CONV,%1)
    case TRUE : $return
  default : ret
[con_END]

[ret]
  DISPLAY_MESSAGE (" ",FALSE)
  default : $return FALSE
[ret_END]
}

