"""Fit check for the parking case: overlap volumes between printed parts and reference bodies,
plus per-part STL export in print orientation (front shell face-down, back plate back-face-down)."""
import json

from build123d import Axis, Pos, export_stl, import_step

STEP = "mechanical/exports/parking-case.step"
OUT = "mechanical/exports/fit-report.json"

root = import_step(STEP)


def walk(node, path=""):
    label = getattr(node, "label", "") or ""
    kids = list(getattr(node, "children", []) or [])
    me = f"{path}/{label}" if label else path
    if not kids:
        yield me, node
    for k in kids:
        yield from walk(k, me)


leaves = list(walk(root))


def ovol(a, b):
    r = a & b
    return 0.0 if r is None else r.volume


parts = {lbl.split("/")[-1]: shp for lbl, shp in leaves if lbl.split("/")[-1] in ("front_shell", "back_plate")}
refs = [(lbl, shp) for lbl, shp in leaves if lbl.split("/")[-1] not in ("front_shell", "back_plate")]

report = {"leaf_count": len(leaves), "parts": {}, "overlaps": [], "printed_overlap": None}
for name, shp in parts.items():
    bb = shp.bounding_box()
    report["parts"][name] = {"volume_mm3": shp.volume, "valid": shp.is_valid,
                             "bounds": [[bb.min.X, bb.min.Y, bb.min.Z], [bb.max.X, bb.max.Y, bb.max.Z]]}

for pname, pshape in parts.items():
    for rlabel, rshape in refs:
        try:
            v = ovol(pshape, rshape)
        except Exception as exc:  # noqa: BLE001
            report["overlaps"].append({"part": pname, "ref": rlabel, "error": str(exc)})
            continue
        if v > 1e-3:
            report["overlaps"].append({"part": pname, "ref": rlabel, "volume_mm3": round(v, 3)})

report["printed_overlap"] = round(ovol(parts["front_shell"], parts["back_plate"]), 4)

shell = parts["front_shell"].rotate(Axis.X, 180)
shell = Pos(0, 0, -shell.bounding_box().min.Z) * shell
plate = Pos(0, 0, -parts["back_plate"].bounding_box().min.Z) * parts["back_plate"]
export_stl(shell, "mechanical/exports/front_shell.stl")
export_stl(plate, "mechanical/exports/back_plate.stl")

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(report, fh, indent=2)
print(json.dumps(report, indent=2))
