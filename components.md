# Components

## Stage 5 prototype — ESP32 + WLED (on hand)

Goal: one working candle on parts already owned, before buying anything for the other 11.

| Part | Spec | Notes |
|------|------|-------|
| ESP32 DevKit | ESP32-WROOM-32, 38-pin, micro-USB | Mounted on a green screw-terminal breakout board (terminals labelled `5V`, `GND`, `P16`, …). Runs WLED |
| USB wall charger + cable | 5 V, USB-A → micro-USB | Powers the ESP32 and the strip. Check the charger's amp rating on its label |
| WS2812B strip | 5 V addressable RGB, **144 LED/m**, uncut reel | Pads `+5V DIN GND`. Factory JST SM 3-pin pigtail: red = 5V, white = GND, green = DIN, plus loose thick red/white power leads |
| Spare JST SM 3-pin pigtail | Mates with the strip connector | Bare ends go straight into the screw terminals |
| Resistor | 150 Ω 1/4 W | Data line series resistor (330 Ω is the textbook value; 150 Ω is fine for a short wire) |
| Flame post | 3D-printed, ~16 mm diameter (LED faces ~20 mm) | Strip wraps around it in a spiral |
| Filament | White PETG, clear PETG | Prusa printer; starting 15% infill |
| Capacitor | 470 µF 16 V electrolytic | Across 5V/GND at the screw terminals, stripe → GND. Not required at the prototype's capped brightness, but on hand so it goes in |

## Production — 12 candles (buy only after the prototype works)

Board choice is not final until the prototype is done. Leaning toward the ESP32-C3 Super Mini: it's smaller,
has USB-C and runs the same WLED.

| Part | Qty | Notes |
|------|-----|-------|
| ESP32-C3 Super Mini | 15 | 3 spares |
| 5 V USB charger, ≥ 1 A | 12 | Name brand. Confirm the rating after measuring the prototype's current draw |
| USB cable, white | 12 | Long enough to reach from the outlet to the sill |
| WS2812B 144/m strip | 12 × N px | N from the sidewalk test. ~1.25 m total at 15 px. Check the reel length on hand |
| Electrolytic cap 470–1000 µF, ≥ 6.3 V | 12 | |
| Resistor 330 Ω (150–470 OK) | 12 | |
| 74AHCT125 level shifter | 12 | Only if the prototype shows 3.3 V data glitches |

## Shelved

| Part | Why |
|------|-----|
| Arduino Uno (clone), CH340 → `/dev/ttyUSB0` | Stage 1–3 bench prototype. No network for Home Assistant |
| Pro Mini 328 (lot) | Battery plan dropped. No network, and a second board type doubles the firmware work |
| 5mm white LEDs ×2 + 150 Ω | Stage 1–3. Too dim at 50 ft |
| 5mm RGB LED, 4-pin | Stage 4 skipped, superseded by WS2812B |
