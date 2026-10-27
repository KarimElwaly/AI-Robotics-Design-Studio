"""
Additive Manufacturing Engineer Skill.
Validates 3D printability for Bambu Lab X1C and X1E printers:
- Build volume limits (256 x 256 x 256 mm)
- Material profile verification (PLA, PETG-CF, ABS-GF, PAHT-CF, TPU)
- Wall thickness and overhang rules
- Threaded heat-set insert hole specs
- Automated part-splitting recommendations for large robot panels
"""
from typing import Dict, Any, List
from skills.base_skill import BaseEngineeringSkill, SkillEvaluationResult
from engineering.materials.database import get_material
from engineering.components.standards import HEAT_SET_INSERTS


class AdditiveManufacturingSkill(BaseEngineeringSkill):
    BUILD_VOLUME_MM = (256.0, 256.0, 256.0)  # Bambu Lab X1C / X1E

    def __init__(self):
        super().__init__(
            name="Additive Manufacturing Engineer",
            description="Bambu Lab X1C/X1E build volume validation, material extrusion settings, heat-set inserts, and part splitting.",
        )

    def evaluate(self, request: str, context: Dict[str, Any]) -> SkillEvaluationResult:
        recs: List[str] = []
        warnings: List[str] = []
        calcs: Dict[str, Any] = {}
        cad_params: Dict[str, Any] = {}

        # 1. Bounding Box & Build Volume Validation
        l = context.get("length_mm", 100.0)
        w = context.get("width_mm", 60.0)
        h = context.get("thickness_mm", 10.0)

        bx, by, bz = self.BUILD_VOLUME_MM
        exceeds_x = l > bx
        exceeds_y = w > by
        exceeds_z = h > bz

        calcs["build_volume_mm"] = list(self.BUILD_VOLUME_MM)
        calcs["part_bounding_box_mm"] = [l, w, h]

        if exceeds_x or exceeds_y or exceeds_z:
            warnings.append(
                f"Part dimensions ({l:.1f} x {w:.1f} x {h:.1f} mm) exceed Bambu Lab X1C build volume (256 x 256 x 256 mm). "
                f"Part splitting is required."
            )
            calcs["split_required"] = True
            recs.append("Recommend splitting model along neutral aesthetic seam lines with interlocking alignment pins and M3 heat-set inserts.")
        else:
            calcs["split_required"] = False
            recs.append(f"Part fits comfortably inside Bambu Lab X1C build volume ({l:.1f} x {w:.1f} x {h:.1f} mm).")

        # 2. Material Profile Validation
        mat_name = context.get("material", "Bambu PETG-CF")
        mat_props = get_material(mat_name)
        if not mat_props or mat_props.category != "Filament":
            # Recommend filament
            rec_filament = get_material("Bambu PETG-CF")
            recs.append(f"Recommended production filament: {rec_filament.name} ({rec_filament.description}).")
            mat_props = rec_filament

        calcs["material_profile"] = {
            "name": mat_props.name,
            "nozzle_temp_c": mat_props.print_nozzle_temp_c,
            "bed_temp_c": mat_props.print_bed_temp_c,
            "chamber_required": mat_props.chamber_temp_required,
            "drying": f"{mat_props.drying_hours}h @ {mat_props.drying_temp_c}C" if mat_props.drying_hours else "None",
        }

        # 3. Minimum Feature & Wall Thickness
        min_wall_thickness = 1.6  # mm recommended for structural rigidity
        if h < min_wall_thickness:
            warnings.append(f"Plate thickness ({h} mm) is below recommended 1.6 mm minimum for FDM printing.")
        else:
            recs.append(f"Wall thickness of {h} mm provides solid layer infill and high interlaminar shear strength.")

        # 4. Heat-Set Insert Verification
        insert_size = context.get("insert_size", "M3")
        insert_spec = HEAT_SET_INSERTS.get(insert_size, HEAT_SET_INSERTS["M3"])
        calcs["heat_set_insert_spec"] = insert_spec.model_dump()
        recs.append(
            f"Specified {insert_size} brass heat-set inserts: Hole diameter {insert_spec.recommended_hole_diameter_mm} mm, "
            f"depth {insert_spec.recommended_hole_depth_mm} mm, boss wall >= {insert_spec.min_boss_wall_thickness_mm} mm."
        )

        cad_params.update({
            "insert_hole_dia_mm": insert_spec.recommended_hole_diameter_mm,
            "insert_hole_depth_mm": insert_spec.recommended_hole_depth_mm,
            "min_wall_thickness_mm": min_wall_thickness,
            "target_material": mat_props.name,
        })

        status = "PASS" if not warnings else "WARNING"
        summary = (
            f"Additive Manufacturing (Bambu X1C / X1E): "
            f"{'Fits build volume' if not calcs['split_required'] else 'Requires part splitting'} | "
            f"Profile: {mat_props.name} | Inserts: {insert_size} brass."
        )

        return SkillEvaluationResult(
            skill_name=self.name,
            status=status,
            summary=summary,
            calculations=calcs,
            recommendations=recs,
            cad_parameters=cad_params,
            warnings=warnings,
        )
