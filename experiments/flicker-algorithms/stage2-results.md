# Stage 2 — Flicker algorithm comparison

**Date:** 2026-10-05
**Setup:** 5mm white diffused LED, D9 → 150 Ω → LED → GND, Arduino Uno clone
**Sketch:** `firmware/arduino/stage2_flicker/` (switch modes over serial: `1`/`2`/`3`)

| Mode | Algorithm | Result |
|------|-----------|--------|
| 1 | Random jump 190–255 every 30–120 ms | Choppy baseline |
| 2 | Smooth walk: ease 15%/tick toward new random target every 60–250 ms | Smooth, calm |
| 3 | Mode 2 + ±6 flutter + gust dip to 110–190 for 150–500 ms every 3–12 s | **Best — chosen** |

Levels are perceived brightness (0–255) with gamma 2.2 applied on output.

**Decision:** Mode 3 is the default (`mode = 3`). Tuning constants are left at the values above
until it's tested inside the printed flame.
