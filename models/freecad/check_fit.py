# Sanity check for candle.FCStd: LED-to-diffuser gaps and part interference.
#   flatpak run --command=FreeCADCmd org.freecad.FreeCAD check_fit.py
import os
import FreeCAD as App
import Part

doc = App.openDocument(os.path.join(os.getcwd(), "candle.FCStd"))
p = doc.getObject("params")
diff = doc.getObject("diffuser").Shape
# vase mode prints only the side wall: drop the flat bottom face of the solid
skin = Part.Compound([f for f in diff.Faces if f.BoundBox.ZLength > 1e-6])
for o in doc.Objects:
    if o.Name.startswith("ref_led"):
        d = o.Shape.distToShape(skin)[0] - p.get("wall")
        print(f"{o.Name:16s} gap to diffuser inner wall {d:.2f} mm (target {p.get('gap')})")

base = doc.getObject("base").Shape
for n in ("fin", "strip_reference"):
    print(f"{n} overlaps base: {doc.getObject(n).Shape.common(base).Volume:.3f} mm3")
# the skirt's printed wall (outer section minus wall) must drop into the groove without touching the base
sk = doc.getObject("diffuser_skirt_sk").Shape
h = App.Vector(0, 0, p.get("skirt_d"))
ring = sk.extrude(h).cut(sk.makeOffset2D(-p.get("wall"), 2).extrude(h))
print(f"diffuser skirt wall overlaps base: {ring.common(base).Volume:.3f} mm3")
