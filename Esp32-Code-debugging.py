#include <WiFi.h>
#include <WiFiUdp.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <esp_system.h>

// =====================
// CONFIGURATION
// =====================
const char* ssid     = "De Klerk 24";       // your WiFi SSID
const char* password = "Joshua500@";        // your WiFi password
const char* udpAddress = "239.0.0.57";      // Multicast group IP
const int udpPort = 12345;                  // must match Python script

// =====================
// GLOBAL OBJECTS
// =====================
WiFiUDP udp;
Adafruit_MPU6050 mpu;

// Streaming control
bool streaming = true;
int sampleDelay = 100;  // milliseconds between packets

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(50); // Short timeout for reading commands
  delay(100);

  // ----- Connect to WiFi -----
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  int attempt = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    attempt++;
    if (attempt > 20) {  // After 10 seconds, break loop
      Serial.println("\nFailed to connect to WiFi. Please check SSID/password.");
      break;
    }
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.print("ESP32 IP address: ");
    Serial.println(WiFi.localIP());
  }

  // ----- Initialize MPU6050 -----
  Wire.begin(21, 22); // SDA=21, SCL=22
  if (!mpu.begin()) {
    Serial.println("MPU6050 not found! Check wiring and power.");
    while (1) delay(1000);
  }
  Serial.println("MPU6050 detected and initialized.");
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  // ----- Start UDP -----
  udp.begin(udpPort);
  Serial.print("UDP started on port ");
  Serial.println(udpPort);
}

void resetProcess() {
  streaming = true;
  sampleDelay = 100;
  Serial.println("Process variables reset. Streaming ON, sampleDelay=100ms.");
}

void loop() {
  // --- Check for commands from Serial Monitor ---
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.equalsIgnoreCase("stop")) {
      streaming = false;
      Serial.println("Streaming stopped.");
    }
    else if (command.equalsIgnoreCase("continue")) {
      streaming = true;
      Serial.println("Streaming resumed.");
    }
    else if (command.equalsIgnoreCase("restart")) {
      Serial.println("Restarting ESP32...");
      delay(100);
      esp_restart();
    }
    else if (command.startsWith("rate")) {
      int newRate = command.substring(4).toInt();
      if (newRate > 0) {
        sampleDelay = newRate;
        Serial.print("Sampling delay set to ");
        Serial.print(sampleDelay);
        Serial.println(" ms");
      } else {
        Serial.println("Invalid rate value.");
      }
    }
    else if (command.equalsIgnoreCase("reset")) {
      resetProcess();
    }
    else if (command.equalsIgnoreCase("status")) {
      Serial.println("--- STATUS ---");
      Serial.print("Streaming: ");
      Serial.println(streaming ? "ON" : "OFF");
      Serial.print("Sample delay: ");
      Serial.print(sampleDelay);
      Serial.println(" ms");
      Serial.print("IP Address: ");
      Serial.println(WiFi.localIP());
      Serial.println("--------------");
    }
    else {
      Serial.print("Unknown command: ");
      Serial.println(command);
    }
  }

  // --- Only send sensor data if streaming is ON ---
  if (streaming) {
    sensors_event_t accel, gyro, temp;
    mpu.getEvent(&accel, &gyro, &temp);

    String jsonData = "{";
    jsonData += "\"accel_x\":" + String(accel.acceleration.x, 2) + ",";
    jsonData += "\"accel_y\":" + String(accel.acceleration.y, 2) + ",";
    jsonData += "\"accel_z\":" + String(accel.acceleration.z, 2) + ",";
    jsonData += "\"gyro_x\":" + String(gyro.gyro.x, 2) + ",";
    jsonData += "\"gyro_y\":" + String(gyro.gyro.y, 2) + ",";
    jsonData += "\"gyro_z\":" + String(gyro.gyro.z, 2) + ",";
    jsonData += "\"temp_c\":" + String(temp.temperature, 2);
    jsonData += "}";

    udp.beginPacket(udpAddress, udpPort);
    udp.print(jsonData);
    udp.endPacket();

    Serial.print("Sent: ");
    Serial.println(jsonData);

    delay(sampleDelay);
  }
}
