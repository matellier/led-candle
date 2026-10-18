# Generates candle.FCStd (PartDesign: one Body per part, assembled in place) + print-oriented STLs in ../stl/.
# Run it inside the FreeCAD GUI (Macro > Macros... > make_candle.py, or through the MCP bridge) so the file
# keeps visibility and colours. Headless also works, but FreeCAD then opens the file with every part hidden:
#   flatpak run --env=CANDLE_DIR=$PWD --command=FreeCADCmd org.freecad.FreeCAD make_candle.py
# After that, edit dimensions in the `params` spreadsheet inside candle.FCStd and press Recompute.
# Coordinates: z = 0 is the top surface of the candle base. +y = street side (front), -y = room side.
import math
import os
import FreeCAD as App
import Part
import Sketcher
import Mesh

HERE = os.environ.get("CANDLE_DIR") or (os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd())
STL_DIR = os.path.join(HERE, "..", "stl")
V = App.Vector

# alias, value/expression, note
PARAMS = [
    ("pitch", "=1000 / 60", "pixel pitch, cut to cut (measured ~16.5 mm)"),
    ("strip_w", "9.5", "strip width (measured)"),
    ("strip_t", "0.5", "strip PCB + adhesive tape"),
    ("led_h", "1.6", "5050 package height"),
    ("led_s", "5", "5050 package size"),
    ("px_side", "2", "pixels up each face (sidewalk test decides)"),
    ("fin_w", "=strip_w", "fin width = strip width"),
    ("fin_t", "6", "fin thickness; strip bends 180 deg over its round top (radius fin_t / 2)"),
    ("bend", "=pi * (fin_t + strip_t) / 2", "strip length used by the bend; must fit between pixels"),
    ("fin_h", "=px_side * pitch - bend / 2", "flat face height: centres the bend in the px gap"),
    ("tenon_d", "6", "fin plug depth into base"),
    ("fit", "0.15", "clearance per side, fin socket"),
    ("gap", "5", "LED face to diffuser"),
    ("wall", "0.8", "diffuser wall thickness"),
    ("env_d", "=fin_t + 2 * (strip_t + led_h)", "front-to-back depth over the LED faces"),
    ("r_out", "=gap + wall", "diffuser outer = LED envelope offset by this"),
    ("flame_h", "=fin_h + 18", "diffuser height above base; grows with px_side"),
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
# Evenly spaced, gently changing sections: big jumps make the B-spline loft pinch in near the base.
PROFILE = [(0.0, 1.0), (0.2, 1.04), (0.4, 1.06), (0.64, 1.0), (0.8, 0.75), (0.92, 0.45), (1.0, 0.05)]
# cavity: (fraction of flame_h, scale, wall factor). Same sections shrunk by wall * factor; the factor > 1 where
# the flame tapers keeps the wall normal to the surface ~wall thick. The tip is too small to shrink, so the
# cavity stops short of it and the last few mm are solid.
CAVITY = [(0.0, 1.0, 1), (0.2, 1.04, 1), (0.4, 1.06, 1), (0.64, 1.0, 1.05), (0.8, 0.75, 1.15), (0.92, 0.45, 1.4),
          (0.95, 0.3, 1.6)]

if "candle" in App.listDocuments():
    App.closeDocument("candle")          # rebuild from scratch; unsaved edits in the open copy are discarded
doc = App.newDocument("candle")
sheet = doc.addObject("Spreadsheet::Sheet", "params")
sheet.set("A1", "name"); sheet.set("B1", "value (mm)"); sheet.set("C1", "note")
for i, (alias, val, note) in enumerate(PARAMS, start=2):
    sheet.set(f"A{i}", alias)
    sheet.set(f"B{i}", val)
    sheet.setAlias(f"B{i}", alias)
    sheet.set(f"C{i}", note)
doc.recompute()
P = {a: sheet.get(a) for a, _, _ in PARAMS}  # current values, used only as solver start points


def expr(obj, **kw):
    for prop, e in kw.items():
        obj.setExpression(prop.replace("__", "."), e)


def new_body(name):
    return doc.addObject("PartDesign::Body", name)


def sketch(body, name, plane="XY_Plane", z=None):
    sk = body.newObject("Sketcher::SketchObject", name)
    pl = next(f for f in body.Origin.OriginFeatures if f.Role == plane)
    sk.AttachmentSupport = [(pl, "")]
    sk.MapMode = "FlatFace"
    if z is not None:
        expr(sk, AttachmentOffset__Base__z=z)
    return sk


def dim(sk, c, e):
    """Add a constraint and drive its value from a spreadsheet expression."""
    i = sk.addConstraint(c)
    sk.setExpression(f"Constraints[{i}]", e)
    return i


def circle(sk, d_expr, d0):
    g = sk.addGeometry(Part.Circle(V(0, 0, 0), V(0, 0, 1), d0 / 2))
    sk.addConstraint(Sketcher.Constraint("Coincident", g, 3, -1, 1))
    dim(sk, Sketcher.Constraint("Diameter", g, d0), d_expr)


def rect(sk, x0, x1, y0, y1, ex0, ex1, ey0, ey1):
    """Axis-aligned rectangle; corners driven by expressions (x/y measured from the sketch origin)."""
    pts = [V(x0, y0, 0), V(x1, y0, 0), V(x1, y1, 0), V(x0, y1, 0)]
    g = [sk.addGeometry(Part.LineSegment(pts[i], pts[(i + 1) % 4])) for i in range(4)]
    for i in range(4):
        sk.addConstraint(Sketcher.Constraint("Coincident", g[i], 2, g[(i + 1) % 4], 1))
    sk.addConstraint(Sketcher.Constraint("Horizontal", g[0]))
    sk.addConstraint(Sketcher.Constraint("Horizontal", g[2]))
    sk.addConstraint(Sketcher.Constraint("Vertical", g[1]))
    sk.addConstraint(Sketcher.Constraint("Vertical", g[3]))
    # corner 0 = (x0, y0), corner 2 = (x1, y1); DistanceX/Y measured from the origin
    dim(sk, Sketcher.Constraint("DistanceX", -1, 1, g[0], 1, x0), ex0)
    dim(sk, Sketcher.Constraint("DistanceY", -1, 1, g[0], 1, y0), ey0)
    dim(sk, Sketcher.Constraint("DistanceX", -1, 1, g[2], 1, x1), ex1)
    dim(sk, Sketcher.Constraint("DistanceY", -1, 1, g[2], 1, y1), ey1)


def rrect(sk, s="1", extra="0"):
    """LED envelope (led_s wide x env_d deep) grown by r_out with round corners, centred on the origin.
    Every point is >= gap from the nearest LED. s scales the whole section; extra adds clearance."""
    sv = float(s)
    cx, cy = P["led_s"] / 2 * sv, P["env_d"] / 2 * sv
    r = P["r_out"] * sv + eval(extra.replace("params.", ""), {}, P)   # solver start point only
    L = lambda a, b: sk.addGeometry(Part.LineSegment(V(*a, 0), V(*b, 0)))
    A = lambda c, a0, a1: sk.addGeometry(Part.ArcOfCircle(Part.Circle(V(*c, 0), V(0, 0, 1), r),
                                                         a0 * math.pi / 180, a1 * math.pi / 180))
    l0 = L((-cx, -cy - r), (cx, -cy - r)); a0 = A((cx, -cy), -90, 0)
    l1 = L((cx + r, -cy), (cx + r, cy)); a1 = A((cx, cy), 0, 90)
    l2 = L((cx, cy + r), (-cx, cy + r)); a2 = A((-cx, cy), 90, 180)
    l3 = L((-cx - r, cy), (-cx - r, -cy)); a3 = A((-cx, -cy), 180, 270)
    chain = [l0, a0, l1, a1, l2, a2, l3, a3]
    for i in range(8):
        sk.addConstraint(Sketcher.Constraint("Tangent", chain[i], 2, chain[(i + 1) % 8], 1))
    sk.addConstraint(Sketcher.Constraint("Horizontal", l0))
    sk.addConstraint(Sketcher.Constraint("Horizontal", l2))
    sk.addConstraint(Sketcher.Constraint("Vertical", l1))
    sk.addConstraint(Sketcher.Constraint("Vertical", l3))
    for a in (a1, a2, a3):
        sk.addConstraint(Sketcher.Constraint("Equal", a0, a))
    sk.addConstraint(Sketcher.Constraint("Symmetric", a0, 3, a2, 3, -1, 1))
    dim(sk, Sketcher.Constraint("Radius", a0, r), f"params.r_out * {s} + {extra}")
    dim(sk, Sketcher.Constraint("DistanceX", a2, 3, a0, 3, 2 * cx), f"params.led_s * {s}")
    dim(sk, Sketcher.Constraint("DistanceY", a0, 3, a2, 3, 2 * cy), f"params.env_d * {s}")


# ================= fin =================
fin = new_body("Fin")
sk = sketch(fin, "FinProfile", "YZ_Plane")      # sketch x = global y (front/back), sketch y = global z
t, h, d = P["fin_t"], P["fin_h"], P["tenon_d"]
b = sk.addGeometry(Part.LineSegment(V(-t / 2, -d, 0), V(t / 2, -d, 0)))
rgt = sk.addGeometry(Part.LineSegment(V(t / 2, -d, 0), V(t / 2, h, 0)))
top = sk.addGeometry(Part.ArcOfCircle(Part.Circle(V(0, h, 0), V(0, 0, 1), t / 2), 0, math.pi))
lft = sk.addGeometry(Part.LineSegment(V(-t / 2, h, 0), V(-t / 2, -d, 0)))
sk.addConstraint(Sketcher.Constraint("Coincident", b, 2, rgt, 1))
sk.addConstraint(Sketcher.Constraint("Tangent", rgt, 2, top, 1))
sk.addConstraint(Sketcher.Constraint("Tangent", top, 2, lft, 1))
sk.addConstraint(Sketcher.Constraint("Coincident", lft, 2, b, 1))
sk.addConstraint(Sketcher.Constraint("Horizontal", b))
sk.addConstraint(Sketcher.Constraint("Vertical", rgt))
sk.addConstraint(Sketcher.Constraint("Vertical", lft))
sk.addConstraint(Sketcher.Constraint("PointOnObject", top, 3, -2))
dim(sk, Sketcher.Constraint("Radius", top, t / 2), "params.fin_t / 2")
dim(sk, Sketcher.Constraint("DistanceY", -1, 1, top, 3, h), "params.fin_h")
dim(sk, Sketcher.Constraint("DistanceY", b, 1, -1, 1, d), "params.tenon_d")
pad = fin.newObject("PartDesign::Pad", "FinPad")
pad.Profile = sk
pad.SideType = "Symmetric"
expr(pad, Length="params.fin_w")
sk.Visibility = False

# ================= diffuser (flame) =================
dif = new_body("Diffuser")
sk = sketch(dif, "SkirtSketch", z="-params.skirt_d")
rrect(sk)
skirt = dif.newObject("PartDesign::Pad", "Skirt")
skirt.Profile = sk
expr(skirt, Length="params.skirt_d")
sk.Visibility = False
secs = []
for i, (f, s) in enumerate(PROFILE):
    sk = sketch(dif, f"FlameSection{i}", z=f"params.flame_h * {f}")
    rrect(sk, str(s))
    sk.Visibility = False
    secs.append(sk)
loft = dif.newObject("PartDesign::AdditiveLoft", "Flame")
loft.Profile = secs[0]
loft.Sections = secs[1:]
loft.Ruled = False
# Hollow it: a real wall-thick shell, open at the bottom for the fin, so it slices right without vase mode.
# (Thickness can't shell this loft: the near-point tip is tighter than the wall.)
sk = sketch(dif, "CavitySkirt")
rrect(sk, extra="-params.wall")
pk = dif.newObject("PartDesign::Pocket", "CavityOpen")   # through the skirt, opens the bottom
pk.Profile = sk
expr(pk, Length="params.skirt_d + 1")
sk.Visibility = False
secs = []
for i, (f, s, k) in enumerate(CAVITY):
    sk = sketch(dif, f"CavitySection{i}", z=f"params.flame_h * {f}")
    rrect(sk, str(s), extra=f"-params.wall * {k}")
    sk.Visibility = False
    secs.append(sk)
cav = dif.newObject("PartDesign::SubtractiveLoft", "Cavity")
cav.Profile = secs[0]
cav.Sections = secs[1:]
cav.Ruled = False

# ================= candle base =================
base = new_body("Base")
sk = sketch(base, "BodySketch")
circle(sk, "params.body_d", P["body_d"])
pad = base.newObject("PartDesign::Pad", "BodyPad")
pad.Profile = sk
pad.Reversed = True                          # grows down from z = 0
expr(pad, Length="params.body_h")
sk.Visibility = False


def pocket(name, sk, length=None, reversed_=False, through=False):
    pk = base.newObject("PartDesign::Pocket", name)
    pk.Profile = sk
    if through:
        pk.Type = "ThroughAll"
    else:
        expr(pk, Length=length)
    pk.Reversed = reversed_
    sk.Visibility = False
    return pk


sk = sketch(base, "HollowSketch", z="-params.body_h")
circle(sk, "params.body_d - 2 * params.body_wall", P["body_d"] - 2 * P["body_wall"])
pocket("Hollow", sk, "params.body_h - params.top_t", reversed_=True)

sk = sketch(base, "SocketSketch")
w2, t2 = P["fin_w"] / 2 + P["fit"], P["fin_t"] / 2 + P["fit"]
rect(sk, -w2, w2, -t2, t2,
     "-(params.fin_w / 2 + params.fit)", "params.fin_w / 2 + params.fit",
     "-(params.fin_t / 2 + params.fit)", "params.fin_t / 2 + params.fit")
pocket("FinSocket", sk, "params.tenon_d")   # fin bottoms out with the strip start flush to the base top

# wire slot right in front of the street-side face, where the strip's DIN pads sit
sk = sketch(base, "WireSlotSketch")
y0 = P["fin_t"] / 2 + P["strip_t"]
rect(sk, -3.5, 3.5, y0, y0 + 3, "-3.5", "3.5", "params.fin_t / 2 + params.strip_t",
     "params.fin_t / 2 + params.strip_t + 3")
pocket("WireSlot", sk, through=True)

sk = sketch(base, "GrooveSketch")
rrect(sk, extra="params.groove_clr")
rrect(sk, extra="-params.wall - params.groove_clr")
pocket("Groove", sk, "params.skirt_d")

sk = sketch(base, "UsbNotchSketch", z="-params.body_h")
yb = -P["body_d"] / 2
rect(sk, -P["usb_w"] / 2, P["usb_w"] / 2, yb - 1, yb + P["body_wall"] + 1,
     "-params.usb_w / 2", "params.usb_w / 2", "-params.body_d / 2 - 1", "-params.body_d / 2 + params.body_wall + 1")
pocket("UsbNotch", sk, "params.usb_h", reversed_=True)

# ================= strip reference (not printed) =================
ref_parts = []


def box(name, L, W, H, x, y, z):
    o = doc.addObject("Part::Box", name)
    expr(o, Length=L, Width=W, Height=H, Placement__Base__x=x, Placement__Base__y=y, Placement__Base__z=z)
    ref_parts.append(o)
    return o


box("ref_strip_front", "params.strip_w", "params.strip_t", "params.fin_h",
    "-params.strip_w / 2", "params.fin_t / 2", "0")
box("ref_strip_back", "params.strip_w", "params.strip_t", "params.fin_h",
    "-params.strip_w / 2", "-params.fin_t / 2 - params.strip_t", "0")
# the 180 deg bend: half tube over the fin's round top, axis along x
m = App.Matrix(0, 0, 1, 0,  1, 0, 0, 0,  0, 1, 0, 0,  0, 0, 0, 1)   # cylinder axis (local z) -> global x, local x -> y, local y -> z
cyl = []
for nm, r in (("ref_bend_out", "params.fin_t / 2 + params.strip_t"), ("ref_bend_in", "params.fin_t / 2")):
    c = doc.addObject("Part::Cylinder", nm)
    c.Angle = 180
    c.Placement = App.Placement(m)
    expr(c, Radius=r, Height="params.strip_w", Placement__Base__x="-params.strip_w / 2",
         Placement__Base__z="params.fin_h")
    c.Visibility = False
    cyl.append(c)
bend = doc.addObject("Part::Cut", "ref_bend")
bend.Base, bend.Tool = cyl
ref_parts.append(bend)
for i in range(int(P["px_side"])):  # LED count fixed at generation; rerun the script if px_side changes
    zc = f"params.pitch * ({i} + 0.5) - params.led_s / 2"
    box(f"ref_led_front{i + 1}", "params.led_s", "params.led_h", "params.led_s",
        "-params.led_s / 2", "params.fin_t / 2 + params.strip_t", zc)
    box(f"ref_led_back{i + 1}", "params.led_s", "params.led_h", "params.led_s",
        "-params.led_s / 2", "-params.fin_t / 2 - params.strip_t - params.led_h", zc)
strip_ref = doc.addObject("Part::Compound", "StripReference")
strip_ref.Links = ref_parts

doc.recompute()

# Visibility and colours live in the GUI half of the file, so they are only saved when the GUI is up
if App.GuiUp:
    import FreeCADGui as Gui
    gd = Gui.getDocument(doc.Name)
    for o in doc.Objects:
        if gd.getObject(o.Name):
            gd.getObject(o.Name).Visibility = False
    style = {base: ((0.9, 0.9, 0.87), 0), fin: ((0.35, 0.55, 0.9), 0), dif: ((1.0, 0.92, 0.75), 65)}
    for o, (colour, transp) in style.items():
        vo = gd.getObject(o.Name)
        vo.Visibility = True
        gd.getObject(o.Tip.Name).Visibility = True   # a Body draws through its Tip feature
        vo.ShapeColor = colour
        vo.Transparency = transp
    for o in ref_parts:   # shown one by one (not via the StripReference compound) so the LEDs get their own colour
        gd.getObject(o.Name).Visibility = True
        gd.getObject(o.Name).ShapeColor = (1.0, 0.8, 0.0) if o.Name.startswith("ref_led") else (0.15, 0.6, 0.25)
    gd.ActiveView.viewIsometric()
    gd.ActiveView.fitAll()

bad = []
for o in doc.Objects:
    if o.isDerivedFrom("Sketcher::SketchObject"):
        if o.solve() != 0 or (hasattr(o, "FullyConstrained") and not o.FullyConstrained):
            bad.append(f"{o.Name} (solve={o.solve()}, fully={getattr(o, 'FullyConstrained', '?')})")
    elif "Invalid" in o.State or "Error" in o.State:
        bad.append(f"{o.Name} {o.State}")
for bd in (fin, dif, base):
    if bd.Shape.isNull() or not bd.Shape.isValid() or len(bd.Shape.Solids) != 1:
        bad.append(f"{bd.Name} shape")
if bad:
    raise SystemExit("problems: " + "; ".join(bad))

doc.saveAs(os.path.join(HERE, "candle.FCStd"))


def export(body, fname, rot=None):
    s = body.Shape.copy()
    if rot:
        s.rotate(V(0, 0, 0), V(1, 0, 0), rot)
    s.translate(V(0, 0, -s.BoundBox.ZMin))
    m = Mesh.Mesh()
    m.addFacets(s.tessellate(0.02))
    m.write(os.path.join(STL_DIR, fname))
    bb = s.BoundBox
    print(f"{fname}: {bb.XLength:.1f} x {bb.YLength:.1f} x {bb.ZLength:.1f} mm, valid={s.isValid()}")


os.makedirs(STL_DIR, exist_ok=True)
export(base, "candle_base.stl", rot=180)   # top face on the bed: socket, slot, groove need no supports
export(fin, "candle_fin.stl")              # upright, plug down
export(dif, "candle_diffuser.stl")         # skirt down, hollow and open at the bottom
for k in ("pitch", "bend", "fin_h", "flame_h"):
    print(k, round(sheet.get(k), 2))
print("bend fits between pixels:", sheet.get("bend") <= sheet.get("pitch") - sheet.get("led_s"))
