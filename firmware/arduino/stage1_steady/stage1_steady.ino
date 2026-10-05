// Stage 1: single 5mm white LED, steady on.
// Wiring: D9 -> 150 ohm -> LED anode (long lead) ; LED cathode (short lead, flat side) -> GND
// See hardware/schematics/stage1-single-led.md

const uint8_t LED_PIN = 9;       // PWM pin (Timer1) - same pin flicker will use in stage 2
const uint8_t BRIGHTNESS = 255;  // 0-255; 255 = fully on

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  analogWrite(LED_PIN, BRIGHTNESS);
  Serial.print("stage1_steady: D9 brightness=");
  Serial.println(BRIGHTNESS);
}

void loop() {
}
