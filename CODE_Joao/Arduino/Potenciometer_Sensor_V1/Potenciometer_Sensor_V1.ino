#include <ArduinoJson.h>

#define VERSION    "0.1.0"
#define BAUD_RATE  115200
#define POT_PIN    A5         // Analog pin where the potentiometer is connected
#define V_REF      5.0        // ADC reference voltage (normally 5V)
#define ADC_RES    1023.0     // ADC resolution (10 bits → 0..1023)

// Time between samples (in milliseconds)
const unsigned long SAMPLE_INTERVAL = 100UL;

StaticJsonDocument<200> doc;
unsigned long lastSampleTime = 0;

void setup() {
  Serial.begin(BAUD_RATE);
  while (!Serial) { ; }  // wait for Serial port to be ready
  Serial.print(F("# Starting potentiometer reading v"));
  Serial.println(VERSION);
}

void loop() {
  unsigned long now = millis();
  if (now - lastSampleTime >= SAMPLE_INTERVAL) {
    lastSampleTime = now;

    // Raw ADC reading (0..1023)
    int rawValue = analogRead(POT_PIN);
    // Convert to voltage (0..5V)
    float voltage = (rawValue / ADC_RES) * V_REF;

    // Build JSON: {"millis":1234, "pot_raw":512, "pot_volt":2.50}
    doc.clear();
    doc["millis"]   = now;
    doc["pot_raw"]  = rawValue;
    doc["pot_volt"] = voltage;

    // Serialize and send over Serial
    serializeJson(doc, Serial);
    Serial.println();
  }
}
