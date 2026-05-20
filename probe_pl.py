"""Probe the PL layer in detail — dump every LINE and ARC with full geometry,
then check whether they form a single closed loop."""

import math
import sys
from collections import defaultdict
from pathlib import Path

import ezdxf

sys.stdout.reconfigure(encoding="utf-8")

DXF_PATH = Path(__file__).parent / "dxf_out" / "survey topo test.dxf"
SNAP = 0.001  # ft — endpoints within this distance count as the same point


def round_pt(p):
    return (round(p[0] / SNAP) * SNAP, round(p[1] / SNAP) * SNAP)


def arc_endpoints(arc):
    cx, cy = arc.dxf.center.x, arc.dxf.center.y
    r = arc.dxf.radius
    a0 = math.radians(arc.dxf.start_angle)
    a1 = math.radians(arc.dxf.end_angle)
    return (
        (cx + r * math.cos(a0), cy + r * math.sin(a0)),
        (cx + r * math.cos(a1), cy + r * math.sin(a1)),
    )


def main():
    doc = ezdxf.readfile(str(DXF_PATH))
    msp = doc.modelspace()

    pl_entities = [e for e in msp if e.dxf.layer == "PL"]
    print(f"=== PL layer: {len(pl_entities)} entities ===\n")

    endpoints_per_entity = []
    for i, e in enumerate(pl_entities):
        t = e.dxftype()
        if t == "LINE":
            s = (e.dxf.start.x, e.dxf.start.y)
            x = (e.dxf.end.x, e.dxf.end.y)
            print(f"  [{i}] LINE   start=({s[0]:.4f}, {s[1]:.4f})  end=({x[0]:.4f}, {x[1]:.4f})  "
                  f"len={math.hypot(x[0]-s[0], x[1]-s[1]):.3f} ft")
            endpoints_per_entity.append((t, s, x, None))
        elif t == "ARC":
            s, x = arc_endpoints(e)
            cx, cy = e.dxf.center.x, e.dxf.center.y
            r = e.dxf.radius
            sa = e.dxf.start_angle
            ea = e.dxf.end_angle
            sweep_deg = (ea - sa) % 360
            print(f"  [{i}] ARC    start=({s[0]:.4f}, {s[1]:.4f})  end=({x[0]:.4f}, {x[1]:.4f})")
            print(f"         center=({cx:.4f}, {cy:.4f})  r={r:.4f}  "
                  f"start_angle={sa:.4f}°  end_angle={ea:.4f}°  sweep={sweep_deg:.4f}°")
            endpoints_per_entity.append((t, s, x, {"cx": cx, "cy": cy, "r": r, "sweep_deg": sweep_deg}))
        else:
            print(f"  [{i}] {t} (skipping unsupported type)")
            endpoints_per_entity.append((t, None, None, None))

    print("\n=== Endpoint connectivity ===")
    incidence = defaultdict(list)
    for i, (t, s, x, _) in enumerate(endpoints_per_entity):
        if s is None:
            continue
        incidence[round_pt(s)].append((i, "start"))
        incidence[round_pt(x)].append((i, "end"))

    for pt, refs in sorted(incidence.items()):
        marker = "  " if len(refs) == 2 else "⚠ "
        print(f"  {marker}({pt[0]:.3f}, {pt[1]:.3f})  used by: "
              + ", ".join(f"seg{i}/{side}" for i, side in refs))

    closed = all(len(refs) == 2 for refs in incidence.values())
    print(f"\nForms a closed loop: {closed}")
    n_unique_pts = len(incidence)
    print(f"Unique endpoints: {n_unique_pts}, segments: {sum(1 for t,_,_,_ in endpoints_per_entity if t in ('LINE','ARC'))}")


if __name__ == "__main__":
    main()
