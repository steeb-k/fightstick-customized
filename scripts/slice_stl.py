"""Usage: flatpak run --filesystem=home --command=python3 org.freecad.FreeCAD scripts/slice_stl.py part.stl out.png x=107 y=10"""
"""Slice a binary STL with a plane x=c or y=c and plot the section."""
import struct, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
def load(path):
    d = open(path, "rb").read(); n = struct.unpack("<I", d[80:84])[0]
    tris = []
    for i in range(n):
        o = 84 + i * 50
        v = struct.unpack("<12f", d[o:o+48])
        tris.append(((v[3],v[4],v[5]), (v[6],v[7],v[8]), (v[9],v[10],v[11])))
    return tris
def slice_(tris, axis, c):
    segs = []
    for t in tris:
        pts = []
        for i in range(3):
            a, b = t[i], t[(i+1)%3]
            da, db = a[axis]-c, b[axis]-c
            if (da < 0) != (db < 0):
                f = da / (da - db)
                pts.append(tuple(a[k] + f*(b[k]-a[k]) for k in range(3)))
        if len(pts) == 2: segs.append(pts)
    return segs
path, out = sys.argv[1], sys.argv[2]
cuts = [(s.split("=")[0], float(s.split("=")[1])) for s in sys.argv[3:]]
win = None
if "--win" in sys.argv:
    pass
tris = load(path)
fig, axs = plt.subplots(len(cuts), 1, figsize=(14, 4.5*len(cuts)))
if len(cuts) == 1: axs = [axs]
for ax, (axn, c) in zip(axs, cuts):
    axis = 0 if axn == "x" else 1; other = 1 - axis
    for p, q in slice_(tris, axis, c):
        ax.plot([p[other], q[other]], [p[2], q[2]], color="k", lw=1)
    ax.set_aspect("equal"); ax.grid(True, lw=0.3)
    ax.set_title("section at %s = %g  (horizontal = %s, vertical = z)" % (axn, c, "y" if other == 1 else "x"))
plt.tight_layout(); plt.savefig(out, dpi=120); print("wrote", out)
