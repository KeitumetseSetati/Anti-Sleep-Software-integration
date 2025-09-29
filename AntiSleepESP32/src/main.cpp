#include <Arduino.h>

// Mock IR sensor reading
int simulatedIrRead()
{
  // Return a simulated IR sensor reading (e.g., 0-1023)
  return 512;
}

// Mock MPU sensor reading
int simulatedMpuRead()
{
  // Return a simulated MPU sensor reading (e.g., 0-360)
  return 180;
}

#define SIMULATION_MODE true // Change to false for real hardware

void setup()
{
  Serial.begin(115200);
  delay(1000);
  Serial.println("=== Anti-Sleep System Started ===");
}

bool detectBlink(int irValue)
{
  float difference = abs(irValue - 512.0);
  if (difference > (512.0 * 0.7))
  {
    static unsigned long lastBlinkTime = 0;
    if (millis() - lastBlinkTime > 300)
    {
      lastBlinkTime = millis();
      return true;
    }
  }
  return false;
}

void checkSleepPatterns()
{
  static unsigned long lastBlinkTime = 0;
  unsigned long timeSinceBlink = millis() - lastBlinkTime;
  if (timeSinceBlink > 10000 && lastBlinkTime > 0)
  {
    Serial.println(" POSSIBLE ASLEEP! No blinking detected.");
  }
}

int simulatedAnalogRead()
{
  return simulatedIrRead(); // Use the simulated IR sensor reading
}

void loop()
{
  int irValue;

#if SIMULATION_MODE
  irValue = simulatedAnalogRead();
#else
  irValue = analogRead(34); // Example IR sensor pin
#endif

  if (detectBlink(irValue))
  {
    static int blinkCount = 0;
    blinkCount++;
    Serial.printf(" Blink detected! Total: %d\n", blinkCount);
  }

  static unsigned long lastCheckTime = 0;
  if (millis() - lastCheckTime > 2000)
  {
    lastCheckTime = millis();
    checkSleepPatterns();
  }

  delay(100);
}