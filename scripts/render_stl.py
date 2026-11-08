"""Usage: flatpak run --filesystem=home --command=python3 org.freecad.FreeCAD scripts/render_stl.py part.stl out.png ELEV AZIM"""
import struct, sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
path, out, elev, azim = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
d = open(path, "rb").read(); n = struct.unpack("<I", d[80:84])[0]
a = np.frombuffer(d[84:84+50*n], dtype=np.dtype([("n","<3f4"),("v","<9f4"),("a","<u2")]))
V = a["v"].reshape(-1, 3, 3).astype(float); N = a["n"].astype(float)
light = np.array([0.3, -0.5, 0.8]); light /= np.linalg.norm(light)
sh = 0.35 + 0.65 * np.clip(N @ light, 0, 1)
fig = plt.figure(figsize=(14, 9)); ax = fig.add_subplot(111, projection="3d")
pc = Poly3DCollection(V, facecolors=[(0.85*s, 0.85*s, 0.9*s) for s in sh], edgecolors="none")
ax.add_collection3d(pc)
mn, mx = V.reshape(-1,3).min(0), V.reshape(-1,3).max(0); ctr = (mn+mx)/2; r = (mx-mn).max()/2
ax.set_xlim(ctr[0]-r, ctr[0]+r); ax.set_ylim(ctr[1]-r, ctr[1]+r); ax.set_zlim(ctr[2]-r, ctr[2]+r)
ax.view_init(elev=elev, azim=azim); ax.set_axis_off()
plt.tight_layout(); plt.savefig(out, dpi=110); print("wrote", out)
