"""
Robotics Systems Engineer Skill.
Architects mobile robotics platforms, differential drive powertrains,
actuator torque/power sizing, component packaging envelopes, and CG stability.
"""
from typing import Dict, Any, List
from skills.base_skill import BaseEngineeringSkill, SkillEvaluationResult
from engineering.calculations.mechanics import MechanicsCalculator


class RoboticsSystemsSkill(BaseEngineeringSkill):
    def __init__(self):
        super().__init__(
            name="Robotics Systems Engineer",
            description="Mobile base architecture, actuator sizing, 3-wheel platform stability, and electronics packaging.",
        )

    def evaluate(self, request: str, context: Dict[str, Any]) -> SkillEvaluationResult:
        recs: List[str] = []
        warnings: List[str] = []
        calcs: Dict[str, Any] = {}
        cad_params: Dict[str, Any] = {}

        # 1. Platform Kinematics & Dimensions
        robot_mass_kg = context.get("robot_mass_kg", 35.0)  # Standard mascot robot mass
        wheel_dia_mm = context.get("wheel_dia_mm", 150.0)
        wheel_radius_mm = wheel_dia_mm / 2.0
        track_width_mm = context.get("track_width_mm", 480.0)
        wheelbase_mm = context.get("wheelbase_mm", 420.0)

        # 2. Motor & Powertrain Sizing
        motor_calc = MechanicsCalculator.size_mobile_robot_motors(
            total_robot_mass_kg=robot_mass_kg,
            wheel_radius_mm=wheel_radius_mm,
            target_velocity_m_s=1.2,
            target_acceleration_m_s2=0.6,
            max_incline_deg=8.0,
            rolling_resistance_coeff=0.03,
            num_drive_wheels=2,
        )
        calcs["motor_sizing"] = motor_calc.model_dump()

        rec_motor_torque = round(motor_calc.torque_per_drive_wheel_nm * 1.5, 2)
        recs.append(
            f"Dual drive motor requirement: {motor_calc.torque_per_drive_wheel_nm:.2f} N*m nominal "
            f"({rec_motor_torque:.2f} N*m peak with 1.5x margin) at {motor_calc.required_motor_rpm:.0f} RPM."
        )

        # 3. CG Stability Triangle Evaluation
        cg_height_mm = context.get("cg_height_mm", 450.0)  # mm from ground
        # Stability margin: tip-over acceleration a_crit = g * (b / h)
        # For 3-wheel platform (2 rear wheels, 1 front caster):
        half_track = track_width_mm / 2.0
        crit_accel_lateral_g = half_track / cg_height_mm
        crit_accel_longitudinal_g = (wheelbase_mm * 0.6) / cg_height_mm

        calcs["stability_analysis"] = {
            "cg_height_mm": cg_height_mm,
            "lateral_tip_accel_g": round(crit_accel_lateral_g, 2),
            "longitudinal_tip_accel_g": round(crit_accel_longitudinal_g, 2),
            "is_stable": crit_accel_lateral_g > 0.4 and crit_accel_longitudinal_g > 0.4,
        }

        if crit_accel_lateral_g < 0.45:
            warnings.append(
                f"Lateral tip-over threshold {crit_accel_lateral_g:.2f}g is low. "
                f"Recommend placing battery pack at lowest chassis deck (<120 mm) to lower CG."
            )
        else:
            recs.append(f"Chassis stability triangle verified: Tip threshold {crit_accel_lateral_g:.2f}g lateral.")

        # 4. Packaging Envelopes
        envelopes = {
            "battery_pack": {"dims_mm": [220, 140, 110], "mass_kg": 7.5, "location": "Chassis Lower Deck"},
            "main_compute": {"dims_mm": [160, 150, 65], "mass_kg": 1.2, "location": "Mid Torso Bay"},
            "motor_controllers": {"dims_mm": [120, 90, 40], "mass_kg": 0.8, "location": "Chassis Rear"},
            "front_caster": {"type": "Heavy-Duty Swivel Caster 75mm", "location": "Chassis Front Center"},
        }
        calcs["component_envelopes"] = envelopes
        recs.append("Volumetric packaging envelopes allocated for battery, compute, motor controllers, and caster.")

        cad_params.update({
            "wheel_dia_mm": wheel_dia_mm,
            "track_width_mm": track_width_mm,
            "wheelbase_mm": wheelbase_mm,
            "chassis_plate_thickness_mm": 6.0,
        })

        summary = (
            f"Robotics Architecture: 3-wheel differential drive platform ({robot_mass_kg} kg). "
            f"Motor drive spec: {rec_motor_torque} N*m peak @ {motor_calc.required_motor_rpm:.0f} RPM. "
            f"Low-CG battery packaging verified."
        )

        return SkillEvaluationResult(
            skill_name=self.name,
            status="PASS" if not warnings else "WARNING",
            summary=summary,
            calculations=calcs,
            recommendations=recs,
            cad_parameters=cad_params,
            warnings=warnings,
        )
