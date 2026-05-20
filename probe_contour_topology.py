"""Are any contour polylines closed? Which contour has the largest extent / longest perimeter?
Findings inform the perimeter strategy."""

import math
import sys
from collections import Counter
from pathlib import Path

import ezdxf

sys.stdout.reconfigure(encoding="utf-8")

DXF_PATH = Path(__file__).parent / "dxf_out" / "survey topo test.dxf"
CONTOUR_LAYERS = {"CONT-HGH", "CONT-NML"}


def main():
    doc = ezdxf.readfile(str(DXF_PATH))
    msp = doc.modelspace()

    contour_polys = [p for p in msp.query("LWPOLYLINE") if p.dxf.layer in CONTOUR_LAYERS]
    print(f"Total contour polylines: {len(contour_polys)}\n")

    closed_count = 0
    closed_by_z = Counter()
    longest_per_z = {}
    total_per_z = Counter()

    for poly in contour_polys:
        z = round(poly.dxf.elevation, 2)
        pts = list(poly.get_points())
        n = len(pts)
        total_per_z[z] += 1

        is_closed = bool(poly.closed)
        if not is_closed and n >= 2:
            d = math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1])
            if d < 0.5:  # close enough to call closed in ft
                is_closed = True
        if is_closed:
            closed_count += 1
            closed_by_z[z] += 1

        # perimeter length
        length = 0.0
        for (x1, y1, *_), (x2, y2, *_) in zip(pts, pts[1:]):
            length += math.hypot(x2 - x1, y2 - y1)
        if is_closed and n >= 2:
            length += math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1])

        cur = longest_per_z.get(z)
        if cur is None or length > cur[1]:
            longest_per_z[z] = (poly, length, n, is_closed)

    print(f"Closed contour polylines: {closed_count} / {len(contour_polys)}")
    print(f"Closed by elevation: {dict(closed_by_z)}\n")

    print("=== Longest polyline at each elevation (sorted by length) ===")
    rows = sorted(longest_per_z.items(), key=lambda kv: -kv[1][1])
    print(f"{'Z (ft)':>10}  {'len (ft)':>10}  {'n_pts':>6}  {'closed':>7}  {'total@Z':>8}")
    for z, (poly, length, n, closed) in rows[:20]:
        print(f"{z:>10.2f}  {length:>10.2f}  {n:>6}  {str(closed):>7}  {total_per_z[z]:>8}")

    print()
    print("=== Bounding boxes of longest polylines ===")
    for z, (poly, length, n, closed) in rows[:5]:
        pts = list(poly.get_points())
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        print(f"  Z={z:.2f}: X=[{min(xs):.1f}, {max(xs):.1f}]  Y=[{min(ys):.1f}, {max(ys):.1f}]  "
              f"closed={closed}  pts={n}  length={length:.1f}")


if __name__ == "__main__":
    main()
