#define CR                     13
#define ESCAPE                 27
#define WARNING                77
#define ALREADY                99
#define NO_DATA_SET            -1
#define ECU_ADDRESS            $12
#define EXT                    "CBC"
#define CONV                   -c           ;für CONVERT
#define ADR_BEGIN              -s0000000
#define ADR_END                -e0FFFFFF
#define CONFIG                 "%2"

#define SEED_PROG              "c:\$security\SEED_DEV.DLL"


#define FCU_ID_DLL             C:\$PROF\XCELLSIS\FCU_ID.DLL
#define FCU_ID_TMP             C:\$PROF\XCELLSIS\FCU_ID.TMP
#define FCU_ID_TMP2            "C:\$PROF\XCELLSIS\FCU_ID.TMP"

#define FCU_LOCAL_ID           $F185

#define ACCESSMODE             1

#define SEED                   $10

#define FALSE                  0
#define TRUE                   1
#define NO_NEW_LINE            2
#define OVER_WRITE             3
#define BAR                    4
#define POPUP_WINDOW           $0100
#define FPA_ACK                $00000000
#define FPA_NACK               $80000001
#define FPA_ABORT              $80000002
#define FPA_RETRY              $80000003
#define FPA_PARAM_OUT_OF_RANGE $80000012


#define RED_FALSE              $4000
#define RED_OVER_WRITE         $4003
#define RED_BAR                $4004
#define BEEP_FALSE             $1000
#define BLINK_FALSE            $2000
#define GREEN_FALSE            $6000
#define GREEN_TRUE             $6001
#define GREEN_BAR              $6004
#define POPUP_FALSE            $0100
#define POPUP_TRUE             $0101

#define COMM_ERROR              1000    ; INCA problems
#define INCA_ERROR              2000    ; INCA device sends error code
#define START_ERROR             3000    ; KWP2000 error
#define USER_ERROR             10000    ; run time error

#define TIMEOUT_MSEC_LONG          6000 ; UDS simulator delay is 2000
#define TIMEOUT_MSEC_SHORT         1000 ; will cause timeout
#define MAX_BLOCK_LEN         $FFFFFFFF ; verify entire block
#define M_16_BIT_BY_ADD8      $00010201 ; 16bit checksum adding bytewise
#define TIMEOUT_MSEC               6000 ; UDS simulator delay is 2000
