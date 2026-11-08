"""Top-down diagram of the shell's top face as one transparent PNG per layer, for stacking into a GIMP XCF.
Usage: flatpak run ... --command=python3 org.freecad.FreeCAD scripts/diagram_top_layers.py OUTDIR
Geometry comes from the parameter block of scripts/arcade_stick.py. Scale: 6 px per mm, origin as in the model
(x across, +y toward the back). Canvas x -150..160, y -115..90."""
import re, sys, math, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch, Polygon

out = sys.argv[1]; os.makedirs(out, exist_ok=True)
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "arcade_stick.py")).read()
def num(name):
    return float(re.search(r"\b%s=(-?[\d.]+)" % name, src).group(1))
def pair_list(name):
    return [tuple(float(v) for v in m) for m in re.findall(r"\((-?[\d.]+),\s*(-?[\d.]+)\)", re.search(r"\b%s=\[(.*?)\]" % name, src).group(1))]
def num_list(name):
    return [float(v) for v in re.search(r"\b%s=\[(.*?)\]" % name, src).group(1).split(",")]
X, YB, YF, R, W = num("X"), num("YB"), num("YF"), num("R"), num("WALL")
EC, SW, BW, SI, SR = num("EDGE_CHAMF_IN"), num("SEAM_W"), num("BEZEL_W"), num("SEAM_INSET"), num("SEAM_R")
FY, RING = num("BEZEL_FRONT_Y"), num("BEZEL_RING_R")
DX = None if re.search(r"BEZEL_DIV_X=None", src) else num("BEZEL_DIV_X")
BTN = pair_list("BUTTONS30"); R30, R24 = num("BTN30_R"), num("BTN24_R")
JX, JY = pair_list("JOY")[0] if False else (num("JOY=\\(") if False else None, None)
m = re.search(r"JOY=\((-?[\d.]+),\s*(-?[\d.]+)\)", src); JX, JY = float(m.group(1)), float(m.group(2))
JR, JDX, JDY = num("JOY_R"), num("JOY_DX"), num("JOY_DY")
PW, PL, PR = num("JOY_PAD_W"), num("JOY_PAD_L"), num("JOY_PAD_R")
RWY, LWY = num_list("RIGHT_WALL_BTNS_Y"), num_list("LEFT_WALL_BTNS_Y")
POSTS = pair_list("POSTS_BACK") + [(x, num("POST_FRONT_Y")) for x in num_list("POSTS_FRONT_X")]
PR_ = num("POST_R")
BH = pair_list("BOARD_HOLES")
RIBS = [tuple(float(v) for v in m) for m in re.findall(r"\(\s*(-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+),\s*([\d.]+)\),\s*#", src)]
B2X0, B2W, B2L = num("B2_X0"), num("B2_W"), num("B2_L")
B2IN = tuple(float(v) for v in re.search(r"B2_HOLE_IN=\(([\d.]+),\s*([\d.]+)\)", src).groups())
USBC_OFF, USBB_OFF = num("USBC_OFF"), num("USBB_OFF")
USB_OUT_W = num("USB_OUT_W")
BPH = num("BOARD_POST_H")

PXMM = 6; X0, X1, Y0, Y1 = -150, 160, -115, 90
WPX, HPX = (X1 - X0) * PXMM, (Y1 - Y0) * PXMM
DPI = 100

def rrect(inset, r=None, **kw):
    """Box outline inset from the outer wall, as a rounded rectangle patch (corner radius concentric unless given)."""
    r = max(R - inset, 0.01) if r is None else r
    return FancyBboxPatch((-X + inset + r, YF + inset + r), 2 * (X - inset - r), (YB - YF) - 2 * (inset + r),
                          boxstyle="round,pad=%g,rounding_size=%g" % (r, r), **kw)

def layer(name, draw, background=False):
    fig = plt.figure(figsize=(WPX / DPI, HPX / DPI), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1); ax.set_aspect("equal"); ax.axis("off")
    draw(ax)
    path = os.path.join(out, name + ".png")
    fig.savefig(path, dpi=DPI, transparent=not background, facecolor="white" if background else "none")
    plt.close(fig); print("layer", name)

layers = []
def L(name, background=False):
    def deco(f):
        layers.append(name); layer(name, f, background); return f
    return deco

@L("00 background and 10 mm grid", background=True)
def _(ax):
    for x in range(-150, 161, 10):
        ax.plot([x, x], [Y0, Y1], color="#d8d8d8", lw=1.2 if x % 50 == 0 else 0.5)
        if x % 50 == 0: ax.text(x, Y0 + 2, str(x), ha="center", va="bottom", fontsize=9, color="#666")
    for y in range(-110, 91, 10):
        ax.plot([X0, X1], [y, y], color="#d8d8d8", lw=1.2 if y % 50 == 0 else 0.5)
        if y % 50 == 0: ax.text(X0 + 2, y, str(y), ha="left", va="center", fontsize=9, color="#666")
    ax.text(X1 - 3, Y1 - 3, "mm, x across, +y toward the back (top edge of the image)", ha="right", va="top", fontsize=10, color="#666")

@L("01 outline, edge chamfer, seam loop")
def _(ax):
    ax.add_patch(rrect(0, fill=False, lw=2.5, color="black"))
    ax.add_patch(rrect(EC, fill=False, lw=1.0, ls="-.", color="tab:brown"))
    ax.add_patch(rrect(SI, r=SR, fill=False, lw=1.0, color="tab:gray"))
    ax.add_patch(rrect(SI + SW, r=SR - SW, fill=False, lw=1.0, color="tab:gray"))
    ax.text(0, YF - 5, "black = outer wall, brown dash-dot = where the 6 mm tall chamfer meets the top (%g in)" % EC + ", gray pair = 1.2 mm seam loop at inset %g with %g mm corners" % (SI, SR),
            ha="center", va="top", fontsize=9)

@L("02 bezel lines (front line, joystick ring)")
def _(ax):
    sm = SI + SW / 2
    ax.add_patch(Rectangle((-X + sm, FY - BW / 2), 2 * (X - sm), BW, color="tab:gray"))
    if DX is not None:
        ax.add_patch(Rectangle((DX - BW / 2, FY - BW / 2), BW, YB - sm - (FY - BW / 2), color="tab:gray"))
        ax.text(DX + 2, 60, "divider x = %g" % DX, ha="left", va="center", fontsize=8, color="tab:gray", rotation=90)
    ax.add_patch(Circle((JX, JY), RING + BW / 2, fill=False, lw=1.0, color="tab:gray"))
    ax.add_patch(Circle((JX, JY), RING - BW / 2, fill=False, lw=1.0, color="tab:gray"))
    ax.text(40, FY - 4, "front line y = %g" % FY, ha="center", va="top", fontsize=8, color="tab:gray")

@L("03 top buttons (six 30 mm)")
def _(ax):
    for i, (x, y) in enumerate(BTN):
        ax.add_patch(Circle((x, y), R30, fill=False, lw=2, color="tab:blue"))
        ax.add_patch(Circle((x, y), 17, fill=False, lw=0.6, ls=":", color="tab:blue"))
        ax.text(x, y, "%d\n(%g, %g)" % (i + 1, x, y), ha="center", va="center", fontsize=7, color="tab:blue")

@L("04 joystick (hole, 95 x 53 plate, 57 x 99 pad, inserts, 65 mm body)")
def _(ax):
    ax.add_patch(Circle((JX, JY), JR, fill=False, lw=2, color="tab:red"))
    ax.add_patch(Rectangle((JX - 26.5, JY - 47.5), 53, 95, fill=False, lw=1.2, color="tab:red"))
    ax.add_patch(FancyBboxPatch((JX - PW / 2 + PR, JY - PL / 2 + PR), PW - 2 * PR, PL - 2 * PR,
                                boxstyle="round,pad=%g,rounding_size=%g" % (PR, PR), fill=False, lw=0.8, ls="--", color="tab:red"))
    for sx in (-1, 1):
        for sy in (-1, 1):
            ax.add_patch(Circle((JX + sx * JDX / 2, JY + sy * JDY / 2), 2.2, color="tab:red"))
    ax.add_patch(Rectangle((JX - 32.5, JY - 32.5), 65, 65, fill=False, lw=0.8, ls=":", color="tab:red"))
    ax.text(JX, JY - 36, "joystick (%g, %g): solid = 24 mm hole, box = 53 x 95 plate,\ndashed = 5 mm pad, dotted = 65 mm body envelope" % (JX, JY),
            ha="center", va="top", fontsize=7, color="tab:red")

@L("05 wall buttons (right 30 mm, left 24 mm)")
def _(ax):
    for y in RWY:
        ax.plot([X, X], [y - R30, y + R30], color="tab:purple", lw=6, solid_capstyle="butt")
        ax.add_patch(Rectangle((X - 30, y - R30), 30, 2 * R30, fill=False, lw=0.6, ls=":", color="tab:purple"))
    for y in LWY:
        ax.plot([-X, -X], [y - R24, y + R24], color="tab:purple", lw=6, solid_capstyle="butt")
        ax.add_patch(Rectangle((-X, y - R24), 26, 2 * R24, fill=False, lw=0.6, ls=":", color="tab:purple"))
    ax.text(X + 3, sum(RWY) / 2, "right wall: 30 mm at y = %g / %g\n(dotted = body reaching 30 mm in)" % tuple(RWY), ha="left", va="center", fontsize=8, color="tab:purple")
    ax.text(-X - 3, sum(LWY) / 2, "left wall: 24 mm\nat y = %g / %g" % tuple(LWY), ha="right", va="center", fontsize=8, color="tab:purple")

@L("06 lid posts (seven, r5.5)")
def _(ax):
    for x, y in POSTS:
        ax.add_patch(Circle((x, y), PR_, color="black", alpha=0.5))
        ax.add_patch(Circle((x, y), 2.2, color="white"))

@L("07 ribs under the top (orange 10 deep, dark orange 7, gold 3)")
def _(ax):
    for x0, y0, x1, y1, d in RIBS:
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, color="tab:orange" if d >= 10 else ("darkorange" if d >= 7 else "gold"), alpha=0.85))

@L("08 board ghost: hung under the top (plain tray build)")
def _(ax):
    xs = [p[0] for p in BH]; ys = [p[1] for p in BH]
    x0, x1 = min(xs) - 4.176, max(xs) + 4.176; y0, y1 = min(ys) - 4.126, max(ys) + 4.126
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, color="tab:green", alpha=0.25))
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, lw=1.2, ls="--", color="tab:green"))
    for x, y in BH:
        ax.add_patch(Circle((x, y), 4, fill=False, lw=1.2, color="tab:green"))
    # hung component side down with the port edge toward -x: USB-C 15.6 and USB-B 29.0 from the front edge
    ax.add_patch(Rectangle((x0 - 2.7, y0 + USBB_OFF - 6), 2.7, 12, color="tab:green", alpha=0.6))
    ax.add_patch(Rectangle((x0 - 1, y0 + USBC_OFF - 4.5), 1, 9, color="tab:green", alpha=0.6))
    ax.text(x0 - 4, y0 + USBC_OFF, "USB-C", ha="right", va="center", fontsize=7, color="darkgreen")
    ax.text(x0 - 4, y0 + USBB_OFF, "USB-B", ha="right", va="center", fontsize=7, color="darkgreen")
    ax.text((x0 + x1) / 2, (y0 + y1) / 2, "GP2040-CE board hung %g mm under the top plate, component side down\n(x %g to %g, y %g to %g), ports toward the joystick side" % (BPH, x0, x1, y0, y1),
            ha="center", va="center", fontsize=8, color="darkgreen")

@L("09 board ghost: on the floor of the board base, ports out the back")
def _(ax):
    x0, x1 = B2X0, B2X0 + B2W; y1 = YB - 1.0 - 0.3; y0 = y1 - B2L
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, color="tab:olive", alpha=0.2))
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, lw=1.2, ls="--", color="tab:olive"))
    for x, y in [(x0 + B2IN[0], y0 + B2IN[1]), (x1 - B2IN[0], y0 + B2IN[1]), (x1 - B2IN[0], y1 - B2IN[1]), (x0 + B2IN[0], y1 - B2IN[1])]:
        ax.add_patch(Circle((x, y), 4, fill=False, lw=1.2, color="tab:olive"))
    ax.add_patch(Rectangle((x1 - USBB_OFF - 6, y1), 12, 2.7, color="tab:olive", alpha=0.7))
    ax.add_patch(Rectangle((x1 - USBC_OFF - 4.5, y1 - 1), 9, 1, color="tab:olive", alpha=0.7))
    ax.text((x0 + x1) / 2, 5, "GP2040-CE board on the floor of the\nboard base (x %g to %g), USB-B and\nUSB-C through the back wall" % (x0, x1),
            ha="center", va="center", fontsize=8, color="olive")

@L("10 USB cutout at the back wall (plain tray build)")
def _(ax):
    ax.plot([-USB_OUT_W / 2, USB_OUT_W / 2], [YB, YB], color="tab:cyan", lw=5, solid_capstyle="butt")
    ax.text(0, YB + 3, "USB cable slot", ha="center", va="bottom", fontsize=8, color="tab:cyan")

@L("11 title")
def _(ax):
    ax.text(X0 + 5, Y1 - 5, "Arcade-stick_top_v7: top face, viewed from above. 250 x 175 mm. Each feature is on its own layer.",
            ha="left", va="top", fontsize=11, weight="bold")

open(os.path.join(out, "layers.txt"), "w").write("\n".join(layers) + "\n")
print("canvas %d x %d px, %d px/mm" % (WPX, HPX, PXMM))
