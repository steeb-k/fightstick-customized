#!/bin/sh
# Render the exploded-view animation frames for both bottom-case variants (transparent background) and encode them
# side by side: exploded_assembly.webp (animated WebP with alpha, plays in every current browser),
# exploded_assembly.webm (VP9 with alpha, smaller; Chrome, Firefox, Edge), exploded_assembly.mp4 (H.264, opaque
# gray-blue background, for anywhere else).
# Usage: scripts/animate.sh [FRAMES] [PX_PER_MM]   (defaults 60 and 2.5)
set -e
cd "$(dirname "$0")/.."
N=${1:-60}; S=${2:-2.5}; D=$(mktemp -d)
FC="flatpak run --filesystem=home --filesystem=/tmp --command=python3 org.freecad.FreeCAD"
$FC scripts/exploded.py --frames "$N" --scale "$S" --out-dir "$D" --variant plain --transparent > "$D/plain.log" 2>&1 &
$FC scripts/exploded.py --frames "$N" --scale "$S" --out-dir "$D" --variant base --transparent > "$D/base.log" 2>&1 &
wait
# plain tray on the left, board base on the right, 40 px of transparent gap between them
STACK="[1]pad=iw+40:ih:40:0:color=#00000000[r];[0][r]hstack=inputs=2,scale=trunc(iw/2)*2:trunc(ih/2)*2,format=rgba[v]"
ffmpeg -y -loglevel error -framerate 30 -i "$D/plain_%03d.png" -framerate 30 -i "$D/base_%03d.png" \
  -filter_complex "$STACK" -map "[v]" -c:v libwebp_anim -lossless 0 -q:v 80 -compression_level 6 -loop 0 -pix_fmt yuva420p exploded_assembly.webp
ffmpeg -y -loglevel error -framerate 30 -i "$D/plain_%03d.png" -framerate 30 -i "$D/base_%03d.png" \
  -filter_complex "$STACK" -map "[v]" -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 0 -crf 30 -auto-alt-ref 0 -row-mt 1 exploded_assembly.webm
ffmpeg -y -loglevel error -framerate 30 -i "$D/plain_%03d.png" -framerate 30 -i "$D/base_%03d.png" \
  -filter_complex "${STACK};color=c=#dbe0e8:s=16x16:r=30[bg];[bg][v]scale2ref[bg2][v2];[bg2][v2]overlay=shortest=1:format=auto,format=yuv420p[o]" -map "[o]" \
  -c:v libx264 -crf 20 -movflags +faststart exploded_assembly.mp4
ls -la exploded_assembly.webp exploded_assembly.webm exploded_assembly.mp4
rm -rf "$D"
