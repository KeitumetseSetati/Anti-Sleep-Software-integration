#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

Adafruit_MPU6050 mpu;

void setup()
{
  Serial.begin(115200);
  delay(1000);
  Serial.println("=== ESP32 + MPU6050 Communication Test ===");

  Wire.begin(21, 22); // SDA, SCL
  if (!mpu.begin())
  {
    Serial.println("MPU6050 not found! Check wiring and power.");
    while (1)
      delay(1000);
  }
  Serial.println("MPU6050 detected and initialized.");

  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  Serial.println("time_ms,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,temp_c");
}

void loop()
{
  sensors_event_t accel, gyro, temp;
  mpu.getEvent(&accel, &gyro, &temp);

  Serial.print(millis());
  Serial.print(",");
  Serial.print(accel.acceleration.x);
  Serial.print(",");
  Serial.print(accel.acceleration.y);
  Serial.print(",");
  Serial.print(accel.acceleration.z);
  Serial.print(",");
  Serial.print(gyro.gyro.x);
  Serial.print(",");
  Serial.print(gyro.gyro.y);
  Serial.print(",");
  Serial.print(gyro.gyro.z);
  Serial.print(",");
  Serial.println(temp.temperature);

  delay(100); // ~10 samples per second
}
