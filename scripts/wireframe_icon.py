"""Grayscale wireframe icon of the assembled stick, for use as a repeating blog background.

Usage: flatpak run --filesystem=home --command=python3 org.freecad.FreeCAD scripts/wireframe_icon.py [--width PX] [--variant plain|base]
Writes wireframe_icon.png (transparent background, gray lines) and wireframe_icon_white.png (same on white).
Only visible edges are drawn: silhouettes, depth steps and creases of the front-most surface, so the ribs and
posts inside the case do not show through. Rendered at 2x and downsampled for smooth lines."""
import os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.image as mimg
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exploded as X

args = sys.argv[1:]
width = int(args[args.index("--width") + 1]) if "--width" in args else 700
variant = args[args.index("--variant") + 1] if "--variant" in args else "plain"

cam = X.camera(45, 30)
placed = X.explode(X.scene(variant, 0.0, 1.0, 1.0), cam, variant, 0.0)      # assembled, opaque
# pick the render scale so the downsampled tile is `width` px wide (2x supersampling)
pts = np.concatenate([(part[0] + off).reshape(-1, 3) for name, parts, off in placed for part in parts])
sx = pts @ cam[0]; span = sx.max() - sx.min()
margin_px = 30
scale = (2 * (width - 2 * margin_px)) / span
img, frame_, idbuf = X.render(placed, cam, scale, margin=2 * margin_px)
zbuf, idbuf, nbuf = X.LAST_BUFFERS

solid = idbuf >= 0
edge = np.zeros_like(solid)
# silhouettes against the background, and between parts
edge[:, 1:] |= solid[:, 1:] != solid[:, :-1]; edge[1:, :] |= solid[1:, :] != solid[:-1, :]
edge[:, 1:] |= (idbuf[:, 1:] != idbuf[:, :-1]) & solid[:, 1:] & solid[:, :-1]
edge[1:, :] |= (idbuf[1:, :] != idbuf[:-1, :]) & solid[1:, :] & solid[:-1, :]
# depth steps (0.6 mm catches the 1 mm bezel grooves) and creases (normals more than 15 degrees apart)
for ax_ in (0, 1):
    dz = np.abs(np.diff(zbuf, axis=ax_)); both = solid[1:, :] & solid[:-1, :] if ax_ == 0 else solid[:, 1:] & solid[:, :-1]
    dn = (nbuf[1:, :] * nbuf[:-1, :]).sum(axis=2) if ax_ == 0 else (nbuf[:, 1:] * nbuf[:, :-1]).sum(axis=2)
    e = both & ((dz > 0.6) | (dn < np.cos(np.radians(15))))
    if ax_ == 0: edge[1:, :] |= e
    else: edge[:, 1:] |= e
# thicken slightly, then downsample 2x for anti-aliasing
thick = edge.copy(); thick[1:, :] |= edge[:-1, :]; thick[:, 1:] |= edge[:, :-1]
H, W = thick.shape; H2, W2 = H // 2, W // 2
dens = thick[:2 * H2, :2 * W2].reshape(H2, 2, W2, 2).mean(axis=(1, 3))
alpha = np.clip(dens * 1.4, 0, 1)
gray = 0.35                                                 # line gray level (0 = black)
rgba = np.zeros((H2, W2, 4)); rgba[..., :3] = gray; rgba[..., 3] = alpha
out1 = os.path.join(X.ROOT, "wireframe_icon.png"); mimg.imsave(out1, rgba)
white = np.ones((H2, W2, 3)); white = white * (1 - alpha[..., None]) + gray * alpha[..., None]
out2 = os.path.join(X.ROOT, "wireframe_icon_white.png"); mimg.imsave(out2, np.clip(white, 0, 1))
print("wrote", out1, "and", out2, "(%d x %d px)" % (W2, H2))
