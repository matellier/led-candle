// Stage 2: flicker on a single 5mm white LED. Three algorithms to compare by eye.
// Wiring unchanged from stage 1: D9 -> 150 ohm -> LED anode ; cathode -> GND
//
// Select a mode over serial (9600 baud): send '1', '2' or '3'. The choice is saved
// in EEPROM, so it survives resets/power cycles.
//   1 = random jump   (port of the old candle_flicker1 - choppy baseline)
//   2 = smooth walk   (eases toward a new random target every 60-250ms)
//   3 = smooth walk + fast flutter + occasional "gust" dips
//
// Levels are in perceived brightness (0-255) and gamma corrected on output, so a dip
// to 50% looks like half as bright rather than barely changing.

#include <EEPROM.h>
#include <math.h>

const uint8_t LED_PIN = 9;
const uint8_t EEPROM_MODE_ADDR = 0;
const uint8_t TICK_MS = 10;            // output update rate (100 Hz)
const float GAMMA = 2.2;

// --- Tuning (bench-adjustable) ---
const float LEVEL_MAX = 255;           // brightest point of normal flicker
const float LEVEL_MIN = 190;           // dimmest point of normal flicker

const uint16_t JUMP_MIN_MS = 30;       // mode 1: time between jumps
const uint16_t JUMP_MAX_MS = 120;

const uint16_t TARGET_MIN_MS = 60;     // modes 2/3: time between new targets
const uint16_t TARGET_MAX_MS = 250;
const float SMOOTHING = 0.15;          // fraction of gap to target closed per tick; higher = snappier

const float JITTER = 6;                // mode 3: fast flutter amplitude (+/-)
const uint16_t GUST_GAP_MIN_MS = 3000; // mode 3: time between gusts
const uint16_t GUST_GAP_MAX_MS = 12000;
const uint16_t GUST_LEN_MIN_MS = 150;  // mode 3: how long a gust holds the flame down
const uint16_t GUST_LEN_MAX_MS = 500;
const float GUST_LEVEL_MIN = 110;      // mode 3: deepest gust dip

uint8_t mode = 3;
float level = LEVEL_MAX;
float target = LEVEL_MAX;
unsigned long nextTick = 0;
unsigned long nextTarget = 0;
unsigned long nextGust = 0;
unsigned long gustEnd = 0;

// Rollover-safe "has this time arrived" check for millis() deadlines.
bool due(unsigned long deadline, unsigned long now) {
  return (long)(now - deadline) >= 0;
}

float randomLevel(float lo, float hi) {
  return random((long)lo, (long)hi + 1);
}

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  randomSeed(analogRead(A0));  // A0 left unconnected for noise

  uint8_t saved = EEPROM.read(EEPROM_MODE_ADDR);
  if (saved >= 1 && saved <= 3) mode = saved;

  nextGust = millis() + random(GUST_GAP_MIN_MS, GUST_GAP_MAX_MS + 1);
  printMode();
}

void loop() {
  readSerial();

  unsigned long now = millis();
  if (!due(nextTick, now)) return;
  nextTick = now + TICK_MS;

  float out;
  switch (mode) {
    case 1:  out = flickerJump(now); break;
    case 2:  out = flickerSmooth(now); break;
    default: out = flickerGust(now); break;
  }
  writeLevel(out);
}

float flickerJump(unsigned long now) {
  if (due(nextTarget, now)) {
    level = randomLevel(LEVEL_MIN, LEVEL_MAX);
    nextTarget = now + random(JUMP_MIN_MS, JUMP_MAX_MS + 1);
  }
  return level;
}

float flickerSmooth(unsigned long now) {
  if (due(nextTarget, now)) {
    target = randomLevel(LEVEL_MIN, LEVEL_MAX);
    nextTarget = now + random(TARGET_MIN_MS, TARGET_MAX_MS + 1);
  }
  level += (target - level) * SMOOTHING;
  return level;
}

float flickerGust(unsigned long now) {
  if (due(nextGust, now)) {
    gustEnd = now + random(GUST_LEN_MIN_MS, GUST_LEN_MAX_MS + 1);
    nextGust = gustEnd + random(GUST_GAP_MIN_MS, GUST_GAP_MAX_MS + 1);
    target = randomLevel(GUST_LEVEL_MIN, LEVEL_MIN);
    nextTarget = gustEnd;  // pick a normal target again once the gust passes
  }
  if (due(nextTarget, now)) {
    target = randomLevel(LEVEL_MIN, LEVEL_MAX);
    nextTarget = now + random(TARGET_MIN_MS, TARGET_MAX_MS + 1);
  }
  level += (target - level) * SMOOTHING;

  float flutter = random((long)(-JITTER * 10), (long)(JITTER * 10) + 1) / 10.0;
  return level + flutter;
}

void writeLevel(float perceived) {
  perceived = constrain(perceived, 0, 255);
  uint8_t pwm = (uint8_t)(255.0 * pow(perceived / 255.0, GAMMA) + 0.5);
  analogWrite(LED_PIN, pwm);
}

void readSerial() {
  if (!Serial.available()) return;
  char c = Serial.read();
  if (c >= '1' && c <= '3') {
    mode = c - '0';
    EEPROM.update(EEPROM_MODE_ADDR, mode);
    nextTarget = 0;
    printMode();
  } else if (c == '?') {
    printMode();
  }
}

void printMode() {
  Serial.print("stage2_flicker mode ");
  Serial.print(mode);
  switch (mode) {
    case 1:  Serial.println(": random jump"); break;
    case 2:  Serial.println(": smooth walk"); break;
    default: Serial.println(": smooth walk + flutter + gusts"); break;
  }
}
