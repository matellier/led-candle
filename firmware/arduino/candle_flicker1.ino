#include <Adafruit_NeoPixel.h>

// simple led flicker

#define PIN 6
Adafruit_NeoPixel strip(1, PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  strip.begin();
}

void loop() {

  int r = 200 + random(55);
  int g = 90 + random(40);
  int b = random(25);

  strip.setPixelColor(0, r, g, b);
  strip.show();

  delay(random(30,120));
}
