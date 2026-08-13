#include <Adafruit_NeoPixel.h>

// simple led flicker with inductor coil to flicker candle

#define LED_PIN 6
#define COIL_PIN 7  // solenoid/inductor coil (100mH/300ohm), driven directly from GPIO — flyback diode across coil, no transistor

Adafruit_NeoPixel strip(1, LED_PIN, NEO_GRB + NEO_KHZ800);

// --- Coil pulse tuning (bench-adjustable) ---
const uint8_t COIL_PULSE_MS = 3;             // how long the coil stays energized per pulse (1-5ms)
const uint16_t COIL_INTERVAL_MIN_MS = 200;   // shortest gap between pulses
const uint16_t COIL_INTERVAL_MAX_MS = 1500;  // longest gap between pulses
const uint8_t COIL_SYNC_CHANCE_PCT = 70;     // % chance a coil pulse rides along with an LED flicker update, rest fire independently

unsigned long nextFlickerTime = 0;
unsigned long nextCoilTime = 0;

void setup() {
  strip.begin();

  pinMode(COIL_PIN, OUTPUT);
  digitalWrite(COIL_PIN, LOW);

  randomSeed(analogRead(A0));  // A0 left unconnected for noise; swap pin if that changes
}

void loop() {
  unsigned long now = millis();

  if (now >= nextFlickerTime) {
    flickerLed();
    nextFlickerTime = now + random(30, 120);

    // Most flicker updates also nudge the coil so the physical kick tracks
    // the visual change, but not every time — keeps it from looking metronomic.
    if (random(100) < COIL_SYNC_CHANCE_PCT) {
      pulseCoil();
      nextCoilTime = now + random(COIL_INTERVAL_MIN_MS, COIL_INTERVAL_MAX_MS + 1);
    }
  }

  if (now >= nextCoilTime) {
    pulseCoil();
    nextCoilTime = now + random(COIL_INTERVAL_MIN_MS, COIL_INTERVAL_MAX_MS + 1);
  }
}

void flickerLed() {
  int r = 200 + random(55);
  int g = 90 + random(40);
  int b = random(25);

  strip.setPixelColor(0, r, g, b);
  strip.show();
}

// Kicks the magnet via the coil. Pulse is short (1-5ms) so the blocking
// delay() here is negligible next to the LED's 30-120ms flicker cadence.
void pulseCoil() {
  digitalWrite(COIL_PIN, HIGH);
  delay(COIL_PULSE_MS);
  digitalWrite(COIL_PIN, LOW);
}
