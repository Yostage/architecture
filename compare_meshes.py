"""Query both Archicad instances and dump their mesh elements for direct
comparison. Assumes port 19723 has our generated mesh and 19724 has Shawn's."""

import json
import sys
import urllib.request
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")


def call(port: int, name: str, params: dict | None = None):
    body = {
        "command": "API.ExecuteAddOnCommand",
        "parameters": {
            "addOnCommandId": {"commandNamespace": "TapirCommand", "commandName": name},
            "addOnCommandParameters": params or {},
        },
    }
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def unwrap(r):
    return r["result"]["addOnCommandResponse"]


def dump_port(port: int, label: str):
    print(f"\n=== {label} (port {port}) ===")
    proj = unwrap(call(port, "GetProjectInfo"))
    print(f"Project: {proj.get('projectName', '<unsaved>')}")

    meshes = unwrap(call(port, "GetElementsByType", {"elementType": "Mesh"}))["elements"]
    print(f"Meshes: {len(meshes)}")

    if not meshes:
        return []

    bboxes = unwrap(call(port, "Get3DBoundingBoxes", {"elements": meshes}))["boundingBoxes3D"]
    details = unwrap(call(port, "GetDetailsOfElements", {"elements": meshes}))["detailsOfElements"]

    summaries = []
    for i, m in enumerate(meshes):
        guid = m["elementId"]["guid"]
        b = bboxes[i]["boundingBox3D"]
        d = details[i].get("details", {})
        sublines = d.get("sublines", [])
        poly = d.get("polygonCoordinates", [])

        n_sublines = len(sublines)
        n_subline_pts = sum(len(s.get("coordinates", [])) for s in sublines)
        n_perim = len(poly)
        # Unique Z values in sublines (rounded)
        all_subline_zs = []
        for s in sublines:
            for c in s.get("coordinates", []):
                all_subline_zs.append(round(c["z"], 3))
        unique_zs = sorted(set(all_subline_zs))

        # Perimeter Z range — varies (Shawn-style) or flat (our v3)?
        perim_zs = [round(c["z"], 3) for c in poly]
        perim_z_unique = len(set(perim_zs))

        summary = {
            "guid": guid,
            "size": (b["xMax"] - b["xMin"], b["yMax"] - b["yMin"], b["zMax"] - b["zMin"]),
            "bbox_x": (b["xMin"], b["xMax"]),
            "bbox_y": (b["yMin"], b["yMax"]),
            "bbox_z": (b["zMin"], b["zMax"]),
            "level": d.get("level"),
            "skirtType": d.get("skirtType"),
            "skirtLevel": d.get("skirtLevel"),
            "n_perim_vertices": n_perim,
            "n_perim_unique_z": perim_z_unique,
            "n_sublines": n_sublines,
            "n_subline_points": n_subline_pts,
            "unique_subline_zs": len(unique_zs),
        }
        summaries.append(summary)
        print(f"  [{i}] guid={guid}")
        print(f"      size       = {summary['size'][0]:>7.2f} × {summary['size'][1]:>7.2f} × {summary['size'][2]:>7.2f} m")
        print(f"      bbox X     = [{summary['bbox_x'][0]:>8.2f}, {summary['bbox_x'][1]:>8.2f}]")
        print(f"      bbox Y     = [{summary['bbox_y'][0]:>8.2f}, {summary['bbox_y'][1]:>8.2f}]")
        print(f"      bbox Z     = [{summary['bbox_z'][0]:>8.2f}, {summary['bbox_z'][1]:>8.2f}]")
        print(f"      level      = {summary['level']}")
        print(f"      skirtType  = {summary['skirtType']!r}")
        print(f"      skirtLevel = {summary['skirtLevel']}")
        print(f"      perimeter  = {summary['n_perim_vertices']} vertices, {summary['n_perim_unique_z']} unique Zs")
        print(f"      sublines   = {summary['n_sublines']}, {summary['n_subline_points']} total pts, {summary['unique_subline_zs']} unique Zs")
    return summaries


ours = dump_port(19723, "OUR mesh")
his = dump_port(19724, "SHAWN's mesh")

print("\n=== Quick diff ===")
# Find the biggest mesh in each (assumed to be the "real" one)
def biggest(arr):
    return max(arr, key=lambda s: s["size"][0] * s["size"][1] * s["size"][2]) if arr else None

ours_big = biggest(ours)
his_big = biggest(his)
if ours_big and his_big:
    for k in ["size", "level", "skirtType", "skirtLevel",
              "n_perim_vertices", "n_perim_unique_z",
              "n_sublines", "n_subline_points", "unique_subline_zs"]:
        a, b = ours_big[k], his_big[k]
        flag = "" if a == b else "  ← DIFF"
        print(f"  {k:22s} ours={str(a):30s} his={str(b):30s}{flag}")
