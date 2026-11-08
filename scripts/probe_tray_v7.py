import FreeCAD as App, Part
doc = App.openDocument("/home/steeb/fightstick/Arcade-stick_bottom_v7.FCStd")
sh = [o for o in doc.Objects if hasattr(o, "Shape")][0].Shape
print("solids", len(sh.Solids), "valid", sh.isValid(), "vol %.0f" % sh.Volume, flush=True)
bx, by = 107.0, 57.0
tests = [
 ("recess centre (air)",            (bx, by, -53.5), False),
 ("recess r2.5 (air)",              (bx+2.5, by, -53.5), False),
 ("boss wall r3.5 at recess z",     (bx+3.5, by, -53.0), True),
 ("boss wall r5.8 mid height",      (bx+5.8, by, -45.0), True),
 ("outside boss r6.3 (air)",        (bx+6.3, by, -45.0), False),
 ("layer1 slot along x (air)",      (bx+2.5, by, -50.4), False),
 ("layer1 beside slot (solid)",     (bx, by+2.5, -50.4), True),
 ("layer2 slot along y (air)",      (bx, by+2.5, -50.0), False),
 ("layer2 beside slot (solid)",     (bx+2.5, by, -50.0), True),
 ("above ledge r2.5 (solid)",       (bx+2.5, by, -49.0), True),
 ("hole centre above ledge (air)",  (bx, by, -49.0), False),
 ("hole r1.5 (air)",                (bx+1.5, by, -45.0), False),
 ("hole edge r1.9 (solid)",         (bx+1.9, by, -45.0), True),
 ("boss top just below lip top",    (bx, by+3.0, -38.6), True),
 ("boss top just above lip top",    (bx, by+3.0, -38.4), False),
 ("outer bevel mid: inside skin",   (122.7, 10.0, -49.0), True),
 ("outer bevel mid: outside (air)", (123.3, 10.0, -49.0), False),
 ("inner bevel mid: in wall",       (120.3, 10.0, -49.0), True),
 ("inner bevel mid: cavity (air)",  (119.7, 10.0, -49.0), False),
 ("bevel bottom edge skin",         (120.8, 10.0, -53.9), True),
 ("bevel bottom beyond (air)",      (121.3, 10.0, -53.9), False),
 ("vertical wall",                  (124.8, 10.0, -42.0), True),
 ("lip",                            (122.3, 10.0, -39.0), True),
 ("lip outside (air)",              (123.8, 10.0, -39.0), False),
 ("floor solid",                    (10.0, 10.0, -53.5), True),
 ("above floor between grid (air)", (10.0, 10.0, -51.0), False),
]
bad = 0
for name, pt, want in tests:
    got = sh.isInside(App.Vector(*pt), 1e-4, True)
    flag = "ok " if got == want else "BAD"
    bad += got != want
    print("%s %-34s %s -> %s" % (flag, name, pt, got), flush=True)
print("probe BAD count:", bad, flush=True)
