"""Parking distance display - two-part PETG wall case.

Frame (board context): X = KiCad X, Y = -KiCad Y, Z = board front, Z=0 board bottom,
origin at board outline centre (KiCad 132, 133).

Parts
- front_shell : printed front-face down. Openings for HC-SR04 transducers, OLED window,
                stop LED, power LED, buzzer sound port; bottom cable exit notch; 4 screw columns.
- back_plate  : printed back-face down. Two keyholes, locating rim, 4 PCB standoffs,
                4 column bosses, 2 HC-SR04 support posts, cable-tie bar.
"""

import json
import math
import os
from pathlib import Path

from build123d import Box, Compound, Cone, Cylinder, Pos, import_step
from cadgen import srgb


def _load_json(name):
    with open(os.environ[name], "r", encoding="utf-8") as fh:
        return json.load(fh)


def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def cyl(x, y, r, z0, z1):
    return Pos(x, y, (z0 + z1) / 2) * Cylinder(r, z1 - z0)


# ---- board-derived datums (from pcb/layout/layout.kicad_pcb, KiCad -> CAD) ----
BOARD_X = 32.0          # half width (64 mm)
BOARD_Y = 33.0          # half height (66 mm)
BOARD_T = 1.62
PCB_HOLES = [(-28, 29), (28, 29), (-28, -29), (28, -29)]          # H1..H4 (M3)
HCSR04_C = (0.0, 45.2)   # module centre, overhanging the top board edge
HCSR04_W, HCSR04_H = 45.0, 20.0
TRANSDUCERS = [(-13.0, 45.2), (13.0, 45.2)]
CAN_R = 8.0
OLED_C = (-14.0, 1.0)    # DS1 footprint origin
OLED_PCB = (29.21, 31.75)
OLED_GLASS_C = (-14.0, -0.43)
OLED_GLASS = (26.7, 19.26)
STOP_LED = (22.0, 15.0)  # D1 body centre (middle pad)
PWR_LED = (22.2, -25.5)  # D3
BUZZER = (17.9, 2.0)     # BZ1 body centre
J1_X = (-14.2, 14.2)     # JST XH header extent

# case datums (design choices)
TOP_COLUMNS = [(-29.5, 46.5), (29.5, 46.5)]
BOTTOM_COLUMNS = [(-26.0, -39.0), (26.0, -39.0)]
COLUMNS = TOP_COLUMNS + BOTTOM_COLUMNS
COLUMN_R = 3.5
INNER_Y_MIN = -42.5
INNER_Y_MAX = 56.5
KEYHOLES = [(-15.0, 10.0), (15.0, 10.0)]   # head entry centres; slot runs +Y
KEYHOLE_SLOT_LEN = 8.0
HCSR04_POSTS = [(-20.0, 53.0), (20.0, 53.0)]


def build(p):
    wall = p["wall"]
    ft = p["front_thickness"]
    fz = p["front_inner_z"]
    so = p["standoff_height"]
    pt = p["plate_thickness"]
    clr = p["board_clearance"]
    gap = p["fit_gap"]

    ix = BOARD_X + clr                    # inner half width
    ox = ix + wall
    oy0, oy1 = INNER_Y_MIN - wall, INNER_Y_MAX + wall
    z_plate_top = -so
    z_plate_bot = z_plate_top - pt
    z_front = fz + ft
    col_top_boss = 1.0                     # shell column / plate boss joint plane

    # ---------------- front shell ----------------
    shell = box(-ox, ox, oy0, oy1, z_plate_top, z_front)
    shell = shell - box(-ix, ix, INNER_Y_MIN, INNER_Y_MAX, z_plate_top - 1, fz)
    for (x, y) in COLUMNS:
        shell = shell + cyl(x, y, COLUMN_R, col_top_boss, fz + 0.01)
    cuts = []
    for (x, y) in COLUMNS:
        cuts.append(cyl(x, y, 1.7, col_top_boss - 1, z_front + 1))      # M3 clearance
        cuts.append(cyl(x, y, 3.2, z_front - 3.0, z_front + 1))         # head counterbore
    d = p["transducer_hole_d"]
    for (x, y) in TRANSDUCERS:
        cuts.append(cyl(x, y, d / 2, fz - 1, z_front + 1))
        cuts.append(Pos(x, y, z_front - 0.8) * Cone(d / 2, d / 2 + 1.2, 1.6))   # outer flare
    wx, wy = p["oled_window_w"], p["oled_window_h"]
    wcx, wcy = OLED_GLASS_C[0], OLED_GLASS_C[1] + p["oled_window_dy"]
    cuts.append(box(wcx - wx / 2, wcx + wx / 2, wcy - wy / 2, wcy + wy / 2, fz - 1, z_front + 1))
    cuts.append(box(wcx - wx / 2 - 1.5, wcx + wx / 2 + 1.5, wcy - wy / 2 - 1.5, wcy + wy / 2 + 1.5,
                    z_front - 0.8, z_front + 1))                         # bezel recess
    cuts.append(cyl(STOP_LED[0], STOP_LED[1], 2.65, fz - 1, z_front + 1))
    cuts.append(cyl(PWR_LED[0], PWR_LED[1], 1.25, fz - 1, z_front + 1))
    cuts.append(cyl(BUZZER[0], BUZZER[1], 0.9, fz - 1, z_front + 1))
    for i in range(6):
        a = math.radians(60 * i)
        cuts.append(cyl(BUZZER[0] + 3.0 * math.cos(a), BUZZER[1] + 3.0 * math.sin(a), 0.9, fz - 1, z_front + 1))
    nw = p["cable_notch_w"]
    cuts.append(box(-nw / 2, nw / 2, oy0 - 1, INNER_Y_MIN + 1, z_plate_top - 1, 3.0))
    for c in cuts:
        shell = shell - c
    shell.label = "front_shell"
    shell.color = srgb("#2B2F36")

    # ---------------- back plate ----------------
    plate = box(-ox, ox, oy0, oy1, z_plate_bot, z_plate_top)
    # locating rim inside the shell walls
    rx0, rx1 = ix - gap, ix - gap - 1.6
    ry0, ry1 = INNER_Y_MIN + gap, INNER_Y_MAX - gap
    rim = box(-rx0, rx0, ry0, ry1, z_plate_top, z_plate_top + 2.0) - \
        box(-rx1, rx1, ry0 + 1.6, ry1 - 1.6, z_plate_top - 1, z_plate_top + 3)
    # stop the rim short of the screw columns with square cuts (no slivers)
    for (x, y) in COLUMNS:
        s = 1 if x > 0 else -1
        rim = rim - box(min(s * (abs(x) - COLUMN_R - 0.6), s * (ix + 1)),
                        max(s * (abs(x) - COLUMN_R - 0.6), s * (ix + 1)),
                        y - COLUMN_R - 0.6, y + COLUMN_R + 0.6,
                        z_plate_top - 1, z_plate_top + 3)
    rim = rim - box(-8.5, 8.5, oy0 - 1, INNER_Y_MIN + 3, z_plate_top - 1, z_plate_top + 3)
    plate = plate + rim
    for (x, y) in COLUMNS:
        plate = plate + cyl(x, y, COLUMN_R, z_plate_top - 0.01, col_top_boss)
    for (x, y) in PCB_HOLES:
        plate = plate + cyl(x, y, 3.5, z_plate_top - 0.01, 0.0)
    post_top = p["hcsr04_back_z"] - 0.3
    for (x, y) in HCSR04_POSTS:
        plate = plate + cyl(x, y, 2.0, z_plate_top - 0.01, post_top)
    # cable-tie bar: two posts and a bridge, 4 mm tie gap under the bridge
    for x in (-6.5, 6.5):
        plate = plate + box(x - 1.25, x + 1.25, -41.25, -38.75, z_plate_top - 0.01, z_plate_top + 5.5)
    plate = plate + box(-7.75, 7.75, -41.25, -38.75, z_plate_top + 4.0, z_plate_top + 5.5)
    pcuts = []
    for (x, y) in COLUMNS:
        pcuts.append(cyl(x, y, 1.3, z_plate_bot + 1.5, col_top_boss + 1))     # M3 self-tap pilot
    for (x, y) in PCB_HOLES:
        pcuts.append(cyl(x, y, 1.3, z_plate_bot + 1.5, 1.0))
    # lead relief under the buzzer pins (CAD x 15.5 / 20.5, y 2.1) in case leads are not trimmed flush
    pcuts.append(box(13.0, 23.0, 0.3, 3.9, z_plate_top - 3.0, z_plate_top + 0.5))
    # keyholes: shank slot at the wall side, wide head pocket above it, 1.5 mm lip toward the front
    hd, sw = p["keyhole_head_d"], p["keyhole_slot_w"]
    shank_depth = 2.5
    pocket_depth = 3.0
    z_shank_top = z_plate_bot + shank_depth
    z_pocket_top = z_shank_top + pocket_depth
    for (x, y) in KEYHOLES:
        pcuts.append(cyl(x, y, hd / 2, z_plate_bot - 1, z_pocket_top))
        pcuts.append(box(x - sw / 2, x + sw / 2, y, y + KEYHOLE_SLOT_LEN, z_plate_bot - 1, z_shank_top + 0.01))
        pcuts.append(cyl(x, y + KEYHOLE_SLOT_LEN, sw / 2, z_plate_bot - 1, z_shank_top + 0.01))
        pcuts.append(box(x - hd / 2, x + hd / 2, y, y + KEYHOLE_SLOT_LEN, z_shank_top, z_pocket_top))
        pcuts.append(cyl(x, y + KEYHOLE_SLOT_LEN, hd / 2, z_shank_top, z_pocket_top))
    for c in pcuts:
        plate = plate - c
    plate.label = "back_plate"
    plate.color = srgb("#4A5059")

    children = [shell, plate]

    if p["show_reference"]:
        inputs = Path(os.environ.get("EMBEDR_MECHANICAL_INPUTS_ROOT", "."))
        board = import_step(inputs / "mechanical/imports/parking-board.step")
        board.label = "ref_board"
        children.append(board)
        mz = p["hcsr04_back_z"]
        mod = box(HCSR04_C[0] - HCSR04_W / 2, HCSR04_C[0] + HCSR04_W / 2,
                  HCSR04_C[1] - HCSR04_H / 2, HCSR04_C[1] + HCSR04_H / 2, mz, mz + 1.6)
        for (x, y) in TRANSDUCERS:
            mod = mod + cyl(x, y, CAN_R, mz + 1.6, mz + 15.0)
        mod.label = "ref_hcsr04"
        mod.color = srgb("#2E6FBF")
        children.append(mod)
        oz = BOARD_T + 8.5
        oled = box(OLED_C[0] - OLED_PCB[0] / 2, OLED_C[0] + OLED_PCB[0] / 2,
                   OLED_C[1] - OLED_PCB[1] / 2, OLED_C[1] + OLED_PCB[1] / 2, oz, oz + 1.6)
        oled = oled + box(OLED_GLASS_C[0] - OLED_GLASS[0] / 2, OLED_GLASS_C[0] + OLED_GLASS[0] / 2,
                          OLED_GLASS_C[1] - OLED_GLASS[1] / 2, OLED_GLASS_C[1] + OLED_GLASS[1] / 2,
                          oz + 1.6, oz + 3.0)
        oled = oled + box(OLED_C[0] - 10.2, OLED_C[0] + 10.2, -13.6, -11.1, BOARD_T, oz)   # 1x8 female header
        oled.label = "ref_oled"
        oled.color = srgb("#1A1A1A")
        children.append(oled)
        led = cyl(STOP_LED[0], STOP_LED[1], 2.5, z_front - 8.6, z_front - 0.2)
        led.label = "ref_stop_led"
        led.color = srgb("#C83C3C")
        children.append(led)

    return Compound(children=children, label="parking_case")


def gen_step():
    return build(_load_json("EMBEDR_MECHANICAL_PARAMETERS"))
