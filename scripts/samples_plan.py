"""Plan-view drawings of the sample tops built by scripts/samples.py (same parameter sets, drawn in 2D).
  flatpak run --filesystem=home --command=freecadcmd org.freecad.FreeCAD scripts/samples_plan.py
Writes samples/plan_8btn.png and samples/plan_diamond.png."""
import os, re, math
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch, Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
# load samples.py with its main() disabled; it loads arcade_stick.py the same way (needs FreeCAD's Part module)
src = open(os.path.join(HERE, "samples.py")).read()
src = re.sub(r"^main\(\)", "# main()", src, flags=re.M)
ns = {"__name__": "samples", "__file__": os.path.join(HERE, "samples.py")}
exec(compile(src, ns["__file__"], "exec"), ns)

OUT = os.path.join(HERE, "..", "samples")

def rrect(ax, x0, y0, x1, y1, r, **kw):
    ax.add_patch(FancyBboxPatch((x0 + r, y0 + r), (x1 - x0) - 2 * r, (y1 - y0) - 2 * r,
                                boxstyle="round,pad=%g" % r, **kw))

def draw(P, out, texture=False, title=""):
    X, YB, YF, R, W = P["X"], P["YB"], P["YF"], P["R"], P["WALL"]
    fig, ax = plt.subplots(figsize=(13, 9.5)); ax.set_aspect("equal")
    ax.set_xlim(-X - 8, X + 8); ax.set_ylim(YF - 8, YB + 8)
    # outline, chamfer break line, seam loop
    rrect(ax, -X, YF, X, YB, R, fc="#dfe3ea", ec="#333", lw=1.4)
    ec = P["EDGE_CHAMF_IN"]
    rrect(ax, -X + ec, YF + ec, X - ec, YB - ec, R - ec, fc="none", ec="#999", lw=0.8, ls="--")
    si, sw = P["SEAM_INSET"], P["SEAM_W"]
    rrect(ax, -X + si, YF + si, X - si, YB - si, P["SEAM_R"], fc="#8a8f99", ec="none")
    rrect(ax, -X + si + sw, YF + si + sw, X - si - sw, YB - si - sw, P["SEAM_R"] - sw, fc="#dfe3ea", ec="none")
    # texture
    if texture:
        tm, td = ns["TEX_MARGIN"], ns["TEX_DEPTH"]
        sii = si + sw
        x0, x1 = -X + sii + tm, X - sii - tm
        y0 = YF + sii + tm; y1 = P["BEZEL_FRONT_Y"] - P["BEZEL_W"] / 2 - tm
        r = max(P["SEAM_R"] - sw - tm, 2.0)
        rrect(ax, x0, y0, x1, y1, r, fc="none", ec="#999", lw=0.6, ls=":")
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; pitch, L, Wd = ns["LOZ_PITCH"], ns["LOZ_L"], ns["LOZ_W"]
        ni = int((x1 - x0) / 2 / pitch) + 1; nj = int((y1 - y0) / 2 / pitch) + 1
        ax.set_clip_on(True)
        clip = FancyBboxPatch((x0 + r, y0 + r), (x1 - x0) - 2 * r, (y1 - y0) - 2 * r, boxstyle="round,pad=%g" % r, transform=ax.transData)
        for i in range(-ni, ni + 1):
            for j in range(-nj, nj + 1):
                a = math.radians(45 if (i + j) % 2 == 0 else -45); c, s = math.cos(a), math.sin(a)
                px, py = cx + i * pitch, cy + j * pitch
                pts = [(px + c * x - s * y, py + s * x + c * y) for (x, y) in [(L / 2, 0), (0, Wd / 2), (-L / 2, 0), (0, -Wd / 2)]]
                p = Polygon(pts, closed=True, fc="#9ea4b0", ec="#555", lw=0.5); ax.add_patch(p); p.set_clip_path(clip)
    # bezel lines
    bw = P["BEZEL_W"]; fy = P["BEZEL_FRONT_Y"]; sm = si + sw / 2
    ax.add_patch(Rectangle((-X + sm, fy - bw / 2), 2 * (X - sm), bw, fc="#8a8f99", ec="none"))
    jx, jy = P["JOY"]
    ax.add_patch(Circle((jx, jy), P["BEZEL_RING_R"], fc="none", ec="#8a8f99", lw=2.2))
    # ribs, posts, board (under the plate)
    for (x0, y0, x1, y1, d) in P["RIBS"]:
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="#f2a65a" if d < 10 else "#d9822b", ec="none", alpha=0.8))
    for (x, y) in ns["ns"]["posts_xy"]():
        ax.add_patch(Circle((x, y), P["POST_R"], fc="#b48a5a", ec="#5a4020", lw=0.8))
    bx0, by0, bx1, by1 = ns["BOARD"]
    ax.add_patch(Rectangle((bx0, by0), bx1 - bx0, by1 - by0, fc="#4caf50", ec="#1b5e20", lw=1.0, alpha=0.35))
    for (x, y) in P["BOARD_HOLES"]:
        ax.add_patch(Circle((x, y), P["BOARD_POST_R"], fc="none", ec="#1b5e20", lw=0.8))
    # joystick pad, plate, holes
    pw, pl = P["JOY_PAD_W"], P["JOY_PAD_L"]
    ax.add_patch(Rectangle((jx - pw / 2, jy - pl / 2), pw, pl, fc="#bcd", ec="#357", lw=0.8, alpha=0.5))
    ax.add_patch(Rectangle((jx - 26.5, jy - 47.5), 53, 95, fc="none", ec="#357", lw=0.8, ls=":"))
    ax.add_patch(Rectangle((jx - 32.5, jy - 32.5), 65, 65, fc="none", ec="#c33", lw=0.8, ls="--"))
    for sx in (-1, 1):
        for sy in (-1, 1):
            ax.add_patch(Circle((jx + sx * P["JOY_DX"] / 2, jy + sy * P["JOY_DY"] / 2), P["INSERT_HOLE_R"], fc="white", ec="#357", lw=0.8))
    ax.add_patch(Circle((jx, jy), P["JOY_R"], fc="white", ec="#333", lw=1.0))
    # buttons: hole, body envelope, number
    for i, (x, y) in enumerate(P["BUTTONS30"], 1):
        ax.add_patch(Circle((x, y), ns["BODY_R"], fc="none", ec="#c33", lw=0.8, ls="--"))
        ax.add_patch(Circle((x, y), P["BTN30_R"], fc="white", ec="#333", lw=1.0))
        ax.text(x, y, str(i), ha="center", va="center", fontsize=11, color="#333")
    for y in P["RIGHT_WALL_BTNS_Y"]:
        ax.add_patch(Rectangle((X - W - 2, y - 15), W + 2, 30, fc="#c33", ec="none", alpha=0.6))
    for y in P["LEFT_WALL_BTNS_Y"]:
        ax.add_patch(Rectangle((-X, y - 12), W + 2, 24, fc="#333", ec="none", alpha=0.6))
        ax.add_patch(Circle((-X + W, y), 13.5, fc="none", ec="#333", lw=0.8, ls="--"))
    ax.set_title(title, fontsize=12); ax.set_axis_off()
    plt.tight_layout(); plt.savefig(out, dpi=110); plt.close(fig); print("wrote", out)

draw(ns["eight_button_params"](), os.path.join(OUT, "plan_8btn.png"),
     title="Sample: eight 30 mm buttons on top, cluster 19 mm left, no right-wall buttons (red dashes = body envelopes)")
draw(ns["diamond_params"](), os.path.join(OUT, "plan_diamond.png"), texture=True,
     title="Sample: v7 layout, no right-wall buttons, diamond plate (lozenge divots 0.6 mm deep) in the palm rest")
