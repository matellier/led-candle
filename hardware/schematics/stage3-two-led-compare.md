# Stage 3 — Two LEDs side by side (diffuser comparison)

Stage 1 circuit plus a second identical LED on D10. Sketch: `firmware/arduino/stage3_compare/`.

| Ref | Part | Value | Connection |
|-----|------|-------|------------|
| R1 | Resistor 1/4 W | 150 Ω | D9 → D1 anode |
| D1 | 5mm white LED "A" | — | In **white PETG** flame; cathode → GND |
| R2 | Resistor 1/4 W | 150 Ω | D10 → D2 anode |
| D2 | 5mm white LED "B" | — | In **clear PETG** flame; cathode → GND |

**Each LED gets its own resistor.** Don't share one resistor between two LEDs: they'd split the
current unevenly and differ in brightness, which would ruin the comparison.

Why D10 and not D8: D8 has no PWM (only pins marked `~` can dim: 3, 5, 6, 9, 10, 11), so it can't flicker.

Total draw: about 2 × 13 mA = 26 mA, well within what the Uno can supply.

## Schematic (for KiCad)

```
 Arduino Uno
 +-----------+
 |      D9 ~ |----[ R1 150Ω ]----+
 |           |                  _|_  D1  LED A (white PETG)
 |           |                  \ /  long lead (+) on top
 |           |                  ---
 |           |                   |
 |     D10 ~ |----[ R2 150Ω ]----|--------+
 |           |                   |       _|_  D2  LED B (clear PETG)
 |           |                   |       \ /  long lead (+) on top
 |           |                   |       ---
 |           |                   |        |
 |      GND  |-------------------+--------+
 +-----------+
```

KiCad symbols: `MCU_Module:Arduino_UNO_R3`, `Device:R` ×2, `Device:LED` ×2.
Nets: `LED_A_DRIVE` = D9 ↔ R1 · `LED_B_DRIVE` = D10 ↔ R2 · R1 ↔ D1.A · R2 ↔ D2.A · `GND` = D1.K, D2.K, U1.GND

## Fair-test checklist
- Same LED model in both flames, pushed in to the **same depth**
- Same flame model and print settings; only the filament changes
- Flames ~5–10 cm apart, viewed from the same distance, room dark
- Swap LEDs between the flames once to rule out one LED being brighter than the other
