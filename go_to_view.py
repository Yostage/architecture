"""Activate a saved View Map entry by name — the real, working version.

POSITIVE RESULT as of Tapir 1.5.0 (2026-06-01). The earlier incarnation of this
file was a negative-result marker: stock Tapir's `ChangeWindow` could only switch
the active *window type* and could not apply a saved View's settings (camera
angle, layer combination, scale, MVO, zoom). Activating a view "as if the user
double-clicked it in the Navigator" had no Tapir command.

That gap is now closed. Upstream PR #398 (shipped in Tapir 1.5.0) extended
`ChangeWindow` to accept a `navigatorItemId`, which on AC27+ routes through
`ACAPI_View_GoToView` and applies all the saved view parameters. (On AC25/26 the
command returns NOTSUPPORTED for `navigatorItemId`; there is no view-settings
path on those versions.)

How it works now:
  1. Walk the ViewMap via API.GetNavigatorItemTree to find a view by name.
  2. Call Tapir's ChangeWindow with that view's navigatorItemId. Done — no
     GetDatabaseIdFromNavigatorItemId hop, no windowType guessing.

Requires Tapir 1.5.0+ (stock). Archicad 27+ for the saved-view settings to apply.

Usage:
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
    """Return the full navigatorItemId object for the named view, or None."""
    r = raw_call("API.GetNavigatorItemTree", {"navigatorTreeId": {"type": "ViewMap"}})
    root = r["result"]["navigatorTree"]["rootItem"]

    def walk(item):
        nav = item["navigatorItem"] if "navigatorItem" in item else item
        if nav.get("name") == target_name:
            return nav["navigatorItemId"]
        for child in nav.get("children", []) or []:
            hit = walk(child)
            if hit:
                return hit
        return None

    return walk(root)


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


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "Physical Model"
    nav_id = find_view(name)
    if not nav_id:
        sys.exit(f"View not found: {name!r}")
    print(f"Found view {name!r}: {nav_id['guid']}")

    # ChangeWindow + navigatorItemId (Tapir 1.5.0+): routes through
    # ACAPI_View_GoToView on AC27+, applying the view's saved layer combo,
    # scale, MVO, dim, and zoom — the real "open this view" action.
    r = tapir("ChangeWindow", {"navigatorItemId": nav_id})
    if r.get("succeeded"):
        print("Switched to view (saved settings applied).")
        return 0
    print(json.dumps(r, indent=2))
    return 1


if __name__ == "__main__":
    sys.exit(main())
