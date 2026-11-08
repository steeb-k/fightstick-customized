# Agent guide: parametric arcade stick enclosure

This repository holds a 3D-printable two-part fight stick enclosure (top shell and bottom case) for Sanwa-style
30 mm snap-in buttons, a Sanwa JLF-style joystick, and a GP2040-CE "RP2040 Advanced Breakout" board. Everything is
generated from one Python script run inside FreeCAD. If you change the design, change the script, rebuild, verify,
and regenerate the diagrams. Never hand-edit the `.FCStd` or `.stl` files.

The owner (steeb) prints these and iterates by printing. Cosmetic and placement choices are theirs: when a change
involves taste or ergonomics (where a button goes, how big a chamfer is, what clearance to leave around a part they
own), ask before deciding. Fit and manufacturability choices (wall thickness, support-free geometry, mesh validity)
you can and should decide yourself.

Write everything in American English: comments, commit messages, file names, chat.

## Layout of the repo

| Path | What it is |
| --- | --- |
| `scripts/arcade_stick.py` | **The source of truth.** One parameter dict `P`, then `build_shell()` and `build_tray(board=False/True)`. |
| `Arcade-stick_top_v7.{FCStd,stl}` | Current top shell (round 5). |
| `Arcade-stick_bottom_v7.{FCStd,stl}` | Current plain bottom tray (board hangs under the top shell). |
| `Arcade-stick_bottom_board_v1.{FCStd,stl}` | Current alternate bottom with the board on the floor and USB-C / USB-B out the back wall. |
| `samples/` | Two sample tops (eight buttons; diamond-plate palm rest) built by `scripts/samples.py` without changing the main script. |
| `README.md` | The human-facing guide: what to buy, how to build, which numbers to change. |
| `scripts/probe_top_v7.py`, `probe_tray_v7.py`, `probe_board_v1.py` | Point-probe test sets and the shell/tray overlap check. Copy and adapt for a new version. |
| `scripts/slice_stl.py`, `scripts/render_stl.py` | Cross sections and shaded renders of an STL. |
| `scripts/diagram_top_layers.py` + `scripts/stack_top_layers_xcf.py` | Layered top-down plan view as a GIMP XCF, for sketching placement changes. |
| `scripts/diagram_board_v1.py` | Plan view of the board base. |
| `scripts/exploded.py`, `scripts/animate.sh`, `scripts/wireframe_icon.py` | Exploded stills, the assembly animation (WebP/WebM/MP4), and the line-art icon. All read `P` from the build script. |
| `GP2040_post_test_jig.stl`, `scripts/testjig.py` | Small plate carrying the four board posts, for checking a board's hole pattern before printing a shell. |

The original STEP files this started from, the round 1 to 4 models (`_v4` to `_v6`) and the scripts that made them were
removed from the working tree on 2026-11-08. They are still in the owner's local git history on the `master` branch,
before the cleanup commit, if an old number is ever needed.

Each design round is one git commit with a descriptive message. Keep doing that: one logical change per commit,
message says what changed and why. Do not push unless asked.

The owner also keeps a change log as a Claude Doc (see `CLAUDE.md`). If you cannot edit it, put the full
before/after/why in the commit message and tell the owner the doc needs a row.

## Coordinate frame and the numbers that matter

Coordinates are the original STEP's. x runs across (outer walls at ±125), y runs front (-100) to back (+75),
z is up with the top surface at z = +1. The shell's bottom edge and the tray's rim meet at z = -50. The plate
underside ("ceiling") is at z = -1.

Print orientation: shell top face down, tray floor down, both without supports. Every feature must be
support-free in that orientation. Holes that open downward in print orientation are fine; ledges inside holes
use the two crossed 0.4 mm bridging layers (see `BRIDGE_LAYER` in the tray bosses) rather than a flat ceiling.

Clearance rules already baked in:

- 30 mm snap-in button body: assume 34 mm across under the plate, so an 18.5 mm keep-out radius from the hole
  center. Nothing (rib, post, board) may enter it. Bodies reach about 30 mm below the plate.
- 24 mm button body: about 27 mm across, 25 mm deep behind the wall.
- Joystick: a 95 x 53 mm plate (long side along y) bolted under a 5 mm pad. The body envelope under the plate is
  taken as 65 mm square around the shaft; the 24 mm shaft hole is `JOY_R`.
- Lid posts: seven, radius `POST_R` 5.5, at `POSTS_BACK` and `POSTS_FRONT_X` x `POST_FRONT_Y`. The tray bosses
  are at the same (x, y) and must stay there.
- The hung board (plain tray build) is 1.6 mm thick with its solder side 12 mm below the plate underside,
  component side toward the tray. Its posts are `BOARD_HOLES`.
- Ribs are 2 to 3 mm wide and must end in a wall, a post, the joystick pad, or another rib. Over something that
  sits under the plate they are shallower, never absent.

## Building and verifying

FreeCAD 1.1.4 is a Flatpak. There is no system `freecad` binary. Build with:

```sh
cd /home/steeb/fightstick
PYTHONUNBUFFERED=1 flatpak run --filesystem=home --command=freecadcmd org.freecad.FreeCAD scripts/arcade_stick.py
```

Add `shell`, `tray` or `board` as arguments to build one part (default is shell and tray). Expect, per part,
`valid=True solids=1` and `mesh solid=True nonmanifold=False selfint=False`, and `ALL OK` at the end. Anything
else is a failure, even if files were written. `freecadcmd` prints `\r`-terminated progress lines, so filter with
`tr '\r' '\n' | grep -E "valid=|mesh |ALL OK|PROBLEMS|Traceback"` when reading the output.

Do not put the `flatpak run ...` command in a zsh variable and expand it as `$FC`; zsh treats the whole string as
one word. Write it out, or use a `sh` script like `scripts/animate.sh` does.

Then verify:

1. **Probes.** Copy the matching `scripts/probe_*.py` to the new version name, update the file names and the
   coordinates you changed, and run it the same way. Each line is a named point that must be solid or air. The
   overlap lines (`sh.common(other).Volume`) must print `0.0000` against both bottoms. A probe that fails is
   usually a bad test point; check the geometry before changing the model.
2. **Sections and renders** through anything you moved:
   ```sh
   flatpak run --filesystem=home --command=python3 org.freecad.FreeCAD scripts/slice_stl.py Arcade-stick_top_v8.stl section.png x=50
   flatpak run --filesystem=home --command=python3 org.freecad.FreeCAD scripts/render_stl.py Arcade-stick_top_v8.stl render.png 30 -60
   ```
   The Flatpak's Python has numpy, matplotlib and PIL; the host Python does not.
3. **Diagrams.** Regenerate the plan view and the exploded stills so the pictures match the model:
   ```sh
   flatpak run --filesystem=home --command=python3 org.freecad.FreeCAD scripts/diagram_top_layers.py /tmp/layers
   gimp -i --quit --batch-interpreter=python-fu-eval -b "exec(open('scripts/stack_top_layers_xcf.py').read())"
   flatpak run --filesystem=home --command=python3 org.freecad.FreeCAD scripts/exploded.py
   scripts/animate.sh        # about six minutes; only if the animation should reflect the change
   ```

Version bumps: when a part's geometry changes, bump its export name (`Arcade-stick_top_v7` appears twice in the
script, in `build_shell()` and in `main()`; likewise for the two bottoms) so the previous files survive as history.
The downstream scripts find the current names by regex, so they follow automatically.

## How the downstream scripts read the parameters (and what breaks them)

`exploded.py`, `diagram_top_layers.py` and friends do not import the build script. They read it as text and
pull values out with regular expressions. Keep these conventions or they silently read the wrong thing:

- Every parameter stays in `P` as `NAME=<literal>`. Numbers are plain literals, not expressions (`X=125.0`, never
  `X=2*62.5`).
- List parameters (`BUTTONS30`, `BOARD_HOLES`, `POSTS_BACK`, `POSTS_FRONT_X`, `RIGHT_WALL_BTNS_Y`,
  `LEFT_WALL_BTNS_Y`) stay on **one line** each.
- Tuple parameters (`JOY`, `B2_HOLE_IN`, `GROOVE_Z`) stay as `NAME=(a, b)` on one line.
- Each `RIBS` entry sits on its own line as `(x0, y0, x1, y1, depth),  # comment`. The trailing comment is
  required; the plan-view script keys on it.
- `BEZEL_DIV_X=None` is matched literally when there is no divider line.
- Export names are string literals of the form `"Arcade-stick_top_v<N>"`, `"Arcade-stick_bottom_v<N>"`,
  `"Arcade-stick_bottom_board_v<N>"`.

If you add a new parameter that a diagram should show, add a `num("NAME")` / `pairs("NAME")` read in that script.

## Recipes

### An eight-button top (all eight 30 mm buttons on the top face)

The current layout has six 30 mm buttons on top (`BUTTONS30`) plus two 30 mm buttons through the right end wall
(`RIGHT_WALL_BTNS_Y`), with two 24 mm buttons through the left wall (`LEFT_WALL_BTNS_Y`). The original STEP had
eight on top; they were cut to six to fit the board under the front edge.

1. Decide the positions with the owner. A fourth column at the current pitch (about 36 mm) lands at x ≈ 118 to
   124, inside the right wall, so one of these has to give: widen the box (`X`), tighten the column pitch, shift
   the whole cluster left toward the divider rib (the cluster's left body edge is now at x ≈ -4 and the divider rib
   is at x -19.5 to -16.3), or shrink the joystick side. Do not pick for them.
2. Add two `(x, y)` tuples to `BUTTONS30`. Keep the list on one line.
3. Clear the keep-outs. For each new center, nothing may lie within 18.5 mm in plan: check `POSTS_BACK`
   (notably `(107, 57)` and `(15, 57)`), the front posts at y -84, the board rectangle x -16..80.3, y -65.5..-20.2
   (the hung board sits only 12 mm down, well inside the 30 mm button body depth), the right rib at x 100.5..103.5
   and its leg at y -2..1, and the back rib at y 67..69. Remove or shorten any rib the body would hit; a rib may
   end at another rib or a post but must not float.
4. Decide what happens to the right-wall buttons. `RIGHT_WALL_BTNS_Y=[]` removes them; then the right rib can
   run the full depth again (its leg into the wall was placed to stop above the upper wall button).
5. If `X` changes, every hard-coded x in `RIBS`, `POSTS_BACK`, `POSTS_FRONT_X` (the ±107 posts sit 18 mm inside
   the wall) and the USB slot centering must be revisited. The tray follows `X` automatically.
6. Rebuild, probe each new hole (air at center, solid 0.5 mm outside radius 15, air at radius 14.5), check the
   overlap is zero, and regenerate the plan view so the owner can see it. Also check the plan view's canvas still
   covers the box if `X` or the y limits grew (`X0, X1, Y0, Y1` in `diagram_top_layers.py`).

### A different joystick plate (Sanwa-style clones, Seimitsu, Hori)

The joystick bolts to the underside of a 5 mm pad with M3 screws into heat-set inserts, so no screws show on top.
Everything about it is in the `JOY*` block:

| Parameter | Meaning | Now |
| --- | --- | --- |
| `JOY` | shaft center (x, y) | (-53.8, 23) |
| `JOY_R` | shaft hole radius | 12 (24 mm hole) |
| `JOY_DX`, `JOY_DY` | mounting-hole spacing across and front to back | 40 x 80 (Sanwa JLF plate) |
| `JOY_PAD_W`, `JOY_PAD_L` | pad size, plate plus 2 mm each side | 57 x 99 for a 53 x 95 plate |
| `JOY_PAD_T` | pad thickness; the plate face sits 7 mm below the top surface | 5 |
| `JOY_HOLE_D` | insert hole depth from the pad face | 5.5 |
| `JOY_RING_R`, `JOY_RING_D` | recess that bears on the dust-washer lubricant ring | 15.5, 0.8 |
| `BEZEL_RING_R` | decorative ring on the top face | 35.25 |
| `JOY_TRAY_HOLE_R`, `GRID_CLEAR_R` | shaft-tip clearance hole in the tray floor and the grid-free circle around it | 5, 16 |

Procedure:

1. Get the real plate from the owner or its drawing: outer size, hole spacing, hole diameter, whether holes are
   slots, and the body size under the plate. Sanwa JLF plates (and most clones) are 40 x 80 on a 53 x 95 plate;
   Seimitsu LS-32/LS-40 flat plates and Hori Hayabusa differ, and some clones are 40 x 82.
2. Set `JOY_DX`, `JOY_DY`, and the pad to plate size plus 4 mm each way. The pad must clear the left wall's inner
   face (x -122.2), the divider rib (x -19.5), and the back lid posts at y 57 (radius 5.5 at x -107 and -14.86).
   Two `RIBS` entries (the split back rib) end on the pad's edges at x -82.0 and -25.0; move those numbers to the
   new pad edges so the ribs still meet the pad.
3. Non-rectangular patterns (five holes, slotted holes, asymmetric): replace the `for sx ... for sy` loop in
   `build_shell()` (the one calling `insert_hole` around the pad) with a `JOY_HOLES` list of (dx, dy) offsets in
   `P`, and mirror that in `diagram_top_layers.py`, `exploded.py` (`JDX`, `JDY`) and the probe script.
4. If the clone's body is larger than 65 mm square, the left-wall buttons (`LEFT_WALL_BTNS_Y`) must move forward
   so their bodies clear it, and `GRID_CLEAR_R` in the tray may need to grow.
5. The inserts in the pad use the shared insert dimensions (next recipe). `JOY_HOLE_D` must stay at or below 6.0
   or the hole breaks into the 2 mm top plate (pad face is at z -6, top surface at +1).
6. Rebuild and probe: air at each insert hole, solid at the pad corners, air in the ring recess, and the plate
   footprint clear of every post.

### A different PCB

Two mounts exist and both are in `P`.

**Hung under the top (plain tray, `tray` target):**

- `BOARD_HOLES`: absolute (x, y) of the mounting holes, any count. The GP2040-CE pattern is 87.962 x 36.948 mm
  with holes 4.176 / 4.126 mm in from the edges, so the outline is the hole rectangle grown by those insets.
- `BOARD_POST_R`, `BOARD_POST_H`, `BOARD_HOLE_D`: post radius, height below the plate underside, insert depth.
  Posts are 12 mm so a USB-C plug on the board passes under every rib without a relief. A taller board stack or a
  plug on the other face changes that; check the tallest component against the ribs above it.
- Ribs tied to this board: the divider rib runs beside the board's x -16 edge; the left rib ends at that divider;
  two 7 mm ribs run through the post columns at x -12.824 and 75.138 (post x minus and plus 1). Move them with the
  board or they will cross the new outline.
- Keep-outs: button bodies (18.5 mm radius), lid posts, the joystick pad, the wall-button bodies. The board also
  must not overlap the tray's penny grid or the shaft clearance circle; the shell/tray overlap check catches hard
  collisions, not clearance.
- The back-wall USB slot (`USB_*`) is for a cable from a hung board. Leave it alone unless the board has no
  external port.
- Print `GP2040_post_test_jig.stl`'s equivalent for the new pattern (adapt `scripts/testjig.py`) so the owner
  can check the holes before printing a whole shell.

**On the floor of the board base (`board` target):** the `B2_*`, `USBC_*`, `USBB_*` block.

- `B2_X0`, `B2_W`, `B2_L`, `B2_T`: board's left x, width (x), length (y), thickness. The board lies long side
  along y with its port edge at the back wall; the ports go through a pocket in the wall with a `B2_SKIN` skin left
  outside.
- `B2_HOLE_IN=(ix, iy)`: holes inset from the edges. It assumes four corner holes with the same inset at each
  corner. For another pattern, replace the `holes = [...]` list in `build_tray()` with explicit coordinates.
- `USBC_OFF`, `USBB_OFF`: port centers measured from the board's +x edge; `USBC_W/H`, `USBB_W/H`: shell sizes.
  A board with different ports means editing the `port_hole` / `rounded_slot_y` calls in `build_tray()`.
- **The base's height is derived from the USB-B.** `zbt = zrim - PORT_CLEAR - USBB_H` puts the board top so the
  USB-B shell's top is closed by the shell's bottom edge; the wall height and the lid-screw head pocket depth
  (`extra`) follow from `B2_T`, `B2_STANDOFF_H` and `TRAY_PLATE`. A board without a USB-B needs a different
  `zbt` rule (pick the tallest back-edge connector, or a fixed board height) or the base comes out wrong.
- Standoffs: `B2_STANDOFF_R`, `B2_STANDOFF_H` (3.5 clears the solder joints), `B2_INSERT_D` (5.5 leaves 0.8 mm
  of floor under the hole; a deeper insert needs a taller standoff, which raises the wall).
- `scripts/exploded.py` draws a GP2040-CE stand-in with hard-coded terminal rows and ports in its `pcb()`
  function. It is cosmetic. Update it if the picture should show the new board, otherwise ignore it.

Also lift the board-specific items off the "before printing" checklist in the change log and add the new
board's measurements that still need confirming.

### Different heat-set inserts

All insert holes in all three parts share one set of dimensions:

| Parameter | Meaning | Now (M3, 5.0 mm OD, 4 mm long) |
| --- | --- | --- |
| `INSERT_HOLE_R` | press-fit hole radius | 2.2 (4.4 mm hole) |
| `INSERT_LIP_R`, `INSERT_LIP_D` | centering lip at the mouth: radius and depth | 2.65, 1.0 |

Per-location depths (insert length plus screw tip room) and the wall left around them:

| Location | Depth parameter | Boss radius | Wall around hole | Hard limit |
| --- | --- | --- | --- | --- |
| Lid posts (shell) | `POST_HOLE_D` 8 | `POST_R` 5.5 | 3.3 | posts are 48 mm tall, plenty |
| Joystick pad | `JOY_HOLE_D` 5.5 | pad edge ≥ 8.5 | 8.5 | ≤ 6.0 or it breaks into the top plate |
| Hung board posts | `BOARD_HOLE_D` 5.5 | `BOARD_POST_R` 5.0 | 2.8 | ≤ `BOARD_POST_H` + 1 |
| Board-base standoffs | `B2_INSERT_D` 5.5 | `B2_STANDOFF_R` 5.0 | 2.8 | ≤ `B2_STANDOFF_H` + `TRAY_PLATE` - 0.8 |

Procedure:

1. Set `INSERT_HOLE_R` to the insert maker's recommended hole diameter / 2 (common: 4.0 mm for M3 x 5.0 OD
   brass, 5.6 to 6.0 mm for M4). Set `INSERT_LIP_R` about 0.4 to 0.5 larger, `INSERT_LIP_D` about 1.
2. Keep at least 2.5 mm of plastic around the hole: raise `POST_R`, `BOARD_POST_R`, `B2_STANDOFF_R` by the same
   amount the hole radius grew. A larger `POST_R` also widens the tray bosses' footprint, but the tray's
   `BOSS_R` is separate (6.0) and must stay larger than the head pocket `BOSS_CB_R` by 2.5 mm or more.
3. Set each depth to insert length plus 1.5 to 2 mm, within the hard limits above.
4. If the screw size changes too, the tray side changes with it: `BOSS_HOLE_R` (M3 clearance 1.7, M4 2.25),
   `BOSS_CB_R` and `BOSS_CB_D` for the socket-head cap screw head (M3: 6.2 x 3.4 pocket; M4: about 7.5 x 4.5),
   and the lid screw length (now M3 x 16 to 20; the board base's deeper head pockets keep it the same).
5. Mixed insert sizes (say M4 lid posts, M3 elsewhere): give `insert_hole()` and `insert_hole_down()` optional
   radius arguments and pass them per call rather than duplicating the functions.
6. Rebuild all three parts, since the shared parameters touch every one, and run all three probe scripts.

## Pitfalls seen so far

- Coincident faces produce non-manifold meshes even when the BRep is valid. Oversize cutters 0.1 to 0.5 mm into
  solid material and extend fused features 0.5 mm into the body they join (the script does this everywhere; keep
  doing it).
- `freecadcmd` does not set `__name__ == "__main__"`, so the script calls `main()` unconditionally. Keep that.
- Set `PYTHONUNBUFFERED=1` or print with `flush=True`; a crash otherwise loses all output.
- The Flatpak sandbox sees only `$HOME` (and `/tmp` with `--filesystem=/tmp`). Keep work files under the repo
  or pass the extra flag.
- Do not `pkill -f` with a pattern that matches your own shell's command line.
- GIMP batch needs `--quit` or it never exits.
- The 24 mm and 30 mm button bodies are assumptions from datasheets, not measurements of the owner's parts; the
  change log's "before printing" list tracks what still needs measuring. Add to it when you add a new assumption.
