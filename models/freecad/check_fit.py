# Sanity check for candle.FCStd: LED-to-diffuser gaps and part interference.
#   flatpak run --command=FreeCADCmd org.freecad.FreeCAD check_fit.py
import os
import FreeCAD as App
import Part

doc = App.openDocument(os.path.join(os.getcwd(), "candle.FCStd"))
p = doc.getObject("params")
diff = doc.getObject("Diffuser").Shape
# vase mode prints only the side wall: drop the flat bottom face of the solid
skin = Part.Compound([f for f in diff.Faces if f.BoundBox.ZLength > 1e-6])
for o in doc.Objects:
    if o.Name.startswith("ref_led") or o.Name == "ref_bend":
        d = o.Shape.distToShape(skin)[0] - p.get("wall")
        print(f"{o.Name:16s} gap to diffuser inner wall {d:.2f} mm (target {p.get('gap')} at LEDs)")
print(f"bend {p.get('bend'):.1f} mm fits in the {p.get('pitch') - p.get('led_s'):.1f} mm between pixels:",
      p.get("bend") <= p.get("pitch") - p.get("led_s"))

base = doc.getObject("Base").Shape
for n in ("Fin", "StripReference"):
    print(f"{n} overlaps base: {doc.getObject(n).Shape.common(base).Volume:.3f} mm3")
print(f"StripReference overlaps fin: {doc.getObject('StripReference').Shape.common(doc.getObject('Fin').Shape).Volume:.3f} mm3")
# the skirt's printed wall (outer section minus wall) must drop into the groove without touching the base
sk = doc.getObject("SkirtSketch")
face = Part.Face(Part.Wire(Part.__sortEdges__(sk.Shape.Edges)))
h = App.Vector(0, 0, p.get("skirt_d"))
ring = face.extrude(h).cut(face.makeOffset2D(-p.get("wall"), 2).extrude(h))
print(f"diffuser skirt wall overlaps base: {ring.common(base).Volume:.3f} mm3")
