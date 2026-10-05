# Components

## Stage 1–3 (prototype, on hand)

| Part | Spec | Notes |
|------|------|-------|
| Arduino Uno (clone) | ATmega328P, CH340 USB → `/dev/ttyUSB0` | Upload via `arduino-cli`, FQBN `arduino:avr:uno` |
| 5mm white LED, diffused | Vf 2.0–3.2 V, If 20 mA max | Long lead = anode (+) |
| Resistor | 150 Ω 1/4 W (220 Ω acceptable) | Series with LED |
| Filament | White PETG | Prusa printer; starting 15% infill |

## Stage 4 (planned)

| Part | Spec | Notes |
|------|------|-------|
| 5mm RGB LED, 4-pin | Common anode or common cathode (TBD) | Longest lead = common pin |
| Resistors ×3 | ~220 Ω (R), ~150 Ω (G, B) | Red Vf ≈ 2 V, G/B ≈ 3 V — values set per datasheet |
