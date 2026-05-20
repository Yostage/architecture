"""Fit the Archicad window to the most recently-created Mesh in the project.
Avoids having to copy/paste a GUID between steps."""

import json
import sys
import urllib.request

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
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


r = call_tapir("GetElementsByType", {"elementType": "Mesh"})
elements = r["result"]["addOnCommandResponse"].get("elements", [])
if not elements:
    sys.exit("No mesh elements found in project.")
# The last element returned is the most recently created.
target = elements[-1]
print(f"Fitting to mesh: {target['elementId']['guid']}")
r2 = call_tapir("FitInWindow", {"elements": [target]})
print(json.dumps(r2, indent=2))
