"""Point probes for Arcade-stick_top_v7 (round 5: joystick at x -53.8, buttons +5, no divider line, seam loop at 7.8, no groove)."""
import FreeCAD as App
def load(n): return [o for o in App.openDocument("/home/steeb/fightstick/%s.FCStd" % n).Objects if hasattr(o, "Shape")][0].Shape
sh = load("Arcade-stick_top_v7")
print("solids", len(sh.Solids), "valid", sh.isValid(), "vol %.0f" % sh.Volume, flush=True)
for t in ("Arcade-stick_bottom_v7", "Arcade-stick_bottom_board_v1"):
    print("overlap with %s: %.4f" % (t, sh.common(load(t)).Volume), flush=True)
JX, JY = -53.8, 23.0
tests = [
 ("joystick hole center (air)",             (JX, JY, 0.0), False),
 ("joystick hole r11.5 (air)",              (JX + 11.5, JY, 0.0), False),
 ("plate beside hole r12.5",                (JX + 12.5, JY, 0.0), True),
 ("old joystick spot now solid plate",      (-73.8, 23.0, 0.0), True),
 ("ring groove r35.25 z 0.5 (air)",         (JX + 35.25, JY, 0.5), False),
 ("ring groove r35.25 z 0.5 (air) left",    (JX - 35.25, JY, 0.5), False),
 ("ring groove bottom z -0.1 solid",        (JX + 35.25, JY, -0.1), True),
 ("inside ring r34.0 z 0.5 solid",          (JX + 34.0, JY, 0.5), True),
 ("old ring spot r35.25 around -73.8 solid",(-73.8 - 35.25, 23.0, 0.5), True),
 ("pad under plate z -5 at pad corner",     (JX + 26.0, JY + 47.0, -5.0), True),
 ("pad edge beyond x -25.3 (air) z -5",     (-24.8, JY, -5.0), False),
 ("pad insert hole (air)",                  (JX + 20.0, JY + 40.0, -5.5), False),
 ("pad insert lip (air)",                   (JX - 20.0 + 2.5, JY - 40.0, -6.5), False),
 ("ring recess under pad (air)",            (JX + 14.0, JY, -6.5), False),
 ("no divider line at x -31.45 z 0.5",      (-31.45, 20.0, 0.5), True),
 ("front line y -25.6 z 0.5 (air)",         (0.0, -25.6, 0.5), False),
 ("front line ends at x 116.0 (air)",       (116.0, -25.6, 0.5), False),
 ("front line beyond x 117.5 solid",        (117.5, -25.6, 0.5), True),
 ("seam loop outer edge in: 8.0 from wall (air)", (0.0, 75.0 - 8.0, 0.5), False),
 ("seam loop 7.5 from wall solid",          (0.0, 75.0 - 7.5, 0.5), True),
 ("seam loop 9.3 from wall solid",          (0.0, 75.0 - 9.3, 0.5), True),
 ("seam loop left wall 8.4 in (air)",       (-125.0 + 8.4, 0.0, 0.5), False),
 ("seam loop front wall 8.4 in (air)",      (0.0, -100.0 + 8.4, 0.5), False),
 ("old seam spot 3.4 from wall solid",      (0.0, 75.0 - 3.4, 0.5), True),
 ("no groove: wall solid at 0.5 in z -6",   (124.5, 10.0, -6.0), True),
 ("no groove: back wall z -4",              (10.0, 74.5, -4.0), True),
 ("button 6 hole at 82.535 (air)",          (82.535 + 14.0, 12.45, 0.0), False),
 ("button 6 old edge now solid",            (77.535 - 14.0, 12.45, 0.0), True),
 ("button 1 hole (air)",                    (18.165, 34.6 + 14.0, 0.0), False),
 ("divider rib x -18 y 0 z -8 solid",       (-18.0, 0.0, -8.0), True),
 ("divider rib full depth y -50 z -10.5",   (-18.0, -50.0, -10.5), True),
 ("divider rib bottom y -50 z -11.5 (air)", (-18.0, -50.0, -11.5), False),
 ("board post 12 tall: z -12.9 solid",      (-11.824 + 3.0, -61.374, -12.9), True),
 ("board post bottom z -13.2 (air)",        (-11.824 + 3.0, -61.374, -13.2), False),
 ("board post insert hole z -9 (air)",      (-11.824, -61.374, -9.0), False),
 ("board post insert hole top z -7.2 solid",(-11.824, -61.374, -7.2), True),
 ("post rib 7 deep z -7.5 solid",           (-11.824, -45.0, -7.5), True),
 ("post rib bottom z -8.5 (air)",           (-11.824, -45.0, -8.5), False),
 ("old divider spot x -31.5 z -8 (air)",    (-31.5, 0.0, -8.0), False),
 ("board edge x -16 clear z -8 (air)",      (-15.9, -45.0, -8.0), False),
 ("left rib extended x -20 y -39 z -8",     (-20.0, -39.0, -8.0), True),
 ("back rib left segment x -100 y 68 z -8", (-100.0, 68.0, -8.0), True),
 ("back rib right segment x 0 y 68 z -8",   (0.0, 68.0, -8.0), True),
 ("back rib absent under pad x -50 y 68 z -8 (air)", (-50.0, 68.0, -8.0), False),
 ("pad present x -50 y 68 z -4",            (-50.0, 68.0, -4.0), True),
 ("back post stub x -14.9 y 70 z -8",       (-14.9, 70.0, -8.0), True),
 ("board post x -11.8 y -24.4 z -6.5",      (-11.824 + 3.0, -24.426, -6.5), True),
 # round 5b: chamfer 6 tall, 2.4 in (inset = 2.4 * (z + 5) / 6); right-wall buttons at y -37 / 3; right rib from y 22
 ("chamfer z -2: inset 1.0 (air)",           (124.0, 10.0, -2.0), False),
 ("chamfer z -2: inset 1.4 solid",           (123.6, 10.0, -2.0), True),
 ("chamfer z 0.5: inset 1.9 (air)",          (123.1, 10.0, 0.5), False),
 ("chamfer z 0.5: inset 2.6 solid",          (122.4, 10.0, 0.5), True),
 ("below chamfer z -5.5: inset 0.2 solid",   (124.8, 10.0, -5.5), True),
 ("chamfer back wall z 0.5 inset 2.6 solid", (10.0, 75.0 - 2.6, 0.5), True),
 ("chamfer back wall z 0.5 inset 1.9 (air)", (10.0, 75.0 - 1.9, 0.5), False),
 ("chamfer corner z 0.5 at 45 deg: inset 2.6 solid", (125.0 - 10.0 + (10.0 - 2.6) * 0.7071, 75.0 - 10.0 + (10.0 - 2.6) * 0.7071, 0.5), True),
 ("upper right-wall hole center y -21 (air)",(123.0, -21.0, -24.75), False),
 ("upper right-wall hole top y -21 z -10.5 (air)", (123.0, -21.0, -10.5), False),
 ("wall solid above hole z -9.3",            (123.0, -21.0, -9.3), True),
 ("old hole spot y 3 now solid",             (123.0, 3.0, -24.75), True),
 ("hole edge y -6.5 (air)",                  (123.0, -6.5, -24.75), False),
 ("wall solid between holes y -41",          (123.0, -41.0, -24.75), True),
 ("lower right-wall hole center y -61 (air)",(123.0, -61.0, -24.75), False),
 ("wall solid at old lower hole y -37",      (123.0, -38.0, -24.75), True),
 ("right rib at y 0 z -8 solid",             (102.0, 0.0, -8.0), True),
 ("right rib at y 23.5 z -8 still solid",    (102.0, 23.5, -8.0), True),
 ("right rib leg y -0.5 x 115 z -8 solid",   (115.0, -0.5, -8.0), True),
 ("no rib at y -4 x 102 z -8 (air)",         (102.0, -4.0, -8.0), False),
 ("no leg at y 23.5 x 115 z -8 (air)",       (115.0, 23.5, -8.0), False),
 # round 5c: seam loop corners r 10 (outer) / 8.8 (inner), arc center (107.2, 57.2) at the back-right corner
 ("loop corner r 9.9 at 45 deg (air)",       (107.2 + 9.9 * 0.7071, 57.2 + 9.9 * 0.7071, 0.5), False),
 ("loop corner r 8.9 at 45 deg (air)",       (107.2 + 8.9 * 0.7071, 57.2 + 8.9 * 0.7071, 0.5), False),
 ("loop corner r 10.2 at 45 deg solid",      (107.2 + 10.2 * 0.7071, 57.2 + 10.2 * 0.7071, 0.5), True),
 ("loop corner r 8.6 at 45 deg solid",       (107.2 + 8.6 * 0.7071, 57.2 + 8.6 * 0.7071, 0.5), True),
 ("old tight corner spot (116.0, 66.0) now solid", (116.0, 66.0, 0.5), True),
 ("front-left corner r 9.4 at 225 deg (air)",(-107.2 - 9.4 * 0.7071, -82.2 - 9.4 * 0.7071, 0.5), False),
 ("loop straight run back y 66.6 (air)",     (0.0, 66.6, 0.5), False),
 ("loop straight run right x 116.6 (air)",   (116.6, 0.0, 0.5), False),
]
bad = 0
for name, pt, want in tests:
    got = sh.isInside(App.Vector(*pt), 1e-4, True)
    flag = "ok " if got == want else "BAD"; bad += got != want
    print("%s %-48s %s -> %s" % (flag, name, pt, got), flush=True)
print("probe BAD count:", bad, flush=True)
