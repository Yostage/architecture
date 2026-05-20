"""
Send a Tapir command to a running Archicad.

Usage:
    python send_to_tapir.py ping             # GetAddOnVersion — sanity check
    python send_to_tapir.py send-mesh        # POST createmeshes_payload.json
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ENDPOINT = "http://127.0.0.1:19723/"
PAYLOAD_PATH = Path(__file__).parent / "createmeshes_payload.json"
TEXTS_PATH = Path(__file__).parent / "createtexts_payload.json"


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
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        return {"__http_error__": e.code, "__body__": e.read().decode("utf-8", errors="replace")}
    except urllib.error.URLError as e:
        return {"__url_error__": str(e)}


def ping() -> int:
    print(f"POST {ENDPOINT}  command=TapirCommand.GetAddOnVersion")
    r = call_tapir("GetAddOnVersion")
    print(json.dumps(r, indent=2))
    return 0 if r.get("succeeded") else 1


def send_mesh() -> int:
    payload = json.loads(PAYLOAD_PATH.read_text(encoding="utf-8"))
    print(f"POST {ENDPOINT}  command=TapirCommand.CreateMeshes")
    print(f"  meshesData[0].polygonCoordinates: {len(payload['meshesData'][0]['polygonCoordinates'])} vertices")
    print(f"  meshesData[0].sublines:           {len(payload['meshesData'][0]['sublines'])} contours")
    r = call_tapir("CreateMeshes", payload)
    print(json.dumps(r, indent=2)[:4000])
    return 0 if r.get("succeeded") else 1


def send_texts() -> int:
    payload = json.loads(TEXTS_PATH.read_text(encoding="utf-8"))
    print(f"POST {ENDPOINT}  command=TapirCommand.CreateTexts  ({len(payload['textsData'])} texts)")
    r = call_tapir("CreateTexts", payload)
    print(json.dumps(r, indent=2)[:2000])
    return 0 if r.get("succeeded") else 1


def _delete_by_type(element_type: str) -> int:
    r = call_tapir("GetElementsByType", {"elementType": element_type})
    if not r.get("succeeded"):
        print(json.dumps(r, indent=2))
        return 1
    elements = r["result"]["addOnCommandResponse"].get("elements", [])
    print(f"Deleting {len(elements)} {element_type} element(s)")
    if not elements:
        return 0
    r2 = call_tapir("DeleteElements", {"elements": elements})
    return 0 if r2.get("succeeded") else 1


def fit(guid: str) -> int:
    print(f"POST {ENDPOINT}  command=TapirCommand.FitInWindow  element={guid}")
    r = call_tapir("FitInWindow", {"elements": [{"elementId": {"guid": guid}}]})
    print(json.dumps(r, indent=2))
    return 0 if r.get("succeeded") else 1


def delete_meshes() -> int:
    return _delete_by_type("Mesh")


def clear_all() -> int:
    """Clear everything our pipeline creates: meshes, texts, and any legacy labels."""
    rc = 0
    for t in ("Mesh", "Text", "Label"):
        rc |= _delete_by_type(t)
    return rc


def main():
    cmds = ("ping", "send-mesh", "send-texts", "fit", "delete-meshes", "clear")
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print(__doc__)
        return 2
    if sys.argv[1] == "ping":
        return ping()
    if sys.argv[1] == "send-mesh":
        return send_mesh()
    if sys.argv[1] == "send-texts":
        return send_texts()
    if sys.argv[1] == "fit":
        return fit(sys.argv[2])
    if sys.argv[1] == "delete-meshes":
        return delete_meshes()
    if sys.argv[1] == "clear":
        return clear_all()


if __name__ == "__main__":
    sys.exit(main())
