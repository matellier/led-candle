# Candle model — base, fin, diffuser

`candle.FCStd` holds all three parts **assembled in place**, plus a `strip_reference` (strip + 5050 packages,
not printed) that shows where the LEDs sit. Every dimension comes from the `params` spreadsheet, so the fin
size also sizes the socket in the base and the diffuser around it. Edit a value, then press Recompute
(Ctrl+R) and re-export the STL.

The diffuser is a solid in the model, because vase mode hollows it at print time. Set its Transparency to
~60 in the GUI to see the fin inside.

| File | What |
|------|------|
| `candle.FCStd` | Parametric model, z = 0 is the top of the candle base, +y = street side |
| `make_candle.py` | Rebuilds `candle.FCStd` and the STLs from scratch (also needed if `px_side` changes, to redraw the reference LEDs) |
| `check_fit.py` | Prints the LED-to-diffuser gaps and checks that no parts overlap |
| `../stl/candle_*.stl` | Print-oriented exports |

```
flatpak run --env=CANDLE_DIR=$PWD --command=FreeCADCmd org.freecad.FreeCAD make_candle.py
flatpak run --command=FreeCADCmd org.freecad.FreeCAD check_fit.py
```

## How the parts attach

```
  side view (cut front-to-back)                  top of the base

            ╱╲   diffuser (vase mode)            ┌──────────────────┐
           ╱  ╲                                  │   ╭──────────╮   │ ← groove: diffuser skirt
          │ ▓  │ ← px3 tip                       │   │  ┌────┐  │   │   drops in, 4 mm deep
          │▓ █ ▓│ ← px2 / px4                    │   │  │fin │  │   │ ← fin socket, 6.5 mm deep
          │▓ █ ▓│ ← px1 / px5                    │   │  └────┘  │   │
  ════════╪╧═█═╧╪════════ base top (z = 0)       │   │  ▭▭▭▭    │   │ ← wire slot (street side)
  ███████ ┊  █  ┊ ███████ ← groove / socket      │   ╰──────────╯   │
  ███████ ┊  ▌  ┊ ███████   10 mm solid top      └──────────────────┘
          │  wires to ESP32 │                       Ø38 candle base
          │   (hollow body) │
          └──── USB notch ──┘
```

1. **Strip → fin.** Use one uncut piece of 5 px. Start at a cut line flush with the base top on the
   **street side** (DIN end, arrows pointing up). Run 2 px up the face, bend 90° in the gap between px2
   and px3, lay px3 on top, bend 90° again, and run 2 px down the room side. The fin's height (2 × pitch)
   and thickness (pitch − 2 × strip) put both bends in the gaps between pixels. The strip's own adhesive
   holds it on. The far (DO) end just stops at the base top, with no wires.
2. **Fin → base.** The fin's 6 mm plug presses into the socket (0.15 mm clearance per side). It should be a
   snug press fit. If it's loose, add a drop of CA glue. If it's tight, set `fit` to 0.2.
3. **Wires.** The three wires on the DIN pads drop straight down through the wire slot in front of the fin,
   through the hollow body and out the USB notch (prototype: to the ESP32 breakout. Production: an ESP32-C3
   Super Mini fits inside the 34 mm bore).
4. **Diffuser → base.** The diffuser's 4 mm skirt drops into the groove (0.3 mm clearance per side), which
   locates it and keeps it centred on the LEDs. It lifts off for access. If it rattles, a dab of hot glue or
   a lower `groove_clr` fixes it.

## Print settings (MK4, 0.6 mm nozzle)

| Part | Orientation | Material | Settings |
|------|-------------|----------|----------|
| Base | Upside down: top face on the bed (the STL is already flipped), so the socket, slot and groove need no supports | White PETG (the top glows a little, like wax next to a flame) | 2–3 perimeters, 15% infill |
| Fin | Upright, plug down | Any (hidden) | 100% infill. It's only 6 mm thick |
| Diffuser | Skirt down | White PETG | **Vase mode**, bottom solid layers = 0, wall ≈ `wall` (0.8 mm). Gives a 0.8 mm tube that fits the groove |

## Current dimensions (`px_side` = 2)

- Diffuser: **~17.8 mm wide seen from the street or room**, 23.4 mm front-to-back, 42 mm above the base
  (46 mm with skirt). The round post design needed 26 mm.
- LED-to-wall gap (from `check_fit.py`): 4.9 mm at px1/px5 (the loft dips slightly near the base), 5.3 mm at
  px2/px4, 5.5 mm above the tip pixel. Raise `gap` to 6 to match the 6 mm corner gap that diffused well in the post test.
- Diffuser cross-section is the LED envelope offset by `gap` with rounded corners, not an ellipse. An ellipse
  of the same width curves in toward the LED corners, leaving only ~3.6 mm there.
