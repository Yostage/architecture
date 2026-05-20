"""
End-to-end topo pilot demo runner.

Regenerates the mesh + labels payloads from the DXF, POSTs both to Tapir, then
fits the Archicad window to the mesh. Single command, no copy/paste.

Pre-reqs:
  - Python venv with requirements.txt installed (.venv/Scripts/python.exe)
  - Archicad 29 running with the Tapir add-on, listening on 127.0.0.1:19723
  - A project open (use a fresh empty one for a clean demo)
  - dxf_out/survey topo test.dxf present (produced from the DWG via ODA File Converter)

Produces: a property-line mesh with contour level lines + 60 elevation labels.
NOT automated (Tapir gap): the "Show User-Defined Ridges" display toggle that
hides triangulation in plan — flip it manually in Mesh Settings for a clean view.

Run:
  .venv\\Scripts\\python.exe run_demo.py
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
PY = sys.executable


def step(label: str, *args: str) -> None:
    print(f"\n=== {label} ===")
    result = subprocess.run([PY, *args], cwd=HERE)
    if result.returncode != 0:
        sys.exit(f"Step failed: {label}")


def main():
    step("Regenerate mesh + labels payloads", "dxf_to_createmeshes.py")
    step("Ping Tapir", "send_to_tapir.py", "ping")
    step("POST mesh", "send_to_tapir.py", "send-mesh")
    step("POST elevation labels", "send_to_tapir.py", "send-labels")
    # send-* print GUIDs in JSON; fit_latest_mesh re-fits to the most recent
    # mesh, so we don't have to parse stdout.
    step("Fit the most recently created mesh in window", "fit_latest_mesh.py")
    print("\nDone. Mesh + labels placed. Switch to 3D (F3), press O for orbit;")
    print("for the clean drawing-set plan, set the mesh to 'Show User-Defined Ridges'.")


if __name__ == "__main__":
    main()
