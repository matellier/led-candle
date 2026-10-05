// Stage 3: side-by-side diffuser comparison. Two 5mm white LEDs, each in a different flame print,
// both driven by the same stage 2 mode 3 flicker so any difference you see comes from the print.
// Wiring: D9  -> 150 ohm -> LED A (white PETG flame)  -> GND
//         D10 -> 150 ohm -> LED B (clear PETG flame)  -> GND
// See hardware/schematics/stage3-two-led-compare.md
//
// Cycle (default): both on 10s -> A only 10s -> B only 10s -> repeat. Phase is printed over serial.
// Serial (9600): 'c' = cycle, 'x' = hold both, 'a' = hold A only, 'b' = hold B only.

#include <math.h>

const uint8_t LED_A_PIN = 9;
const uint8_t LED_B_PIN = 10;          // must be a PWM pin (3, 5, 6, 9, 10, 11) for flicker
const uint8_t TICK_MS = 10;
const float GAMMA = 2.2;

const unsigned long PHASE_MS = 10000;  // how long each cycle phase lasts

// --- Flicker tuning (stage 2 mode 3 values) ---
const float LEVEL_MAX = 255;
const float LEVEL_MIN = 190;
const uint16_t TARGET_MIN_MS = 60;
const uint16_t TARGET_MAX_MS = 250;
const float SMOOTHING = 0.15;
const float JITTER = 6;
const uint16_t GUST_GAP_MIN_MS = 3000;
const uint16_t GUST_GAP_MAX_MS = 12000;
const uint16_t GUST_LEN_MIN_MS = 150;
const uint16_t GUST_LEN_MAX_MS = 500;
const float GUST_LEVEL_MIN = 110;

enum Phase : uint8_t { BOTH, A_ONLY, B_ONLY };

bool cycling = true;
Phase phase = BOTH;
unsigned long phaseEnd = 0;

float level = LEVEL_MAX;
float target = LEVEL_MAX;
unsigned long nextTick = 0;
unsigned long nextTarget = 0;
unsigned long nextGust = 0;
unsigned long gustEnd = 0;

bool due(unsigned long deadline, unsigned long now) {
  return (long)(now - deadline) >= 0;
}

float randomLevel(float lo, float hi) {
  return random((long)lo, (long)hi + 1);
}

void setup() {
  Serial.begin(9600);
  pinMode(LED_A_PIN, OUTPUT);
  pinMode(LED_B_PIN, OUTPUT);
  randomSeed(analogRead(A0));

  unsigned long now = millis();
  nextGust = now + random(GUST_GAP_MIN_MS, GUST_GAP_MAX_MS + 1);
  phaseEnd = now + PHASE_MS;
  printPhase();
}

void loop() {
  readSerial();

  unsigned long now = millis();
  if (cycling && due(phaseEnd, now)) {
    phase = (Phase)((phase + 1) % 3);
    phaseEnd = now + PHASE_MS;
    printPhase();
  }

  if (!due(nextTick, now)) return;
  nextTick = now + TICK_MS;

  uint8_t pwm = toPwm(flickerGust(now));
  analogWrite(LED_A_PIN, phase != B_ONLY ? pwm : 0);
  analogWrite(LED_B_PIN, phase != A_ONLY ? pwm : 0);
}

float flickerGust(unsigned long now) {
  if (due(nextGust, now)) {
    gustEnd = now + random(GUST_LEN_MIN_MS, GUST_LEN_MAX_MS + 1);
    nextGust = gustEnd + random(GUST_GAP_MIN_MS, GUST_GAP_MAX_MS + 1);
    target = randomLevel(GUST_LEVEL_MIN, LEVEL_MIN);
    nextTarget = gustEnd;
  }
  if (due(nextTarget, now)) {
    target = randomLevel(LEVEL_MIN, LEVEL_MAX);
    nextTarget = now + random(TARGET_MIN_MS, TARGET_MAX_MS + 1);
  }
  level += (target - level) * SMOOTHING;

  float flutter = random((long)(-JITTER * 10), (long)(JITTER * 10) + 1) / 10.0;
  return level + flutter;
}

uint8_t toPwm(float perceived) {
  perceived = constrain(perceived, 0, 255);
  return (uint8_t)(255.0 * pow(perceived / 255.0, GAMMA) + 0.5);
}

void readSerial() {
  if (!Serial.available()) return;
  char c = Serial.read();
  switch (c) {
    case 'c': cycling = true;  phase = BOTH;   phaseEnd = millis() + PHASE_MS; break;
    case 'x': cycling = false; phase = BOTH;   break;
    case 'a': cycling = false; phase = A_ONLY; break;
    case 'b': cycling = false; phase = B_ONLY; break;
    default: return;
  }
  printPhase();
}

void printPhase() {
  Serial.print(cycling ? "cycle: " : "hold: ");
  switch (phase) {
    case BOTH:   Serial.println("both A+B"); break;
    case A_ONLY: Serial.println("A only (D9, white PETG)"); break;
    case B_ONLY: Serial.println("B only (D10, clear PETG)"); break;
  }
}
