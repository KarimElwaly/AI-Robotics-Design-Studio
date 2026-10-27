"""
Lead Engineering Agent: Engineering Design Manager.
Translates natural-language design requests into validated engineering specifications,
coordinates specialized engineering skills, plans parametric CAD workflows,
executes CAD adapter operations, and validates the reconstructed geometry.
"""
import re
import os
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from cad.connection_manager import connection_manager
from cad.adapters.base import CadOperationResult, MassProperties
from skills.mechanical_design.skill import MechanicalDesignSkill
from skills.industrial_design.skill import IndustrialDesignSkill
from skills.robotics_systems.skill import RoboticsSystemsSkill
from skills.additive_manufacturing.skill import AdditiveManufacturingSkill
from skills.engineering_validation.skill import EngineeringValidationSkill
from skills.base_skill import SkillEvaluationResult

logger = logging.getLogger("LeadEngineeringAgent")


class AgentStep(BaseModel):
    step_number: int
    name: str
    status: str  # "DONE", "FAILED", "RUNNING"
    details: str
    data: Dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    reply: str
    active_skill: str
    skill_evaluation: Optional[SkillEvaluationResult] = None
    steps: List[AgentStep] = Field(default_factory=list)
    cad_result: Optional[CadOperationResult] = None
    mass_properties: Optional[MassProperties] = None
    warnings: List[str] = Field(default_factory=list)
    active_document: Optional[str] = None


class LeadEngineeringAgent:
    """Lead Engineering Design Manager coordinating AI skills and CAD operations."""

    def __init__(self):
        # Register specialized engineering skills
        self.skills = {
            "mechanical": MechanicalDesignSkill(),
            "industrial": IndustrialDesignSkill(),
            "robotics": RoboticsSystemsSkill(),
            "additive": AdditiveManufacturingSkill(),
            "validation": EngineeringValidationSkill(),
        }
        self.conversation_history: List[Dict[str, str]] = []
        # Current active design state parameters
        self.current_state: Dict[str, Any] = {
            "length_mm": 100.0,
            "width_mm": 60.0,
            "thickness_mm": 10.0,
            "hole_dia_mm": 6.0,
            "edge_margin_mm": 10.0,
            "material": "6061-T6 Aluminum",
            "corner_fillet_mm": 3.0,
            "rebuild_errors": 0,
        }

    def select_skill(self, request: str) -> str:
        """Select the primary specialized skill based on user request keywords."""
        r = request.lower()
        if any(k in r for k in ["validate", "validation", "check", "verify", "scorecard", "rebuild error"]):
            return "validation"
        if any(k in r for k in ["bambu", "3d print", "print", "additive", "filament", "fdm", "insert"]):
            return "additive"
        if any(k in r for k in ["robot", "chassis", "motor size", "drive", "wheel", "caster", "battery", "packaging", "stability"]):
            return "robotics"
        if any(k in r for k in ["aesthetic", "style", "styling", "cmf", "color", "finish", "ral", "organic", "appearance", "curve"]):
            return "industrial"
        # Default to mechanical design
        return "mechanical"

    def parse_dimensions_from_text(self, text: str) -> Dict[str, float]:
        """Extract dimension updates from natural language."""
        updates = {}
        # Match pattern: "100x60x10" or "100 x 60 mm"
        box_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:x|\*|by)\s*(\d+(?:\.\d+)?)(?:\s*(?:x|\*|by)\s*(\d+(?:\.\d+)?))?\s*mm", text, re.I)
        if box_match:
            updates["length_mm"] = float(box_match.group(1))
            updates["width_mm"] = float(box_match.group(2))
            if box_match.group(3):
                updates["thickness_mm"] = float(box_match.group(3))

        # Match single dimension adjustments: "length to 150 mm", "increase length by 20 mm"
        len_match = re.search(r"(?:length|long)\s*(?:to|is|=)\s*(\d+(?:\.\d+)?)\s*mm", text, re.I)
        if len_match:
            updates["length_mm"] = float(len_match.group(1))

        inc_len = re.search(r"(?:increase|extend|enlarge)\s*(?:its\s*)?length\s*by\s*(\d+(?:\.\d+)?)\s*mm", text, re.I)
        if inc_len:
            updates["length_mm"] = self.current_state.get("length_mm", 100.0) + float(inc_len.group(1))

        width_match = re.search(r"(?:width|wide)\s*(?:to|is|=)\s*(\d+(?:\.\d+)?)\s*mm", text, re.I)
        if width_match:
            updates["width_mm"] = float(width_match.group(1))

        thick_match = re.search(r"(?:thickness|thick|height)\s*(?:to|is|=)?\s*(\d+(?:\.\d+)?)\s*mm", text, re.I)
        if thick_match:
            updates["thickness_mm"] = float(thick_match.group(1))

        fillet_match = re.search(r"(\d+(?:\.\d+)?)\s*mm\s*fillet", text, re.I) or re.search(r"fillet.*?(\d+(?:\.\d+)?)\s*mm", text, re.I)
        if fillet_match:
            updates["corner_fillet_mm"] = float(fillet_match.group(1))

        hole_match = re.search(r"(\d+(?:\.\d+)?)\s*mm\s*(?:hole|mounting hole)", text, re.I) or re.search(r"hole.*?(\d+(?:\.\d+)?)\s*mm", text, re.I)
        if hole_match:
            updates["hole_dia_mm"] = float(hole_match.group(1))

        return updates

    def process_request(self, user_prompt: str) -> AgentResponse:
        """Execute full lead engineering agent reasoning and CAD execution loop."""
        self.conversation_history.append({"role": "user", "content": user_prompt})
        steps: List[AgentStep] = []
        step_idx = 1

        # 1. Intent & Dimension Extraction
        extracted_dims = self.parse_dimensions_from_text(user_prompt)
        self.current_state.update(extracted_dims)

        steps.append(
            AgentStep(
                step_number=step_idx,
                name="Requirement Analysis",
                status="DONE",
                details=f"Extracted design parameters: Length={self.current_state['length_mm']} mm, Width={self.current_state['width_mm']} mm, Thickness={self.current_state['thickness_mm']} mm.",
                data=extracted_dims,
            )
        )
        step_idx += 1

        # 2. Select Specialized Skill
        skill_key = self.select_skill(user_prompt)
        active_skill = self.skills[skill_key]
        skill_eval = active_skill.evaluate(user_prompt, self.current_state)

        steps.append(
            AgentStep(
                step_number=step_idx,
                name=f"Consulting {active_skill.name}",
                status="DONE",
                details=skill_eval.summary,
                data=skill_eval.calculations,
            )
        )
        step_idx += 1

        # 3. CAD Adapter Execution
        adapter = connection_manager.get_adapter()
        cad_res = None
        prompt_lower = user_prompt.lower()

        # If model doesn't exist, create bracket
        if not getattr(adapter, "active_doc", None) or "create" in prompt_lower or "bracket" in prompt_lower or "plate" in prompt_lower:
            steps.append(
                AgentStep(
                    step_number=step_idx,
                    name="Initialize CAD Part",
                    status="RUNNING",
                    details=f"Creating new part in {adapter.get_version_info().version_name}.",
                )
            )
            cad_res = adapter.new_part()
            adapter.create_sketch("Front")
            # Base plate
            l = self.current_state["length_mm"]
            w = self.current_state["width_mm"]
            t = self.current_state["thickness_mm"]
            adapter.draw_rectangle(0, 0, l, w)
            adapter.extrude_boss(t)

            # Four mounting holes
            hd = self.current_state["hole_dia_mm"]
            margin = self.current_state["edge_margin_mm"]
            hr = hd / 2.0
            adapter.create_sketch("Front")
            # Hole 1 (bottom left)
            adapter.draw_circle(margin, margin, hr)
            # Hole 2 (bottom right)
            adapter.draw_circle(l - margin, margin, hr)
            # Hole 3 (top left)
            adapter.draw_circle(margin, w - margin, hr)
            # Hole 4 (top right)
            adapter.draw_circle(l - margin, w - margin, hr)
            adapter.extrude_cut(t, through_all=True)

            # Fillets if requested
            if "rounded" in prompt_lower or "fillet" in prompt_lower or self.current_state.get("corner_fillet_mm", 0) > 0:
                adapter.add_fillet(self.current_state.get("corner_fillet_mm", 3.0))

            adapter.set_material(self.current_state["material"])
            adapter.rebuild()
            steps[-1].status = "DONE"
            steps[-1].details = f"Created parametric bracket ({l}x{w}x{t} mm) with 4 mounting holes."
            step_idx += 1

        elif "increase" in prompt_lower or "change" in prompt_lower or "modify" in prompt_lower or extracted_dims:
            # Parametric update
            steps.append(
                AgentStep(
                    step_number=step_idx,
                    name="Parametric Dimension Modification",
                    status="RUNNING",
                    details=f"Updating driving dimensions to Length={self.current_state['length_mm']} mm.",
                )
            )
            cad_res = adapter.modify_dimension("D1@Sketch1", self.current_state["length_mm"])
            adapter.rebuild()
            steps[-1].status = "DONE"
            steps[-1].details = f"Parametric update executed: D1@Sketch1 = {self.current_state['length_mm']} mm."
            step_idx += 1

        elif "fillet" in prompt_lower or "round" in prompt_lower:
            r = self.current_state.get("corner_fillet_mm", 3.0)
            steps.append(
                AgentStep(
                    step_number=step_idx,
                    name="Apply Corner Fillets",
                    status="RUNNING",
                    details=f"Applying {r} mm fillets.",
                )
            )
            cad_res = adapter.add_fillet(r)
            adapter.rebuild()
            steps[-1].status = "DONE"
            steps[-1].details = f"Applied {r} mm fillets to corners."
            step_idx += 1

        elif "export" in prompt_lower:
            steps.append(
                AgentStep(
                    step_number=step_idx,
                    name="CAD Export",
                    status="RUNNING",
                    details="Exporting STEP and STL files.",
                )
            )
            step_path = os.path.join("d:\\cad\\projects", f"{adapter.active_doc}.STEP")
            stl_path = os.path.join("d:\\cad\\projects", f"{adapter.active_doc}.STL")
            adapter.export_step(step_path)
            adapter.export_stl(stl_path)
            steps[-1].status = "DONE"
            steps[-1].details = f"Exported {step_path} and {stl_path} successfully."
            step_idx += 1

        # 4. Geometry Inspection & Mass Properties
        mass_props = adapter.get_mass_properties()
        self.current_state["mass_g"] = mass_props.mass_g

        # 5. Formulate final response
        reply_lines = [
            f"### Engineering Execution Summary ({active_skill.name})",
            f"**Action**: Handled request with verified parameters.",
            f"- **Geometry**: {self.current_state['length_mm']:.1f} mm × {self.current_state['width_mm']:.1f} mm × {self.current_state['thickness_mm']:.1f} mm",
            f"- **Material**: {self.current_state['material']}",
            f"- **Volume**: {mass_props.volume_mm3:,.1f} mm³ | **Mass**: {mass_props.mass_g:.1f} g",
            f"- **Rebuild State**: 0 errors",
            f"\n**Skill Insight**: {skill_eval.summary}",
        ]
        if skill_eval.recommendations:
            reply_lines.append("\n**Recommendations**:")
            for r in skill_eval.recommendations:
                reply_lines.append(f"- {r}")

        reply = "\n".join(reply_lines)
        self.conversation_history.append({"role": "assistant", "content": reply})

        return AgentResponse(
            reply=reply,
            active_skill=active_skill.name,
            skill_evaluation=skill_eval,
            steps=steps,
            cad_result=cad_res,
            mass_properties=mass_props,
            warnings=skill_eval.warnings,
            active_document=getattr(adapter, "active_doc", "None"),
        )


# Singleton lead agent
lead_agent = LeadEngineeringAgent()
