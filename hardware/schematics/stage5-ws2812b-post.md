# Stage 5 — WS2812B strip wrapped on the flame post (ESP32 + WLED)

Prototype candle: a **144 LED/m WS2812B** strip wrapped in a spiral around the 3D-printed **~16 mm post**. It's driven by
an **ESP32-WROOM-32 DevKit** on a screw-terminal breakout running **WLED**, and powered from a 5 V USB wall charger.

The strip is still uncut. Wrap ~20 pixels for the sidewalk test, and use WLED's LED count to choose how many are
lit. Cut and size the post afterwards.

## Strip wires (factory pigtail)

| Wire | Pad on strip | Goes to (breakout terminal) |
|------|--------------|-----------------------------|
| **Red** | +5V | **5V** |
| **White** | GND | **GND** between P12 and P13 (same row as 5V). **Not** the terminal next to 5V: that's **CMD** (flash pin), see below |
| **Green** | DIN | **P16** through R1 |
| Loose thick red / white | +5V / GND | Extra power leads, same nets as the JST red/white. Not needed for the prototype. Insulate the bare ends |

Check the colors against the pads before powering. Cheap strips don't always follow the convention, but the
pad labels (`+5V  DIN  GND`) printed next to the wires are correct.

**The terminal next to 5V is CMD, not GND.** CMD is GPIO11, the flash command line. If ground goes on CMD, the
ESP32 can't read its flash once the strip is powered: it won't boot, never joins Wi-Fi, and esptool reads the
flash ID as `ff/ffff`. On this breakout the 5V row reads, from the USB end: 5V, CMD, SD3, SD2, P13, **GND**, P12…

## Direction: the pigtail must be on the DIN end

Data flows one way. The arrows (▶) on the strip point **away from the input**, and the pads at the
input end read **DIN**, while the far end reads **DO**. The pigtail at the bottom of the post must be on the
**DIN** end. If it's on the DO end, nothing lights. That won't damage anything, but it means re-soldering.

## Parts

| Ref | Part | Value | Needed? |
|-----|------|-------|---------|
| U1 | ESP32-WROOM-32 DevKit on screw-terminal breakout | — | Yes |
| R1 | Resistor, 1/4 W, in series with data | **150 Ω** on hand (330 Ω textbook, 150–470 OK) | **Yes.** It damps ringing and protects the first pixel's DIN |
| C1 | Electrolytic cap across 5V/GND | **470 µF 16 V** on hand (470–1000 µF, ≥ 6.3 V) | Optional at the capped prototype brightness, but on hand so it goes in. Stripe → GND |
| J1 | Spare JST SM 3-pin mating pigtail | — | Plugs into the strip. Its bare ends go straight into the screw terminals, so no breadboard is needed |
| — | USB charger + micro-USB cable | 5 V | Powers the board and the strip |

## Schematic (for KiCad)

```
 USB charger 5V ══ micro-USB ══╗
                               ▼
 ESP32 DevKit (breakout)                       16 mm post (spiral wrap, 16 px)
 +-------------+                               +---------------------------+
 |             |                               |  px16  (top, DO end)      |
 |        5V   |------+------- red ----------->| +5V    ...                |
 |             |     _|_ C1 (optional)         |        px2                |
 |             |     --- (+) to 5V             |        px1 (bottom, DIN)  |
 |       GND   |------+------- white --------->| GND                       |
 |             |                               |                           |
 |       P16   |----[ R1 150Ω ]---- green ---->| DIN                       |
 +-------------+                               +---------------------------+
```

KiCad symbols: `RF_Module:ESP32-WROOM-32` or a generic `Connector_Generic` for the DevKit (U1), `Device:R` (R1),
`Device:C_Polarized` (C1), `LED:WS2812B` chained (DOUT → next DIN) or `Connector_Generic:Conn_01x03` for the strip.

Nets: `+5V` = U1.5V ↔ C1.+ ↔ strip +5V · `GND` = U1.GND ↔ C1.− ↔ strip GND ·
`LED_DATA` = U1.GPIO16 ↔ R1.1 · `LED_DIN` = R1.2 ↔ strip DIN

## Hookup (screw terminals)

1. **Unplug USB while wiring.**
2. Plug the spare pigtail into the strip connector. Strip ~6 mm off each loose end and twist the strands. Tinning
   with solder is optional for screw terminals.
3. White → **GND** terminal first. A data line connected before ground is the most common way to kill the first pixel.
4. Red → **5V** terminal.
5. One leg of R1 → **P16** terminal. Solder or twist the green wire to R1's other leg, then cover it with heat-shrink or tape.
6. Optional C1: across the **5V** and **GND** terminals (they are *not* side by side). The stripe (−) goes to GND.
7. Plug in USB.

Finding P16: the breakout labels it **P16**. It's on the same terminal row as CLK/SD0/SD1, and it's the 8th terminal from
the USB end: CLK, SD0, SD1, P15, P2, P0, P4, **P16**. The DevKit itself may print it as G16, D16, IO16 or RX2. It's
the same pin as WLED's **Data GPIO 16**.

Why P16 (GPIO16): it's **WLED's default LED pin on ESP32**, so it works with no pin configuration. Avoid P0, P2,
P12 and P15. They're boot-strapping pins, and the strip's data line can stop the board from booting.

## WLED setup

1. Flash from a Chrome or Edge browser at **install.wled.me** (USB cable to the PC; choose the plain ESP32 build):
   1. **Disconnect all external wiring (strip, breadboard) from the board.** Flashing works fine on the breakout,
      but with the breadboard wired in, the installer hung at "Erasing" and esptool read the flash ID as `ff/ffff`
      instead of `5e/4016` (4MB).
   2. Open install.wled.me.
   3. **Hold BOOT**: the button on the **right** of the USB connector, with the USB end facing you.
   4. Click **Install**.
   5. Release BOOT once it starts erasing. The erase and write take a few minutes.
2. Connect to Wi-Fi. Once it's on the network, choose **Add to Home Assistant** and enter
   `http://192.168.50.140:8123`. Then follow the HA prompt to set up the WLED integration.
3. **Config → LED Preferences.** Neither the installer nor HA asks for the LED count, and WLED defaults to **30**, so set it here:
   - Length: **17** (the number wrapped). GPIO: **16**. Type: WS281x. Color order: **GRB**
   - **Automatic Brightness Limiter: on, max current 500 mA** (see the power budget)
4. Effects to try for the flame: **Candle**, **Candle Multi**, **Fire Flicker**. Use an amber color (R 255, G ~100, B 0).

## Power budget (why the limiter is set to 500 mA)

The DevKit's 5V terminal is fed from the micro-USB port, usually through a small protection diode. It's
good for roughly 500 mA. That diode drops the strip supply to about 4.7 V, which helps the 3.3 V data signal register.

Rough figures per WS2812B pixel at full brightness: ~20 mA per color channel, so **~60 mA for full white**.

| What's lit | Per pixel | × 20 px | OK at 500 mA? |
|------------|-----------|---------|---------------|
| Full white (255,255,255) | ~60 mA | **~1.2 A** | ❌ WLED's limiter dims it automatically |
| Amber candle (255, ~100, 0) | ~28 mA | ~560 mA | ⚠️ Limiter trims it slightly |
| Amber at ~40% brightness | ~11 mA | ~225 mA | ✅ |
| Off (pixels still idle) | ~1 mA | ~20 mA | ✅ |

WLED's limiter handles this, so no code cap is needed. Also check the charger's label: the limit is whichever is
lower, the charger rating or 500 mA. Turn the board-side limit up only after measuring with a USB power meter.

## Before the first power-up
- [ ] Pigtail on the **DIN** end (arrows point up the post, away from the wires)
- [ ] Red = +5V, white = GND confirmed against the pad labels
- [ ] R1 in the green (data) line, on **P16**
- [ ] C1 polarity correct (if fitted)
- [ ] WLED: LED count set, current limiter at 500 mA, before turning the brightness up

## If pixels flicker randomly or show wrong colors
The ESP32 sends a 3.3 V signal; WS2812B wants about 3.5 V. It usually works anyway, especially at 4.7 V strip supply.
If not, first shorten the green wire. If that doesn't fix it, add a 74AHCT125 level shifter (production parts list).
