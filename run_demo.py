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
    step("Regenerate payloads", "dxf_to_createmeshes.py")
    step("Ping Tapir", "send_to_tapir.py", "ping")
    # Clear prior demo output so re-runs stay clean (idempotent). NOTE: this
    # deletes ALL meshes/labels in the project — intended for the fresh/empty
    # demo project, not a real working file.
    step("Clear existing meshes", "send_to_tapir.py", "delete-meshes")
    step("Clear existing labels", "send_to_tapir.py", "delete-labels")
    step("POST mesh", "send_to_tapir.py", "send-mesh")
    # NOTE: contour-label placement is NOT run here. Tapir's CreateLabels can't
    # bind a standalone text-label library part — it produces empty label shells
    # with a stray leader to origin (verified 2026-05-20). The label code remains
    # available via `send_to_tapir.py send-labels` for when that's fixed/extended.
    # See Future Work.md.
    step("Fit the most recently created mesh in window", "fit_latest_mesh.py")
    print("\nDone. Mesh placed (property-line perimeter + contour level lines).")
    print("For the clean drawing-set plan, set the mesh to 'Show User-Defined Ridges'.")
    print("Contour elevation labels are not auto-placed (Tapir gap — see Future Work).")


if __name__ == "__main__":
    main()
