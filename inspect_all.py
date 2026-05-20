"""Dump every element type and count in the currently loaded Archicad project."""

import json
import sys
import urllib.request
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

ENDPOINT = "http://127.0.0.1:19723/"


def call_tapir(name, params=None):
    body = {
        "command": "API.ExecuteAddOnCommand",
        "parameters": {
            "addOnCommandId": {"commandNamespace": "TapirCommand", "commandName": name},
            "addOnCommandParameters": params or {},
        },
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def unwrap(r):
    return r["result"]["addOnCommandResponse"]


# All Archicad element types we want to check.
TYPES = [
    "Wall", "Column", "Beam", "Window", "Door", "Object", "Lamp",
    "Slab", "Roof", "Mesh", "Zone", "CurtainWall", "Shell", "Skylight",
    "Morph", "Stair", "Railing", "Opening",
    "Polyline", "Line", "Arc", "Circle", "Text", "Label", "Hatch",
    "Detail", "Worksheet", "Section", "Elevation", "InteriorElevation",
]

print("=== All elements by type ===")
totals = Counter()
mesh_guids = []
other_elements = []  # non-mesh things that might be the cutout

for t in TYPES:
    r = call_tapir("GetElementsByType", {"elementType": t})
    if not r.get("succeeded"):
        continue
    elems = unwrap(r).get("elements", [])
    if elems:
        totals[t] = len(elems)
        print(f"  {t:25s} {len(elems)}")
        for e in elems:
            if t == "Mesh":
                mesh_guids.append(e["elementId"]["guid"])
            else:
                other_elements.append((t, e["elementId"]["guid"]))

print(f"\nTotal: {sum(totals.values())}")

if other_elements:
    print("\n=== Non-Mesh elements (potential cutouts/footprints) ===")
    refs = [{"elementId": {"guid": g}} for (_, g) in other_elements]
    bb_resp = unwrap(call_tapir("Get3DBoundingBoxes", {"elements": refs}))
    boxes = bb_resp.get("boundingBoxes3D", [])
    det_resp = unwrap(call_tapir("GetDetailsOfElements", {"elements": refs}))
    details = det_resp.get("detailsOfElements", [])
    for i, (t, g) in enumerate(other_elements):
        box = boxes[i].get("boundingBox3D") if i < len(boxes) else None
        det = details[i] if i < len(details) else {}
        print(f"\n  [{t}] {g}")
        if box:
            print(f"    bbox X=[{box['xMin']:.2f}, {box['xMax']:.2f}]  "
                  f"Y=[{box['yMin']:.2f}, {box['yMax']:.2f}]  "
                  f"Z=[{box['zMin']:.2f}, {box['zMax']:.2f}]   "
                  f"size=({box['xMax']-box['xMin']:.2f}, {box['yMax']-box['yMin']:.2f}, {box['zMax']-box['zMin']:.2f})")
        # Print compact details
        layer = det.get("layerIndex")
        id_ = det.get("id")
        print(f"    id='{id_}'  type={det.get('type')}  layerIndex={layer}  floor={det.get('floorIndex')}")
