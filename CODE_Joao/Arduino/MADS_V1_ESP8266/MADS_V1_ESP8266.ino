#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_LIS3DH.h>
#include <Adafruit_SHT31.h>
#include <DHT.h>
#include <math.h>

#define VERSION "1.1.0"
#define BAUD_RATE 115200

// Topmost field in the output JSON
#define DATA_FIELD "data"

// I²C addresses
#define LIS3DH_ADDRESS      0x19    // Adafruit accelerometer
#define SHT31_ADDR          0x44    // Grove Temperature & Humidity Sensor

// DHT11 sensor
#define DHTPIN   D5       
#define DHTTYPE  DHT11
DHT dht(DHTPIN, DHTTYPE);           // DHT11 Temperature & Humidity Sensor

// Grove Sound Sensor v1.7
const int SOUND_PIN   = A0;      // Sound sensor analog input
const int NUM_SAMPLES = 500;     // Number of readings per window
const int SAMPLE_US   = 20;      // µs between readings

// Vibration sensor SW-420
#define VIB_PIN  D7

// Use the same sampling interval as the accelerometer code (200 ms → 5 Hz)
#define SAMPLE_DELAY_MS  200 

Adafruit_LIS3DH lis  = Adafruit_LIS3DH();
Adafruit_SHT31 sht31 = Adafruit_SHT31();

// Accelerometer offsets in g
float offsetX = 0.0;
float offsetY = 0.0;
float offsetZ = 0.0;

void setup() {
  Serial.begin(BAUD_RATE);
  while(!Serial);
  Wire.begin();  // On ESP8266 this defaults to SDA=D2, SCL=D1
  Serial.println("\nMADS "  VERSION " - Sensor Fusion Test\n");

  pinMode(LED_BUILTIN, OUTPUT);

  // --- Initialize SHT31 sensor ---
  Serial.println("Initializing SHT31 sensor...");
  if (! sht31.begin(SHT31_ADDR)) {
    Serial.println("Error: couldn't find SHT31");
    while (1) delay(10);
  }
  Serial.println("SHT31 initialized successfully!");

  // --- Initialize LIS3DH accelerometer ---
  Serial.println("Initializing LIS3DH accelerometer...");
  if (! lis.begin(LIS3DH_ADDRESS)) {
    Serial.println("Failed to initialize LIS3DH!");
    while (1) delay(10);
  }
  lis.setRange(LIS3DH_RANGE_2_G);       // ±2g full-scale
  lis.setDataRate(LIS3DH_DATARATE_50_HZ);
  delay(100);
  Serial.println("LIS3DH initialized successfully!");
  
  // --- Initialize DHT11 sensor ---
  Serial.println("Initializing DHT11 sensor...");
  dht.begin();
  delay(100);
  float temp = dht.readTemperature();
  if (isnan(temp)) {
    Serial.println("Error: couldn't read from DHT11!");
    while (1) delay(10);
  }
  Serial.println("DHT11 initialized successfully!");

  // --- Initial test of the sound sensor ---
  Serial.println("Testing sound sensor...");
  int soundReading = analogRead(SOUND_PIN);
  Serial.print("Initial sound sensor reading (0-1023): ");
  Serial.println(soundReading);
  delay(500);

  // --- Set up vibration sensor ---
  pinMode(VIB_PIN, INPUT);

  Serial.println("Setup complete!");
  delay(1000);
}

template<typename T>
T threshold_value(T value, T threshold) {
  return value > threshold ? value : 0;
}

void loop() {
  static unsigned long prev_time = 0;
  unsigned long current_time = millis();
  static bool onoff = LOW;
  unsigned long now = micros();

  // --- Accelerometer ---
  sensors_event_t event;
  lis.getEvent(&event);

  // convert to g and apply offsets
  float ax = event.acceleration.x / 9.80665 - offsetX;
  float ay = event.acceleration.y / 9.80665 - offsetY;
  float az = event.acceleration.z / 9.80665 - offsetZ;

  // vector magnitude (resultant acceleration) and vibration
  float magnitude = sqrt(ax * ax + ay * ay + az * az);
  float vibration = fabs(magnitude - 1.0);

  // --- Temperature and Humidity --- 
  // Read temperature (°C) and humidity (%RH)
  float sht31_temperature = sht31.readTemperature();
  float sht31_humidity    = sht31.readHumidity();
  float dht_temperature   = dht.readTemperature();
  float dht_humidity      = dht.readHumidity();

  // --- Sound Level ---
  int vMin = 1023, vMax = 0;
  // fast reading window (~10ms)
  for (int i = 0; i < NUM_SAMPLES; i++) {
    int v = analogRead(SOUND_PIN);
    if (v < vMin) vMin = v;
    if (v > vMax) vMax = v;
    delayMicroseconds(SAMPLE_US);
  }
  int sound_level = vMax - vMin;  // peak-to-peak value 0–1023

  // Vibration sensor reading
  int vibration_state = !digitalRead(VIB_PIN);
  

  // --- Json Output ---
  if (current_time - prev_time >= SAMPLE_DELAY_MS*4) {
    onoff = !onoff;  // Toggle LED state
    digitalWrite(LED_BUILTIN, onoff);

    // Prepare JSON output
    char buf[256];
    snprintf(buf, sizeof(buf),
      "{\"millis\":%lu,\"data\":"
        "{\"X\":%.3f,\"Y\":%.3f,\"Z\":%.3f,"
        "\"magnitude\":%.3f,\"vibration\":%.3f,"
        "\"sht31_temperature\":%.2f,\"sht31_humidity\":%.2f,"
        "\"dht_temperature\":%.2f,\"dht_humidity\":%.2f,"
        "\"sound_level\":%d,\"vibration_state\":%d}"
      "}",
      millis(),
      ax, ay, az,
      magnitude, vibration,
      sht31_temperature, sht31_humidity,
      dht_temperature, dht_humidity,
      sound_level, vibration_state
    );
    Serial.println(buf);

    prev_time = now;
  }

  delay(SAMPLE_DELAY_MS);
}
