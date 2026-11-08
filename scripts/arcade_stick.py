"""Parametric rebuild of the arcade stick top shell and bottom tray.

Run headless:
  flatpak run --filesystem=home --command=freecadcmd org.freecad.FreeCAD scripts/arcade_stick.py

Coordinate frame = the original STEP: x across (250 wide), y front(-)/back(+),
z up with the top surface at z=+1. The tray is modelled mated to the shell.
Every number that matters is in P below.
"""
import FreeCAD as App, Part, MeshPart, math, sys
V = App.Vector
OUT = "/home/steeb/fightstick/"

P = dict(
    # ---- box ----
    X=125.0, YB=75.0, YF=-100.0, R=10.0,       # outer half-width, back wall, front wall, corner radius
    WALL=2.8, TOP=2.0,                          # wall thickness, top plate thickness
    ZTOP=1.0, ZBOT=-50.0,                       # top surface, shell bottom (= tray rim); round 3: 10 mm taller
    REBATE_H=1.5, REBATE_IN=1.45,               # lap joint: shell rebate height, wall left (tray lip fits inside)
    LIP_CLEAR=0.1,
    GROOVE_Z=(-5.0, -2.0), GROOVE_D=0.0,        # groove around the outside walls; round 5: none, the walls are smooth (was 1.4 deep over 3 tall)
    EDGE_CHAMF=6.0, EDGE_CHAMF_IN=2.4,          # chamfer around the top edge: 6 tall, 2.4 in = the tray bevel's 22 deg (round 5b; was 2 x 2 at 45 deg). 0 = none
    PALM_CHAMF=0.0,                             # 45 deg palm-rest slope across the front (0 = none; 15 was tried and rejected)
    # ---- top face decoration ----
    SEAM_W=1.2, SEAM_D=1.0, SEAM_FRONT_GAP=1.7, # seam loop (0.4 -> 0.8 -> 1.2 wide); gap from the palm chamfer break line, if any
    SEAM_INSET=7.8,                             # loop's outer edge from the outer wall; round 5: 5 mm further in than the wall thickness (was 2.8, right at the chamfer)
    SEAM_R=10.0,                                # loop's outer corner radius: the enclosure's own (round 5c; was the concentric offset, 2.2 at this inset)
    BEZEL_W=1.2, BEZEL_D=1.0,                   # inner lines the same width as the seam loop (were 0.7 / ring 0.5)
    BEZEL_FRONT_Y=-25.6, BEZEL_DIV_X=None,      # front line's inner edge 48 mm from the joystick center; round 5: no divider line
    # ---- controls ----
    BUTTONS30=[(18.165, 34.6), (13.165, -1.05), (51.535, 48.1), (46.535, 12.45), (87.535, 48.1), (82.535, 12.45)],   # round 5: all 5 mm right
    BTN30_R=15.0, BTN24_R=12.0,
    JOY=(-53.8, 23.0), JOY_R=12.0, JOY_DX=40.0, JOY_DY=80.0,       # round 5: 20 mm in from the left (was -73.8)
    # round 3: hidden joystick screws. A pad under the plate carries blind insert holes; a shallow recess
    # around the shaft hole bears on the 30 mm lubricant ring (1 mm proud of the plate) so it stays pressed.
    JOY_PAD_W=57.0, JOY_PAD_L=99.0, JOY_PAD_R=4.0, JOY_PAD_T=5.0,   # 95 x 53 plate + 2 mm each side; 5 mm thick
    JOY_HOLE_D=5.5,                                                 # insert hole depth incl. lip, from the pad face
    JOY_RING_R=15.5, JOY_RING_D=0.8,                                # recess: 31 mm dia, 0.8 deep (ring 1 mm proud -> 0.2 squeeze)
    BEZEL_RING_R=35.25,                         # ring centerline radius; width = BEZEL_W
    RIGHT_WALL_BTNS_Y=[-61.0, -21.0],           # 30 mm buttons on the right wall; round 5e: bodies clear button 6's body (y -2.55) by 3.45 (were -32, 8)
    LEFT_WALL_BTNS_Y=[-31.0, -61.0],            # 24 mm buttons on the left wall
    WALL_BTN_Z=-24.75,                          # centered in the taller wall
    # ---- lid posts (shell) / bosses (tray) ----
    POST_R=5.5, POST_HOLE_D=8.0,                # insert hole depth incl. lip: 4 mm insert + room for an M3 x 20 tip
    # ---- heat-set inserts (M3, 5.0 OD, 4 mm long): hole + a 1 mm centering lip at the mouth ----
    INSERT_HOLE_R=2.2, INSERT_LIP_R=2.65, INSERT_LIP_D=1.0,
    POST_FRONT_Y=-84.0,                         # 16 mm from the new front wall
    POSTS_BACK=[(-107.0, 57.0), (107.0, 57.0), (-14.86, 57.0), (15.0, 57.0)],
    POSTS_FRONT_X=[-107.0, 107.0, -12.0],
    BOSS_R=6.0,                                 # tray boss outside radius (was 5.5 with a 9 mm bore: 1 mm walls, one snapped)
    BOSS_CB_R=3.1, BOSS_CB_D=3.4,               # head recess from the underside: 6.2 mm dia, 3.4 deep (M3 SHCS head 5.5 x 3.0)
    BOSS_HOLE_R=1.7,                            # 3.4 mm M3 clearance hole the rest of the way up
    BRIDGE_LAYER=0.4,                           # support-free ledge: two crossed slot layers bridge the recess before the round hole
    # ---- GP2040-CE RP2040 Advanced Breakout ----
    # round 3: board moved 12 mm toward the joystick (x -16 to 80.3) for clearance from the right-wall buttons
    BOARD_HOLES=[(-11.824, -61.374), (76.138, -61.374), (76.138, -24.426), (-11.824, -24.426)],
    BOARD_POST_R=5.0, BOARD_POST_H=12.0, BOARD_HOLE_D=5.5,   # round 5d: posts 12 tall, 2 below the ribs, so the USB-C plug needs no relief (was 6)
    # ---- ribs under the top plate: (x0, y0, x1, y1, depth below the plate) ----
    # Round 3: 10 mm deep where nothing is underneath (the box is 10 mm taller); 7 mm over the 24 mm button
    # bodies on the left wall (tops 10.25 mm below the plate) and over the board (round 5d: its solder side is
    # 12 mm below the plate, so 7 leaves 3 mm). The green areas from the print review are 3 mm wide.
    # Every rib ends in a wall, a post, the joystick pad, or another rib.
    RIBS=[
        # divider: round 5 moved beside the board edge (x -16), between it and the joystick body envelope (-21.3);
        # fused into the two left board posts and the back-center post stub
        (-19.5, -97.5, -16.3, 72.5, 10.0),     # divider, front wall to back wall, full depth: the plug passes 1 mm+ below it
        (-25.0, 67.0, 122.5, 69.0, 10.0),      # back rib: joystick pad (right edge -25.3) to right wall
        (-122.5, 67.0, -82.0, 69.0, 10.0),     # back rib: left wall to the joystick pad (left edge -82.3)
        (100.5, -2.0, 103.5, 72.5, 10.0),      # right rib: back wall down to just above the upper right-wall button body (y -6)
        (100.5, -2.0, 122.5, 1.0, 10.0),       # right rib's leg into the right wall (the green L)
        (-95.0, -72.0, 122.5, -70.0, 10.0),    # front rib, main span
        (-122.5, -72.0, -95.0, -70.0, 7.0),    # front rib over the forward left-wall button body, into the left wall
        (-95.0, -40.0, -16.3, -38.0, 10.0),    # left rib: behind the plug path, ends in the divider
        (-122.5, -40.0, -95.0, -38.0, 7.0),    # left rib over the rear left-wall button body, into the left wall
        (-12.824, -70.0, -10.824, -24.426, 7.0),  # through both left board posts, front rib to rear post (3 mm above the board)
        (75.138, -70.0, 77.138, -24.426, 7.0),    # through both right board posts
        (-13.0, -79.0, -11.0, -70.0, 10.0),    # center front post to front rib (lines up with the left board rib)
        (106.0, -79.0, 108.0, -70.0, 10.0),    # right front post to front rib
        (-108.0, -79.0, -106.0, -70.0, 7.0),   # left front post to front rib (button body beside and below it)
        (-108.0, 62.0, -106.0, 72.5, 10.0),    # back posts to the back wall, through the back rib
        (-16.36, 62.0, -13.36, 72.5, 10.0),
        (13.5, 62.0, 16.5, 72.5, 10.0),
        (105.5, 62.0, 108.5, 72.5, 10.0),
    ],
    # ---- USB cutout at back wall centre, straddling the seam ----
    USB_IN_W=9.8, USB_IN_H=4.9, USB_IN_R=2.4, USB_IN_D=1.45, USB_OUT_W=7.0, USB_OUT_H=3.5, USB_OUT_R=1.0,
    # ---- tray ----
    TRAY_PLATE=2.8, TRAY_BEVEL_H=10.0, TRAY_BEVEL_IN=4.0,   # outside bevel: 10 tall, 4 in = 22 deg from vertical (7 in / 35 deg drooped)
    TRAY_WALL_H=4.0,                                        # vertical outside wall below the rim
    TRAY_LIP_H=1.5,
    GRID_WALL=1.6, GRID_H=4.5, GRID_CELL_MIN=(21.86, 20.83), GRID_BEVEL_EXT=1.5, GRID_CLEAR_R=16.0,
    JOY_TRAY_HOLE_R=5.0,
    # ---- alternate base: GP2040-CE board on the floor, USB-C and USB-B out the back wall ----
    # The board lies front to back (long axis y) with its port edge in a pocket in the back wall. The outside
    # bevel is filled in over the board's span so the back face is a flat vertical panel there.
    # Height: the USB-B slot is open at the top and the shell's bottom edge closes it, so the board top sits
    # PORT_CLEAR + USBB_H below the rim and the vertical wall height follows from the stack below the board.
    # The lid-screw head pockets get deeper by the same amount, so the lid screws stay M3 x 16..20.
    B2_X0=26.0, B2_W=45.3, B2_L=96.3, B2_T=1.6,  # board outline (5 mm from the back-center boss), thickness
    B2_HOLE_IN=(4.176, 4.126),                   # mounting holes inset from the board edges (x, y)
    B2_EDGE_GAP=0.3,                             # board back edge to the pocket face
    B2_SKIN=1.0,                                 # wall left outside the board-edge pocket
    B2_STANDOFF_R=5.0, B2_STANDOFF_H=3.5, B2_INSERT_D=5.5,   # 3.5 clears the solder joints; 0.8 mm floor stays under the hole
    B2_PANEL_MARGIN=3.0, B2_PANEL_FLARE=4.0,     # flat panel: past the board each side, 45 deg ends
    USBC_OFF=15.6, USBC_W=8.94, USBC_H=3.26,     # USB-C: center from the board's +x edge, shell size; face flush
    USBB_OFF=29.0, USBB_W=12.0, USBB_H=10.9,     # USB-B: likewise; shell 2.7 proud of the board edge
    PORT_CLEAR=0.7, PORT_R=1.5,
    BUMP_CLEAR=0.15,                             # plug that fills the shell's half of the old USB slot
)

# ------------------------------------------------------------------ helpers
def rrect_wire(x0, x1, y0, y1, r, z):
    r = max(r, 0.01)
    e = []
    e.append(Part.makeLine(V(x0 + r, y0, z), V(x1 - r, y0, z)))
    e.append(Part.makeCircle(r, V(x1 - r, y0 + r, z), V(0, 0, 1), -90, 0))
    e.append(Part.makeLine(V(x1, y0 + r, z), V(x1, y1 - r, z)))
    e.append(Part.makeCircle(r, V(x1 - r, y1 - r, z), V(0, 0, 1), 0, 90))
    e.append(Part.makeLine(V(x1 - r, y1, z), V(x0 + r, y1, z)))
    e.append(Part.makeCircle(r, V(x0 + r, y1 - r, z), V(0, 0, 1), 90, 180))
    e.append(Part.makeLine(V(x0, y1 - r, z), V(x0, y0 + r, z)))
    e.append(Part.makeCircle(r, V(x0 + r, y0 + r, z), V(0, 0, 1), 180, 270))
    return Part.Wire(e)

def outline(inset, z):
    """Box outline inset by `inset` from the outer wall, as a wire at height z."""
    return rrect_wire(-P["X"] + inset, P["X"] - inset, P["YF"] + inset, P["YB"] - inset, P["R"] - inset, z)

def prism(inset, z0, z1):
    return Part.Face(outline(inset, z0)).extrude(V(0, 0, z1 - z0))

def loft(inset0, z0, inset1, z1):
    return Part.makeLoft([outline(inset0, z0), outline(inset1, z1)], True, True)

def box(x0, y0, z0, x1, y1, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))

def cyl(r, x, y, z0, z1):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0))

def cyl_x(r, y, z, x0, x1):
    return Part.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))

def cyl_y(r, x, z, y0, y1):
    return Part.makeCylinder(r, y1 - y0, V(x, y0, z), V(0, 1, 0))

def halfspace_above(zoff):
    """Region z > y + zoff (above a 45 deg plane rising toward +y), spanning the whole box."""
    ys = [P["YF"] - 60, P["YF"] - 60, P["YF"] + 200, P["YF"] + 200]
    pts = [V(-P["X"] - 5, P["YF"] - 60, P["YF"] - 60 + zoff), V(-P["X"] - 5, P["YF"] - 60, 200),
           V(-P["X"] - 5, 200, 200), V(-P["X"] - 5, 200, 200 + zoff)]
    # polygon in the yz plane at x=-X-5: on-plane points at both y extremes, closed high above
    pts = [V(-P["X"] - 5, P["YF"] - 60, P["YF"] - 60 + zoff), V(-P["X"] - 5, 150, 150 + zoff),
           V(-P["X"] - 5, 150, 400), V(-P["X"] - 5, P["YF"] - 60, 400)]
    f = Part.Face(Part.makePolygon(pts + [pts[0]]))
    return f.extrude(V(2 * P["X"] + 10, 0, 0))

def slot_y(w, h, r, zc, y0, y1):
    """Slot through a y-wall: width w (x), from zc-h to zc+h ... built as rounded-top opening:
    x in [-w/2,w/2], z from zc - h (open below) to zc + h with corner radius r at the top."""
    s = box(-w / 2, y0, zc - h, w / 2, y1, zc + h - r)
    s = s.fuse(box(-w / 2 + r, y0, zc - h, w / 2 - r, y1, zc + h))
    for sx in (-1, 1):
        s = s.fuse(cyl_y(r, sx * (w / 2 - r), zc + h - r, y0, y1))
    return s

def rounded_slot_y(wd, ht, r, zseam, y0, y1):
    """Rounded rectangle wd wide (x) by 2*ht tall (z), centred on the seam, extruded from y0 to y1."""
    w = rrect_wire(-wd / 2, wd / 2, zseam - ht, zseam + ht, r, 0)
    s = Part.Face(w).extrude(V(0, 0, -(y1 - y0)))
    s.rotate(V(0, 0, 0), V(1, 0, 0), 90)      # local (x,y,z) -> world (x,-z,y)
    s.translate(V(0, y0, 0))
    return s

def usb_cutout(zseam, upper):
    """USB opening at the back wall centre, straddling the shell/tray seam.
    Wide shallow recess from the inside, narrower slot through the outer skin.
    upper=True returns the shell half, False the tray half."""
    yb, w = P["YB"], P["WALL"]
    yin, yout = yb - w, yb - P["USB_IN_D"]
    inner = rounded_slot_y(P["USB_IN_W"], P["USB_IN_H"], P["USB_IN_R"], zseam, yin - 0.1, yout)
    outer = rounded_slot_y(P["USB_OUT_W"], P["USB_OUT_H"], P["USB_OUT_R"], zseam, yout - 0.01, yb + 0.1)
    both = inner.fuse(outer)
    keep = box(-20, yin - 1, zseam if upper else zseam - 20, 20, yb + 1, zseam + 20 if upper else zseam)
    return both.common(keep)

def insert_hole(x, y, zface, depth):
    """Blind heat-set insert hole going up from a downward-facing face at zface: a centering lip
    (INSERT_LIP_R, INSERT_LIP_D deep) at the mouth, then the press-fit hole to `depth` below... i.e. above the face."""
    lip = cyl(P["INSERT_LIP_R"], x, y, zface - 1, zface + P["INSERT_LIP_D"])
    hole = cyl(P["INSERT_HOLE_R"], x, y, zface + P["INSERT_LIP_D"] - 0.01, zface + depth)
    return lip.fuse(hole)

def insert_hole_down(x, y, zface, depth):
    """Blind heat-set insert hole going down from an upward-facing face at zface (standoff top)."""
    lip = cyl(P["INSERT_LIP_R"], x, y, zface - P["INSERT_LIP_D"], zface + 1)
    hole = cyl(P["INSERT_HOLE_R"], x, y, zface - depth, zface - P["INSERT_LIP_D"] + 0.01)
    return lip.fuse(hole)

def port_hole(cx, cz, w, h, y0, y1):
    """Rounded rectangle w by h centered at (cx, cz) through a y-wall from y0 to y1, PORT_CLEAR added all round."""
    c = P["PORT_CLEAR"]
    s = rounded_slot_y(w + 2 * c, h / 2 + c, P["PORT_R"], cz, y0, y1)
    s.translate(V(cx, 0, 0))
    return s

def posts_xy():
    return list(P["POSTS_BACK"]) + [(x, P["POST_FRONT_Y"]) for x in P["POSTS_FRONT_X"]]

def check(shape, name):
    shape = shape.removeSplitter()
    print("%s: valid=%s solids=%d volume=%.0f bbox=%s" % (name, shape.isValid(), len(shape.Solids), shape.Volume, shape.BoundBox))
    return shape

def export(shape, name):
    doc = App.newDocument(name.replace("-", "_"))
    o = doc.addObject("Part::Feature", name); o.Shape = shape
    doc.saveAs(OUT + name + ".FCStd")
    m = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.05, AngularDeflection=math.radians(10), Relative=False)
    ok = m.isSolid() and not m.hasNonManifolds() and not m.hasSelfIntersections()
    print("  mesh solid=%s nonmanifold=%s selfint=%s facets=%d" % (m.isSolid(), m.hasNonManifolds(), m.hasSelfIntersections(), m.CountFacets))
    if not m.isSolid():
        from collections import Counter
        cnt = Counter()
        for f in m.Facets:
            i = f.PointIndices
            for a, b in ((i[0], i[1]), (i[1], i[2]), (i[2], i[0])):
                cnt[(min(a, b), max(a, b))] += 1
        pts = m.Points
        locs = sorted({tuple(round((getattr(pts[a], c) + getattr(pts[b], c)) / 2, 1) for c in "xyz") for (a, b), n in cnt.items() if n == 1})
        print("  open edges at:", locs[:20])
    m.write(OUT + name + ".stl")
    return ok

# ------------------------------------------------------------------ top shell
def build_shell():
    X, YB, YF, W = P["X"], P["YB"], P["YF"], P["WALL"]
    ZT, ZB = P["ZTOP"], P["ZBOT"]
    zceil = ZT - P["TOP"]
    ec = P["EDGE_CHAMF"]
    pc = P["PALM_CHAMF"]
    yfront_top = YF + pc                        # palm chamfer break line on the top face (= YF when none)
    c_out = ZT - yfront_top                     # palm plane z = y + c_out
    c_in = c_out - W * math.sqrt(2)             # parallel plane, wall thickness inboard

    # outer body with a 45 deg chamfer around the top edge
    outer = prism(0, ZB, ZT - ec)
    if ec > 0:
        outer = outer.fuse(loft(0, ZT - ec, P["EDGE_CHAMF_IN"], ZT))
    cavity = prism(W, ZB - 1, zceil)
    if pc > 0:
        cavity = cavity.cut(halfspace_above(c_in))
    shell = outer.cut(cavity)

    # lid posts: from the rebate top up into the plate (clipped later by the chamfer)
    zpost0 = ZB + P["REBATE_H"]
    for (x, y) in posts_xy():
        shell = shell.fuse(cyl(P["POST_R"], x, y, zpost0, zceil + 0.5))
    # ribs
    for (x0, y0, x1, y1, d) in P["RIBS"]:
        shell = shell.fuse(box(x0, y0, zceil - d, x1, y1, zceil + 0.5))
    # board standoffs
    for (x, y) in P["BOARD_HOLES"]:
        shell = shell.fuse(cyl(P["BOARD_POST_R"], x, y, zceil - P["BOARD_POST_H"], zceil + 0.5))
    # joystick pad: the mounting plate sits on this, screws into inserts from below
    jx, jy = P["JOY"]
    zpad = zceil - P["JOY_PAD_T"]
    pw, pl, pr = P["JOY_PAD_W"], P["JOY_PAD_L"], P["JOY_PAD_R"]
    shell = shell.fuse(Part.Face(rrect_wire(jx - pw / 2, jx + pw / 2, jy - pl / 2, jy + pl / 2, pr, zpad)).extrude(V(0, 0, P["JOY_PAD_T"] + 0.5)))

    # optional palm-rest slope across the whole front
    if pc > 0:
        shell = shell.cut(halfspace_above(c_out))

    cuts = []
    # rebate for the tray lip
    cuts.append(prism(P["REBATE_IN"], ZB - 0.1, ZB + P["REBATE_H"]))
    # outside groove: wedge = band prism minus 45 deg loft
    if P["GROOVE_D"] > 0:
        gz0, gz1 = P["GROOVE_Z"]
        cuts.append(prism(-0.1, gz0, gz1).cut(loft(0, gz0, P["GROOVE_D"], gz1)))
    # seam loop on the top face
    si_ = P["SEAM_INSET"]
    sy0 = yfront_top + (P["SEAM_FRONT_GAP"] if pc > 0 else si_)   # no palm slope: same inset as the other sides
    so = rrect_wire(-X + si_, X - si_, sy0, YB - si_, P["SEAM_R"], ZT - P["SEAM_D"])
    si = rrect_wire(-X + si_ + P["SEAM_W"], X - si_ - P["SEAM_W"], sy0 + P["SEAM_W"], YB - si_ - P["SEAM_W"], P["SEAM_R"] - P["SEAM_W"], ZT - P["SEAM_D"])
    cuts.append(Part.Face(so).extrude(V(0, 0, P["SEAM_D"] + 1)).cut(Part.Face(si).extrude(V(0, 0, P["SEAM_D"] + 1))))
    # bezel lines
    bw, bd = P["BEZEL_W"], P["BEZEL_D"]
    jx, jy = P["JOY"]
    r0, r1 = P["BEZEL_RING_R"] - bw / 2, P["BEZEL_RING_R"] + bw / 2
    cuts.append(cyl(r1, jx, jy, ZT - bd, ZT + 1).cut(cyl(r0, jx, jy, ZT - bd - 1, ZT + 2)))
    fy = P["BEZEL_FRONT_Y"]; dx = P["BEZEL_DIV_X"]
    sm = P["SEAM_INSET"] + P["SEAM_W"] / 2     # end lines mid-way across the seam groove
    cuts.append(box(-X + sm, fy - bw / 2, ZT - bd, X - sm, fy + bw / 2, ZT + 1))
    if dx is not None:
        cuts.append(box(dx - bw / 2, fy - bw / 2, ZT - bd, dx + bw / 2, YB - sm, ZT + 1))
    # top holes
    for (x, y) in P["BUTTONS30"]:
        cuts.append(cyl(P["BTN30_R"], x, y, zceil - 1, ZT + 1))
    cuts.append(cyl(P["JOY_R"], jx, jy, zpad - 1, ZT + 1))
    cuts.append(cyl(P["JOY_RING_R"], jx, jy, zpad - 1, zpad + P["JOY_RING_D"]))       # lubricant ring recess
    for sx in (-1, 1):
        for sy in (-1, 1):
            cuts.append(insert_hole(jx + sx * P["JOY_DX"] / 2, jy + sy * P["JOY_DY"] / 2, zpad, P["JOY_HOLE_D"]))
    # wall buttons
    for y in P["RIGHT_WALL_BTNS_Y"]:
        cuts.append(cyl_x(P["BTN30_R"], y, P["WALL_BTN_Z"], X - W - 1, X + 1))
    for y in P["LEFT_WALL_BTNS_Y"]:
        cuts.append(cyl_x(P["BTN24_R"], y, P["WALL_BTN_Z"], -X - 1, -X + W + 1))
    # insert holes in the lid posts and board posts
    for (x, y) in posts_xy():
        cuts.append(insert_hole(x, y, zpost0, P["POST_HOLE_D"]))
    for (x, y) in P["BOARD_HOLES"]:
        cuts.append(insert_hole(x, y, zceil - P["BOARD_POST_H"], P["BOARD_HOLE_D"]))
    # USB opening, shell half
    cuts.append(usb_cutout(ZB, True))

    allcuts = cuts[0].fuse(cuts[1:])
    shell = shell.cut(allcuts)
    return check(shell, "Arcade-stick_top_v7")

# ------------------------------------------------------------------ bottom tray
def build_tray(board=False):
    """Plain tray (board=False) or the alternate base with the GP2040-CE board on the floor (board=True)."""
    X, YB, YF, W = P["X"], P["YB"], P["YF"], P["WALL"]
    zrim = P["ZBOT"]                               # tray rim top = shell bottom
    zlip = zrim + P["TRAY_LIP_H"]
    if board:
        zbt = zrim - P["PORT_CLEAR"] - P["USBB_H"]                        # board top: USB-B top just under the shell
        zbb = zbt - P["B2_T"]                                             # board bottom
        zfloor = zbb - P["B2_STANDOFF_H"]
        zbot = zfloor - P["TRAY_PLATE"]
        zwall0 = zbot + P["TRAY_BEVEL_H"]
        extra = (zrim - zwall0) - P["TRAY_WALL_H"]                        # taller than the plain tray by this
        print("  board base: vertical wall %.2f (plain tray %.2f, +%.2f); head pockets %.2f deep" % (zrim - zwall0, P["TRAY_WALL_H"], extra, P["BOSS_CB_D"] + extra))
    else:
        zwall0 = zrim - P["TRAY_WALL_H"]
        zbot = zwall0 - P["TRAY_BEVEL_H"]
        zfloor = zbot + P["TRAY_PLATE"]
        extra = 0.0
    # outside: bevel, vertical wall, rim; lip inset to clear the shell rebate
    body = loft(P["TRAY_BEVEL_IN"], zbot, 0, zwall0)
    body = body.fuse(prism(0, zwall0 - 0.01, zrim))
    body = body.fuse(prism(P["REBATE_IN"] + P["LIP_CLEAR"], zrim - 0.01, zlip))
    if board:
        bx0 = P["B2_X0"]; bx1 = bx0 + P["B2_W"]
        by1 = YB - P["B2_SKIN"] - P["B2_EDGE_GAP"]; by0 = by1 - P["B2_L"]
        # flat panel: fills the bevel over the board span, 45 deg ends in plan
        m, fl = P["B2_PANEL_MARGIN"], P["B2_PANEL_FLARE"]
        pts = [V(bx0 - m - fl, YB - fl, zbot), V(bx1 + m + fl, YB - fl, zbot), V(bx1 + m, YB, zbot), V(bx0 - m, YB, zbot)]
        panel = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, 0, zwall0 - zbot + 0.3))
        body = body.fuse(panel)
    # inside: floor, inner bevel parallel to the outer one at wall thickness W measured
    # perpendicular to the slope, then the vertical inner wall at inset W
    slope = P["TRAY_BEVEL_IN"] / P["TRAY_BEVEL_H"]
    h = W / math.sin(math.atan2(P["TRAY_BEVEL_H"], P["TRAY_BEVEL_IN"]))   # horizontal offset between the two bevel faces
    zi_top = zwall0 + (h - W) / slope                                     # where the inner bevel meets the inner wall
    cav = Part.makeLoft([outline(W + (zi_top - zfloor) * slope, zfloor), outline(W, zi_top)], True, True)
    cav = cav.fuse(prism(W, zi_top - 0.01, zlip + 1))
    body = body.cut(cav)
    if board:
        # pocket in the back wall for the board edge and the USB-C shell: from just under the board up to just
        # over the USB-C, leaving B2_SKIN of wall; 45 deg top so it prints floor-down. Cut before the standoffs
        # are fused so they stay whole. The USB-B gets its own open-topped slot below.
        ypk = YB - P["B2_SKIN"]
        yin = YB - W - (zi_top - (zbb - 0.3)) * slope - 0.1               # inner bevel face at the pocket bottom
        zpk0 = zbb - 0.3
        zpk1 = zbt + P["USBC_H"] + P["PORT_CLEAR"] + 1.0
        pp = [V(0, yin, zpk0), V(0, ypk, zpk0), V(0, ypk, zpk1), V(0, yin, zpk1 + (ypk - yin))]
        pocket = Part.Face(Part.makePolygon(pp + [pp[0]])).extrude(V(bx1 - bx0 + 1.0, 0, 0))
        pocket.translate(V(bx0 - 0.5, 0, 0))
        body = body.cut(pocket)

    # penny grid on the floor
    fx = X - (W + (zi_top - zfloor) * slope); fy0 = YF + (W + (zi_top - zfloor) * slope); fy1 = YB - (W + (zi_top - zfloor) * slope)
    gw, ext = P["GRID_WALL"], P["GRID_BEVEL_EXT"]
    spanx = 2 * fx + gw; spany = (fy1 - fy0) + gw
    nx = int(spanx // (P["GRID_CELL_MIN"][0] + gw)); ny = int(spany // (P["GRID_CELL_MIN"][1] + gw))
    px, py = spanx / nx, spany / ny
    print("  grid: %dx%d cells, pitch %.2f x %.2f, cell %.2f x %.2f" % (nx, ny, px, py, px - gw, py - gw))
    grid = None
    zg1 = zfloor + P["GRID_H"]
    for i in range(nx + 1):
        xc = -fx - gw / 2 + i * px
        b = box(xc - gw / 2, fy0 - ext, zfloor - 0.5, xc + gw / 2, fy1 + ext, zg1)
        grid = b if grid is None else grid.fuse(b)
    for j in range(ny + 1):
        yc = fy0 - gw / 2 + j * py
        grid = grid.fuse(box(-fx - ext, yc - gw / 2, zfloor - 0.5, fx + ext, yc + gw / 2, zg1))
    jx, jy = P["JOY"]
    grid = grid.cut(cyl(P["GRID_CLEAR_R"], jx, jy, zfloor - 1, zg1 + 1))
    if board:
        grid = grid.cut(box(bx0 - 1, by0 - 1, zfloor - 1, bx1 + 1, by1 + 1, zg1 + 1))   # clear under the board
    # keep the grid inside the tray walls (trim what pokes into the bevel beyond ext)
    grid = grid.common(Part.makeLoft([outline(W + (zi_top - zfloor) * slope - ext - 0.3, zfloor - 1), outline(W + (zi_top - zfloor) * slope - ext - 0.3, zg1 + 1)], True, True))
    body = body.fuse(grid)

    # bosses: solid up to the lip, head recess from the underside just deeper than an M3 SHCS head,
    # then a 3.4 mm clearance hole. The screw head sits in the floor and the boss above it is nearly solid.
    for (x, y) in posts_xy():
        body = body.fuse(cyl(P["BOSS_R"], x, y, zfloor - 0.5, zlip))
    cuts = []
    bl, hr, cb = P["BRIDGE_LAYER"], P["BOSS_HOLE_R"], P["BOSS_CB_R"]
    zseat = zbot + P["BOSS_CB_D"] + extra
    for (x, y) in posts_xy():
        cuts.append(cyl(cb, x, y, zbot - 1, zseat))
        # ledge above the recess, printable without supports: layer 1 bridges the recess leaving a slot
        # along x, layer 2 the same along y, then the round hole. Each layer only bridges straight lines.
        cuts.append(box(x - cb - 0.1, y - hr, zseat - 0.01, x + cb + 0.1, y + hr, zseat + bl))
        cuts.append(box(x - hr, y - cb - 0.1, zseat + bl - 0.01, x + hr, y + cb + 0.1, zseat + 2 * bl))
        cuts.append(cyl(hr, x, y, zseat + 2 * bl - 0.01, zlip + 1))
    cuts.append(cyl(P["JOY_TRAY_HOLE_R"], jx, jy, zbot - 1, zfloor + 1))
    if not board:
        cuts.append(usb_cutout(zrim, False))
        name = "Arcade-stick_bottom_v7"
    else:
        # board standoffs with heat-set inserts from the top
        ix, iy = P["B2_HOLE_IN"]
        holes = [(bx0 + ix, by0 + iy), (bx1 - ix, by0 + iy), (bx1 - ix, by1 - iy), (bx0 + ix, by1 - iy)]
        for (x, y) in holes:
            body = body.fuse(cyl(P["B2_STANDOFF_R"], x, y, zfloor - 0.5, zbb))
            cuts.append(insert_hole_down(x, y, zbb, P["B2_INSERT_D"]))
        # port holes through the panel skin (the pocket is already open behind it)
        cuts.append(port_hole(bx1 - P["USBC_OFF"], zbt + P["USBC_H"] / 2, P["USBC_W"], P["USBC_H"], ypk - 0.5, YB + 0.5))
        # USB-B: slot open at the top, through the pocket, the wall top and the lip; the shell's bottom edge
        # closes it. Printed floor-down it needs no bridge at all.
        c = P["PORT_CLEAR"]
        z0 = zbt - c; z1 = zlip + 2
        slot = rounded_slot_y(P["USBB_W"] + 2 * c, (z1 - z0) / 2, P["PORT_R"], (z0 + z1) / 2, yin - 0.3, YB + 0.5)
        slot.translate(V(bx1 - P["USBB_OFF"], 0, 0))
        cuts.append(slot)
        # plug for the shell's half of the old USB slot: the slot shape less BUMP_CLEAR, flush outside
        c = P["BUMP_CLEAR"]
        yin_s, yout = YB - W, YB - P["USB_IN_D"]
        inner = rounded_slot_y(P["USB_IN_W"] - 2 * c, P["USB_IN_H"] / 2 - c, P["USB_IN_R"] - c, zrim, yin_s, yout - c)
        outer = rounded_slot_y(P["USB_OUT_W"] - 2 * c, P["USB_OUT_H"] / 2 - c, P["USB_OUT_R"] - c, zrim, yout - c - 0.01, YB)
        body = body.fuse(inner.fuse(outer))
        print("  board: x %.1f..%.1f  y %.1f..%.1f  bottom z %.2f top z %.2f; USB-C center x %.1f z %.2f; USB-B center x %.1f z %.2f"
              % (bx0, bx1, by0, by1, zbb, zbt, bx1 - P["USBC_OFF"], zbt + P["USBC_H"] / 2, bx1 - P["USBB_OFF"], zbt + P["USBB_H"] / 2))
        print("  pocket: y %.2f..%.2f z %.2f..%.2f; floor z %.2f; head seat z %.2f" % (yin, ypk, zpk0, zpk1, zfloor, zseat))
        name = "Arcade-stick_bottom_board_v1"
    body = body.cut(cuts[0].fuse(cuts[1:]))
    return check(body, name)

def main():
    import traceback
    which = [a for a in sys.argv if a in ("shell", "tray", "board")] or ["shell", "tray"]
    ok = True
    try:
        if "shell" in which:
            ok &= export(build_shell(), "Arcade-stick_top_v7")
        if "tray" in which:
            ok &= export(build_tray(), "Arcade-stick_bottom_v7")
        if "board" in which:
            ok &= export(build_tray(board=True), "Arcade-stick_bottom_board_v1")
    except Exception:
        traceback.print_exc(); ok = False
    print("ALL OK" if ok else "PROBLEMS", flush=True)

main()  # freecadcmd does not set __name__ == "__main__"
