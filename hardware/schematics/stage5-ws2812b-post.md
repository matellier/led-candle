# Stage 5 — WS2812B strip wrapped on the flame post (ESP32 + WLED)

Prototype candle: a **60 LED/m WS2812B** strip wrapped in a spiral around the 3D-printed **~16 mm post**. It's driven by
an **ESP32-WROOM-32 DevKit** on a screw-terminal breakout running **WLED**, and powered from a 5 V USB wall charger.

The strip is still uncut. Wrap ~20 pixels for the sidewalk test, and use WLED's LED count to choose how many are
lit. Cut and size the post afterwards.

## Strip wires (soldered direct to the DIN-end pads)

The strip is cut to 16 px. The wires are soldered straight to the pads; the factory pigtail is no longer used.

| Wire | Pad on strip | Goes to (breakout terminal) |
|------|--------------|-----------------------------|
| **Red** | +5V | **5V** |
| **Teal** | GND | **GND** between P12 and P13 (same row as 5V). **Not** the terminal next to 5V: that's **CMD** (flash pin), see below |
| **White** | DIN | **P16** |

These colors don't follow the usual convention (white = GND). Go by the pad labels (`+5V  DIN  GND`), not the colors.

**The terminal next to 5V is CMD, not GND.** CMD is GPIO11, the flash command line. If ground goes on CMD, the
ESP32 can't read its flash once the strip is powered: it won't boot, never joins Wi-Fi, and esptool reads the
flash ID as `ff/ffff`. On this breakout the 5V row reads, from the USB end: 5V, CMD, SD3, SD2, P13, **GND**, P12…

## Direction: the wires must be on the DIN end

Data flows one way. The arrows (▶) on the strip point **away from the input**, and the pads at the
input end read **DIN**, while the far end reads **DO**. The wires at the bottom of the post must be on the
**DIN** end. If it's on the DO end, nothing lights. That won't damage anything, but it means re-soldering.

## Parts

| Ref | Part | Value | Needed? |
|-----|------|-------|---------|
| U1 | ESP32-WROOM-32 DevKit on screw-terminal breakout | — | Yes |
| — | 3 wires soldered to the strip's DIN-end pads | — | Run to the screw terminals (directly or via breadboard rails) |
| — | USB charger + micro-USB cable | 5 V | Powers the board and the strip |

## Schematic (for KiCad)

```
 USB charger 5V ══ micro-USB ══╗
                               ▼
 ESP32 DevKit (breakout)                       16 mm post (spiral wrap, 16 px)
 +-------------+                               +---------------------------+
 |             |                               |  px16  (top, DO end)      |
 |        5V   |-------------- red ----------->| +5V    ...                |
 |             |                               |        px2                |
 |             |                               |        px1 (bottom, DIN)  |
 |       GND   |-------------- teal ---------->| GND                       |
 |             |                               |                           |
 |       P16   |-------------- white --------->| DIN                       |
 +-------------+                               +---------------------------+
```

KiCad symbols: `RF_Module:ESP32-WROOM-32` or a generic `Connector_Generic` for the DevKit (U1),
`LED:WS2812B` chained (DOUT → next DIN) or `Connector_Generic:Conn_01x03` for the strip.

Nets: `+5V` = U1.5V ↔ strip +5V · `GND` = U1.GND ↔ strip GND · `LED_DATA` = U1.GPIO16 ↔ strip DIN

No data resistor or bulk capacitor. The strip vendor's wiring diagram uses neither, and the prototype runs fine
without them. If the first pixel misbehaves, a 150–470 Ω resistor in the data line is the first thing to add back.

## Hookup (screw terminals)

1. **Unplug USB while wiring.**
2. Teal → **GND** terminal first. A data line connected before ground is the most common way to kill the first pixel.
3. Red → **5V** terminal.
4. White → **P16** terminal.
5. Plug in USB.

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
   - Length: **16** (the number wrapped). GPIO: **16**. Type: WS281x. Color order: **GRB**
   - **Automatic Brightness Limiter: on, max current 500 mA** (see the power budget)
4. Effects to try for the flame: **Candle**, **Candle Multi**, **Fire Flicker**. Use an amber color (R 255, G ~100, B 0).

## Power budget (why the limiter is set to 500 mA)

The DevKit's 5V terminal is fed from the micro-USB port, usually through a small protection diode. It's
good for roughly 500 mA. That diode drops the strip supply to about 4.7 V, which helps the 3.3 V data signal register.

Rough figures per WS2812B pixel at full brightness: ~20 mA per color channel, so **~60 mA for full white**.

| What's lit | Per pixel | × 16 px | OK at 500 mA? |
|------------|-----------|---------|---------------|
| Full white (255,255,255) | ~60 mA | **~960 mA** | ❌ WLED's limiter dims it automatically |
| Amber candle (255, ~100, 0) | ~28 mA | ~450 mA | ✅ Just under |
| Amber at ~40% brightness | ~11 mA | ~180 mA | ✅ |
| Off (pixels still idle) | ~1 mA | ~16 mA | ✅ |

WLED's limiter handles this, so no code cap is needed. Also check the charger's label: the limit is whichever is
lower, the charger rating or 500 mA. Turn the board-side limit up only after measuring with a USB power meter.

## Before the first power-up
- [ ] Wires on the **DIN** end (arrows point up the post, away from the wires)
- [ ] Red = +5V, teal = GND, white = DIN confirmed against the pad labels
- [ ] Ground on a real **GND** terminal, not CMD
- [ ] WLED: LED count set, current limiter at 500 mA, before turning the brightness up

## If pixels flicker randomly or show wrong colors
The ESP32 sends a 3.3 V signal; WS2812B wants about 3.5 V. It usually works anyway, especially at 4.7 V strip supply.
If not, first shorten the data wire, then add a 150–470 Ω resistor in it. If that doesn't fix it, add a 74AHCT125 level shifter (production parts list).
