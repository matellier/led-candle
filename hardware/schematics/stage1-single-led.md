# Stage 1 — Single 5mm white LED on Arduino Uno

## LED polarity

| Lead | Name | Polarity | Other clue |
|------|------|----------|------------|
| **Long** | Anode | **+** | — |
| **Short** | Cathode | **−** | Flat edge on the plastic rim; larger "anvil" inside the lens |

If the leads were trimmed, use the flat edge, or a multimeter in diode mode (red probe on anode → LED glows faintly).
Wiring it backwards won't hurt it at 5 V through a resistor; it just won't light.

## Parts

| Ref | Part | Value | Needed? |
|-----|------|-------|---------|
| R1 | Resistor, 1/4 W | **150 Ω** (OK range 150–220 Ω) | **Yes — required** |
| D1 | 5mm white diffused LED | Vf 2.0–3.2 V, If 20 mA max | — |
| — | Diode | — | **No.** An LED is itself a diode; nothing inductive to protect against |
| — | Capacitor | — | **No.** Steady/PWM LED at 13 mA doesn't need decoupling |

## Resistor math

Uno pin = 5 V. R = (Vsupply − Vf) / I

| R | Vf 2.8 V | Vf 3.0 V | Vf 3.2 V | Verdict |
|---|----------|----------|----------|---------|
| 100 Ω | 22 mA ❌ | 20 mA | 18 mA | At/over the limit — avoid |
| **150 Ω** | 15 mA | 13 mA | 12 mA | **Recommended** — bright, safe margin |
| 220 Ω | 10 mA | 9 mA | 8 mA | Fine if that's what you have; slightly dimmer |

The 20 mA spec is a maximum, not a target. Going from 13 → 20 mA is only about 1.4× brighter (and your eye sees it as less than that).
Uno pins are rated 20 mA recommended / 40 mA absolute max per pin, so 13 mA is comfortable.

## Schematic (for KiCad)

```
        Arduino Uno
      +-------------+
      |             |
      |        D9 ~ |----[ R1 150Ω ]----+
      |             |                   |
      |             |                  _|_  D1 white LED
      |             |                  \ /   anode   = top (long lead)
      |             |                  ---   cathode = bottom (short lead)
      |             |                   |
      |        GND  |-------------------+
      +-------------+
```

KiCad symbols:
- `MCU_Module:Arduino_UNO_R3` (U1). Use pin **D9** and any **GND**
- `Device:R` (R1, 150Ω)
- `Device:LED` (D1). The triangle points toward GND; the bar is the cathode

Nets: `LED_DRIVE` = U1.D9 ↔ R1.1 · `LED_A` = R1.2 ↔ D1.A · `GND` = D1.K ↔ U1.GND

## Breadboard

1. Jumper Uno **D9** → breadboard row A.
2. R1 from row A → row B.
3. LED **long lead** in row B, **short lead** in row C.
4. Jumper row C → Uno **GND**.

The resistor can go on either side of the LED. It just has to be in series.

## Why D9?

Flicker (Stage 2) needs a PWM pin (marked `~`: 3, 5, 6, 9, 10, 11). D9, D10, D11 are also the planned
R/G/B pins for the 4-pin RGB LED in Stage 4, so the white LED wiring carries forward unchanged.
