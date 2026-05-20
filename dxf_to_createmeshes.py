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
OUTPUT_PATH = Path(__file__).parent / "createmeshes_payload.json"

# Archicad's JSON API always accepts coordinates in meters, regardless of the
# project's display units. This survey is in feet, so every coordinate gets
# scaled. 1 ft = 0.3048 m exactly.
FOOT_TO_METER = 0.3048

# Concave hull ratio (Shapely): 1.0 = convex hull, smaller = more concave.
# 0.0 risks fragmenting, ~0.1–0.3 hugs the data tightly without artifacts.
HULL_RATIO = 0.2

# Translate output so the mesh sits near Archicad's project origin instead of
# at the survey's raw local coordinates (which are typically thousands of
# meters away). Without this, the mesh is technically valid but invisible in
# the default 3D view bounds.
CENTER_TO_ORIGIN = True


def coord3d(x: float, y: float, z: float) -> dict:
    """Build a Coordinate3D dict. Inputs already in meters."""
    return {"x": float(x), "y": float(y), "z": float(z)}


def extract_contour_sublines(msp, base_z_m: float) -> list[dict]:
    """ONE SUBLINE PER VERTEX. Matches Shawn's manual Magic-Wand workflow:
    each contour vertex becomes an independent ridge point with no
    connectivity to its neighbors. Archicad then triangulates a free TIN
    through all points, giving the smooth-graded appearance of Shawn's
    example mesh. (Earlier version preserved polyline connectivity, which
    forced Archicad to honor each contour as a ridge and produced visibly
    sharper terrain — geometrically more faithful but didn't visually
    match Shawn's reference.)"""
    sublines = []
    for poly in msp.query("LWPOLYLINE"):
        if poly.dxf.layer not in CONTOUR_LAYERS:
            continue
        z_rel = float(poly.dxf.elevation) * FOOT_TO_METER - base_z_m
        for x, y, *_ in poly.get_points():
            sublines.append({
                "coordinates": [coord3d(x * FOOT_TO_METER, y * FOOT_TO_METER, z_rel)]
            })
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


def assemble_perimeter(msp, base_z_m: float) -> tuple[list[dict], str]:
    """Concave hull of contour vertices. Each hull vertex carries its source
    contour's Z (relative to base_z_m). Mirrors Shawn's Magic-Wand workflow:
    perimeter snaps to existing contours, so vertex Z follows the terrain."""
    pts_ft = _collect_contour_vertices_ft(msp)
    if len(pts_ft) < 3:
        return [], "no-contour-points"

    # Build a lookup so we can recover Z after the 2D hull operation.
    # Some vertices coincide in X/Y across contours (rare but possible);
    # break ties by taking the median Z within a small bin.
    xy_to_zs: dict = defaultdict(list)
    for x, y, z in pts_ft:
        xy_to_zs[(round(x, 3), round(y, 3))].append(z)

    multipoint = MultiPoint([(x, y) for (x, y, _) in pts_ft])
    hull = shapely.concave_hull(multipoint, ratio=HULL_RATIO)
    if not isinstance(hull, Polygon):
        return [], f"concave_hull returned {type(hull).__name__}"

    perimeter = []
    for x, y in list(hull.exterior.coords)[:-1]:  # drop the closing duplicate
        key = (round(x, 3), round(y, 3))
        zs = xy_to_zs.get(key)
        if not zs:
            # Shouldn't happen with concave_hull on a MultiPoint input, but
            # fall back to nearest-point search if it does.
            zs = [min(pts_ft, key=lambda p: (p[0] - x) ** 2 + (p[1] - y) ** 2)[2]]
        z_ft = sorted(zs)[len(zs) // 2]  # median
        z_rel_m = (z_ft * FOOT_TO_METER) - base_z_m
        perimeter.append(coord3d(x * FOOT_TO_METER, y * FOOT_TO_METER, z_rel_m))

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
        mesh_level = base_z_m

    payload = {
        "meshesData": [
            {
                "polygonCoordinates": perimeter,
                "sublines": sublines,
                "level": mesh_level,
                "skirtType": "SolidBodyWithSkirt",
                "skirtLevel": 100.0 * FOOT_TO_METER,
                "floorIndex": 0,
            }
        ]
    }
    return payload, source


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
    payload, perim_source = build_payload(msp)
    summarize(payload, perim_source)

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Full payload written to: {OUTPUT_PATH}")
    print(f"  ({OUTPUT_PATH.stat().st_size:,} bytes)")
    print()
    print("To send via Tapir JSON API (when Archicad is running):")
    print("  POST http://127.0.0.1:19723/")
    print("  {")
    print('    "command": "API.ExecuteAddOnCommand",')
    print('    "parameters": {')
    print('      "addOnCommandId": {')
    print('        "commandNamespace": "TapirCommand",')
    print('        "commandName": "CreateMeshes"')
    print('      },')
    print('      "addOnCommandParameters": <payload above>')
    print('    }')
    print("  }")


if __name__ == "__main__":
    main()
