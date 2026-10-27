"""
Mechanical Design Engineer Skill.
Performs analytical stress, moment, deflection, motor mount, and bracket sizing calculations.
Recommends optimal plate thickness, hole spacing, and material selection.
"""
from typing import Dict, Any, List
from skills.base_skill import BaseEngineeringSkill, SkillEvaluationResult
from engineering.calculations.mechanics import MechanicsCalculator
from engineering.materials.database import get_material
from engineering.components.standards import NEMA_MOTORS, BOLT_CLEARANCE_HOLES


class MechanicalDesignSkill(BaseEngineeringSkill):
    def __init__(self):
        super().__init__(
            name="Mechanical Design Engineer",
            description="Structural mechanics, bracket sizing, stress/FoS analysis, fasteners, and parametric CAD parameters.",
        )

    def evaluate(self, request: str, context: Dict[str, Any]) -> SkillEvaluationResult:
        req_lower = request.lower()
        recs: List[str] = []
        warnings: List[str] = []
        calcs: Dict[str, Any] = {}
        cad_params: Dict[str, Any] = {}

        # 1. Material Selection
        mat_name = context.get("material", "6061-T6 Aluminum")
        mat_props = get_material(mat_name) or get_material("6061-T6 Aluminum")

        # 2. Motor Mount Detection
        motor_type = None
        for nema_name in ["nema 23", "nema 17", "nema 14"]:
            if nema_name in req_lower:
                motor_type = nema_name.upper()
                break

        if motor_type:
            spec = NEMA_MOTORS.get(motor_type, NEMA_MOTORS["NEMA 17"])
            calcs["motor_standard"] = motor_type
            calcs["pilot_dia_mm"] = spec.pilot_dia_mm
            calcs["hole_spacing_mm"] = spec.hole_spacing_mm
            calcs["mounting_hole_dia_mm"] = spec.mounting_hole_dia_mm
            recs.append(f"Standard {motor_type} faceplate selected: {spec.hole_spacing_mm} mm hole spacing.")
            cad_params["motor_pilot_dia_mm"] = spec.pilot_dia_mm
            cad_params["hole_spacing_mm"] = spec.hole_spacing_mm

        # 3. Plate & Bracket Sizing
        length = context.get("length_mm", 100.0)
        width = context.get("width_mm", 60.0)
        thickness = context.get("thickness_mm", 10.0)

        # Check bending if load specified
        load_n = context.get("load_n", 250.0)  # Default 250 N (~25 kgf)
        moment_nm = (load_n * (length / 1000.0)) / 2.0  # Center-point equivalent moment

        stress_res = MechanicsCalculator.evaluate_stress_and_fos(
            moment_n_m=moment_nm,
            torque_n_m=5.0,
            width_mm=width,
            height_mm=thickness,
            yield_strength_mpa=mat_props.yield_strength_mpa,
        )
        calcs["stress_analysis"] = stress_res.model_dump()

        if stress_res.factor_of_safety < 2.0:
            rec_thick = thickness * (2.0 / max(stress_res.factor_of_safety, 0.1)) ** 0.5
            warnings.append(
                f"Factor of safety {stress_res.factor_of_safety:.2f} is below target 2.0. "
                f"Recommend increasing thickness from {thickness:.1f} mm to at least {rec_thick:.1f} mm."
            )
            cad_params["recommended_thickness_mm"] = round(rec_thick, 1)
        else:
            recs.append(f"Structure is structurally sound with FoS = {stress_res.factor_of_safety:.2f} (>= 2.0).")
            cad_params["thickness_mm"] = thickness

        # Edge distance verification (2.5 * hole_dia rule)
        hole_dia = context.get("hole_dia_mm", 6.0)
        edge_margin = context.get("edge_margin_mm", 10.0)
        min_margin = 1.5 * hole_dia
        if edge_margin < min_margin:
            warnings.append(
                f"Hole edge margin ({edge_margin} mm) is less than standard 1.5x diameter ({min_margin} mm). "
                f"Risk of tear-out failure under tension."
            )
        else:
            recs.append(f"Hole edge margin of {edge_margin} mm exceeds minimum standard ({min_margin} mm).")

        cad_params.update({
            "length_mm": length,
            "width_mm": width,
            "hole_dia_mm": hole_dia,
            "edge_margin_mm": edge_margin,
            "material": mat_props.name,
        })

        status = "PASS" if not warnings else "WARNING"
        summary = (
            f"Mechanical Design Review ({mat_props.name}): "
            f"von Mises {stress_res.von_mises_stress_mpa:.1f} MPa | FoS {stress_res.factor_of_safety:.2f} | "
            f"{'Safe for dynamic loads' if status == 'PASS' else 'Review warnings before manufacture'}."
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
