# LED Candle — Roadmap

Goal: 12 multi-color window candles that are **clearly visible from the sidewalk (~50 ft)**, with realistic
flicker and holiday colors, controlled from Home Assistant. Start at the simplest possible circuit and add one thing at a time.

> The earlier magnet/inductor flame experiments (`firmware/arduino/candle_flicker2.ino`) are retired.
> `candle_flicker1.ino` and `candle_flicker2.ino` are kept for reference only.

Each stage ends with a short note in `experiments/` saying what worked and what didn't.

---

## Stage 0 — Toolchain ✅
- [x] `arduino-cli` + `arduino:avr` core installed; Uno clone on `/dev/ttyUSB0`
- [x] Test upload + serial read verified

## Stage 1 — One white LED, steady on ✅
- [x] Sketch: `firmware/arduino/stage1_steady/`
- [x] Schematic: `hardware/schematics/stage1-single-led.md`
- [x] Wire D9 → 150 Ω → LED → GND; confirm it lights (150 Ω, lit)
- [ ] Draw schematic in KiCad (`hardware/schematics/`)

## Stage 2 — Flicker ✅
- [x] PWM flicker on D9, non-blocking (`millis()`), tunable constants — `firmware/arduino/stage2_flicker/`
- [x] Compare 3 flicker modes by eye (1 random jump, 2 smooth walk, 3 smooth + flutter + gusts) — switch via serial `1`/`2`/`3` → **mode 3 chosen**
- [x] Log what looks most like a real flame → `experiments/flicker-algorithms/stage2-results.md`
- [ ] Fine-tune mode 3 inside the flame print (carries into Stage 3)

## Stage 3 — Diffuser / flame print experiments ⏸ (resumes in Stage 7)
- [x] Side-by-side sketch: `firmware/arduino/stage3_compare/` (A=D9, B=D10; cycles both → A → B, 10 s each)
- [x] Schematic: `hardware/schematics/stage3-two-led-compare.md`
- [x] Test 1: white PETG (A) vs clear PETG (B), same flame model → 5mm LED too dim at 50 ft either way
      (`experiments/diffusion-tests/stage3-results.md`). **Diffuser tests paused until Stage 5 picks the LED.**

Change **one variable at a time**, holding the others fixed. Baseline: white PETG, 15% infill, same flame model.

| Variable | Values to try |
|----------|---------------|
| Infill % | 0 (hollow), 10, 15, 25, 40, 100 |
| Infill pattern | Gyroid, grid, honeycomb, lightning |
| Walls / perimeters | 1, 2, 3 (and vase/spiral mode, single wall) |
| LED insertion depth | Tip at flame base, middle, near top |
| LED type | Diffused (current) vs water-clear |

How to judge: photograph each test from the **same spot, same distance, phone camera on locked/manual
exposure**, in a dark room plus once from outside through the window. Record in a table in
`experiments/diffusion-tests/` (print settings, photo, notes: brightness, hot spot, glow evenness).

Expect wall count and wall thickness to matter more than infill %. Light mostly passes through the
outer walls, and dense infill mostly adds hot spots and shadows.

## Stage 4 — 4-pin RGB LED ⏭ skipped (superseded by WS2812B in Stage 5)
- [ ] Identify common-anode vs common-cathode (multimeter diode test)
- [ ] Wire R/G/B to D9/D10/D11, one resistor per color
- [ ] Color presets: warm white candle, red, green, orange, blue, purple, plus holiday cycles
- [ ] Flicker applied to the color mix (brightness flicker + slight hue shift toward orange)
- [ ] Re-run the best Stage 3 diffuser with RGB. RGB LEDs often show color fringing that the print has to blend

## Stage 5 — Brightness: move to addressable LEDs ← **current**
Decided 2026-10-05: 5mm LEDs can't be seen well from the sidewalk. Moving to **WS2812B 5V** (on hand).
- Strip on hand: **144 LED/m** WS2812B, uncut on the reel. Pixels wrap in a spiral around an **18 mm printed post**.
  Post height is sized to the pixel count the sidewalk test picks
- Candle color = RGB amber mix (R high, G ~40–50%, B ~0); holiday colors come for free
- Trade-off: no true warm white. If a white mode is wanted, **SK6812 RGBW "WW"** is a drop-in upgrade
- Rejected: three 5mm LEDs in one flame (still dim); 12V 5050 strip (needs 12V → 3 cells or a booster)

Decided 2026-10-10: **ESP32 + WLED, powered by a 5V USB charger per candle** (outlet near every window).
**Prototype one working candle on parts already on hand before buying anything for the other 11.**
- Visibility at 50 ft takes ~8–15 pixels → ~150–250 mA average. An 18650 would last only 2–3 nights, so batteries are out
- WLED gives Home Assistant control, built-in candle/fire effects, multi-candle sync and a current limiter with no custom code
- The Pro Mini 328s are shelved: no network, and a second board type doubles the firmware work

Prototype circuit (ESP32-WROOM-32 DevKit on screw-terminal breakout, on hand): P16 → 150 Ω → strip DIN; strip 5V/GND
from the breakout 5V/GND (micro-USB from a wall charger); WLED current limiter at 500 mA.
Full wiring + WLED setup: `hardware/schematics/stage5-ws2812b-post.md`.

**Open questions:**
- [x] Strip density → 144/m
- [x] Flame layout → wrapped around an 18 mm post
- [x] Data resistor on hand → 150 Ω
- [ ] 470–1000 µF / ≥6.3 V capacitor on hand?
- [ ] Does the ESP32's 3.3 V data drive the strip reliably, or does it need a 74AHCT125 level shifter?

Next:
- [ ] Wrap ~20 uncut pixels on the test post; wire to the on-hand ESP32 (P16 / 5V / GND)
- [ ] Flash WLED; set the LED count (20), GPIO 16 and the 500 mA current limit
- [ ] Use the WLED LED count to compare 4 / 8 / 12 / 15 lit
- [ ] Sidewalk test at ~50 ft (dusk and full dark): pick the pixel count and brightness
- [ ] Measure current draw at the chosen count and brightness, which sets the charger rating
- [ ] Judge WLED's Candle / Candle Multi effect against Stage 2 mode 3
- [ ] Prototype candle working → **then** order production parts (`components.md`)

## Stage 6 — Firmware + Home Assistant
- [ ] WLED config per candle: name (`candle-<room>`), LED count, GPIO, color order, current limit. Back up the
      config JSON to `firmware/wled/`
- [ ] Add to Home Assistant (WLED integration, auto-discovered)
- [ ] Automations: on at sunset, off after 6 h (replaces the photocell + timer)
- [ ] Presets: amber candle (default) plus holiday colors; one HA group or scene drives all 12
- [ ] Fallback if WLED's candle doesn't look as good as mode 3: **ESPHome** with mode 3 ported to a custom addressable light effect

## Stage 7 — Candle body
- [ ] Post height sized to the chosen pixel count; flame diffuser over it (resume the Stage 3 tests here)
- [ ] Base enclosure for the production board with the USB port reachable and a cable exit
- [ ] Full candle shell, top/cap

## Stage 8 — Production (12 candles)
- [ ] Final schematic + perfboard or small PCB in KiCad
- [ ] Build 12 candles; document the build steps
- [ ] Flash and name all 12, add them to HA, and verify the group automation

Parts list for 12: `components.md` (buy only after the prototype works).

---

## Open decisions (decided at the stage where they matter)
| Decision | Stage | Current recommendation |
|----------|-------|------------------------|
| Flicker algorithm | 2 | ✅ Mode 3: smooth walk + flutter + gusts (WLED effect may replace it, see Stage 5) |
| RGB LED type | 4 | Skipped |
| Final LED | 5 | ✅ WS2812B 144/m, wrapped around an 18 mm post; SK6812 RGBW WW if a true white is wanted |
| Pixel count per candle | 5 | Sidewalk test; expect 8–15 |
| Controller | 5 | ✅ ESP32 + WLED (2026-10-10). Prototype on the on-hand ESP32-WROOM-32 DevKit; production leaning ESP32-C3 Super Mini. Pro Mini 328 / ATtiny85 shelved |
| Firmware | 6 | WLED; ESPHome + mode 3 as fallback |
| Power | 5 | ✅ 5 V USB charger per candle. 18650 rejected (2–3 nights per charge at 15 px) |
| On/off | 6 | Home Assistant: sunset on, off after 6 h |
| Level shifter | 5 | Test without one; add a 74AHCT125 if pixels glitch |
