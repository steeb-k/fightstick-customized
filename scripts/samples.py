"""Sample top shells built from scripts/arcade_stick.py without touching it or the v7 files.

  flatpak run --filesystem=home --command=freecadcmd org.freecad.FreeCAD scripts/samples.py [8btn] [diamond]

Outputs go to samples/ (FCStd + STL):
  Arcade-stick_top_v7_sample_8btn     eight 30 mm buttons on top (cluster shifted 19 mm left, fourth column
                                      dropped toward the front to clear the seam loop and the back-right lid post),
                                      no right-wall buttons
  Arcade-stick_top_v7_sample_diamond  the v7 top without the two right-wall buttons, with a diamond-plate texture
                                      inside the palm-rest bezel area (lozenge-shaped divots, face stays flush)

The build script is executed with its main() call disabled, so its P dict and builders are reused as they are.
"""
import os, re, sys, math, copy
import FreeCAD as App, Part
V = App.Vector

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "arcade_stick.py")).read()
src = re.sub(r"^main\(\)", "# main()", src, flags=re.M)
ns = {"__name__": "arcade_stick", "__file__": os.path.join(HERE, "arcade_stick.py")}
exec(compile(src, ns["__file__"], "exec"), ns)
P0 = copy.deepcopy(ns["P"])
ns["OUT"] = os.path.join(HERE, "..", "samples") + os.sep
os.makedirs(ns["OUT"], exist_ok=True)

# ---------------------------------------------------------------- shared checks
BODY_R = 17.0        # 30 mm button body envelope under the plate (34 mm), as used everywhere else
BOARD = (-16.0, -65.5, 80.3, -20.19)   # hung board outline

def rect_dist(px, py, x0, y0, x1, y1):
    cx = min(max(px, x0), x1); cy = min(max(py, y0), y1)
    return math.hypot(px - cx, py - cy)

def clearance_report(P):
    """Print the plan-view clearances of every 30 mm top button against the things under the plate."""
    posts = ns["posts_xy"]()
    X, W = P["X"], P["WALL"]
    seam_in = X - P["SEAM_INSET"] - P["SEAM_W"]
    jx, jy = P["JOY"]
    print("  button clearances (negative = interference under the 34 mm body assumption):")
    for i, (bx, by) in enumerate(P["BUTTONS30"], 1):
        dpost = min(math.hypot(bx - px, by - py) for (px, py) in posts) - P["POST_R"] - BODY_R
        dboard = rect_dist(bx, by, *BOARD) - BODY_R
        dribs = min(rect_dist(bx, by, x0, y0, x1, y1) for (x0, y0, x1, y1, d) in P["RIBS"]) - BODY_R
        dwall = (X - W) - abs(bx) - BODY_R
        dseam = seam_in - (abs(bx) + P["BTN30_R"])
        djoy = max(abs(bx - jx), abs(by - jy)) - 32.5 - BODY_R
        dpad = rect_dist(bx, by, jx - P["JOY_PAD_W"] / 2, jy - P["JOY_PAD_L"] / 2, jx + P["JOY_PAD_W"] / 2, jy + P["JOY_PAD_L"] / 2) - BODY_R
        print("   %d (%7.2f,%7.2f) post %5.1f  board %5.1f  ribs %5.1f  wall %5.1f  seam %5.1f  joystick body %5.1f  pad %5.1f"
              % (i, bx, by, dpost, dboard, dribs, dwall, dseam, djoy, dpad), flush=True)

def overlap_check(shape):
    for n in ("Arcade-stick_bottom_v7", "Arcade-stick_bottom_board_v1"):
        doc = App.openDocument(os.path.join(HERE, "..", n + ".FCStd"))
        other = [o for o in doc.Objects if hasattr(o, "Shape")][0].Shape
        print("  overlap with %s: %.4f" % (n, shape.common(other).Volume), flush=True)
        App.closeDocument(doc.Name)

def probe(shape, tests):
    bad = 0
    for name, (x, y, z), want in tests:
        got = shape.isInside(V(x, y, z), 1e-6, True)
        ok = got == want; bad += not ok
        print("   %s %-48s (%.2f, %.2f, %.2f) %s" % ("ok " if ok else "BAD", name, x, y, z, "solid" if got else "air"), flush=True)
    return bad

def build_variant(name, P, post=None):
    ns["P"].clear(); ns["P"].update(P)
    shell = ns["build_shell"]()
    if post is not None:
        shell = ns["check"](post(shell, P), name)
    ok = ns["export"](shell, name)
    return shell, ok

# ---------------------------------------------------------------- 1. eight buttons on top
def eight_button_params():
    P = copy.deepcopy(P0)
    S = 19.0                                      # whole cluster left (17 keeps column 2's back button at v7's margin from the post at (15, 57); 19 is 1.8 mm closer)
    six = [(x - S, y) for (x, y) in P0["BUTTONS30"]]
    c3t, c3b = six[4], six[5]
    # fourth column: back button 36 mm from column 3's back button, dropped to y 30 so its hole stays 1 mm+ off the
    # seam loop groove and clear of the lid post at (107, 57); front button 36 mm from both its neighbors (the
    # two-circle intersection)
    y4t = 30.0
    c4t = (c3t[0] + math.sqrt(36.0 ** 2 - (c3t[1] - y4t) ** 2), y4t)
    dx, dy = c4t[0] - c3b[0], c4t[1] - c3b[1]; d = math.hypot(dx, dy)
    mx, my = (c3b[0] + c4t[0]) / 2, (c3b[1] + c4t[1]) / 2; h = math.sqrt(36.0 ** 2 - (d / 2) ** 2)
    c4b = (mx + h * dy / d, my - h * dx / d)
    P["BUTTONS30"] = [(round(x, 3), round(y, 3)) for (x, y) in six + [c4t, c4b]]
    P["RIGHT_WALL_BTNS_Y"] = []
    ribs = []
    for r in P0["RIBS"]:
        if r[:4] == (-19.5, -97.5, -16.3, 72.5):
            ribs.append((-19.5, -97.5, -16.3, -19.6, 10.0))   # divider: front wall to the back-left board post; column 1's front body is above
        elif r[:4] in ((100.5, -2.0, 103.5, 72.5), (100.5, -2.0, 122.5, 1.0)):
            continue                                          # right rib and its leg sat under the new column
        else:
            ribs.append(r)
    ribs.append((79.0, -29.5, 122.5, -27.5, 7.0))     # cross rib: right rear board post to the right wall, under column 4 (7 deep over the board edge)
    ribs.append((100.5, -72.0, 103.5, -27.5, 10.0))   # right rib: front rib up to the cross rib
    P["RIBS"] = ribs
    return P

# ---------------------------------------------------------------- 2. diamond plate in the palm rest
TEX_DEPTH = 0.6        # lozenge divots this deep; the face between them stays flush
TEX_MARGIN = 3.0       # untextured border kept between the pattern and the seam loop / front bezel line
LOZ_L, LOZ_W, LOZ_PITCH = 10.0, 3.6, 10.0

def lozenge(cx, cy, ang, z0, z1):
    a = math.radians(ang); c, s = math.cos(a), math.sin(a)
    pts = [(LOZ_L / 2, 0), (0, LOZ_W / 2), (-LOZ_L / 2, 0), (0, -LOZ_W / 2)]
    vs = [V(cx + c * x - s * y, cy + s * x + c * y, z0) for (x, y) in pts]
    return Part.Face(Part.makePolygon(vs + [vs[0]])).extrude(V(0, 0, z1 - z0))

def diamond_plate(shell, P):
    X, YF, ZT = P["X"], P["YF"], P["ZTOP"]
    si = P["SEAM_INSET"] + P["SEAM_W"]                        # seam loop inner edge
    x0, x1 = -X + si + TEX_MARGIN, X - si - TEX_MARGIN
    y0 = YF + si + TEX_MARGIN
    y1 = P["BEZEL_FRONT_Y"] - P["BEZEL_W"] / 2 - TEX_MARGIN   # front bezel line's front edge
    r = max(P["SEAM_R"] - P["SEAM_W"] - TEX_MARGIN, 2.0)
    # the pattern area clips the lozenges; the divots are the lozenges themselves, TEX_DEPTH into the top face
    field = Part.Face(ns["rrect_wire"](x0, x1, y0, y1, r, ZT - TEX_DEPTH - 1)).extrude(V(0, 0, TEX_DEPTH + 3))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    ni = int((x1 - x0) / 2 / LOZ_PITCH) + 1; nj = int((y1 - y0) / 2 / LOZ_PITCH) + 1
    loz = []
    for i in range(-ni, ni + 1):
        for j in range(-nj, nj + 1):
            loz.append(lozenge(cx + i * LOZ_PITCH, cy + j * LOZ_PITCH, 45 if (i + j) % 2 == 0 else -45, ZT - TEX_DEPTH, ZT + 1))
    cutter = loz[0].fuse(loz[1:]).common(field)
    print("  diamond plate: pattern area x %.1f..%.1f y %.1f..%.1f, %d lozenge divots %.0f x %.1f at %.0f mm pitch, %.1f deep"
          % (x0, x1, y0, y1, len(loz), LOZ_L, LOZ_W, LOZ_PITCH, TEX_DEPTH), flush=True)
    return shell.cut(cutter)

def diamond_params():
    P = copy.deepcopy(P0)
    P["RIGHT_WALL_BTNS_Y"] = []
    return P

# ---------------------------------------------------------------- run
def main():
    which = [a for a in sys.argv[1:] if a in ("8btn", "diamond")] or ["8btn", "diamond"]
    ok = True
    if "8btn" in which:
        P = eight_button_params()
        print("8btn BUTTONS30 =", P["BUTTONS30"], flush=True)
        clearance_report(P)
        shell, good = build_variant("Arcade-stick_top_v7_sample_8btn", P)
        ok &= good
        tests = []
        for i, (bx, by) in enumerate(P["BUTTONS30"], 1):
            tests += [("button %d hole center (air)" % i, (bx, by, 0.0), False),
                      ("button %d plate at r15.5" % i, (bx + 15.5, by, 0.0), True)]
        tests += [("old right-wall button spot solid", (P["X"] - 1.0, -61.0, P["WALL_BTN_Z"]), True),
                  ("old right-wall button spot solid 2", (P["X"] - 1.0, -21.0, P["WALL_BTN_Z"]), True),
                  ("divider rib present at y -30", (-18.0, -30.0, -8.0), True),
                  ("divider rib gone at y 0", (-18.0, 0.0, -8.0), False),
                  ("cross rib under column 4", (110.0, -28.5, -6.0), True),
                  ("cross rib 7 deep over board edge", (80.0, -28.5, -9.0), False),
                  ("right rib down to the front rib", (102.0, -50.0, -8.0), True),
                  ("old right rib gone at y 30", (102.0, 30.0, -8.0), False),
                  ("seam loop groove at right still open", (P["X"] - P["SEAM_INSET"] - 0.6, 27.0, 0.5), False)]
        bad = probe(shell, tests); ok &= bad == 0
        overlap_check(shell)
    if "diamond" in which:
        P = diamond_params()
        shell, good = build_variant("Arcade-stick_top_v7_sample_diamond", P, post=diamond_plate)
        ok &= good
        ZT = P["ZTOP"]
        tests = [("lozenge divot at pattern center (air at z 0.8)", (0.0, -58.6, ZT - 0.2), False),
                 ("divot bottom solid (z 0.3)", (0.0, -58.6, ZT - 0.7), True),
                 ("face between lozenges flush (solid at z 0.8)", (5.0, -58.6, ZT - 0.2), True),
                 ("lozenge clipped at the pattern edge (solid)", (113.5, -58.6, ZT - 0.2), True),
                 ("border beside seam loop flush", (0.0, -90.0, ZT - 0.2), True),
                 ("border behind front bezel line flush", (0.0, -28.0, ZT - 0.2), True),
                 ("front bezel line still cut", (0.0, -25.6, ZT - 0.5), False),
                 ("seam loop still cut", (0.0, -100.0 + 7.8 + 0.6, ZT - 0.5), False),
                 ("old right-wall button spot solid", (P["X"] - 1.0, -61.0, P["WALL_BTN_Z"]), True),
                 ("old right-wall button spot solid 2", (P["X"] - 1.0, -21.0, P["WALL_BTN_Z"]), True)]
        bad = probe(shell, tests); ok &= bad == 0
        overlap_check(shell)
    print("ALL OK" if ok else "PROBLEMS", flush=True)

main()
