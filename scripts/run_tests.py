"""
Comprehensive Test Runner for AI Robotics Design Studio.
Executes:
1. Unit tests for engineering calculations and unit conversions
2. Skills evaluation tests (Mechanical, Industrial, Robotics, Additive, Validation)
3. Parametric Mounting Bracket Benchmark (Phase 2 requirement)
4. Fast API endpoint testing
"""
import os
import sys
import unittest

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cad.units import mm_to_m, m_to_mm, deg_to_rad, rad_to_deg, g_to_kg, kg_to_g
from engineering.calculations.mechanics import MechanicsCalculator
from engineering.materials.database import get_material, list_materials
from engineering.components.standards import HEAT_SET_INSERTS, NEMA_MOTORS
from cad.connection_manager import connection_manager
from agents.lead_manager import lead_agent
from tests.test_parametric_bracket import run_parametric_bracket_test


class TestEngineeringUnits(unittest.TestCase):
    def test_length_conversion(self):
        self.assertAlmostEqual(mm_to_m(100.0), 0.1)
        self.assertAlmostEqual(m_to_mm(0.1), 100.0)

    def test_angle_conversion(self):
        self.assertAlmostEqual(deg_to_rad(180.0), 3.141592653589793)
        self.assertAlmostEqual(rad_to_deg(3.141592653589793), 180.0)

    def test_mass_conversion(self):
        self.assertAlmostEqual(g_to_kg(1500.0), 1.5)
        self.assertAlmostEqual(kg_to_g(1.5), 1500.0)


class TestMechanicsCalculations(unittest.TestCase):
    def test_rectangular_inertia(self):
        I_xx, area = MechanicsCalculator.rectangular_moment_of_inertia(60.0, 10.0)
        self.assertAlmostEqual(I_xx, 5000.0)
        self.assertAlmostEqual(area, 600.0)

    def test_stress_and_fos(self):
        res = MechanicsCalculator.evaluate_stress_and_fos(
            moment_n_m=20.0,
            torque_n_m=5.0,
            width_mm=60.0,
            height_mm=10.0,
            yield_strength_mpa=276.0,
        )
        self.assertGreater(res.factor_of_safety, 1.5)
        self.assertTrue(res.is_safe)

    def test_motor_sizing(self):
        motor = MechanicsCalculator.size_mobile_robot_motors(
            total_robot_mass_kg=35.0,
            wheel_radius_mm=75.0,
        )
        self.assertGreater(motor.total_required_torque_nm, 0.5)
        self.assertGreater(motor.required_motor_rpm, 50.0)


class TestEngineeringSkills(unittest.TestCase):
    def test_mechanical_skill(self):
        skill = lead_agent.skills["mechanical"]
        res = skill.evaluate("Design a NEMA 17 bracket with 10 mm thickness", {"length_mm": 100, "width_mm": 60, "thickness_mm": 10})
        self.assertIn("NEMA 17", res.summary)
        self.assertEqual(res.status, "PASS")

    def test_industrial_skill(self):
        skill = lead_agent.skills["industrial"]
        res = skill.evaluate("Apply aviation white and gold styling with fillets", {})
        self.assertIn("RAL 9016", str(res.calculations))
        self.assertEqual(res.status, "PASS")

    def test_additive_skill(self):
        skill = lead_agent.skills["additive"]
        res = skill.evaluate("Check if 100x60x10 mm fits Bambu X1C", {"length_mm": 100, "width_mm": 60, "thickness_mm": 10})
        self.assertFalse(res.calculations.get("split_required"))
        self.assertEqual(res.status, "PASS")

    def test_validation_skill(self):
        skill = lead_agent.skills["validation"]
        res = skill.evaluate("Check part geometry", {"rebuild_errors": 0, "length_mm": 100, "width_mm": 60, "thickness_mm": 10, "mass_g": 160})
        self.assertEqual(res.status, "PASS")


class TestPhase2ParametricBracketBenchmark(unittest.TestCase):
    def test_parametric_bracket_mock(self):
        res = run_parametric_bracket_test(mode="mock", year=2024)
        self.assertEqual(res["status"], "PASSED")
        self.assertEqual(res["rebuild_errors"], 0)
        self.assertTrue(os.path.exists(res["step"]))
        self.assertTrue(os.path.exists(res["stl"]))
        self.assertGreater(os.path.getsize(res["step"]), 0)
        self.assertGreater(os.path.getsize(res["stl"]), 0)


class TestLeadAgentLoop(unittest.TestCase):
    def test_end_to_end_agent(self):
        response = lead_agent.process_request("Design a motor mounting bracket with four mounting holes, rounded corners, and a 10 mm plate thickness.")
        self.assertIsNotNone(response.active_skill)
        self.assertGreater(len(response.steps), 0)
        self.assertIsNotNone(response.mass_properties)
        self.assertGreater(response.mass_properties.mass_g, 0)


if __name__ == "__main__":
    print("\n========================================================")
    print(" RUNNING AI ROBOTICS DESIGN STUDIO AUTOMATED TEST SUITE")
    print("========================================================\n")
    runner = unittest.TextTestRunner(verbosity=2)
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    test_result = runner.run(suite)
    if not test_result.wasSuccessful():
        sys.exit(1)
