"""Query the currently open Archicad project for all Mesh elements and dump
the comparable state: count, bbox, vertex count, level, skirt. Writes a JSON
snapshot tagged by a label argument so we can compare two projects side by side.

Usage:
    python inspect_meshes.py <label>

Writes:  snapshots/<label>.json
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ENDPOINT = "http://127.0.0.1:19723/"
SNAPSHOT_DIR = Path(__file__).parent / "snapshots"


def call_tapir(command_name: str, params: dict | None = None) -> dict:
    body = {
        "command": "API.ExecuteAddOnCommand",
        "parameters": {
            "addOnCommandId": {
                "commandNamespace": "TapirCommand",
                "commandName": command_name,
            },
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
        return json.loads(resp.read().decode("utf-8"))


def unwrap(r: dict) -> dict:
    if not r.get("succeeded"):
        raise RuntimeError(f"Tapir call failed: {json.dumps(r)[:500]}")
    return r["result"]["addOnCommandResponse"]


def main(label: str):
    print(f"=== Inspecting meshes (label='{label}') ===")

    # 1) project info
    proj = unwrap(call_tapir("GetProjectInfo"))
    print(f"Project: {proj.get('projectName', '<unsaved>')}  path={proj.get('projectPath', '')}")

    # 2) all mesh elements
    meshes_resp = unwrap(call_tapir("GetElementsByType", {"elementType": "Mesh"}))
    mesh_refs = meshes_resp.get("elements", [])
    print(f"Mesh elements: {len(mesh_refs)}")

    if not mesh_refs:
        snapshot = {"label": label, "project": proj, "meshes": []}
    else:
        # 3) bounding boxes
        bboxes_resp = unwrap(call_tapir("Get3DBoundingBoxes", {"elements": mesh_refs}))
        boxes = bboxes_resp.get("boundingBoxes3D", [])

        # 4) details
        details_resp = unwrap(call_tapir("GetDetailsOfElements", {"elements": mesh_refs}))
        details = details_resp.get("detailsOfElements", [])

        meshes = []
        for i, ref in enumerate(mesh_refs):
            guid = ref["elementId"]["guid"]
            box = boxes[i].get("boundingBox3D") if i < len(boxes) else None
            det = details[i] if i < len(details) else None
            meshes.append({
                "guid": guid,
                "boundingBox": box,
                "details": det,
            })
            if box:
                print(f"  [{i}] guid={guid}")
                print(f"        bbox X=[{box['xMin']:.2f}, {box['xMax']:.2f}]  "
                      f"Y=[{box['yMin']:.2f}, {box['yMax']:.2f}]  "
                      f"Z=[{box['zMin']:.2f}, {box['zMax']:.2f}]")
                print(f"        size=({box['xMax']-box['xMin']:.2f}, "
                      f"{box['yMax']-box['yMin']:.2f}, "
                      f"{box['zMax']-box['zMin']:.2f})")
        snapshot = {"label": label, "project": proj, "meshes": meshes}

    SNAPSHOT_DIR.mkdir(exist_ok=True)
    out = SNAPSHOT_DIR / f"{label}.json"
    out.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1])
