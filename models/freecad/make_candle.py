# Generates candle.FCStd (parametric, all parts assembled) + print-oriented STLs in ../stl/.
# Run from this directory:
#   flatpak run --command=FreeCADCmd org.freecad.FreeCAD make_candle.py
# After that, edit dimensions in the `params` spreadsheet inside candle.FCStd and press Recompute.
# Coordinates: z = 0 is the top surface of the candle base. +y = street side (front), -y = room side.
import os
import FreeCAD as App
import Part
import Mesh

HERE = os.environ.get("CANDLE_DIR", os.getcwd())
STL_DIR = os.path.join(HERE, "..", "stl")

# alias, value/expression, note
PARAMS = [
    ("pitch", "=1000 / 144", "WS2812B 144/m pixel pitch"),
    ("strip_w", "9.5", "strip width (measured)"),
    ("strip_t", "0.5", "strip PCB + adhesive tape"),
    ("led_h", "1.6", "5050 package height"),
    ("led_s", "5", "5050 package size"),
    ("px_side", "2", "pixels up each face (sidewalk test decides)"),
    ("fin_w", "=strip_w", "fin width = strip width"),
    ("fin_t", "=pitch - 2 * strip_t", "fin thickness: top face holds exactly one pixel"),
    ("fin_h", "=px_side * pitch", "fin height above base; bends land between pixels"),
    ("tenon_d", "6", "fin plug depth into base"),
    ("fit", "0.15", "clearance per side, fin socket"),
    ("gap", "5", "LED face to diffuser, front/back/top"),
    ("wall", "0.8", "diffuser vase-mode wall"),
    ("env_d", "=fin_t + 2 * (strip_t + led_h)", "front-to-back depth over the LED faces"),
    ("r_out", "=gap + wall", "diffuser outer = LED envelope offset by this"),
    ("flame_h", "=fin_h + strip_t + led_h + gap + 21", "diffuser height above base; grows with px_side"),
    ("skirt_d", "4", "diffuser skirt depth = groove depth"),
    ("groove_clr", "0.3", "clearance per side, diffuser groove"),
    ("body_d", "38", "candle base outer diameter"),
    ("body_h", "90", "candle base height"),
    ("body_wall", "2", "candle base wall"),
    ("top_t", "10", "solid top of base"),
    ("usb_w", "10", "cable notch width"),
    ("usb_h", "7", "cable notch height"),
]

# flame loft profile: (fraction of flame_h, scale of the rounded-rectangle section)
PROFILE = [(0.0, 1.0), (0.24, 1.06), (0.48, 1.0), (0.71, 0.65), (0.88, 0.3)]

doc = App.newDocument("candle")
sheet = doc.addObject("Spreadsheet::Sheet", "params")
for i, (alias, val, note) in enumerate(PARAMS, start=2):
    sheet.set(f"A{i}", alias)
    sheet.set(f"B{i}", val)
    sheet.setAlias(f"B{i}", alias)
    sheet.set(f"C{i}", note)
sheet.set("A1", "name"); sheet.set("B1", "value (mm)"); sheet.set("C1", "note")
doc.recompute()


def expr(obj, **kw):
    for prop, e in kw.items():
        obj.setExpression(prop.replace("__", "."), e)


def box(name, L, W, H, x, y, z):
    b = doc.addObject("Part::Box", name)
    expr(b, Length=L, Width=W, Height=H, Placement__Base__x=x, Placement__Base__y=y, Placement__Base__z=z)
    return b


def rrect(name, s, z, extra="0"):
    # LED envelope (led_s wide x env_d deep) grown by r_out with round corners: every point on the
    # diffuser is >= gap from the nearest LED. s scales the whole section; extra adds clearance.
    pl = doc.addObject("Part::Plane", name + "_env")
    expr(pl, Length=f"params.led_s * {s}", Width=f"params.env_d * {s}",
         Placement__Base__x=f"-params.led_s * {s} / 2", Placement__Base__y=f"-params.env_d * {s} / 2",
         Placement__Base__z=z)
    off = doc.addObject("Part::Offset2D", name)
    off.Source = pl
    off.Join = "Arc"
    expr(off, Value=f"params.r_out * {s} + {extra}")
    pl.Visibility = False
    return off


def rrect_prism(name, z, h, extra="0"):
    sec = rrect(name + "_sk", 1, z, extra)
    ex = doc.addObject("Part::Extrusion", name)
    ex.Base = sec
    ex.Dir = App.Vector(0, 0, 1)
    ex.Solid = True
    expr(ex, LengthFwd=h)
    sec.Visibility = False
    return ex


def cut(name, base, *tools):
    tool = tools[0]
    if len(tools) > 1:
        tool = doc.addObject("Part::MultiFuse", name + "_tools")
        tool.Shapes = list(tools)
    c = doc.addObject("Part::Cut", name)
    c.Base, c.Tool = base, tool
    return c


def hide(*objs):
    for o in objs:
        o.Visibility = False


# ---------------- fin ----------------
fin = box("fin", "params.fin_w", "params.fin_t", "params.fin_h + params.tenon_d",
          "-params.fin_w / 2", "-params.fin_t / 2", "-params.tenon_d")

# ---------------- diffuser (flame) ----------------
skirt = rrect_prism("diffuser_skirt", "-params.skirt_d", "params.skirt_d")
secs = [rrect(f"flame_s{i}", s, f"params.flame_h * {f}") for i, (f, s) in enumerate(PROFILE)]
tip = doc.addObject("Part::Vertex", "flame_tip")
expr(tip, Z="params.flame_h")
loft = doc.addObject("Part::Loft", "flame_loft")
loft.Sections = secs + [tip]
loft.Solid = True
loft.Ruled = False
hide(*secs, tip)
diffuser = doc.addObject("Part::MultiFuse", "diffuser")
diffuser.Shapes = [skirt, loft]
diffuser.Refine = True

# ---------------- candle base ----------------
outer = doc.addObject("Part::Cylinder", "base_outer")
expr(outer, Radius="params.body_d / 2", Height="params.body_h", Placement__Base__z="-params.body_h")
hollow = doc.addObject("Part::Cylinder", "base_hollow")
expr(hollow, Radius="params.body_d / 2 - params.body_wall", Height="params.body_h - params.top_t + 1",
     Placement__Base__z="-params.body_h - 1")
socket = box("fin_socket", "params.fin_w + 2 * params.fit", "params.fin_t + 2 * params.fit", "params.tenon_d + 1.5",
             "-params.fin_w / 2 - params.fit", "-params.fin_t / 2 - params.fit", "-params.tenon_d - 0.5")
# wire slot right in front of the street-side face, where the strip's DIN pads sit
wires = box("wire_slot", "7", "3", "params.top_t + 2",
            "-3.5", "params.fin_t / 2 + params.strip_t", "-params.top_t - 1")
g_out = rrect_prism("groove_outer", "-params.skirt_d", "params.skirt_d + 1", "params.groove_clr")
g_in = rrect_prism("groove_inner", "-params.skirt_d - 1", "params.skirt_d + 3", "-params.wall - params.groove_clr")
groove = cut("groove", g_out, g_in)
usb = box("usb_notch", "params.usb_w", "params.body_wall + 4", "params.usb_h + 1",
          "-params.usb_w / 2", "-params.body_d / 2 - 1", "-params.body_h - 1")
base = cut("base", outer, hollow, socket, wires, groove, usb)

# ---------------- strip reference (not printed) ----------------
ref = []
ref.append(box("ref_strip_front", "params.strip_w", "params.strip_t", "params.fin_h",
               "-params.strip_w / 2", "params.fin_t / 2", "0"))
ref.append(box("ref_strip_back", "params.strip_w", "params.strip_t", "params.fin_h",
               "-params.strip_w / 2", "-params.fin_t / 2 - params.strip_t", "0"))
ref.append(box("ref_strip_top", "params.strip_w", "params.fin_t + 2 * params.strip_t", "params.strip_t",
               "-params.strip_w / 2", "-params.fin_t / 2 - params.strip_t", "params.fin_h"))
for i in range(int(sheet.get("px_side"))):  # LED count fixed at generation; rerun the script if px_side changes
    zc = f"params.pitch * ({i} + 0.5) - params.led_s / 2"
    ref.append(box(f"ref_led_front{i + 1}", "params.led_s", "params.led_h", "params.led_s",
                   "-params.led_s / 2", "params.fin_t / 2 + params.strip_t", zc))
    ref.append(box(f"ref_led_back{i + 1}", "params.led_s", "params.led_h", "params.led_s",
                   "-params.led_s / 2", "-params.fin_t / 2 - params.strip_t - params.led_h", zc))
ref.append(box("ref_led_tip", "params.led_s", "params.led_s", "params.led_h",
               "-params.led_s / 2", "-params.led_s / 2", "params.fin_h + params.strip_t"))
strip_ref = doc.addObject("Part::MultiFuse", "strip_reference")
strip_ref.Shapes = ref

doc.recompute()

# GUI colours/transparency are stored only when the GUI is up; harmless otherwise
if App.GuiUp:
    import FreeCADGui as Gui
    Gui.getDocument("candle").getObject("diffuser").Transparency = 60

bad = [o.Name for o in doc.Objects if hasattr(o, "Shape") and o.isDerivedFrom("Part::Feature")
       and o.Visibility and (o.Shape.isNull() or not o.Shape.isValid())]
if bad:
    raise SystemExit(f"invalid shapes: {bad}")

doc.saveAs(os.path.join(HERE, "candle.FCStd"))


def export(obj, fname, rot=None):
    s = obj.Shape.copy()
    if rot:
        s.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), rot)
    s.translate(App.Vector(0, 0, -s.BoundBox.ZMin))
    m = Mesh.Mesh()
    m.addFacets(s.tessellate(0.02))
    m.write(os.path.join(STL_DIR, fname))
    bb = s.BoundBox
    print(f"{fname}: {bb.XLength:.1f} x {bb.YLength:.1f} x {bb.ZLength:.1f} mm, valid={s.isValid()}")


os.makedirs(STL_DIR, exist_ok=True)
export(base, "candle_base.stl", rot=180)   # top face on the bed: socket, slot, groove need no supports
export(fin, "candle_fin.stl")              # upright, plug down
export(diffuser, "candle_diffuser.stl")    # skirt down, vase mode
for k in ("fin_t", "fin_h", "env_d", "r_out"):
    print(k, round(sheet.get(k), 2))
