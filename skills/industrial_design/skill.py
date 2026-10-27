"""
Industrial Product Designer Skill.
Curates product aesthetics, aviation-inspired styling, CMF palettes
(RAL 9016 Gloss White, RAL 1036 Metallic Gold), G2 surface curvature,
ergonomic touchpoints, and exterior panel seam planning.
"""
from typing import Dict, Any, List
from skills.base_skill import BaseEngineeringSkill, SkillEvaluationResult


class IndustrialDesignSkill(BaseEngineeringSkill):
    def __init__(self):
        super().__init__(
            name="Industrial Product Designer",
            description="Aesthetic direction, CMF specifications, organic surfacing, ergonomics, and seam line architecture.",
        )

    def evaluate(self, request: str, context: Dict[str, Any]) -> SkillEvaluationResult:
        req_lower = request.lower()
        recs: List[str] = []
        warnings: List[str] = []
        calcs: Dict[str, Any] = {}
        cad_params: Dict[str, Any] = {}

        # 1. CMF Architecture (Color, Material, Finish)
        cmf_palette = {
            "primary_body": {
                "color_name": "Traffic White",
                "ral": "RAL 9016",
                "hex": "#F6F6F6",
                "finish": "High-Gloss Polyurethane or Polished Gelcoat",
                "application": "Main exterior shell panels and aerodynamic wing surfaces",
            },
            "accent_trim": {
                "color_name": "Gold Metallic",
                "ral": "RAL 1036",
                "hex": "#8F7242",
                "finish": "Satin Anodized / Metallic Pearl",
                "application": "Joint accents, wing pivot bezels, sensor shrouds",
            },
            "face_display": {
                "color_name": "Obsidian Black",
                "hex": "#111111",
                "finish": "Anti-Reflective Optical Polycarbonate",
                "application": "Expressive face display screen and integrated sensor visor",
            },
        }
        calcs["cmf_palette"] = cmf_palette
        recs.append("Applied Aviation White (RAL 9016) + Satin Gold (RAL 1036) dual-tone CMF signature.")

        # 2. Corner Radii & Organic Fillets
        fillet_radius = context.get("corner_fillet_mm", 5.0)
        if "fillet" in req_lower or "rounded" in req_lower or "smooth" in req_lower:
            recs.append(f"Specified G2 continuous curvature corner blend with {fillet_radius} mm radius.")
            cad_params["fillet_radius_mm"] = fillet_radius
        else:
            cad_params["fillet_radius_mm"] = 3.0

        # 3. Seam Line Architecture
        panel_gap = 1.5  # mm standard aesthetic reveal gap
        calcs["recommended_panel_reveal_gap_mm"] = panel_gap
        recs.append(f"Recommended {panel_gap} mm reveal gaps along exterior split lines for clean manufacturing alignment.")

        # 4. Proportions & Silhouette
        if "mascot" in req_lower or "robot" in req_lower:
            target_height = context.get("height_mm", 1400.0)
            calcs["overall_height_mm"] = target_height
            calcs["torso_to_base_ratio"] = "1 : 1.618 (Golden Ratio Silhouette)"
            recs.append("Aesthetic silhouette follows aviation wing sweeps with tapered waist for friendly, agile presence.")

        cad_params.update({
            "panel_reveal_gap_mm": panel_gap,
            "chamfer_deg": 45.0,
        })

        summary = (
            "Industrial Design Specification: Aviation-inspired organic surfacing with "
            "RAL 9016 Gloss White and RAL 1036 Gold accents. Continuous curvature blends applied."
        )

        return SkillEvaluationResult(
            skill_name=self.name,
            status="PASS",
            summary=summary,
            calculations=calcs,
            recommendations=recs,
            cad_parameters=cad_params,
            warnings=warnings,
        )
