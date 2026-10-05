# LED Candle — Roadmap

Goal: battery-powered window candles that are **clearly visible from the sidewalk**, with realistic
flicker and holiday colors. Start at the simplest possible circuit and add one thing at a time.

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

## Stage 3 — Diffuser / flame print experiments ⏸ (resumes after Stage 5)
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
- Candle color = RGB amber mix (R high, G ~40–50%, B ~0); holiday colors come for free
- One data pin for any number of pixels; same Adafruit_NeoPixel library as `candle_flicker1.ino`
- Runs directly from one 18650 (WS2812B rated 3.5–5.3 V)
- Trade-off: no true warm white. If a white mode is wanted, **SK6812 RGBW "WW"** is a drop-in upgrade (`NEO_GRBW`)
- Rejected: three 5mm LEDs in one flame (still dim); 12V 5050 strip (needs 12V → 3 cells or a booster)

Prototype circuit (Uno): D6 → 330 Ω → strip DIN; strip 5V/GND from the Uno 5V/GND; 470–1000 µF cap across 5V/GND;
brightness capped in code to stay within USB current.

**Open questions (answer before writing the sketch):**
- [ ] Parts on hand: 330 Ω (220–470 OK) resistor? 470–1000 µF / ≥6.3 V capacitor?
- [ ] Flame cavity inside size (W × H): decides straight 3–4 pixel segment vs wrapped around a post
- [ ] WS2812B strip density: 30 / 60 / 144 pixels per meter?

Next:
- [ ] Sketch: amber mode 3 flicker on 1 / 3 / 4 pixels, selectable over serial
- [ ] Sidewalk test at ~50 ft (dusk and full dark): how many pixels it takes
- [ ] Measure current draw at the chosen pixel count (feeds the Stage 7 battery sizing)

## Stage 6 — Candle body
- [ ] Full candle shell, flame mount, top/cap
- [ ] Battery compartment with access door
- [ ] Mount for the electronics board and light sensor window

## Stage 7 — Power, sensing, and the small controller
- [ ] Move off the Uno to a small, low-power controller (ATtiny85 or 3.3 V Pro Mini). Sleep between flicker updates
- [ ] Battery: **18650** (leaning). Name-brand protected cells, removable + external charger (not charged inside the candle).
      Estimate: 4 px amber flicker ≈ 60 mA → ~8 nights at 6 h/night per 3000 mAh cell; full color ≈ 2 nights
- [ ] Power-cut transistor for the LEDs (WS2812B draws ~1 mA/pixel even when dark)
- [ ] On/off: **photocell at dusk + 6-hour run timer** (classic window-candle behavior), with optional manual switch
- [ ] Battery life target (TBD, e.g. a full holiday season on one set)

## Stage 8 — Production
- [ ] Final schematic + perfboard or small PCB in KiCad
- [ ] Build N candles; document the build steps
- [ ] Final firmware with color/holiday mode selection (button or timer-based)

---

## Open decisions (decided at the stage where they matter)
| Decision | Stage | Current recommendation |
|----------|-------|------------------------|
| Flicker algorithm | 2 | ✅ Mode 3: smooth walk + flutter + gusts |
| RGB LED type | 4 | Whatever is on hand; common-cathode is simpler to code |
| Final LED | 5 | ✅ WS2812B (on hand); SK6812 RGBW WW if a true white is wanted |
| Controller | 7 | ATtiny85 (cheap, tiny, enough PWM for 1 addressable LED) |
| Battery | 7 | 18650, protected, removable; confirm after measuring current |
