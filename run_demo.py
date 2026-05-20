"""
End-to-end topo pilot demo runner.

Regenerates the CreateMeshes payload from the DXF, POSTs it to Tapir, then
fits the Archicad window to the new mesh. Single command, no copy/paste.

Pre-reqs:
  - Python venv with requirements.txt installed (.venv/Scripts/python.exe)
  - Archicad 29 running with the Tapir add-on, listening on 127.0.0.1:19723
  - A project open (use a fresh empty one for a clean demo)
  - dxf_out/survey topo test.dxf present (produced from the DWG via ODA File Converter)

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
    step("Regenerate CreateMeshes payload", "dxf_to_createmeshes.py")
    step("Ping Tapir", "send_to_tapir.py", "ping")
    step("POST mesh", "send_to_tapir.py", "send-mesh")
    # send-mesh prints the GUID in JSON; the script below re-fits to whatever
    # the most recent mesh in the project is, so we don't have to parse stdout.
    step("Fit the most recently created mesh in window", "fit_latest_mesh.py")
    print("\nDone. Switch to 3D (F3), press O for orbit.")


if __name__ == "__main__":
    main()
