"""
Engineering Units Conversion Engine for SOLIDWORKS Automation.
Converts user engineering units (mm, degrees, grams) to and from
SOLIDWORKS COM API internal SI units (meters, radians, kilograms).
"""
import math
from typing import Union, Tuple, List

# Conversion factors
MM_TO_METERS = 0.001
METERS_TO_MM = 1000.0

INCH_TO_METERS = 0.0254
METERS_TO_INCH = 39.37007874

DEG_TO_RAD = math.pi / 180.0
RAD_TO_DEG = 180.0 / math.pi

GRAMS_TO_KG = 0.001
KG_TO_GRAMS = 1000.0

MM3_TO_M3 = 1e-9
M3_TO_MM3 = 1e9


def mm_to_m(val: float) -> float:
    """Convert millimeters to meters."""
    return float(val) * MM_TO_METERS


def m_to_mm(val: float) -> float:
    """Convert meters to millimeters."""
    return float(val) * METERS_TO_MM


def deg_to_rad(val: float) -> float:
    """Convert degrees to radians."""
    return float(val) * DEG_TO_RAD


def rad_to_deg(val: float) -> float:
    """Convert radians to degrees."""
    return float(val) * RAD_TO_DEG


def g_to_kg(val: float) -> float:
    """Convert grams to kilograms."""
    return float(val) * GRAMS_TO_KG


def kg_to_g(val: float) -> float:
    """Convert kilograms to grams."""
    return float(val) * KG_TO_GRAMS


def mm3_to_m3(val: float) -> float:
    """Convert cubic millimeters to cubic meters."""
    return float(val) * MM3_TO_M3


def m3_to_mm3(val: float) -> float:
    """Convert cubic meters to cubic millimeters."""
    return float(val) * M3_TO_MM3


def convert_point_to_m(point_mm: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Convert 3D coordinate from mm to meters."""
    return (mm_to_m(point_mm[0]), mm_to_m(point_mm[1]), mm_to_m(point_mm[2]))


def convert_point_to_mm(point_m: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Convert 3D coordinate from meters to mm."""
    return (m_to_mm(point_m[0]), m_to_mm(point_m[1]), m_to_mm(point_m[2]))
