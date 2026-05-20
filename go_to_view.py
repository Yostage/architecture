"""Attempt to programmatically activate a saved View Map entry by name.

NEGATIVE RESULT — kept as a regression marker.

What we tried (2026-05-19, against Archicad 29 + Tapir 1.4.0):
  1. Walk the ViewMap via API.GetNavigatorItemTree to find a view by name.
  2. Resolve its navigatorItemId → databaseId via Tapir's
     GetDatabaseIdFromNavigatorItemId. This works.
  3. Call Tapir's ChangeWindow with windowType=3DModel + the resolved databaseId.
     Fails with "databaseId does not belong to the requested windowType".
  4. Trying other windowType values: "3D", "Perspective3D", "Axonometry3D", "View"
     all fail with "Invalid parameter: windowType". Only "3DModel" is a valid
     3D window type per ConvertWindowTypeToString in Tapir's source.

Conclusion: Tapir's ChangeWindow only switches the active *window type*. It
cannot apply a saved View's settings (camera angle, layer combination, scale,
etc.) to the current window. There is no Tapir command for "open this saved
view as if the user double-clicked it in the Navigator."

Workarounds:
  - User opens the view manually: Navigator → View Map → double-click.
  - Or extend Tapir with a new C++ command that wraps Archicad's ACAPI for
    navigator-item activation. Several hours of work + an .apx rebuild.

Usage (for posterity / future reattempts):
  python go_to_view.py "Physical Model"
"""

import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

ENDPOINT = "http://127.0.0.1:19723/"


def raw_call(command: str, params=None):
    body = {"command": command, "parameters": params or {}}
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def find_view(target_name: str):
    r = raw_call("API.GetNavigatorItemTree", {"navigatorTreeId": {"type": "ViewMap"}})
    root = r["result"]["navigatorTree"]["rootItem"]

    def walk(item):
        nav = item.get("navigatorItem") or item.get("rootItem") or item
        if "navigatorItem" in item:
            nav = item["navigatorItem"]
        if nav.get("name") == target_name:
            return nav["navigatorItemId"]["guid"]
        for child in nav.get("children", []) or []:
            hit = walk(child)
            if hit:
                return hit
        return None

    return walk(root)


name = sys.argv[1] if len(sys.argv) > 1 else "Physical Model"
guid = find_view(name)
if not guid:
    sys.exit(f"View not found: {name!r}")
print(f"Found view {name!r}: {guid}")

def tapir(name, params):
    body = {
        "command": "API.ExecuteAddOnCommand",
        "parameters": {
            "addOnCommandId": {"commandNamespace": "TapirCommand", "commandName": name},
            "addOnCommandParameters": params,
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


# Resolve view's navigator item ID → database ID
r = tapir("GetDatabaseIdFromNavigatorItemId", {"navigatorItemIds": [{"navigatorItemId": {"guid": guid}}]})
print(json.dumps(r, indent=2))
db_id = r["result"]["addOnCommandResponse"]["databases"][0]["databaseId"]

# Switch window to that database (3D in our case)
for window_type in ["3D", "3DModel", "Perspective3D", "Axonometry3D", "View"]:
    r2 = tapir("ChangeWindow", {"windowType": window_type, "databaseId": db_id})
    success = r2["result"]["addOnCommandResponse"].get("success", False)
    print(f"  windowType={window_type:20s} succeeded={success}")
    if success:
        print(f"    {json.dumps(r2)[:300]}")
        break
    else:
        err = r2["result"]["addOnCommandResponse"].get("error", {}).get("message", "?")
        print(f"    error: {err}")
