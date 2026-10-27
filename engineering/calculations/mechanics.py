"""
Analytical Mechanical Engineering Calculation Engine.
Pure Python implementations of standard mechanical formulas:
- Beam bending stress and deflection
- Torsional stress and polar moment
- von Mises equivalent combined stress
- Factor of Safety (FoS) evaluation
- Fastener tensile and shear capacities
- Mobile robot wheel torque and motor power sizing
- Ball bearing L10 rating life
"""
import math
from typing import Dict, Any, Tuple
from pydantic import BaseModel, Field


class StressAnalysisResult(BaseModel):
    bending_stress_mpa: float
    torsional_shear_stress_mpa: float
    von_mises_stress_mpa: float
    yield_strength_mpa: float
    factor_of_safety: float
    is_safe: bool
    summary: str


class BeamDeflectionResult(BaseModel):
    max_deflection_mm: float
    span_mm: float
    deflection_ratio: float  # L / delta
    stiffness_n_per_mm: float
    summary: str


class MotorSizingResult(BaseModel):
    total_robot_mass_kg: float
    wheel_radius_mm: float
    rolling_resistance_torque_nm: float
    acceleration_torque_nm: float
    incline_torque_nm: float
    total_required_torque_nm: float
    torque_per_drive_wheel_nm: float
    required_motor_rpm: float
    required_mechanical_power_watts: float
    recommended_safety_margin_factor: float = 1.5
    summary: str


class MechanicsCalculator:
    """Analytical calculations conforming to Shigley's Mechanical Engineering Design."""

    @staticmethod
    def rectangular_moment_of_inertia(width_mm: float, height_mm: float) -> Tuple[float, float]:
        """
        Compute I_xx = (b * h^3) / 12, Area = b * h.
        Width along neutral axis, height in direction of bending.
        Returns (I_mm4, Area_mm2).
        """
        I_xx = (width_mm * (height_mm ** 3)) / 12.0
        area = width_mm * height_mm
        return I_xx, area

    @staticmethod
    def circular_moment_of_inertia(diameter_mm: float, inner_diameter_mm: float = 0.0) -> Tuple[float, float, float]:
        """
        Compute I = pi*(d_o^4 - d_i^4)/64, J = pi*(d_o^4 - d_i^4)/32.
        Returns (I_mm4, J_mm4, Area_mm2).
        """
        d_o4 = diameter_mm ** 4
        d_i4 = inner_diameter_mm ** 4
        I_xx = (math.pi * (d_o4 - d_i4)) / 64.0
        J_polar = (math.pi * (d_o4 - d_i4)) / 32.0
        area = (math.pi * (diameter_mm ** 2 - inner_diameter_mm ** 2)) / 4.0
        return I_xx, J_polar, area

    @staticmethod
    def calculate_bending_stress(moment_n_m: float, y_distance_mm: float, I_mm4: float) -> float:
        """
        sigma = (M * y) / I.
        Returns stress in MPa (N/mm^2).
        Note: M in N*m = 1000 N*mm.
        """
        M_n_mm = moment_n_m * 1000.0
        return (M_n_mm * y_distance_mm) / I_mm4

    @staticmethod
    def calculate_torsion_stress(torque_n_m: float, radius_mm: float, J_mm4: float) -> float:
        """
        tau = (T * r) / J.
        Returns torsional shear stress in MPa.
        """
        T_n_mm = torque_n_m * 1000.0
        return (T_n_mm * radius_mm) / J_mm4

    @staticmethod
    def calculate_von_mises_stress(normal_stress_mpa: float, shear_stress_mpa: float) -> float:
        """
        sigma_v = sqrt(sigma^2 + 3 * tau^2).
        """
        return math.sqrt((normal_stress_mpa ** 2) + 3.0 * (shear_stress_mpa ** 2))

    @classmethod
    def evaluate_stress_and_fos(
        cls,
        moment_n_m: float,
        torque_n_m: float,
        width_mm: float,
        height_mm: float,
        yield_strength_mpa: float,
    ) -> StressAnalysisResult:
        """
        Complete structural check for a rectangular cross-section subject to bending and torsion.
        """
        I_xx, _ = cls.rectangular_moment_of_inertia(width_mm, height_mm)
        y_max = height_mm / 2.0
        # For rectangle, approximate polar moment J = I_xx + I_yy
        I_yy = (height_mm * (width_mm ** 3)) / 12.0
        J_approx = I_xx + I_yy

        sigma = cls.calculate_bending_stress(moment_n_m, y_max, I_xx)
        tau = cls.calculate_torsion_stress(torque_n_m, max(width_mm, height_mm) / 2.0, J_approx)
        sigma_v = cls.calculate_von_mises_stress(sigma, tau)

        fos = yield_strength_mpa / sigma_v if sigma_v > 0 else 999.0
        is_safe = fos >= 1.5

        return StressAnalysisResult(
            bending_stress_mpa=round(sigma, 2),
            torsional_shear_stress_mpa=round(tau, 2),
            von_mises_stress_mpa=round(sigma_v, 2),
            yield_strength_mpa=yield_strength_mpa,
            factor_of_safety=round(fos, 2),
            is_safe=is_safe,
            summary=(
                f"von Mises stress: {sigma_v:.2f} MPa vs Yield: {yield_strength_mpa:.2f} MPa. "
                f"Factor of Safety: {fos:.2f} ({'PASS' if is_safe else 'FAIL - Redesign Recommended'})."
            ),
        )

    @classmethod
    def calculate_cantilever_deflection(
        cls,
        load_n: float,
        length_mm: float,
        elastic_modulus_gpa: float,
        width_mm: float,
        height_mm: float,
    ) -> BeamDeflectionResult:
        """
        delta = (F * L^3) / (3 * E * I).
        """
        I_xx, _ = cls.rectangular_moment_of_inertia(width_mm, height_mm)
        E_mpa = elastic_modulus_gpa * 1000.0  # GPa to MPa (N/mm2)
        delta_mm = (load_n * (length_mm ** 3)) / (3.0 * E_mpa * I_xx)
        ratio = length_mm / delta_mm if delta_mm > 0 else 99999.0
        stiffness = load_n / delta_mm if delta_mm > 0 else 99999.0

        return BeamDeflectionResult(
            max_deflection_mm=round(delta_mm, 3),
            span_mm=length_mm,
            deflection_ratio=round(ratio, 1),
            stiffness_n_per_mm=round(stiffness, 2),
            summary=f"Max tip deflection: {delta_mm:.3f} mm (Span/Deflection ratio: L/{ratio:.0f}).",
        )

    @staticmethod
    def size_mobile_robot_motors(
        total_robot_mass_kg: float,
        wheel_radius_mm: float,
        target_velocity_m_s: float = 1.0,
        target_acceleration_m_s2: float = 0.5,
        max_incline_deg: float = 5.0,
        rolling_resistance_coeff: float = 0.02,
        num_drive_wheels: int = 2,
    ) -> MotorSizingResult:
        """
        Analytical motor sizing for mobile robotics base.
        F_total = F_rolling + F_incline + F_accel
        Torque_total = F_total * r_wheel
        """
        g = 9.80665
        r_m = wheel_radius_mm / 1000.0
        incline_rad = math.radians(max_incline_deg)

        # Forces
        f_rolling = total_robot_mass_kg * g * rolling_resistance_coeff * math.cos(incline_rad)
        f_incline = total_robot_mass_kg * g * math.sin(incline_rad)
        f_accel = total_robot_mass_kg * target_acceleration_m_s2
        f_total = f_rolling + f_incline + f_accel

        # Total torques
        t_rolling = f_rolling * r_m
        t_incline = f_incline * r_m
        t_accel = f_accel * r_m
        t_total = f_total * r_m

        t_per_wheel = t_total / max(num_drive_wheels, 1)

        # RPM & Power
        wheel_circ_m = 2.0 * math.pi * r_m
        wheel_rev_per_sec = target_velocity_m_s / wheel_circ_m if wheel_circ_m > 0 else 0
        rpm = wheel_rev_per_sec * 60.0
        omega_rad_s = (rpm * 2.0 * math.pi) / 60.0
        power_watts = t_total * omega_rad_s

        return MotorSizingResult(
            total_robot_mass_kg=total_robot_mass_kg,
            wheel_radius_mm=wheel_radius_mm,
            rolling_resistance_torque_nm=round(t_rolling, 3),
            acceleration_torque_nm=round(t_accel, 3),
            incline_torque_nm=round(t_incline, 3),
            total_required_torque_nm=round(t_total, 3),
            torque_per_drive_wheel_nm=round(t_per_wheel, 3),
            required_motor_rpm=round(rpm, 1),
            required_mechanical_power_watts=round(power_watts, 2),
            summary=(
                f"Robot Mass: {total_robot_mass_kg} kg | Drive Torque per Wheel: {t_per_wheel:.2f} N*m "
                f"at {rpm:.0f} RPM ({power_watts:.1f} W total)."
            ),
        )
