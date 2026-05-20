"""List all items in the View Map of the currently open project — flat, indented
by tree depth. Useful for finding saved 3D views with preserved camera angles."""

import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

ENDPOINT = "http://127.0.0.1:19723/"


def call(command: str, params: dict | None = None):
    body = {"command": command, "parameters": params or {}}
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def walk(item, depth=0):
    """Yield (depth, type, name, guid) tuples flattening the tree."""
    nav = item.get("navigatorItem") or item.get("rootItem") or item
    if "navigatorItem" in item:
        nav = item["navigatorItem"]
    name = nav.get("name", "")
    prefix = nav.get("prefix", "")
    label = (f"{prefix} {name}".strip() if prefix else name) or "(unnamed)"
    typ = nav.get("type", "?")
    guid = nav["navigatorItemId"]["guid"]
    yield depth, typ, label, guid
    for child in nav.get("children", []) or []:
        yield from walk(child, depth + 1)


def dump_tree(tree_type: str):
    r = call("API.GetNavigatorItemTree", {"navigatorTreeId": {"type": tree_type}})
    if not r.get("succeeded"):
        print(f"  {tree_type} fetch FAILED: {json.dumps(r)[:200]}")
        return
    root = r["result"]["navigatorTree"]["rootItem"]
    print(f"\n=== {tree_type} ===")
    for depth, typ, label, guid in walk(root):
        indent = "  " * depth
        print(f"{indent}{label:50s} [{typ}]  {guid[:8]}…")


for t in ("ViewMap", "ProjectMap", "LayoutBook"):
    dump_tree(t)
