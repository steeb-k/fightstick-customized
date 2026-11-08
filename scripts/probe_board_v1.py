"""Point probes for Arcade-stick_bottom_board_v1 (board base: wall 9.5, floor z -66.7, board z -63.2..-61.6)."""
import FreeCAD as App, Part
doc = App.openDocument("/home/steeb/fightstick/Arcade-stick_bottom_board_v1.FCStd")
sh = [o for o in doc.Objects if hasattr(o, "Shape")][0].Shape
shell = [o for o in App.openDocument("/home/steeb/fightstick/Arcade-stick_top_v7.FCStd").Objects if hasattr(o, "Shape")][0].Shape
print("solids", len(sh.Solids), "valid", sh.isValid(), "vol %.0f" % sh.Volume, flush=True)
print("overlap with shell v6: volume %.4f" % sh.common(shell).Volume, flush=True)
bx, by = 107.0, 57.0
tests = [
 ("pocket bore mid height (air)",        (bx+2.5, by, -64.0), False),
 ("boss wall beside bore",               (bx+3.5, by, -64.0), True),
 ("head seat just below ledge (air)",    (bx+2.5, by, -60.7), False),
 ("ledge layer solid beside slot",       (bx, by+2.5, -60.4), True),
 ("3.4 hole above ledge (air)",          (bx, by, -55.0), False),
 ("hole edge r1.9 solid",                (bx+1.9, by, -55.0), True),
 ("vertical wall z -55",                 (124.8, 10.0, -55.0), True),
 ("outside vertical wall (air)",         (125.2, 10.0, -55.0), False),
 ("bevel skin z -65",                    (122.6, 10.0, -65.0), True),
 ("outside bevel (air)",                 (123.2, 10.0, -65.0), False),
 ("floor solid",                         (10.0, 10.0, -67.5), True),
 ("above floor between grid (air)",      (10.0, 10.0, -61.0), False),
 ("panel skin y 74.5 z -66",             (48.0, 74.5, -66.0), True),
 ("panel outside y 75.2 (air)",          (48.0, 75.2, -66.0), False),
 ("no panel at x 0: y 74.5 z -66 (air)", (0.0, 74.5, -66.0), False),
 ("panel flare x 75.5 y 73.5 z -66",     (75.5, 73.5, -66.0), True),
 ("beyond flare x 80 y 73.5 z -66 (air)",(80.0, 73.5, -66.0), False),
 ("pocket air y 73.5 z -62 (board edge)",(60.0, 73.5, -62.0), False),
 ("pocket air y 73.5 z -57 (over USB-C)",(60.0, 73.5, -57.0), False),
 ("pocket top closed y 73.5 z -56.0",    (60.0, 73.5, -56.0), True),
 ("wall above pocket y 73 z -53",        (60.0, 73.0, -53.0), True),
 ("inner bevel removed y 71 z -63.3",    (60.0, 71.0, -63.3), False),
 ("inner bevel kept below pocket y 70.6 z -64.5", (60.0, 70.6, -64.5), True),
 ("USB-B slot center z -56 (air)",       (42.3, 74.5, -56.0), False),
 ("USB-B slot edge x+6.5 (air)",         (48.8, 74.5, -56.0), False),
 ("USB-B slot edge x+7.0 solid",         (49.3, 74.5, -56.0), True),
 ("USB-B slot through lip z -49 (air)",  (42.3, 72.8, -49.0), False),
 ("USB-B slot through wall top z -50.5 (air)", (42.3, 74.0, -50.5), False),
 ("lip beside slot x 50 z -49",          (50.0, 72.8, -49.0), True),
 ("USB-B slot bottom z -62.2 (air)",     (42.3, 74.5, -62.2), False),
 ("below USB-B z -62.5 solid",           (42.3, 74.5, -62.5), True),
 ("USB-B body room y 72.5 z -51 (air)",  (42.3, 72.5, -51.0), False),
 ("USB-C hole center (air)",             (55.7, 74.5, -59.97), False),
 ("USB-C hole edge x+5 (air)",           (60.7, 74.5, -59.97), False),
 ("USB-C hole edge x+5.4 solid",         (61.1, 74.5, -59.97), True),
 ("USB-C top z -57.8 (air)",             (55.7, 74.5, -57.8), False),
 ("above USB-C z -57.3 solid",           (55.7, 74.5, -57.3), True),
 ("web between slot and USB-C x 49.8",   (49.8, 74.5, -59.97), True),
 ("standoff solid near top",             (30.176+3.5, -18.474, -63.5), True),
 ("standoff top just above (air)",       (30.176+3.5, -18.474, -63.0), False),
 ("insert lip (air)",                    (30.176+2.5, -18.474, -63.7), False),
 ("insert hole r2 (air)",                (30.176+2.0, -18.474, -68.0), False),
 ("insert hole wall r2.4 solid",         (30.176+2.4, -18.474, -68.0), True),
 ("floor under insert hole z -69.1",     (30.176, -18.474, -69.1), True),
 ("hole bottom z -68.6 (air)",           (30.176, -18.474, -68.6), False),
 ("back standoff full top at y+4",       (67.124, 73.574, -63.3), True),
 ("grid cleared under board",            (48.0, 20.0, -64.0), False),
 ("grid wall x -47.96 y 10 z -64",       (-47.96, 10.0, -64.0), True),
 ("plug inner part z -48 y 72.8",        (0.0, 72.8, -48.0), True),
 ("plug inner top z -47.6 (air)",        (0.0, 72.8, -47.6), False),
 ("plug outer part z -48.6 y 74.8",      (0.0, 74.8, -48.6), True),
 ("plug outer top z -48.3 (air)",        (0.0, 74.8, -48.3), False),
 ("plug outer edge x 3.5 (air)",         (3.5, 74.8, -49.0), False),
 ("plug outside y 75.2 (air)",           (0.0, 75.2, -49.0), False),
 ("lip top z -48.4 (air)",               (20.0, 72.8, -48.4), False),
]
bad = 0
for name, pt, want in tests:
    got = sh.isInside(App.Vector(*pt), 1e-4, True)
    flag = "ok " if got == want else "BAD"
    bad += got != want
    print("%s %-46s %s -> %s" % (flag, name, pt, got), flush=True)
print("probe BAD count:", bad, flush=True)
