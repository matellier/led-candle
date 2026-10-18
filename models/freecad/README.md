# Candle model — base, fin, diffuser

`candle.FCStd` is a PartDesign model with **one Body per printed part**, shown assembled in place:

| Body | Features |
|------|----------|
| `Base` | `BodySketch` → `BodyPad` (down from z = 0), then pockets: `Hollow`, `FinSocket` (exactly plug depth, so the fin bottoms out with the strip start flush), `WireSlot`, `Groove`, `UsbNotch` |
| `Fin` | `FinProfile` (YZ plane: rectangle with a round top) → `FinPad`, symmetric to the plane |
| `Diffuser` | `SkirtSketch` → `Skirt` pad, the `Flame` additive loft through `FlameSection0…6`, then hollowed: `CavityOpen` pocket (opens the bottom) and the `Cavity` subtractive loft through `CavitySection0…6` |

`StripReference` (strip, bend and 5050 packages) is a plain Part compound you don't print. It shows where the
LEDs sit. Every sketch is fully constrained, and its dimensions come from the `params` spreadsheet. The fin
size therefore also sizes the socket in the base and the diffuser around it. Edit a value, press Recompute
(Ctrl+R), then export each Body as an STL again.

The diffuser is a real hollow shell, open at the bottom, with a `wall` (0.8 mm) wall. It slices correctly
in normal mode, with no infill and no bottom, so it doesn't depend on vase mode. The cavity uses the flame
sections shrunk by `wall`, slightly more where the flame tapers so the wall stays ~0.8 mm (0.76–0.88 mm
measured). The top ~2 mm of the tip is solid, because it's too narrow to hollow. PartDesign Thickness can't
shell this loft, which is why the cavity is cut explicitly (`CAVITY` in `make_candle.py`). It's shown 65%
transparent so the fin and LEDs are visible inside.

| File | What |
|------|------|
| `candle.FCStd` | Parametric model, z = 0 is the top of the candle base, +y = street side |
| `make_candle.py` | Rebuilds `candle.FCStd` and the STLs from scratch (also needed if `px_side` changes, to redraw the reference LEDs) |
| `check_fit.py` | Prints the LED-to-diffuser gaps, checks the bend fits between pixels and that no parts overlap |
| `../stl/candle_*.stl` | Print-oriented exports |

Rebuild **inside the FreeCAD GUI**: Macro → Macros… → pick `make_candle.py` → Execute (or run it through the
MCP bridge). Visibility and colours are stored in the GUI half of the file, so a headless rebuild opens with
every part hidden. The fit check runs fine headless:

```
flatpak run --command=FreeCADCmd org.freecad.FreeCAD check_fit.py
```

## How the parts attach

```
  side view (cut front-to-back)                  top of the base

            ╱╲   diffuser (0.8 mm shell)         ┌──────────────────┐
           ╱  ╲                                  │   ╭──────────╮   │ ← groove: diffuser skirt
          │ ╭─╮ │ ← 180° bend, no pixel          │   │  ┌────┐  │   │   drops in, 4 mm deep
          │▓│█│▓│ ← px2 / px3                    │   │  │fin │  │   │ ← fin socket, 6 mm deep  
          │ │█│ │                                │   │  └────┘  │   │
          │▓│█│▓│ ← px1 / px4                    │   │  ▭▭▭▭    │   │ ← wire slot (street side)
  ════════╪╧═█═╧╪════════ base top (z = 0)       │   ╰──────────╯   │
  ███████ ┊  █  ┊ ███████ ← groove / socket      └──────────────────┘
  ███████ ┊  ▌  ┊ ███████   10 mm solid top         Ø38 candle base
          │  wires to ESP32 │
          └──── USB notch ──┘
```

1. **Strip → fin.** Use one uncut piece of 4 px (pixels are ~16.7 mm apart, cut to cut). Start at a cut line
   flush with the base top on the **street side** (DIN end, arrows pointing up). Run 2 px up the face, bend
   it **180° over the fin's round top** (radius 3 mm), and run 2 px down the room side. Only the two flat
   faces are stuck down. The bend uses ~10 mm of strip, and `fin_h` centres it in the ~11.7 mm of bare strip
   between px2 and px3, so px3 ends up directly behind px2. The far (DO) end stops at the base top, with no wires.
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
| Fin | Upright, plug down, round top up | Any (hidden) | 100% infill. It's only 6 mm thick |
| Diffuser | Skirt down | White PETG | Normal mode: 1 perimeter (0.8 mm extrusion width = `wall`), no supports. The STL is already hollow and open at the bottom. Vase mode also works |

## Current dimensions (`px_side` = 2, pitch 1000/60)

- Diffuser: **~17.7 mm wide seen from the street or room**, 23.2 mm front-to-back, 46 mm above the base
  (50 mm with skirt). The round post design needed 26 mm. The tip is rounded and sits ~14 mm above the
  bend, which keeps the unlit top of the flame short.
- Fin: 9.5 × 6 mm, 31 mm above the base plus the 6 mm plug.
- LED-to-wall gap (from `check_fit.py`): 5.3 mm at px1/px4 and 5.2 mm at px2/px3. Raise `gap` to 6 to match
  the 6 mm corner gap that diffused well in the post test. The bend is 2.2 mm from the wall where the flame
  tapers. It has no LEDs on it, so that's fine.
- The loft sections are evenly spaced and change gently (`PROFILE` in `make_candle.py`). Big jumps between
  sections make the B-spline loft pinch in near the base, which earlier cut the px1 gap to 4.7 mm.
- Diffuser cross-section is the LED envelope offset by `gap` with rounded corners, not an ellipse. An ellipse
  of the same width curves in toward the LED corners, leaving only ~3.6 mm there.
