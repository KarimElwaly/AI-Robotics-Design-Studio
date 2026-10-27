"""
Engineering Standard Specifications & Catalog Dimensions.
Covers Bambu Lab heat-set brass inserts, ISO metric clearance holes,
and standard robotics actuator faceplate dimensions (NEMA steppers).
"""
from typing import Dict, Optional
from pydantic import BaseModel


class HeatSetInsertSpec(BaseModel):
    thread_size: str
    outer_diameter_mm: float
    length_mm: float
    recommended_hole_diameter_mm: float
    recommended_hole_depth_mm: float
    min_boss_wall_thickness_mm: float
    recommended_insertion_temp_c: int


HEAT_SET_INSERTS: Dict[str, HeatSetInsertSpec] = {
    "M2": HeatSetInsertSpec(
        thread_size="M2",
        outer_diameter_mm=3.2,
        length_mm=4.0,
        recommended_hole_diameter_mm=3.0,
        recommended_hole_depth_mm=4.8,
        min_boss_wall_thickness_mm=1.2,
        recommended_insertion_temp_c=240,
    ),
    "M2.5": HeatSetInsertSpec(
        thread_size="M2.5",
        outer_diameter_mm=3.6,
        length_mm=4.5,
        recommended_hole_diameter_mm=3.4,
        recommended_hole_depth_mm=5.2,
        min_boss_wall_thickness_mm=1.4,
        recommended_insertion_temp_c=240,
    ),
    "M3": HeatSetInsertSpec(
        thread_size="M3",
        outer_diameter_mm=4.2,
        length_mm=5.0,
        recommended_hole_diameter_mm=4.0,
        recommended_hole_depth_mm=5.7,
        min_boss_wall_thickness_mm=1.6,
        recommended_insertion_temp_c=240,
    ),
    "M4": HeatSetInsertSpec(
        thread_size="M4",
        outer_diameter_mm=5.6,
        length_mm=6.0,
        recommended_hole_diameter_mm=5.4,
        recommended_hole_depth_mm=6.8,
        min_boss_wall_thickness_mm=2.0,
        recommended_insertion_temp_c=250,
    ),
    "M5": HeatSetInsertSpec(
        thread_size="M5",
        outer_diameter_mm=7.1,
        length_mm=7.0,
        recommended_hole_diameter_mm=6.8,
        recommended_hole_depth_mm=8.0,
        min_boss_wall_thickness_mm=2.5,
        recommended_insertion_temp_c=250,
    ),
}


class BoltClearanceHoleSpec(BaseModel):
    thread_size: str
    close_fit_dia_mm: float
    normal_fit_dia_mm: float
    loose_fit_dia_mm: float
    head_counterbore_dia_mm: float
    head_counterbore_depth_mm: float


BOLT_CLEARANCE_HOLES: Dict[str, BoltClearanceHoleSpec] = {
    "M3": BoltClearanceHoleSpec(thread_size="M3", close_fit_dia_mm=3.2, normal_fit_dia_mm=3.4, loose_fit_dia_mm=3.6, head_counterbore_dia_mm=6.0, head_counterbore_depth_mm=3.5),
    "M4": BoltClearanceHoleSpec(thread_size="M4", close_fit_dia_mm=4.3, normal_fit_dia_mm=4.5, loose_fit_dia_mm=4.8, head_counterbore_dia_mm=7.5, head_counterbore_depth_mm=4.5),
    "M5": BoltClearanceHoleSpec(thread_size="M5", close_fit_dia_mm=5.3, normal_fit_dia_mm=5.5, loose_fit_dia_mm=5.8, head_counterbore_dia_mm=9.0, head_counterbore_depth_mm=5.5),
    "M6": BoltClearanceHoleSpec(thread_size="M6", close_fit_dia_mm=6.4, normal_fit_dia_mm=6.6, loose_fit_dia_mm=7.0, head_counterbore_dia_mm=11.0, head_counterbore_depth_mm=6.5),
    "M8": BoltClearanceHoleSpec(thread_size="M8", close_fit_dia_mm=8.4, normal_fit_dia_mm=9.0, loose_fit_dia_mm=10.0, head_counterbore_dia_mm=14.5, head_counterbore_depth_mm=8.5),
}


class NemaMotorSpec(BaseModel):
    nema_size: str
    face_width_mm: float
    pilot_dia_mm: float
    pilot_depth_mm: float
    hole_spacing_mm: float
    mounting_hole_dia_mm: float
    shaft_dia_mm: float


NEMA_MOTORS: Dict[str, NemaMotorSpec] = {
    "NEMA 14": NemaMotorSpec(nema_size="NEMA 14", face_width_mm=35.2, pilot_dia_mm=22.0, pilot_depth_mm=2.0, hole_spacing_mm=26.0, mounting_hole_dia_mm=3.2, shaft_dia_mm=5.0),
    "NEMA 17": NemaMotorSpec(nema_size="NEMA 17", face_width_mm=42.3, pilot_dia_mm=22.0, pilot_depth_mm=2.0, hole_spacing_mm=31.0, mounting_hole_dia_mm=3.2, shaft_dia_mm=5.0),
    "NEMA 23": NemaMotorSpec(nema_size="NEMA 23", face_width_mm=57.2, pilot_dia_mm=38.1, pilot_depth_mm=1.6, hole_spacing_mm=47.1, mounting_hole_dia_mm=5.2, shaft_dia_mm=6.35),
}
