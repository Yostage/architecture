"""
Read the survey DXF → emit the JSON payload for Tapir's CreateMeshes command.

Dry-run only: prints the JSON, does NOT send it to Archicad. Once Archicad is
running with Tapir loaded, the payload below can be POSTed to the Tapir
JSON endpoint (or sent via an MCP tool) verbatim.

Pilot architecture, one-shot:
  contour polylines + Z  →  CreateMeshes "sublines"
  PL-layer lot boundary  →  CreateMeshes "polygonCoordinates" (arc tessellated)
  one HTTP call          →  one Archicad Mesh element
"""

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import ezdxf
import shapely
from shapely.geometry import MultiPoint, Polygon

sys.stdout.reconfigure(encoding="utf-8")

DXF_PATH = Path(__file__).parent / "dxf_out" / "survey topo test.dxf"
CONTOUR_LAYERS = {"CONT-HGH", "CONT-NML"}
# MTEXT elevation labels live on the same layers as the contour lines.
CONTOUR_LABEL_LAYERS = {"CONT-HGH", "CONT-NML"}
OUTPUT_PATH = Path(__file__).parent / "createmeshes_payload.json"
# Forked Tapir 1.4.2 CreateTexts payload (replaces the old CreateLabels approach,
# which couldn't place clean standalone text).
TEXTS_OUTPUT_PATH = Path(__file__).parent / "createtexts_payload.json"
# Character height in mm for the contour elevation labels (tune to taste/scale).
TEXT_HEIGHT_MM = 2.5

# Archicad's JSON API always accepts coordinates in meters, regardless of the
# project's display units. This survey is in feet, so every coordinate gets
# scaled. 1 ft = 0.3048 m exactly.
FOOT_TO_METER = 0.3048

# Perimeter source:
#   "property_line" — the PL-layer boundary (Shawn's method: "add mesh to
#                     property boundary", contours beyond it are clipped).
#   "concave_hull"  — concave hull of all contour vertices (full data extent).
# Shawn's tutorial uses the property line, so that's the default.
PERIMETER_MODE = "property_line"
PERIMETER_LAYER = "PL"

# Concave hull ratio (Shapely): 1.0 = convex hull, smaller = more concave.
# 0.0 risks fragmenting, ~0.1–0.3 hugs the data tightly without artifacts.
HULL_RATIO = 0.2

# Endpoint clustering tolerance for stitching the PL boundary (feet). Survey
# corners have sub-mm float noise; this absorbs it. ~15 mm.
SNAP_FT = 0.05

# Arc tessellation target chord length (feet) for curved property-line segments.
ARC_TARGET_CHORD_FT = 3.0

# Translate output so the mesh sits near Archicad's project origin instead of
# at the survey's raw local coordinates (which are typically thousands of
# meters away). Without this, the mesh is technically valid but invisible in
# the default 3D view bounds.
CENTER_TO_ORIGIN = True

# Subline encoding mode:
#   "polyline" — one subline per contour, preserving connectivity. Archicad
#                stores these as level lines (user ridges). HYPOTHESIS: this is
#                what lets the 2D plan show clean topo lines instead of
#                triangulation — the drawing-set output Shawn needs.
#   "points"   — one subline per vertex; no connectivity. Archicad free-TINs
#                through them → smooth triangulated look (Shawn's stuck state).
SUBLINE_MODE = "polyline"

# Stock-Tapir mode. The `ridges`/`showLines` mesh fields exist ONLY in Scott's
# forked Tapir; public/stock Tapir doesn't understand them and may reject the
# whole payload. Set True to omit those fields and emit a stock-compatible
# payload — then get the clean contour-line display via the Mesh tool default
# instead (see "Guide - Stock Tapir (No Fork).md"). Labels (CreateTexts) are
# still fork-only and must be placed by hand on stock Tapir.
STOCK_TAPIR = False


def coord3d(x: float, y: float, z: float) -> dict:
    """Build a Coordinate3D dict. Inputs already in meters."""
    return {"x": float(x), "y": float(y), "z": float(z)}


def extract_contour_sublines(msp, base_z_m: float) -> list[dict]:
    """Emit sublines for CreateMeshes. Mode controlled by SUBLINE_MODE.

    Archicad expects coord Z relative to the mesh `level`, so we subtract
    base_z_m from each elevation."""
    sublines = []
    for poly in msp.query("LWPOLYLINE"):
        if poly.dxf.layer not in CONTOUR_LAYERS:
            continue
        z_rel = float(poly.dxf.elevation) * FOOT_TO_METER - base_z_m
        pts = [coord3d(x * FOOT_TO_METER, y * FOOT_TO_METER, z_rel)
               for x, y, *_ in poly.get_points()]
        if SUBLINE_MODE == "polyline":
            if len(pts) >= 2:
                sublines.append({"coordinates": pts})
        else:  # "points"
            for p in pts:
                sublines.append({"coordinates": [p]})
    return sublines


def find_base_z_m(msp) -> float:
    """Minimum contour elevation across all contour polylines, in meters."""
    zs = [
        float(p.dxf.elevation) for p in msp.query("LWPOLYLINE")
        if p.dxf.layer in CONTOUR_LAYERS
    ]
    if not zs:
        raise SystemExit("No contour polylines found.")
    return min(zs) * FOOT_TO_METER


def _collect_contour_vertices_ft(msp) -> list[tuple[float, float, float]]:
    """All contour-line vertices (feet), each carrying its source contour's Z."""
    pts = []
    for poly in msp.query("LWPOLYLINE"):
        if poly.dxf.layer not in CONTOUR_LAYERS:
            continue
        z = float(poly.dxf.elevation)
        for x, y, *_ in poly.get_points():
            pts.append((float(x), float(y), z))
    return pts


def _nearest_contour_z_ft(x: float, y: float, contour_pts: list) -> float:
    """Elevation (ft) of the contour vertex nearest to (x, y). Used to give
    property-line perimeter vertices a terrain-following Z instead of a flat
    edge."""
    return min(contour_pts, key=lambda p: (p[0] - x) ** 2 + (p[1] - y) ** 2)[2]


def _arc_endpoints_ft(arc):
    cx, cy, r = arc.dxf.center.x, arc.dxf.center.y, arc.dxf.radius
    a0, a1 = math.radians(arc.dxf.start_angle), math.radians(arc.dxf.end_angle)
    return ((cx + r * math.cos(a0), cy + r * math.sin(a0)),
            (cx + r * math.cos(a1), cy + r * math.sin(a1)))


def _tessellate_arc_ft(arc, from_pt, to_pt):
    """Interior points of the arc from from_pt to to_pt (feet, exclusive)."""
    cx, cy, r = arc.dxf.center.x, arc.dxf.center.y, arc.dxf.radius
    a_from = math.atan2(from_pt[1] - cy, from_pt[0] - cx)
    a0, a1 = math.radians(arc.dxf.start_angle), math.radians(arc.dxf.end_angle)
    ccw_sweep = (a1 - a0) % (2 * math.pi)
    a_to = math.atan2(to_pt[1] - cy, to_pt[0] - cx)
    diff_ccw = (a_to - a_from) % (2 * math.pi)
    going_ccw = abs(diff_ccw - ccw_sweep) < 1e-3
    sweep = diff_ccw if going_ccw else -(2 * math.pi - diff_ccw)
    n = max(2, math.ceil(r * abs(sweep) / ARC_TARGET_CHORD_FT))
    for i in range(1, n):
        a = a_from + sweep * (i / n)
        yield (cx + r * math.cos(a), cy + r * math.sin(a))


def _cluster_ids(points, tol):
    """Assign each point a cluster id, merging points within tol of each other."""
    centers, ids = [], []
    for p in points:
        hit = next((i for i, c in enumerate(centers)
                    if math.hypot(p[0] - c[0], p[1] - c[1]) <= tol), None)
        if hit is None:
            centers.append(p)
            ids.append(len(centers) - 1)
        else:
            ids.append(hit)
    return ids


def _walk_pl_loop(msp):
    """Walk the PL layer's LINE + ARC segments into one closed polygon of
    (x, y) feet, tessellating arcs. Returns None if it isn't a clean loop."""
    segs = [e for e in msp if e.dxf.layer == PERIMETER_LAYER
            and e.dxftype() in ("LINE", "ARC")]
    if not segs:
        return None
    endpoints = []
    for e in segs:
        if e.dxftype() == "LINE":
            endpoints.append(((e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)))
        else:
            endpoints.append(_arc_endpoints_ft(e))

    flat = [p for pair in endpoints for p in pair]
    cids = _cluster_ids(flat, SNAP_FT)
    incidence: dict = defaultdict(list)
    for i in range(len(segs)):
        incidence[cids[2 * i]].append((i, "start"))
        incidence[cids[2 * i + 1]].append((i, "end"))
    if any(len(v) != 2 for v in incidence.values()):
        return None  # not a single closed loop

    walk, used, cur, direction = [], set(), 0, "forward"
    while True:
        s, x = endpoints[cur]
        if direction == "forward":
            walk.append((cur, s, x)); nxt = cids[2 * cur + 1]
        else:
            walk.append((cur, x, s)); nxt = cids[2 * cur]
        used.add(cur)
        if len(used) == len(segs):
            break
        cand = [(i, side) for (i, side) in incidence[nxt] if i != cur]
        if len(cand) != 1:
            return None
        cur, side = cand[0]
        direction = "forward" if side == "start" else "reverse"

    poly = []
    for idx, s_pt, e_pt in walk:
        poly.append(s_pt)
        if segs[idx].dxftype() == "ARC":
            poly.extend(_tessellate_arc_ft(segs[idx], s_pt, e_pt))
    return poly


def assemble_perimeter(msp, base_z_m: float) -> tuple[list[dict], str]:
    """Build the mesh perimeter per PERIMETER_MODE. Returns (coords, label)."""
    contour_pts = _collect_contour_vertices_ft(msp)

    if PERIMETER_MODE == "property_line":
        pl = _walk_pl_loop(msp)
        if pl:
            perimeter = [
                coord3d(x * FOOT_TO_METER, y * FOOT_TO_METER,
                        _nearest_contour_z_ft(x, y, contour_pts) * FOOT_TO_METER - base_z_m)
                for (x, y) in pl
            ]
            return perimeter, f"property line / PL layer ({len(perimeter)} vertices)"
        # fall through to hull if PL can't be assembled
        print("  PL layer not a clean loop; falling back to concave hull")

    if len(contour_pts) < 3:
        return [], "no-contour-points"
    xy_to_zs: dict = defaultdict(list)
    for x, y, z in contour_pts:
        xy_to_zs[(round(x, 3), round(y, 3))].append(z)
    hull = shapely.concave_hull(MultiPoint([(x, y) for x, y, _ in contour_pts]), ratio=HULL_RATIO)
    if not isinstance(hull, Polygon):
        return [], f"concave_hull returned {type(hull).__name__}"
    perimeter = []
    for x, y in list(hull.exterior.coords)[:-1]:
        zs = xy_to_zs.get((round(x, 3), round(y, 3))) or [_nearest_contour_z_ft(x, y, contour_pts)]
        z_ft = sorted(zs)[len(zs) // 2]
        perimeter.append(coord3d(x * FOOT_TO_METER, y * FOOT_TO_METER, z_ft * FOOT_TO_METER - base_z_m))
    return perimeter, f"concave hull (ratio={HULL_RATIO}, {len(perimeter)} vertices)"


def build_payload(msp) -> tuple[dict, str]:
    base_z_m = find_base_z_m(msp)  # absolute meters
    sublines = extract_contour_sublines(msp, base_z_m)
    if not sublines:
        raise SystemExit("No contour sublines found — abort.")

    perimeter, source = assemble_perimeter(msp, base_z_m)
    if not perimeter:
        xs = [c["x"] for s in sublines for c in s["coordinates"]]
        ys = [c["y"] for s in sublines for c in s["coordinates"]]
        perimeter = [
            coord3d(min(xs), min(ys), 0.0),
            coord3d(max(xs), min(ys), 0.0),
            coord3d(max(xs), max(ys), 0.0),
            coord3d(min(xs), max(ys), 0.0),
        ]
        source = "fallback bbox"

    if CENTER_TO_ORIGIN:
        all_x = [c["x"] for s in sublines for c in s["coordinates"]] + [c["x"] for c in perimeter]
        all_y = [c["y"] for s in sublines for c in s["coordinates"]] + [c["y"] for c in perimeter]
        offset_x = (min(all_x) + max(all_x)) / 2
        offset_y = (min(all_y) + max(all_y)) / 2
        for s in sublines:
            for c in s["coordinates"]:
                c["x"] -= offset_x
                c["y"] -= offset_y
        for c in perimeter:
            c["x"] -= offset_x
            c["y"] -= offset_y
        mesh_level = 0.0
    else:
        offset_x = offset_y = 0.0
        mesh_level = base_z_m

    mesh_data = {
        "polygonCoordinates": perimeter,
        "sublines": sublines,
        "level": mesh_level,
        "skirtType": "SolidBodyWithSkirt",
        "skirtLevel": 100.0 * FOOT_TO_METER,
        "floorIndex": 0,
    }
    if not STOCK_TAPIR:
        # Forked Tapir 1.4.2: show only the contour level lines in plan, not the
        # triangulation — the drawing-set display, set at creation (no reliance
        # on the Mesh tool default). Omitted on stock Tapir (STOCK_TAPIR=True).
        mesh_data["ridges"] = "UserDefined"
        mesh_data["showLines"] = True

    payload = {"meshesData": [mesh_data]}
    return payload, source, (offset_x, offset_y)


def build_texts_payload(msp, offset_x_m: float, offset_y_m: float) -> dict:
    """One standalone Text per contour MTEXT, at its DWG position, sharing the
    mesh's ft→m + centering transform so labels land on the contour lines.
    Uses forked Tapir's CreateTexts (textsData)."""
    texts = []
    for t in msp.query("MTEXT TEXT"):
        if t.dxf.layer not in CONTOUR_LABEL_LAYERS:
            continue
        try:
            text = t.plain_text() if t.dxftype() == "MTEXT" else t.dxf.text
        except Exception:
            text = None
        if not text:
            continue
        ins = t.dxf.insert
        x_m = float(ins.x) * FOOT_TO_METER - offset_x_m
        y_m = float(ins.y) * FOOT_TO_METER - offset_y_m
        texts.append({
            "coordinate": {"x": x_m, "y": y_m, "z": 0.0},
            "text": text.strip(),
            "height": TEXT_HEIGHT_MM,
        })
    return {"textsData": texts}


def summarize(payload: dict, perim_source: str) -> None:
    mesh = payload["meshesData"][0]
    sublines = mesh["sublines"]
    total_vertices = sum(len(s["coordinates"]) for s in sublines)
    zs = sorted({s["coordinates"][0]["z"] for s in sublines})
    perim = mesh["polygonCoordinates"]
    xs = [c["x"] for c in perim]
    ys = [c["y"] for c in perim]
    print("=== CreateMeshes payload summary ===")
    print(f"  sublines:              {len(sublines)} contour polylines")
    print(f"  total subline vertices: {total_vertices}")
    print(f"  unique contour Zs:     {len(zs)} (range {min(zs):.2f} → {max(zs):.2f})")
    print(f"  perimeter source:      {perim_source}")
    print(f"  perimeter:             {len(perim)} vertices, bbox "
          f"({min(xs):.2f}, {min(ys):.2f}) → ({max(xs):.2f}, {max(ys):.2f})")
    print(f"  level:                 {mesh['level']:.2f}")
    print(f"  skirtType:             {mesh['skirtType']}")
    print()


def main():
    doc = ezdxf.readfile(str(DXF_PATH))
    msp = doc.modelspace()
    payload, perim_source, offset = build_payload(msp)
    summarize(payload, perim_source)

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Mesh payload written to: {OUTPUT_PATH} ({OUTPUT_PATH.stat().st_size:,} bytes)")

    texts_payload = build_texts_payload(msp, offset[0], offset[1])
    TEXTS_OUTPUT_PATH.write_text(json.dumps(texts_payload, indent=2), encoding="utf-8")
    n = len(texts_payload["textsData"])
    sample = sorted({t["text"] for t in texts_payload["textsData"]})[:8]
    print(f"Texts payload written to: {TEXTS_OUTPUT_PATH} ({n} labels, sample values {sample})")


if __name__ == "__main__":
    main()
