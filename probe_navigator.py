"""Probe the official Archicad JSON API for navigator-related commands.

Tapir's command surface doesn't include enumeration of the Navigator (View Map /
Project Map / Layout Book), so we tested the official Archicad commands. Results
from running against Archicad 29 + Tapir 1.4.0 on 2026-05-19:

  WORKS:
    API.IsAlive                              — liveness check
    API.GetPublisherSetNames                 — returns the publisher set names
    API.GetNavigatorItemTree                 — REQUIRES {"navigatorTreeId": {"type": "ViewMap"|"ProjectMap"|"LayoutBook"}}

  EXISTS BUT NEEDS PARAMS (4002):
    API.GetNavigatorItemsType

  NOT FOUND (2002):
    API.GetViewSettings, API.GetNavigatorItemIdByType, API.GetNavigatorItemsByType,
    API.GetPublisherSets, API.GetViews, API.GetSavedViews

The working command (API.GetNavigatorItemTree with one of the three tree types)
is what list_views.py uses to enumerate everything in the project's navigator.
"""

import json
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

ENDPOINT = "http://127.0.0.1:19723/"


def raw_call(command: str, parameters: dict | None = None) -> dict:
    body = {"command": command, "parameters": parameters or {}}
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"__http_error__": e.code, "__body__": e.read().decode("utf-8", errors="replace")[:300]}


CANDIDATES = [
    "API.GetNavigatorItemTree",
    "API.GetNavigatorItemsType",
    "API.GetPublisherSetNames",
    "API.GetViewSettings",
    "API.GetNavigatorItemIdByType",
    "API.GetNavigatorItemsByType",
    "API.GetPublisherSets",
    "API.GetViews",
    "API.GetSavedViews",
    "API.IsAlive",
]

for cmd in CANDIDATES:
    r = raw_call(cmd)
    success = r.get("succeeded", False)
    print(f"  {cmd:50s} {'OK' if success else 'FAIL'}: {json.dumps(r)[:200]}")

print("\n--- Trying GetNavigatorItemTree with various param shapes ---")
for params in [
    {"navigatorTreeId": {"type": "ViewMap"}},
    {"navigatorTreeId": {"type": "ProjectMap"}},
    {"navigatorTreeId": {"type": "LayoutBook"}},
    {"navigatorTreeId": {"type": "PublisherSets"}},
    {"type": "ViewMap"},
]:
    r = raw_call("API.GetNavigatorItemTree", params)
    success = r.get("succeeded", False)
    print(f"  params={json.dumps(params)[:60]:62s} {'OK' if success else 'FAIL'}")
    if success:
        print(f"    {json.dumps(r['result'])[:800]}")
        print()
