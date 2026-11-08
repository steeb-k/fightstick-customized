"""Plan view of Arcade-stick_bottom_board_v1 (the alternate base with the GP2040-CE board on the floor)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch, Polygon
fig, ax = plt.subplots(figsize=(12, 9))
ax.add_patch(FancyBboxPatch((-115, -90), 230, 155, boxstyle="round,pad=10,rounding_size=10", fill=False, lw=2))          # outer wall at the rim
ax.add_patch(FancyBboxPatch((-115, -90), 230, 155, boxstyle="round,pad=6,rounding_size=6", fill=False, lw=1, ls="--", color="gray"))  # bevel foot (4 mm in)
ax.add_patch(Polygon([(19, 71), (78.3, 71), (74.3, 75), (23, 75)], closed=True, color="tab:brown", alpha=0.6, label="flat back panel (bevel filled, 45 deg ends)"))
bx0, bx1, by0, by1 = 26.0, 71.3, -22.6, 73.7
ax.add_patch(Rectangle((bx0, by0), bx1 - bx0, by1 - by0, color="tab:green", alpha=0.3, label="GP2040-CE board 45.3 x 96.3, component side up, 3.5 mm standoffs"))
for x, y in [(30.176, -18.474), (67.124, -18.474), (67.124, 69.574), (30.176, 69.574)]:
    ax.add_patch(Circle((x, y), 5, fill=False, color="tab:green", lw=1.5)); ax.add_patch(Circle((x, y), 2.2, color="tab:green"))
ax.add_patch(Rectangle((55.7 - 5.17, 73.2), 10.34, 2.8, color="tab:cyan", label="USB-C hole 10.3 x 4.7 (face 1 mm inside the wall)"))
ax.add_patch(Rectangle((42.3 - 6.7, 73.2), 13.4, 2.8, color="tab:blue", label="USB-B slot 13.4 wide, open at the top: the shell closes it (shell 1.4 mm proud)"))
ax.add_patch(Rectangle((-4.75, 72.2), 9.5, 2.8, color="tab:red", label="plug filling the shell's old USB slot"))
for x, y in [(-107, 57), (107, 57), (-14.86, 57), (15, 57), (-107, -84), (107, -84), (-12, -84)]:
    ax.add_patch(Circle((x, y), 6, color="k", alpha=0.5))
ax.add_patch(Circle((-73.8, 23), 5, fill=False, color="tab:red", lw=1.5)); ax.add_patch(Circle((-73.8, 23), 16, fill=False, color="tab:red", ls=":", lw=0.8))
ax.text(-73.8, 44, "joystick shaft hole\n(grid cleared r16)", ha="center", fontsize=8, color="tab:red")
ax.text(48.6, 25, "penny grid cleared\nunder the board", ha="center", fontsize=8, color="tab:green")
ax.text(48.6, 80, "ports exit here, board edge in a 1 mm-skin pocket", ha="center", fontsize=8)
ax.set_aspect("equal"); ax.set_xlim(-150, 160); ax.set_ylim(-112, 90); ax.grid(True, lw=0.3); ax.set_xlabel("x (mm)"); ax.set_ylabel("y (mm), +y = back")
ax.set_title("Arcade-stick_bottom_board_v1 plan view: base 19.5 mm tall (wall 9.5 + bevel 10), floor 66.7 mm below the top plate.\nBlack = lid bosses (r6, head pocket 8.9 deep so the M3 x 16 to 20 lid screws stay), green = board on four r5 standoffs with M3 inserts", fontsize=9)
ax.legend(loc="lower right", fontsize=8)
plt.tight_layout(); plt.savefig("/home/steeb/fightstick/Arcade-stick_bottom_board_v1_layout.png", dpi=110); print("diagram written")
