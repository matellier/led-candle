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

## Stage 3 — Diffuser / flame print experiments ← **current**
- [x] Side-by-side sketch: `firmware/arduino/stage3_compare/` (A=D9, B=D10; cycles both → A → B, 10 s each)
- [x] Schematic: `hardware/schematics/stage3-two-led-compare.md`
- [ ] Test 1: white PETG (A) vs clear PETG (B), same flame model

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

## Stage 4 — 4-pin RGB LED
- [ ] Identify common-anode vs common-cathode (multimeter diode test)
- [ ] Wire R/G/B to D9/D10/D11, one resistor per color
- [ ] Color presets: warm white candle, red, green, orange, blue, purple, plus holiday cycles
- [ ] Flicker applied to the color mix (brightness flicker + slight hue shift toward orange)
- [ ] Re-run the best Stage 3 diffuser with RGB. RGB LEDs often show color fringing that the print has to blend

## Stage 5 — Brightness decision ("visible from the sidewalk")
A single 5 mm LED at ~13 mA may be too dim through a diffuser behind window glass. Test the best
5 mm result outside at dusk **and** after full dark. If too dim, move to (recommended order):
1. **SK6812 RGBW addressable LED** (NeoPixel family). A true white channel gives a warm candle color, there's
   one data pin, and full color. Trade-off: about 1 mA quiescent draw even when "off" → needs a power-cut
   transistor for battery life.
2. High-brightness LED + MOSFET driver (e.g. 0.5–1 W warm white). Brightest, but white only.

## Stage 6 — Candle body
- [ ] Full candle shell, flame mount, top/cap
- [ ] Battery compartment with access door
- [ ] Mount for the electronics board and light sensor window

## Stage 7 — Power, sensing, and the small controller
- [ ] Move off the Uno to a small, low-power controller (ATtiny85 or 3.3 V Pro Mini). Sleep between flicker updates
- [ ] Battery choice sized from measured current. Measure real mA in Stage 5 before picking
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
| Final LED | 5 | SK6812 RGBW if the 5 mm LED is too dim |
| Controller | 7 | ATtiny85 (cheap, tiny, enough PWM for 1 addressable LED) |
| Battery | 7 | Decide after measuring current |
