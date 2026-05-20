"""Probe a DXF for what's actually in it — layers, entity counts, polyline elevations."""

import sys
from collections import Counter, defaultdict
from pathlib import Path

import ezdxf

sys.stdout.reconfigure(encoding="utf-8")

DXF_PATH = Path(__file__).parent / "dxf_out" / "survey topo test.dxf"


def main():
    doc = ezdxf.readfile(str(DXF_PATH))
    msp = doc.modelspace()

    print(f"=== {DXF_PATH.name} ===")
    print(f"DXF version: {doc.dxfversion}")
    print(f"Units: {doc.units}")
    print()

    # All layers in the file
    print(f"=== Layers ({len(doc.layers)}) ===")
    for layer in sorted(doc.layers, key=lambda L: L.dxf.name):
        print(f"  {layer.dxf.name}")
    print()

    # Entity types in model space
    type_counts = Counter(e.dxftype() for e in msp)
    print(f"=== Entity types in modelspace ({sum(type_counts.values())} total) ===")
    for t, n in type_counts.most_common():
        print(f"  {t:20s} {n:>6}")
    print()

    # Entities per layer
    layer_counts: dict = defaultdict(Counter)
    for e in msp:
        layer_counts[e.dxf.layer][e.dxftype()] += 1
    print(f"=== Entities per layer ===")
    for layer in sorted(layer_counts.keys()):
        total = sum(layer_counts[layer].values())
        breakdown = ", ".join(f"{t}={n}" for t, n in layer_counts[layer].most_common())
        print(f"  {layer:30s} total={total:>5}   ({breakdown})")
    print()

    # Polyline elevation sampling
    POLY_TYPES = {"LWPOLYLINE", "POLYLINE", "POLYLINE2D", "POLYLINE3D"}
    polys = [e for e in msp if e.dxftype() in POLY_TYPES]
    print(f"=== Polylines ({len(polys)}) ===")

    layer_z_summary: dict = defaultdict(list)
    for e in polys:
        layer = e.dxf.layer
        if e.dxftype() == "LWPOLYLINE":
            z_set = {round(e.dxf.elevation, 3)}
            n_pts = len(list(e.get_points()))
        else:
            z_set = {round(v.dxf.location.z, 3) for v in e.vertices}
            n_pts = len(list(e.vertices))
        layer_z_summary[layer].append((e.dxftype(), z_set, n_pts))

    for layer in sorted(layer_z_summary.keys()):
        polys_in_layer = layer_z_summary[layer]
        all_zs = set()
        for _, z_set, _ in polys_in_layer:
            all_zs |= z_set
        unique_zs = sorted(z for z in all_zs if z is not None)
        z_preview = unique_zs[:8]
        if len(unique_zs) > 8:
            z_preview_str = f"{z_preview} ... ({len(unique_zs)} unique Z values, range {min(unique_zs):.3f} → {max(unique_zs):.3f})"
        else:
            z_preview_str = f"{z_preview}"
        print(f"  layer '{layer}': {len(polys_in_layer)} polylines, Zs={z_preview_str}")
    print()

    # Text entities (for spot-elevation labels)
    text_types = {"TEXT", "MTEXT"}
    texts = [e for e in msp if e.dxftype() in text_types]
    print(f"=== Text entities ({len(texts)}) ===")
    layer_text: dict = defaultdict(list)
    for t in texts:
        try:
            content = t.dxf.text if t.dxftype() == "TEXT" else t.text
        except AttributeError:
            content = "<unreadable>"
        layer_text[t.dxf.layer].append(content)
    for layer in sorted(layer_text.keys()):
        sample = layer_text[layer][:5]
        print(f"  layer '{layer}': {len(layer_text[layer])} texts, sample={sample}")
    print()

    # Block references (might hide spot elevations as inserted blocks)
    inserts = [e for e in msp if e.dxftype() == "INSERT"]
    if inserts:
        print(f"=== Block references ({len(inserts)}) ===")
        block_names = Counter(e.dxf.name for e in inserts)
        for name, n in block_names.most_common(20):
            print(f"  {name}: {n}")


if __name__ == "__main__":
    main()
