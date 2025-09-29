#include <Arduino.h>

#define IR_PIN 34  // IR sensor connected to ADC pin
#define BUZZER_PIN 5

unsigned long lastBlinkTime = 0;
const unsigned long blinkDebounce = 300;
const float blinkThreshold = 0.7;
int blinkCount = 0;
const float irBaseline = 512.0;

const unsigned long SLEEP_THRESHOLD = 10000;
const unsigned long LONG_BLINK_THRESHOLD = 2000;

void setup() {
  Serial.begin(115200);
  pinMode(BUZZER_PIN, OUTPUT);
}

bool detectBlink() {
  int irValue = analogRead(IR_PIN);
  float difference = abs(irValue - irBaseline);

  if (difference > (irBaseline * blinkThreshold)) {
    if (millis() - lastBlinkTime > blinkDebounce) {
      lastBlinkTime = millis();
      return true;
    }
  }
  return false;
}

void checkSleepPatterns() {
  unsigned long timeSinceBlink = millis() - lastBlinkTime;
  if (timeSinceBlink > SLEEP_THRESHOLD && lastBlinkTime > 0) {
    Serial.println("🚨 NO BLINKING DETECTED - POSSIBLE ASLEEP!");
    Serial.print("Time since last blink: ");
    Serial.println(timeSinceBlink / 1000);
    digitalWrite(BUZZER_PIN, HIGH);
    delay(2000);
    digitalWrite(BUZZER_PIN, LOW);
  }
}

void loop() {
  if (detectBlink()) {
    blinkCount++;
    Serial.print("✅ BLINK DETECTED! Total: ");
    Serial.println(blinkCount);
  }

  static unsigned long lastCheckTime = 0;
  if (millis() - lastCheckTime > 2000) {
    lastCheckTime = millis();
    checkSleepPatterns();
  }

  static unsigned long lastStatusTime = 0;
  if (millis() - lastStatusTime > 5000) {
    lastStatusTime = millis();
    Serial.print("⏰ System time: ");
    Serial.print(millis() / 1000);
    Serial.print("s | Total blinks: ");
    Serial.print(blinkCount);
    Serial.print(" | Last blink: ");
    Serial.print((millis() - lastBlinkTime) / 1000);
    Serial.println("s ago");
  }

  delay(100);
}
