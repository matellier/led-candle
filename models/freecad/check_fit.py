# Sanity check for candle.FCStd: LED-to-diffuser gaps and part interference.
#   flatpak run --command=FreeCADCmd org.freecad.FreeCAD check_fit.py
import os
import FreeCAD as App
import Part

doc = App.openDocument(os.path.join(os.getcwd(), "candle.FCStd"))
p = doc.getObject("params")
diff = doc.getObject("Diffuser").Shape
# the diffuser is a hollow shell, so the nearest point to anything inside it is on the inner wall
for o in doc.Objects:
    if o.Name.startswith("ref_led") or o.Name == "ref_bend":
        d = o.Shape.distToShape(diff)[0]
        print(f"{o.Name:16s} gap to diffuser inner wall {d:.2f} mm (target {p.get('gap')} at LEDs)")
print(f"bend {p.get('bend'):.1f} mm fits in the {p.get('pitch') - p.get('led_s'):.1f} mm between pixels:",
      p.get("bend") <= p.get("pitch") - p.get("led_s"))

base = doc.getObject("Base").Shape
for n in ("Fin", "StripReference"):
    print(f"{n} overlaps base: {doc.getObject(n).Shape.common(base).Volume:.3f} mm3")
print(f"StripReference overlaps fin: {doc.getObject('StripReference').Shape.common(doc.getObject('Fin').Shape).Volume:.3f} mm3")
# the skirt must drop into the groove without touching the base
print(f"Diffuser overlaps base: {diff.common(base).Volume:.3f} mm3")
print(f"Diffuser overlaps fin: {diff.common(doc.getObject('Fin').Shape).Volume:.3f} mm3")
