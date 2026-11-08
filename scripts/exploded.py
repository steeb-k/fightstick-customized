"""Exploded (blow-up) parts diagram of the arcade stick, one image per bottom case.

Usage (FreeCAD's flatpak python has numpy + matplotlib):
  flatpak run --filesystem=home --command=python3 org.freecad.FreeCAD scripts/exploded.py [--top FILE] [--tray FILE] [--base FILE] [--scale PX_PER_MM]
  ... scripts/exploded.py --frames N --out-dir DIR     writes N animation frames per variant (DIR/plain_000.png ...):
      from very blown up with translucent cases, easing into the assembled unit with the cases turning solid.
      --transparent writes RGBA frames (nothing behind the parts). scripts/animate.sh renders them and encodes
      exploded_assembly.webp and .webm (both with alpha, for web pages) and exploded_assembly.mp4 (on the gray-blue background).
Defaults come from scripts/arcade_stick.py: the parameter block (button, joystick, board positions) and the
export names (Arcade-stick_top_vN, Arcade-stick_bottom_vN, Arcade-stick_bottom_board_vN), so rebuilding the
model and re-running this script keeps the diagrams current. Outputs exploded_plain_tray.png and
exploded_board_base.png in the project folder.

View: from the front-right, 45 degrees around, 30 degrees up, orthographic. Parts explode along their assembly
direction: top buttons up, wall buttons outward, joystick and board down, bottom case further down. The spacing is
computed so no part's projection overlaps the one above it. Colors: top case white, bottom case black, 30 mm
buttons red, 24 mm buttons black, board green, joystick red ball / black body / gray shaft and plate.
"""
import os, re, sys, math, struct
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
src = open(os.path.join(HERE, "arcade_stick.py")).read()
def num(name): return float(re.search(r"\b%s=(-?[\d.]+)" % name, src).group(1))
def pairs(name): return [tuple(float(v) for v in m) for m in re.findall(r"\((-?[\d.]+),\s*(-?[\d.]+)\)", re.search(r"\b%s=\[(.*?)\]" % name, src).group(1))]
def nums(name): return [float(v) for v in re.search(r"\b%s=\[(.*?)\]" % name, src).group(1).split(",")]
def export_name(prefix):
    return re.search(r'"(%s\d+)"' % prefix, src).group(1)

args = sys.argv[1:]
def opt(flag, default):
    return args[args.index(flag) + 1] if flag in args else default
TOP = opt("--top", export_name("Arcade-stick_top_v") + ".stl")
TRAY = opt("--tray", export_name("Arcade-stick_bottom_v") + ".stl")
BASE = opt("--base", export_name("Arcade-stick_bottom_board_v") + ".stl")
SCALE = float(opt("--scale", "4"))

X, YB, YF, W = num("X"), num("YB"), num("YF"), num("WALL")
ZT, TOPT = num("ZTOP"), num("TOP"); ZCEIL = ZT - TOPT
BTN = pairs("BUTTONS30"); R30, R24 = num("BTN30_R"), num("BTN24_R")
m = re.search(r"JOY=\((-?[\d.]+),\s*(-?[\d.]+)\)", src); JX, JY = float(m.group(1)), float(m.group(2))
PADT = num("JOY_PAD_T"); JDX, JDY = num("JOY_DX"), num("JOY_DY")
POSTS = pairs("POSTS_BACK") + [(x, num("POST_FRONT_Y")) for x in nums("POSTS_FRONT_X")]
ZB, REBATE_H, TRAY_LIP_H = num("ZBOT"), num("REBATE_H"), num("TRAY_LIP_H")
RWY, LWY, WBZ = nums("RIGHT_WALL_BTNS_Y"), nums("LEFT_WALL_BTNS_Y"), num("WALL_BTN_Z")
BH = pairs("BOARD_HOLES"); BPH = num("BOARD_POST_H")
B2X0, B2W, B2L, B2T = num("B2_X0"), num("B2_W"), num("B2_L"), num("B2_T")
B2_STAND, B2_SKIN, B2_GAP = num("B2_STANDOFF_H"), num("B2_SKIN"), num("B2_EDGE_GAP")
USBC_OFF, USBB_OFF = num("USBC_OFF"), num("USBB_OFF")
PORT_CLEAR, USBB_H = num("PORT_CLEAR"), num("USBB_H")
TRAY_PLATE, BEVEL_H = num("TRAY_PLATE"), num("TRAY_BEVEL_H")

# ------------------------------------------------------------------ colors
C = dict(white=(0.96, 0.96, 0.96), black=(0.20, 0.20, 0.22), red=(0.85, 0.12, 0.10), darkred=(0.55, 0.08, 0.07),
         green=(0.12, 0.48, 0.22), lightgreen=(0.30, 0.66, 0.34), gray=(0.62, 0.63, 0.66), silver=(0.80, 0.81, 0.84),
         dark=(0.12, 0.12, 0.13), brass=(0.80, 0.62, 0.25))

# ------------------------------------------------------------------ primitives (triangle arrays, shape (n, 3, 3))
def load_stl(path):
    d = open(path, "rb").read(); n = struct.unpack("<I", d[80:84])[0]
    a = np.frombuffer(d[84:84 + 50 * n], dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]))
    return a["v"].reshape(-1, 3, 3).astype(float)

def box(x0, y0, z0, x1, y1, z1):
    p = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0], [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]])
    f = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    return p[np.array(f)]

def frame(axis):
    """Orthonormal (u, v, w) with w along axis."""
    w = np.array(axis, float); w /= np.linalg.norm(w)
    a = np.array([0, 0, 1.0]) if abs(w[2]) < 0.9 else np.array([1.0, 0, 0])
    u = np.cross(a, w); u /= np.linalg.norm(u); v = np.cross(w, u)
    return u, v, w

def cylinder(r, c, axis, h0, h1, n=40, r_top=None):
    """Cylinder (or cone frustum) of radius r around the line through c along axis, from h0 to h1 along it."""
    u, v, w = frame(axis); c = np.array(c, float); rt = r if r_top is None else r_top
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    ring0 = c + h0 * w + r * (np.outer(np.cos(t), u) + np.outer(np.sin(t), v))
    ring1 = c + h1 * w + rt * (np.outer(np.cos(t), u) + np.outer(np.sin(t), v))
    tris = []
    for i in range(n):
        j = (i + 1) % n
        tris.append([ring0[i], ring0[j], ring1[j]]); tris.append([ring0[i], ring1[j], ring1[i]])
        tris.append([c + h0 * w, ring0[j], ring0[i]]); tris.append([c + h1 * w, ring1[i], ring1[j]])
    return np.array(tris)

def sphere(r, c, n=48):
    c = np.array(c, float); tris = []
    for i in range(n // 2):
        p0, p1 = np.pi * i / (n // 2), np.pi * (i + 1) / (n // 2)
        for j in range(n):
            t0, t1 = 2 * np.pi * j / n, 2 * np.pi * (j + 1) / n
            pt = lambda p, t: c + r * np.array([np.sin(p) * np.cos(t), np.sin(p) * np.sin(t), np.cos(p)])
            tris.append([pt(p0, t0), pt(p1, t0), pt(p1, t1)]); tris.append([pt(p0, t0), pt(p1, t1), pt(p0, t1)])
    return np.array(tris)

def transform(tris, offset):
    return tris + np.array(offset, float)

# ------------------------------------------------------------------ component models
def button30(center, axis, face_h):
    """Sanwa-style 30 mm snap-in: rim and plunger above the panel face, body behind it. center is on the panel
    face, axis points out of the panel, face_h is the coordinate of the face along the axis (0 here)."""
    parts = []
    parts.append((cylinder(17.0, center, axis, 0.0, 3.0), C["red"]))             # rim
    parts.append((cylinder(12.5, center, axis, 3.0, 5.0), C["red"]))             # plunger
    parts.append((cylinder(11.0, center, axis, 5.0, 6.0, r_top=9.0), C["red"]))  # plunger dome
    parts.append((cylinder(14.6, center, axis, -25.0, 0.0), C["darkred"]))       # body behind the panel
    return parts

def button24(center, axis):
    return [(cylinder(13.5, center, axis, 0.0, 2.5), C["black"]), (cylinder(10.0, center, axis, 2.5, 4.5), C["black"]),
            (cylinder(8.5, center, axis, 4.5, 5.3, r_top=7.0), C["black"]), (cylinder(11.6, center, axis, -22.0, 0.0), C["dark"])]

def insert(x, y, zface, up=False):
    """M3 x 5 x 4 heat-set insert in place: a brass cylinder with its bore showing on the open end. zface is the
    face of the hole; up=True means the hole faces down (post under the top), so the insert sits above the face."""
    z0, z1 = (zface, zface + 4.0) if up else (zface - 4.0, zface)
    parts = [(cylinder(2.5, (x, y, 0), (0, 0, 1), z0, z1, n=24), C["brass"])]
    zb = z0 if up else z1
    parts.append((cylinder(1.6, (x, y, 0), (0, 0, 1), zb - 0.06, zb + 0.06, n=16), C["dark"]))
    return parts

def joystick(lift=None):
    """Mounting plate under the pad, body below, shaft through the top, ball on top. Model coordinates."""
    zplate = ZCEIL - PADT          # plate top against the pad
    parts = []
    parts.append((box(JX - 26.5, JY - 47.5, zplate - 2.0, JX + 26.5, JY + 47.5, zplate), C["gray"]))
    for sx in (-1, 1):                                   # the four plate holes, as dark disks
        for sy in (-1, 1):
            parts.append((cylinder(1.7, (JX + sx * JDX / 2, JY + sy * JDY / 2, 0), (0, 0, 1), zplate - 2.05, zplate + 0.05, n=16), C["dark"]))
    parts.append((box(JX - 32.5, JY - 32.5, zplate - 34.0, JX + 32.5, JY + 32.5, zplate - 2.0), C["black"]))
    parts.append((cylinder(4.5, (JX, JY, 0), (0, 0, 1), zplate - 2.0, ZT + 44.0), C["gray"]))
    parts.append((cylinder(2.2, (JX, JY, 0), (0, 0, 1), ZT + 44.0, ZT + 52.0, n=24), C["dark"]))   # threaded stud
    parts.append((cylinder(22.0, (JX, JY, 0), (0, 0, 1), ZT, ZT + 1.2), C["black"]))          # dust washer
    parts.append((sphere(17.5, (JX, JY, ball_center_z(lift))), C["red"]))                  # ball top, lifted off the stud
    return parts

BALL_LIFT = 35.0
# explode offsets, mm: the cases are translucent so parts may overlap in the picture
EXPLODE = dict(buttons_up=35.0, wall_out=40.0, joystick_down=30.0, board_down={"plain": 110.0, "base": 115.0}, bottom_down=165.0)
def ball_center_z(lift=None): return ZT + 44.0 + 17.5 + (BALL_LIFT if lift is None else lift)   # bottom on the shaft tip; the stud is inside

def pcb(x0, y0, z0, long_axis, comp_dir, port_edge):
    """GP2040-CE Advanced Breakout, simplified. Board 96.3 x 45.3 x 1.6 with its low corner at (x0, y0), z0 = underside.
    long_axis 'x' or 'y'; comp_dir +1 components on top, -1 underneath; port_edge 'lo' or 'hi': which end of the
    long axis carries USB-C and USB-B. Features are defined on the board drawing: u across from the edge the USB-C is
    nearest (0..45.3), v along from the port edge (0..96.3), and mapped into the world with the right mirror."""
    L, Wd, T = B2L, B2W, B2T
    parts = []
    # mirror: local u = N x P (N = component-side normal, P = toward the port edge); compare with the across axis
    N = np.array([0, 0, float(comp_dir)])
    P = (np.array([1.0, 0, 0]) if long_axis == "x" else np.array([0, 1.0, 0])) * (1 if port_edge == "hi" else -1)
    A = np.array([0, 1.0, 0]) if long_axis == "x" else np.array([1.0, 0, 0])
    mirror = np.dot(np.cross(N, P), A) < 0
    def place(u, v, h0, h1, color):
        (u0, u1), (v0, v1) = u, v
        b0, b1 = (Wd - u1, Wd - u0) if mirror else (u0, u1)
        a0, a1 = (L - v1, L - v0) if port_edge == "hi" else (v0, v1)
        if comp_dir > 0: zz0, zz1 = z0 + T + h0, z0 + T + h1
        else: zz0, zz1 = z0 - h1, z0 - h0
        if long_axis == "x": parts.append((box(x0 + a0, y0 + b0, zz0, x0 + a1, y0 + b1, zz1), color))
        else: parts.append((box(x0 + b0, y0 + a0, zz0, x0 + b1, y0 + a1, zz1), color))
    # board, with the four mounting holes as dark disks on both faces
    if long_axis == "x": parts.append((box(x0, y0, z0, x0 + L, y0 + Wd, z0 + T), C["green"]))
    else: parts.append((box(x0, y0, z0, x0 + Wd, y0 + L, z0 + T), C["green"]))
    for a in (4.176, L - 4.176):
        for b in (4.126, Wd - 4.126):
            hx, hy = (x0 + a, y0 + b) if long_axis == "x" else (x0 + b, y0 + a)
            parts.append((cylinder(1.7, (hx, hy, 0), (0, 0, 1), z0 - 0.05, z0 + T + 0.05, n=16), C["dark"]))
    place((USBC_OFF - 4.5, USBC_OFF + 4.5), (-0.3, 7.2), 0.0, 3.3, C["silver"])            # USB-C, face flush with the edge
    place((USBB_OFF - 6.0, USBB_OFF + 6.0), (-2.7, 13.3), 0.0, USBB_H, C["silver"])         # USB-B, 2.7 proud
    place((Wd / 2 - 6.5, Wd / 2 + 6.5), (L - 14.5, L), 0.0, 7.0, C["silver"])              # USB-A at the far end
    for i in range(8):                                                                      # terminal column, USB-B side
        place((Wd - 8.5, Wd - 0.5), (10.0 + i * 10.0, 19.5 + i * 10.0), 0.0, 10.0, C["lightgreen"])
    for i in range(4):                                                                      # short terminal column, USB-C side
        place((0.5, 8.5), (48.0 + i * 10.0, 57.5 + i * 10.0), 0.0, 10.0, C["lightgreen"])
    place((1.0, 6.0), (10.0, 34.0), 0.0, 8.5, C["dark"])                                    # 20-pin header
    place((1.0, 6.0), (36.0, 46.0), 0.0, 8.5, C["dark"])                                    # 4-pin harness header
    place((Wd / 2 - 3.5, Wd / 2 + 3.5), (44.0, 51.0), 0.0, 1.0, C["dark"])                  # RP2040
    place((Wd / 2 - 2.0, Wd / 2 + 2.0), (60.0, 64.0), 0.0, 2.5, C["dark"])                  # buttons
    return parts

# ------------------------------------------------------------------ scene assembly
def scene(variant, factor=1.0, a_top=None, a_bot=None):
    """factor scales every explode distance (0 = assembled); a_top / a_bot override the case alphas."""
    a_top = ALPHA_TOP if a_top is None else a_top; a_bot = ALPHA_BOTTOM if a_bot is None else a_bot
    """Returns groups: list of (name, parts, explode_axis) in stacking order top to bottom.
    parts: list of (tris, color). explode_axis: 'z' (stack), '+x', '-x' (sideways)."""
    groups = []
    top_btns = []
    for (x, y) in BTN: top_btns += button30((x, y, ZT), (0, 0, 1), 0)
    groups.append(("30 mm buttons", top_btns, "up"))
    right = []
    for y in RWY: right += button30((X, y, WBZ), (1, 0, 0), 0)
    groups.append(("right wall buttons", right, "+x"))
    left = []
    for y in LWY: left += button24((-X, y, WBZ), (-1, 0, 0))
    groups.append(("24 mm buttons", left, "-x"))
    # top case, translucent, with its heat-set inserts in place inside the posts (opaque brass)
    zpost = ZB + REBATE_H; zpad = ZCEIL - PADT
    top = [(load_stl(os.path.join(ROOT, TOP)), C["white"], a_top)]
    for (x, y) in POSTS: top += insert(x, y, zpost, up=True)
    for sx in (-1, 1):
        for sy in (-1, 1): top += insert(JX + sx * JDX / 2, JY + sy * JDY / 2, zpad, up=True)
    if variant == "plain":
        for (x, y) in BH: top += insert(x, y, ZCEIL - BPH, up=True)
    groups.append(("top case", top, "fixed"))
    groups.append(("joystick", joystick(BALL_LIFT * factor), "down"))
    if variant == "plain":
        xs = [p[0] for p in BH]; ys = [p[1] for p in BH]
        x0, y0 = min(xs) - 4.176, min(ys) - 4.126
        groups.append(("GP2040-CE board", pcb(x0, y0, ZCEIL - BPH - B2T, "x", -1, "lo"), "down"))   # component side down
        groups.append(("bottom case", [(load_stl(os.path.join(ROOT, TRAY)), C["black"], a_bot)], "down"))
    else:
        zrim = num("ZBOT")
        zbt = zrim - PORT_CLEAR - USBB_H; zbb = zbt - B2T
        y1 = YB - B2_SKIN - B2_GAP; y0 = y1 - B2L
        groups.append(("GP2040-CE board", pcb(B2X0, y0, zbb, "y", +1, "hi"), "down"))
        bot = [(load_stl(os.path.join(ROOT, BASE)), C["black"], a_bot)]
        ix, iy = 4.176, 4.126; x1 = B2X0 + B2W
        for (x, y) in [(B2X0 + ix, y0 + iy), (x1 - ix, y0 + iy), (x1 - ix, y1 - iy), (B2X0 + ix, y1 - iy)]: bot += insert(x, y, zbb)
        groups.append(("bottom case", bot, "down"))
    return groups

ALPHA_TOP, ALPHA_BOTTOM = 0.45, 0.55

def screw_paths(variant):
    """Each path is a list of (point, group name): the screw's start, the insert it passes, the hole it ends in.
    Points are in model coordinates; the group's explode offset is applied when drawing."""
    zpost = ZB + REBATE_H; zpad = ZCEIL - PADT; zlip = ZB + TRAY_LIP_H
    paths = []
    for (x, y) in POSTS:                                           # lid screws: tray boss up into the shell post insert
        paths.append([((x, y, zlip), "bottom case"), ((x, y, zpost + 4), "top case")])
    for sx in (-1, 1):                                             # joystick plate up into the pad inserts
        for sy in (-1, 1):
            x, y = JX + sx * JDX / 2, JY + sy * JDY / 2
            paths.append([((x, y, zpad - 2), "joystick"), ((x, y, zpad + 4), "top case")])
    paths.append([((JX, JY, ball_center_z() - 17.5), "joystick"), ((JX, JY, ZT + 44.0), "joystick")])   # ball onto the stud
    if variant == "plain":
        for (x, y) in BH:                                          # board up into the board-post inserts
            paths.append([((x, y, ZCEIL - BPH - B2T), "GP2040-CE board"), ((x, y, ZCEIL - BPH + 4), "top case")])
    else:
        zrim = ZB; zbt = zrim - PORT_CLEAR - USBB_H; zbb = zbt - B2T
        y1 = YB - B2_SKIN - B2_GAP; y0 = y1 - B2L; ix, iy = 4.176, 4.126; x1 = B2X0 + B2W
        for (x, y) in [(B2X0 + ix, y0 + iy), (x1 - ix, y0 + iy), (x1 - ix, y1 - iy), (B2X0 + ix, y1 - iy)]:
            paths.append([((x, y, zbt), "GP2040-CE board"), ((x, y, zbb - 4), "bottom case")])
    return paths

# ------------------------------------------------------------------ camera, projection, rasterizer
def camera(az_deg, el_deg):
    a, e = math.radians(az_deg), math.radians(el_deg)
    d = np.array([math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)])   # toward the viewer
    right = np.array([math.cos(a), math.sin(a), 0.0])
    up = np.cross(d, right); up /= np.linalg.norm(up)
    return right, up, d

def project(pts, cam):
    right, up, d = cam
    return pts @ right, pts @ up, pts @ d

def explode(groups, cam, variant, factor=1.0):
    """Fixed offsets per group (see EXPLODE), times factor. Returns list of (name, parts, offset)."""
    out = []
    for name, parts, mode in groups:
        off = np.zeros(3)
        if mode == "+x": off = np.array([EXPLODE["wall_out"], 0, 0.0])
        elif mode == "-x": off = np.array([-EXPLODE["wall_out"], 0, 0.0])
        elif mode == "up": off = np.array([0, 0, EXPLODE["buttons_up"]])
        elif name == "joystick": off = np.array([0, 0, -EXPLODE["joystick_down"]])
        elif name == "GP2040-CE board": off = np.array([0, 0, -EXPLODE["board_down"][variant]])
        elif name == "bottom case": off = np.array([0, 0, -EXPLODE["bottom_down"]])
        out.append((name, parts, off * factor))
    return out

def render(placed, cam, scale, light=(0.30, -0.45, 0.84), bg=(0.86, 0.88, 0.91), margin=40, frame=None, transparent=False):
    """frame = (x0, y1, scale, margin, Wpx, Hpx) from an earlier render keeps the canvas identical between frames.
    transparent=True composites over nothing and returns an RGBA image (straight alpha) instead of RGB on `bg`."""
    right, up, d = cam
    L = np.array(light, float); L /= np.linalg.norm(L)
    tris_all = []; cols = []; ids = []; alphas = []
    for gi, (name, parts, off) in enumerate(placed):
        for part in parts:
            t, c = part[0], part[1]; a = part[2] if len(part) > 2 else 1.0
            tris_all.append(t + off); cols.append(np.repeat([c], len(t), axis=0)); ids.append(np.full(len(t), gi)); alphas.append(np.full(len(t), a))
    T = np.concatenate(tris_all); Cc = np.concatenate(cols); Ids = np.concatenate(ids); Al = np.concatenate(alphas)
    P = T.reshape(-1, 3)
    sx, sy, sz = project(P, cam)
    if frame is None:
        x0, x1, y0, y1 = sx.min(), sx.max(), sy.min(), sy.max()
        Wpx = int((x1 - x0) * scale) + 2 * margin; Hpx = int((y1 - y0) * scale) + 2 * margin
    else:
        x0, y1, scale, margin, Wpx, Hpx = frame
    px = (sx - x0) * scale + margin; py = (y1 - sy) * scale + margin
    px = px.reshape(-1, 3); py = py.reshape(-1, 3); sz = sz.reshape(-1, 3)
    # flat shading per triangle, normal flipped toward the viewer
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); ln = np.linalg.norm(n, axis=1); ok = ln > 1e-9
    n[ok] /= ln[ok][:, None]; flip = (n @ d) < 0; n[flip] *= -1
    shade = 0.50 + 0.50 * np.clip(n @ L, 0, 1)
    img = np.zeros((Hpx, Wpx, 3)) if transparent else np.ones((Hpx, Wpx, 3)) * np.array(bg)   # premultiplied when transparent
    abuf = np.zeros((Hpx, Wpx)); zbuf = np.full((Hpx, Wpx), -1e18); idbuf = np.full((Hpx, Wpx), -1)
    nbuf = np.zeros((Hpx, Wpx, 3))                     # face normal of the front-most opaque surface, for wireframes
    zbuf_t = np.full((Hpx, Wpx), -1e18); idbuf_t = np.full((Hpx, Wpx), -1)
    depth = sz.mean(axis=1)
    opaque = np.where((Al >= 0.999) & ok)[0]; transl = np.where((Al < 0.999) & ok)[0]
    order = list(opaque[np.argsort(-depth[opaque])]) + list(transl[np.argsort(depth[transl])])   # opaque front-first, then translucent back-to-front
    for i in order:
        xs, ys, zs = px[i], py[i], sz[i]
        bx0, bx1 = int(max(np.floor(xs.min()), 0)), int(min(np.ceil(xs.max()), Wpx - 1))
        by0, by1 = int(max(np.floor(ys.min()), 0)), int(min(np.ceil(ys.max()), Hpx - 1))
        if bx1 < bx0 or by1 < by0: continue
        gx, gy = np.meshgrid(np.arange(bx0, bx1 + 1) + 0.5, np.arange(by0, by1 + 1) + 0.5)
        (xa, ya), (xb, yb), (xc, yc) = (xs[0], ys[0]), (xs[1], ys[1]), (xs[2], ys[2])
        area = (xb - xa) * (yc - ya) - (xc - xa) * (yb - ya)
        if abs(area) < 1e-9: continue
        w0 = ((xb - gx) * (yc - gy) - (xc - gx) * (yb - gy)) / area
        w1 = ((xc - gx) * (ya - gy) - (xa - gx) * (yc - gy)) / area
        w2 = 1 - w0 - w1
        inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        if not inside.any(): continue
        z = w0 * zs[0] + w1 * zs[1] + w2 * zs[2]
        sub_z = zbuf[by0:by1 + 1, bx0:bx1 + 1]
        upd = inside & (z > sub_z)
        if not upd.any(): continue
        if Al[i] >= 0.999:
            sub_z[upd] = z[upd]
            img[by0:by1 + 1, bx0:bx1 + 1][upd] = np.array(Cc[i]) * shade[i]
            idbuf[by0:by1 + 1, bx0:bx1 + 1][upd] = Ids[i]
            nbuf[by0:by1 + 1, bx0:bx1 + 1][upd] = n[i]
            abuf[by0:by1 + 1, bx0:bx1 + 1][upd] = 1.0
        else:
            a = Al[i]; sub = img[by0:by1 + 1, bx0:bx1 + 1]
            sub[upd] = sub[upd] * (1 - a) + np.array(Cc[i]) * shade[i] * a
            sa = abuf[by0:by1 + 1, bx0:bx1 + 1]; sa[upd] = sa[upd] * (1 - a) + a
            sub_t = zbuf_t[by0:by1 + 1, bx0:bx1 + 1]; front = upd & (z > sub_t)
            sub_t[front] = z[front]; idbuf_t[by0:by1 + 1, bx0:bx1 + 1][front] = Ids[i]
    # outlines: object id changes or depth jumps
    edge = np.zeros((Hpx, Wpx), bool)
    edge[:, 1:] |= idbuf[:, 1:] != idbuf[:, :-1]; edge[1:, :] |= idbuf[1:, :] != idbuf[:-1, :]
    dz = np.abs(np.diff(zbuf, axis=1)); edge[:, 1:] |= (dz > 2.5) & (idbuf[:, 1:] >= 0) & (idbuf[:, :-1] >= 0)
    dz = np.abs(np.diff(zbuf, axis=0)); edge[1:, :] |= (dz > 2.5) & (idbuf[1:, :] >= 0) & (idbuf[:-1, :] >= 0)
    img[edge] = img[edge] * 0.35
    # lighter outlines for the translucent surfaces (silhouettes and depth jumps of their front surface)
    et = np.zeros((Hpx, Wpx), bool)
    et[:, 1:] |= idbuf_t[:, 1:] != idbuf_t[:, :-1]; et[1:, :] |= idbuf_t[1:, :] != idbuf_t[:-1, :]
    dz = np.abs(np.diff(zbuf_t, axis=1)); et[:, 1:] |= (dz > 2.5) & (idbuf_t[:, 1:] >= 0) & (idbuf_t[:, :-1] >= 0)
    dz = np.abs(np.diff(zbuf_t, axis=0)); et[1:, :] |= (dz > 2.5) & (idbuf_t[1:, :] >= 0) & (idbuf_t[:-1, :] >= 0)
    et &= (zbuf_t > zbuf)
    img[et] = img[et] * 0.6
    global LAST_BUFFERS; LAST_BUFFERS = (zbuf, idbuf, nbuf)
    if transparent:
        rgb = np.where(abuf[..., None] > 1e-6, img / np.maximum(abuf, 1e-6)[..., None], 0.0)
        return np.clip(np.dstack([rgb, abuf]), 0, 1), (x0, y1, scale, margin, Wpx, Hpx), idbuf
    return np.clip(img, 0, 1), (x0, y1, scale, margin, Wpx, Hpx), idbuf

def to_px(pt, frame_, cam):
    x0, y1, scale, margin = frame_[:4]
    sx, sy, _ = project(np.array([pt]), cam)
    return (sx[0] - x0) * scale + margin, (y1 - sy[0]) * scale + margin

# ------------------------------------------------------------------ one diagram
def draw_screw_lines(ax, placed, variant, frame_, cam, alpha=1.0):
    offs = {name: off for name, parts, off in placed}
    for path in screw_paths(variant):
        pts = [to_px(np.array(pt) + offs[g], frame_, cam) for pt, g in path]
        ax.plot([q[0] for q in pts], [q[1] for q in pts], ls=(0, (2, 3)), color="0.25", lw=1.0, alpha=alpha, zorder=3)

def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * t)

def centering_shift(variant, cam, factor):
    """z shift that puts the exploded scene's screen center where the assembled unit's center is."""
    right, up, d = cam
    def center_y(f):
        placed = explode(scene(variant, f), cam, variant, f)
        pts = np.concatenate([(part[0] + off).reshape(-1, 3) for name, parts, off in placed for part in parts])
        sy = pts @ up
        return (sy.min() + sy.max()) / 2
    return (center_y(0.0) - center_y(factor)) / up[2]

def shared_frame(cam, scale, blow):
    """Canvas that fits the most exploded state of both variants (centered), so frames can sit side by side."""
    right, up, d = cam
    allpts = []
    for v in ("plain", "base"):
        g = centering_shift(v, cam, blow)
        placed = explode(scene(v, blow), cam, v, blow)
        allpts.append(np.concatenate([(part[0] + off + np.array([0, 0, g])).reshape(-1, 3) for name, parts, off in placed for part in parts]))
    P = np.concatenate(allpts); sx, sy = P @ right, P @ up
    margin = 40
    Wpx = int((sx.max() - sx.min()) * scale) + 2 * margin; Hpx = int((sy.max() - sy.min()) * scale) + 2 * margin
    return (sx.min(), sy.max(), scale, margin, Wpx, Hpx)

def animate(variant, n, out_dir, scale, blow=2.5, hold_start=24, hold_end=30, transparent=False):
    """Frames from fully blown up (factor `blow`, translucent cases) to assembled (factor 0, solid cases). The whole
    scene is shifted so the parts converge on the middle of the frame instead of on the top case's position."""
    cam = camera(45, 30)
    frame_ = shared_frame(cam, scale, blow)
    g_full = centering_shift(variant, cam, blow)
    seq = [0.0] * hold_start + [i / (n - 1) for i in range(n)] + [1.0] * hold_end
    last = None
    for k, u in enumerate(seq):
        path = os.path.join(out_dir, "%s_%03d.png" % (variant, k))
        if last is not None and u == last[0]:
            import shutil; shutil.copyfile(last[1], path); continue
        e = ease(u); factor = blow * (1 - e)
        a_top = ALPHA_TOP + (1.0 - ALPHA_TOP) * e; a_bot = ALPHA_BOTTOM + (1.0 - ALPHA_BOTTOM) * e
        placed = explode(scene(variant, factor, a_top, a_bot), cam, variant, factor)
        g = g_full * (factor / blow)
        placed = [(name, parts, off + np.array([0, 0, g])) for name, parts, off in placed]
        img, _, _ = render(placed, cam, scale, frame=frame_, transparent=transparent)
        H, Wd = img.shape[:2]
        fig = plt.figure(figsize=(Wd / 100, H / 100), dpi=100)
        ax = fig.add_axes([0, 0, 1, 1]); ax.imshow(img, interpolation="none"); ax.axis("off"); ax.set_xlim(0, Wd); ax.set_ylim(H, 0)
        draw_screw_lines(ax, placed, variant, frame_, cam, alpha=1 - e)   # the screw lines fade out as it closes
        fig.savefig(path, dpi=100, transparent=transparent); plt.close(fig)
        last = (u, path); print("frame", k, "of", len(seq), flush=True)

def make(variant, out):
    cam = camera(45, 30)
    placed = explode(scene(variant), cam, variant)
    img, frame_, idbuf = render(placed, cam, SCALE)
    H, Wd = img.shape[:2]
    fig = plt.figure(figsize=(Wd / 100, H / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.imshow(img); ax.axis("off"); ax.set_xlim(0, Wd); ax.set_ylim(H, 0)
    draw_screw_lines(ax, placed, variant, frame_, cam)
    fig.savefig(out, dpi=100); plt.close(fig); print("wrote", out)

if __name__ == "__main__":
    if "--frames" in args:
        n = int(opt("--frames", "60")); out_dir = opt("--out-dir", os.path.join(ROOT, "exploded_frames")); os.makedirs(out_dir, exist_ok=True)
        which = opt("--variant", "both")
        for v in (["plain", "base"] if which == "both" else [which]):
            animate(v, n, out_dir, SCALE, transparent="--transparent" in args)
    else:
        make("plain", os.path.join(ROOT, "exploded_plain_tray.png"))
        make("base", os.path.join(ROOT, "exploded_board_base.png"))
