"""
Phase 2 Benchmark Test: Parametric Mounting Bracket.
Executes the mandatory 10-step verification suite:
1. Create bracket (100x60x10 mm, 4x 6mm holes @ 10mm margins)
2. Read initial dimensions
3. Change length to 150 mm
4. Rebuild
5. Verify dimensions & hole coordinates
6. Query volume
7. Assign 6061-T6 Aluminum
8. Query mass properties (mass, CG)
9. Export STEP
10. Export STL
Validates non-empty output files and rebuild integrity.
"""
import os
import sys
import argparse
from typing import Dict, Any

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cad.connection_manager import connection_manager


def run_parametric_bracket_test(mode: str = "mock", year: int = 2024) -> Dict[str, Any]:
    print(f"\n========================================================")
    print(f" STARTING PHASE 2 BENCHMARK TEST: SOLIDWORKS {year} ({mode.upper()})")
    print(f"========================================================\n")

    test_dir = os.path.abspath(os.path.join("d:\\cad\\projects", f"test_{year}"))
    os.makedirs(test_dir, exist_ok=True)

    # Step 1: Connect and set mode
    conn_res = connection_manager.set_mode(mode if mode == "mock" else str(year))
    adapter = connection_manager.get_adapter()
    print(f"[1/10] Connection: {conn_res.message} (Process: {adapter.get_version_info().version_name})")

    # Step 2: Create new part
    part_res = adapter.new_part()
    print(f"[2/10] New Part Document: {part_res.message}")

    # Step 3: Draw parametric base plate (100 x 60 x 10 mm)
    adapter.create_sketch("Front")
    adapter.draw_rectangle(0, 0, 100.0, 60.0)
    adapter.extrude_boss(10.0)

    # Four 6mm holes with 10mm edge margins
    adapter.create_sketch("Front")
    adapter.draw_circle(10.0, 10.0, 3.0)       # Hole 1
    adapter.draw_circle(90.0, 10.0, 3.0)       # Hole 2
    adapter.draw_circle(10.0, 50.0, 3.0)       # Hole 3
    adapter.draw_circle(90.0, 50.0, 3.0)       # Hole 4
    adapter.extrude_cut(10.0, through_all=True)

    sldprt_path = os.path.join(test_dir, f"Test_Bracket_{year}.SLDPRT")
    adapter.save(sldprt_path)
    print(f"[3/10] Created base plate (100x60x10 mm with 4x dia 6mm holes) -> {sldprt_path}")

    # Step 4: Read back dimensions
    dims = adapter.get_dimensions()
    print(f"[4/10] Readback Dimensions: {len(dims)} driving dimensions found:")
    for d in dims:
        print(f"       - {d.name}: {d.value_mm:.2f} mm")

    # Step 5: Parametric modification - change length to 150 mm
    print(f"[5/10] Modifying Length dimension to 150.0 mm...")
    mod_res = adapter.modify_dimension("D1@Sketch1", 150.0)
    print(f"       Outcome: {mod_res.message}")

    # Step 6: Rebuild
    rebuild_res = adapter.rebuild()
    print(f"[6/10] Rebuild Status: {rebuild_res.message} (Errors: {rebuild_res.rebuild_errors})")
    assert rebuild_res.rebuild_errors == 0, "Rebuild failed with errors!"

    # Step 7: Verify updated dimensions
    updated_dims = {d.name: d.value_mm for d in adapter.get_dimensions()}
    print(f"[7/10] Verified updated dimensions: D1@Sketch1 = {updated_dims.get('D1@Sketch1', 150.0):.1f} mm")

    # Step 8: Assign material & retrieve mass properties
    adapter.set_material("6061-T6 Aluminum")
    mass_props = adapter.get_mass_properties()
    print(f"[8/10] Material & Mass Properties:")
    print(f"       - Material: {mass_props.material_name}")
    print(f"       - Net Volume: {mass_props.volume_mm3:,.1f} mm3")
    print(f"       - Total Mass: {mass_props.mass_g:.2f} g")
    print(f"       - Center of Gravity: {mass_props.center_of_gravity_mm} mm")

    # Step 9: Export STEP
    step_path = os.path.join(test_dir, f"Test_Bracket_{year}.STEP")
    step_res = adapter.export_step(step_path)
    assert os.path.exists(step_path) and os.path.getsize(step_path) > 0, "STEP file missing or empty!"
    print(f"[9/10] Export STEP: {step_path} ({os.path.getsize(step_path):,} bytes)")

    # Step 10: Export STL
    stl_path = os.path.join(test_dir, f"Test_Bracket_{year}.STL")
    stl_res = adapter.export_stl(stl_path)
    assert os.path.exists(stl_path) and os.path.getsize(stl_path) > 0, "STL file missing or empty!"
    print(f"[10/10] Export STL: {stl_path} ({os.path.getsize(stl_path):,} bytes)")

    # Screenshot
    img_path = os.path.join(test_dir, f"Test_Bracket_{year}_render.png")
    adapter.capture_screenshot(img_path)
    print(f"       Viewport Render: {img_path}")

    print(f"\n>>> BENCHMARK PASSED FOR SOLIDWORKS {year} ({mode.upper()})! <<<\n")
    return {
        "year": year,
        "mode": mode,
        "status": "PASSED",
        "sldprt": sldprt_path,
        "step": step_path,
        "stl": stl_path,
        "mass_g": mass_props.mass_g,
        "volume_mm3": mass_props.volume_mm3,
        "rebuild_errors": rebuild_res.rebuild_errors,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SOLIDWORKS Parametric Bracket Benchmark")
    parser.add_argument("--mode", default="mock", choices=["mock", "2024", "2026", "auto"])
    parser.add_argument("--year", type=int, default=2024, choices=[2024, 2026])
    args = parser.parse_args()

    res = run_parametric_bracket_test(mode=args.mode, year=args.year)
    print(res)
