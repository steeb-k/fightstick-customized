"""Stack the layer PNGs from scripts/diagram_top_layers.py into a GIMP XCF plus a flattened preview.
Usage: gimp -i --quit --batch-interpreter=python-fu-eval -b "exec(open('scripts/stack_top_layers_xcf.py').read())"
Set D below to the folder holding the layer PNGs and layers.txt."""
from gi.repository import Gimp, Gio
import os
D = "/tmp/claude-1000/-home-steeb-fightstick/76ba8ea5-101b-4979-9d91-94bc5c0e36e8/scratchpad/top_layers"
names = [l.strip() for l in open(os.path.join(D, "layers.txt")) if l.strip()]
W, H = 1860, 1230
img = Gimp.Image.new(W, H, Gimp.ImageBaseType.RGB)
img.set_resolution(6 * 25.4, 6 * 25.4)          # 6 px per mm
for n in names:                                   # bottom to top; inserting at position 0 keeps the latest on top
    layer = Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE, img, Gio.File.new_for_path(os.path.join(D, n + ".png")))
    layer.set_name(n)
    img.insert_layer(layer, None, 0)
Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, img, Gio.File.new_for_path("/home/steeb/fightstick/Arcade-stick_top_v7_layout.xcf"), None)
flat = img.duplicate(); flat.flatten()
Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, flat, Gio.File.new_for_path("/home/steeb/fightstick/Arcade-stick_top_v7_layout_layers.png"), None)
print("layers:", len(img.get_layers()))
