#include <ArduinoJson.h>
#define VERSION "1.1.0"
#define BAUD_RATE 115200
// Digital inputs
#define DI1 2
#define DI2 3
#define DI3 4
// Analog pins
#define AI1 A0
#define AI2 A1
#define AI3 A2
#define AI4 A3
#define AI5 A4
// Main lood delay: this is typically a small value, used to save power
#define DELAY 40UL     // microseconds
// Sampling period: this is the time between samples, must be larger than DELAY
#define TIMESTEP 160UL // milliseconds
// Topmost field in the output JSON
#define DATA_FIELD "data"

JsonDocument doc;
String out;
const double to_V = 5.0 / 1024.0;
const double to_A = 20.0 / 2.8;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(BAUD_RATE);
  Serial.print("# Starting JSON reader v" VERSION "\n");
  pinMode(LED_BUILTIN, OUTPUT);
  // Define pin modes
  pinMode(AI1, INPUT);
  pinMode(AI2, INPUT);
  pinMode(AI3, INPUT);
  pinMode(AI4, INPUT);
  pinMode(AI5, INPUT);
}

template<typename T>
T threshold_value(T value, T threshold) {
  return value > threshold ? value : 0;
} 

void loop() {
  static unsigned long prev_time = 0;
  static unsigned long timestep_us = TIMESTEP * 1000;
  static unsigned long delay = DELAY;
  static unsigned int threshold = 1;
  static bool onoff = LOW, pause = false, raw = false;
  unsigned long now = micros();
  static unsigned long v = 0; // accumulator for serial values
  
  // Serial input
  // This allows to change parameters on the fly. Toggle parameters are read
  // as a single character, while commands that take a numeric argument 
  // (integer) follow this convention: 123X, where 123 is the value and X is the
  // command. The commands are always single characters and correspond 
  // to the following switch cases:
  char ch;
  // Read serial in
  if (Serial.available()) {
    ch = Serial.read();
    switch (ch) {
      case '0'...'9': // numeric value accumulator
        v = v * 10 + ch - '0';
        break;
      case 'p': // set timestep_us to the current accumulator value
        timestep_us = constrain(v * 1000, 1000, 1E6);
        v = 0;
        break;
      case 'd': // set delay to the current accumulator value
        delay = constrain(v, 1, timestep_us / 10.0);
        v = 0;
        break;
      case 't': // set threshold to the current accumulator value
        threshold = constrain(v, 0, 1023);
        v = 0;
        break;
      case 'x': // toggle pause mode
        pause = !pause;
        break;
      case 'r': // toggle raw mode
        raw = !raw;
        break;
      case '?': // provide inline help
        Serial.print("Version: " VERSION "\n");
        Serial.print("Usage:\n");
        Serial.print("- 10p  set sampling period to 10 milliseconds (now ");
        Serial.print(timestep_us / 1000);
        Serial.print(" ms)\n- 30d  set loop delay to 30 microseconds (now ");
        Serial.print(delay);
        Serial.print(" us)\n- 280t set threshold to 280 (now ");
        Serial.print(threshold);
        Serial.print(")\n");
        Serial.print("- x    toggle pause\n");
        Serial.print("- r    toggle raw output\n");
        break;
      default:
        v = 0;
    }
  }

  if (pause) return;

  if (now - prev_time >= timestep_us) {
    bool active = false;
    digitalWrite(LED_BUILTIN, onoff);
    onoff = !onoff;
    doc["millis"] = millis();

    // Digital inputs
    doc[DATA_FIELD]["DI1"] = digitalRead(DI1);
    doc[DATA_FIELD]["DI2"] = digitalRead(DI2);
    doc[DATA_FIELD]["DI3"] = digitalRead(DI3);

    // Analog Inputs
    doc[DATA_FIELD]["AI1"] = threshold_value<int>(analogRead(AI1), threshold);
    active = active || (doc[DATA_FIELD]["AI1"].as<double>() > 0);
    doc[DATA_FIELD]["AI2"] = threshold_value<int>(analogRead(AI2), threshold);
    active = active || (doc[DATA_FIELD]["AI2"].as<double>() > 0);
    doc[DATA_FIELD]["AI3"] = threshold_value<int>(analogRead(AI3), threshold);
    active = active || (doc[DATA_FIELD]["AI3"].as<double>() > 0);
    doc[DATA_FIELD]["AI4"] = threshold_value<int>(analogRead(AI4), threshold);
    active = active || (doc[DATA_FIELD]["AI4"].as<double>() > 0);
    doc[DATA_FIELD]["AI5"] = threshold_value<int>(analogRead(AI5), threshold);
    active = active || (doc[DATA_FIELD]["AI5"].as<double>() > 0);
    if (active > 0) {
      if (raw) {
        Serial.print(doc[DATA_FIELD]["AI1"].as<double>());
        Serial.print(" "); 
        Serial.print(doc[DATA_FIELD]["AI2"].as<double>());
        Serial.print(" "); 
        Serial.print(doc[DATA_FIELD]["AI3"].as<double>());
        Serial.print(" "); 
        Serial.print(doc[DATA_FIELD]["AI4"].as<double>());
        Serial.print(" "); 
        Serial.print(doc[DATA_FIELD]["AI5"].as<double>());
        Serial.print("\n");
      } else {
        serializeJson(doc, out);
        Serial.print(out);
        Serial.print("\n");
      }
    }
    prev_time = now;
  }
  delayMicroseconds(delay);
}
