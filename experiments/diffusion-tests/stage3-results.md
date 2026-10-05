# Stage 3 — Diffuser test 1: white PETG vs clear PETG

**Date:** 2026-10-05
**Setup:** `firmware/arduino/stage3_compare/`. Two 5mm white LEDs (150 Ω each) on D9/D10, same mode 3 flicker,
cycling both → A → B every 10 s. A = white PETG flame (15% infill), B = clear PETG flame, same model.

## Result
- Sketch and wiring worked as expected.
- **Main finding: a 5mm LED at ~13 mA is too dim to enjoy from ~50 ft**, whichever filament is used.
  The filament comparison doesn't matter until the light source is brighter.
- White vs clear preference: not recorded. Repeat this test with the new LEDs.

## Decision
Move to WS2812B addressable LEDs (already on hand). See ROADMAP Stage 5.
