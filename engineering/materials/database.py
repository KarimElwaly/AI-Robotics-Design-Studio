"""
Engineering Materials Database.
Provides verified mechanical and thermal properties for metals, engineering polymers,
and 3D printing filaments (specifically Bambu Lab profiles).
"""
from typing import Dict, Optional, List
from pydantic import BaseModel


class MaterialProperties(BaseModel):
    name: str
    category: str  # "Metal", "Filament", "Polymer"
    density_kg_m3: float
    density_g_cm3: float
    yield_strength_mpa: float
    ultimate_tensile_strength_mpa: float
    elastic_modulus_gpa: float
    poisson_ratio: float
    max_service_temp_c: float
    solidworks_name: str
    description: str
    print_nozzle_temp_c: Optional[int] = None
    print_bed_temp_c: Optional[int] = None
    chamber_temp_required: bool = False
    drying_temp_c: Optional[int] = None
    drying_hours: Optional[int] = None


MATERIALS_DB: Dict[str, MaterialProperties] = {
    "6061-T6 Aluminum": MaterialProperties(
        name="6061-T6 Aluminum",
        category="Metal",
        density_kg_m3=2700.0,
        density_g_cm3=2.70,
        yield_strength_mpa=276.0,
        ultimate_tensile_strength_mpa=310.0,
        elastic_modulus_gpa=68.9,
        poisson_ratio=0.33,
        max_service_temp_c=150.0,
        solidworks_name="6061-T6 (SS)",
        description="Standard aerospace & robotics aluminum alloy. Excellent strength-to-weight ratio and machinability.",
    ),
    "1018 Steel": MaterialProperties(
        name="1018 Steel",
        category="Metal",
        density_kg_m3=7870.0,
        density_g_cm3=7.87,
        yield_strength_mpa=370.0,
        ultimate_tensile_strength_mpa=440.0,
        elastic_modulus_gpa=205.0,
        poisson_ratio=0.29,
        max_service_temp_c=400.0,
        solidworks_name="AISI 1018 Steel, cold drawn",
        description="General purpose low-carbon cold-drawn steel with good weldability and ductility.",
    ),
    "304 Stainless Steel": MaterialProperties(
        name="304 Stainless Steel",
        category="Metal",
        density_kg_m3=8000.0,
        density_g_cm3=8.00,
        yield_strength_mpa=215.0,
        ultimate_tensile_strength_mpa=505.0,
        elastic_modulus_gpa=193.0,
        poisson_ratio=0.29,
        max_service_temp_c=800.0,
        solidworks_name="AISI 304",
        description="Austenitic stainless steel with high corrosion resistance.",
    ),
    "C360 Brass": MaterialProperties(
        name="C360 Brass",
        category="Metal",
        density_kg_m3=8500.0,
        density_g_cm3=8.50,
        yield_strength_mpa=310.0,
        ultimate_tensile_strength_mpa=400.0,
        elastic_modulus_gpa=100.0,
        poisson_ratio=0.31,
        max_service_temp_c=200.0,
        solidworks_name="Brass",
        description="Free-cutting brass, standard material for threaded heat-set inserts and bushings.",
    ),
    "Bambu PLA Basic": MaterialProperties(
        name="Bambu PLA Basic",
        category="Filament",
        density_kg_m3=1240.0,
        density_g_cm3=1.24,
        yield_strength_mpa=55.0,
        ultimate_tensile_strength_mpa=60.0,
        elastic_modulus_gpa=2.6,
        poisson_ratio=0.36,
        max_service_temp_c=50.0,
        solidworks_name="PLA",
        description="High-precision prototyping filament. Low warpage, easy to print on Bambu X1C.",
        print_nozzle_temp_c=220,
        print_bed_temp_c=55,
        chamber_temp_required=False,
    ),
    "Bambu PETG-CF": MaterialProperties(
        name="Bambu PETG-CF",
        category="Filament",
        density_kg_m3=1270.0,
        density_g_cm3=1.27,
        yield_strength_mpa=68.0,
        ultimate_tensile_strength_mpa=76.0,
        elastic_modulus_gpa=4.2,
        poisson_ratio=0.37,
        max_service_temp_c=75.0,
        solidworks_name="PETG",
        description="Carbon-fiber reinforced PETG with high stiffness, matte finish, and good impact resistance.",
        print_nozzle_temp_c=255,
        print_bed_temp_c=70,
        chamber_temp_required=False,
        drying_temp_c=65,
        drying_hours=8,
    ),
    "Bambu ABS-GF": MaterialProperties(
        name="Bambu ABS-GF",
        category="Filament",
        density_kg_m3=1080.0,
        density_g_cm3=1.08,
        yield_strength_mpa=48.0,
        ultimate_tensile_strength_mpa=55.0,
        elastic_modulus_gpa=3.8,
        poisson_ratio=0.35,
        max_service_temp_c=95.0,
        solidworks_name="ABS",
        description="Glass-fiber reinforced ABS. High heat resistance and dimensionally stable for robot chassis.",
        print_nozzle_temp_c=260,
        print_bed_temp_c=90,
        chamber_temp_required=True,
        drying_temp_c=80,
        drying_hours=8,
    ),
    "Bambu PAHT-CF": MaterialProperties(
        name="Bambu PAHT-CF",
        category="Filament",
        density_kg_m3=1210.0,
        density_g_cm3=1.21,
        yield_strength_mpa=95.0,
        ultimate_tensile_strength_mpa=110.0,
        elastic_modulus_gpa=5.2,
        poisson_ratio=0.38,
        max_service_temp_c=140.0,
        solidworks_name="Nylon 6/10",
        description="High-temperature carbon-fiber nylon for load-bearing robotics gears, brackets, and motor mounts.",
        print_nozzle_temp_c=290,
        print_bed_temp_c=100,
        chamber_temp_required=True,
        drying_temp_c=80,
        drying_hours=12,
    ),
    "Bambu TPU 95A": MaterialProperties(
        name="Bambu TPU 95A",
        category="Filament",
        density_kg_m3=1200.0,
        density_g_cm3=1.20,
        yield_strength_mpa=18.0,
        ultimate_tensile_strength_mpa=35.0,
        elastic_modulus_gpa=0.05,
        poisson_ratio=0.45,
        max_service_temp_c=80.0,
        solidworks_name="Rubber",
        description="Flexible elastomer for robot tires, bumpers, shock-absorbing mounts, and seals.",
        print_nozzle_temp_c=230,
        print_bed_temp_c=35,
        chamber_temp_required=False,
    ),
}


def get_material(name: str) -> Optional[MaterialProperties]:
    """Retrieve material properties with case-insensitive search."""
    name_clean = name.strip().lower()
    for mat_name, props in MATERIALS_DB.items():
        if mat_name.lower() == name_clean:
            return props
    for mat_name, props in MATERIALS_DB.items():
        if name_clean in mat_name.lower():
            return props
    return None


def list_materials(category: Optional[str] = None) -> List[MaterialProperties]:
    """List materials, optionally filtered by category."""
    if not category:
        return list(MATERIALS_DB.values())
    return [m for m in MATERIALS_DB.values() if m.category.lower() == category.lower()]
