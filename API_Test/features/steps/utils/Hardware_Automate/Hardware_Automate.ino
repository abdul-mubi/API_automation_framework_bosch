
enum testerResponse {
  ledOFF,           //LED-00 , Return status as LED OFF
  ledON,            //LED-01 , Return status as LED ON
  ledBlink          //LED-02 , Return status as LED blinking
};
enum testerAction {
  unknown,          //DO nothing unknown action received
  releaseButton,    //FBT-00 , Release button
  clickButton,      //FBT-01 , Press button and after delay release button
  getLedStatus      //LED-?? , Get LED status
};

/********************************Global Variables and Macro********************************/
#define OBU_LED_BLINK_INETRVAL  1000                                           // in ms
#define OBU_LED_BLINK_LATENCY OBU_LED_BLINK_INETRVAL * 0.1                    //10% of latency for LED state change

const int buttonPin = 13;                                                       // the number of the button pin (OBU button controll pin)
const int ledPin = 12;
String line = "";
bool received_line = 0;
testerAction actionToDO = unknown;
testerResponse flashLedStatus = ledOFF;
unsigned long previousMillis = 0;                                               // will store last time LED was updated
bool previousPinState = LOW;
const long interval = OBU_LED_BLINK_INETRVAL + OBU_LED_BLINK_LATENCY;           // interval at which to blink (milliseconds) + 100


void setup() {
  pinMode(buttonPin, OUTPUT);
  pinMode(ledPin,INPUT);
  Serial.begin(115200);
  Serial.println("RHS-001");
  delay(300);
}

void loop() {
  checkLEDStatus();
  if(received_line) {
   actionToDO = decodeActionFromTester(line);
   //Serial.println(line);
   
   switch(actionToDO) {
    case releaseButton:
    {
      digitalWrite(buttonPin,LOW);
      //Serial.println("release button");
     break; 
    }
    case clickButton:
    {
      digitalWrite(buttonPin,HIGH);
      delay(1000);
      digitalWrite(buttonPin,LOW);
      //Serial.println("clickButton");
      break;
    }
    case getLedStatus:
    {
      //Serial.println("getLedStatus");
      encodeResponseToTester();
      break;
    }
    default:
    {
      Serial.println("Default status");
    }
   }
   
   line = "";
   received_line = 0;
  }
  
}

//Function is calling in polling method from function "loop" make sure while adding delay in function 'loop'
void checkLEDStatus() {
    unsigned long currentMillis = millis();
    bool currentPinState = digitalRead(ledPin);

    if (currentMillis - previousMillis >= interval) {
      previousMillis = currentMillis - OBU_LED_BLINK_LATENCY;

      if(previousPinState != currentPinState) {
        flashLedStatus = ledBlink;
      }
      else if(currentPinState == HIGH) {
        flashLedStatus = ledON;
      }
      else if(currentPinState == LOW) {
        flashLedStatus = ledOFF;
      }

      previousPinState = currentPinState;
    }
}

testerAction decodeActionFromTester(String data) {
  if(data.indexOf("FBT-00") > (-1)) {
    return releaseButton;
  }
  else if(data.indexOf("FBT-01") > (-1)) {
    return clickButton;
  }
  else if(data.indexOf("LED-??") > (-1)) {
    return getLedStatus;
  }
  else {
    return unknown;
  }
}

void encodeResponseToTester() {
  switch(flashLedStatus) {
    case ledOFF: {
      Serial.println("LED-00");
      break;
    }
    case ledON: {
      Serial.println("LED-01");
      break;
    }
    case ledBlink: {
      Serial.println("LED-02");
      break;
    }
  }
}

/*Serial interrupt routine 
Holds the latest line received*/
void serialEvent() {
  char ser_data;
  while (Serial.available()) {
    ser_data = (char)Serial.read();
    line += ser_data;
    if(ser_data == '\n') {
      received_line = 1;
    }
  }
}
