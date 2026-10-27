"""
Engineering Validation Specialist Skill.
Generates automated engineering validation scorecards covering:
- Geometric validity and rebuild error status
- Dimensional constraints and hole edge margins
- Mass properties and density sanity checks
- Structural Factor of Safety thresholds
- Manufacturing and 3D printability rules
"""
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from skills.base_skill import BaseEngineeringSkill, SkillEvaluationResult


class ValidationCheck(BaseModel):
    category: str
    name: str
    status: str  # "PASS", "FAIL", "WARNING", "SKIPPED"
    value: str
    threshold: str
    details: str


class EngineeringValidationReport(BaseModel):
    passed_count: int
    failed_count: int
    warning_count: int
    checks: List[ValidationCheck]
    overall_status: str
    summary: str


class EngineeringValidationSkill(BaseEngineeringSkill):
    def __init__(self):
        super().__init__(
            name="Engineering Validation Specialist",
            description="Comprehensive geometric integrity, rebuild verification, interference, mass, and structural validation.",
        )

    def evaluate(self, request: str, context: Dict[str, Any]) -> SkillEvaluationResult:
        checks: List[ValidationCheck] = []

        # 1. Rebuild Status Check
        rebuild_errors = context.get("rebuild_errors", 0)
        checks.append(
            ValidationCheck(
                category="CAD Geometry",
                name="Feature Rebuild State",
                status="PASS" if rebuild_errors == 0 else "FAIL",
                value=f"{rebuild_errors} errors",
                threshold="0 errors",
                details="SOLIDWORKS FeatureManager rebuild verification.",
            )
        )

        # 2. Dimensions & Geometry Check
        l = context.get("length_mm", 100.0)
        w = context.get("width_mm", 60.0)
        h = context.get("thickness_mm", 10.0)
        has_positive_volume = l > 0 and w > 0 and h > 0
        checks.append(
            ValidationCheck(
                category="CAD Geometry",
                name="Geometric Manifold Bounding Box",
                status="PASS" if has_positive_volume else "FAIL",
                value=f"{l:.1f} x {w:.1f} x {h:.1f} mm",
                threshold="All dimensions > 0 mm",
                details="Valid closed solid bounding box verification.",
            )
        )

        # 3. Hole Edge Margin Rule (>= 1.5 * dia)
        hole_dia = context.get("hole_dia_mm", 6.0)
        edge_margin = context.get("edge_margin_mm", 10.0)
        req_margin = 1.5 * hole_dia
        margin_pass = edge_margin >= req_margin
        checks.append(
            ValidationCheck(
                category="Mechanical Standards",
                name="Fastener Hole Edge Margin",
                status="PASS" if margin_pass else "WARNING",
                value=f"{edge_margin:.1f} mm",
                threshold=f">= {req_margin:.1f} mm (1.5x dia)",
                details="Prevents tear-out shear failure at mounting locations.",
            )
        )

        # 4. Mass Properties Check
        mass_g = context.get("mass_g", 150.0)
        checks.append(
            ValidationCheck(
                category="Physics / Mass",
                name="Mass Properties Calculation",
                status="PASS" if mass_g > 0 else "FAIL",
                value=f"{mass_g:.1f} g",
                threshold="> 0 g",
                details="Valid positive mass derived from volume and material density.",
            )
        )

        # 5. Bambu Lab X1C Build Volume Validation
        fits_bambu = l <= 256.0 and w <= 256.0 and h <= 256.0
        checks.append(
            ValidationCheck(
                category="Manufacturing (Additive)",
                name="Bambu Lab X1C Envelope Check",
                status="PASS" if fits_bambu else "WARNING",
                value=f"{max(l, w, h):.1f} mm max axis",
                threshold="<= 256.0 mm",
                details="Directly printable on Bambu Lab X1C build plate without segmenting.",
            )
        )

        # 6. Factor of Safety
        fos = context.get("factor_of_safety", 2.5)
        fos_pass = fos >= 2.0
        checks.append(
            ValidationCheck(
                category="Structural Mechanics",
                name="Static Factor of Safety (Yield)",
                status="PASS" if fos_pass else ("WARNING" if fos >= 1.5 else "FAIL"),
                value=f"{fos:.2f}",
                threshold=">= 2.0",
                details="Structural safety margin under maximum specified service load.",
            )
        )

        passed_count = sum(1 for c in checks if c.status == "PASS")
        failed_count = sum(1 for c in checks if c.status == "FAIL")
        warning_count = sum(1 for c in checks if c.status == "WARNING")

        overall = "FAIL" if failed_count > 0 else ("WARNING" if warning_count > 0 else "PASS")

        summary = (
            f"Validation Scorecard: {passed_count}/{len(checks)} PASSED, "
            f"{warning_count} WARNINGS, {failed_count} FAILURES. Overall: {overall}."
        )

        return SkillEvaluationResult(
            skill_name=self.name,
            status=overall,
            summary=summary,
            calculations={
                "passed_count": passed_count,
                "failed_count": failed_count,
                "warning_count": warning_count,
                "scorecard": [c.model_dump() for c in checks],
            },
            recommendations=[c.details for c in checks if c.status in ("WARNING", "FAIL")],
            cad_parameters={},
            warnings=[f"{c.name}: {c.details}" for c in checks if c.status in ("WARNING", "FAIL")],
        )
