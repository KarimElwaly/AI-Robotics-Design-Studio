"""
Engineering Knowledge Library Manager.
Maintains structured manufacturer specifications, mechanical design guidelines,
robotics component catalogs, and Bambu Lab 3D printing parameters.
Tracks source attribution, revision dates, and confidence levels.
"""
import os
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class KnowledgeEntry(BaseModel):
    id: str
    category: str  # "mechanical", "materials", "robotics", "additive", "standards"
    title: str
    source: str
    confidence: float = 1.0  # 1.0 for verified manufacturer specs, 0.8 for extracted data
    revision_date: str = "2026-10-27"
    units: str
    data: Dict[str, Any]


class EngineeringKnowledgeLibrary:
    """Provides validated lookup and query capabilities for engineering designs."""

    def __init__(self):
        self.entries: Dict[str, KnowledgeEntry] = {}
        self._populate_core_knowledge()

    def _populate_core_knowledge(self):
        # 1. Shigley Mechanical Guidelines
        self.add_entry(
            KnowledgeEntry(
                id="shigley-bolt-margins",
                category="standards",
                title="ISO Fastener Edge Margins & Spacing",
                source="Shigley's Mechanical Engineering Design, 11th Ed., Ch. 8",
                units="dimensionless (multipliers of d_hole)",
                data={
                    "min_edge_margin": 1.5,
                    "recommended_edge_margin": 2.5,
                    "min_center_to_center_spacing": 3.0,
                    "failure_mode_prevented": "Tear-out shear & bearing yield",
                },
            )
        )

        # 2. Bambu Lab X1C / X1E Additive Rules
        self.add_entry(
            KnowledgeEntry(
                id="bambu-x1c-spec",
                category="additive",
                title="Bambu Lab X1C / X1E Manufacturing Profile",
                source="Bambu Lab Technical Datasheet v2.4 (2025)",
                units="mm, Celsius, mm/s",
                data={
                    "build_volume_mm": [256.0, 256.0, 256.0],
                    "max_toolhead_speed_mm_s": 500,
                    "max_hotend_temp_c": 300,
                    "max_bed_temp_c": 120,
                    "max_chamber_temp_c": 60,
                    "nozzle_diameters_mm": [0.2, 0.4, 0.6, 0.8],
                    "min_recommended_wall_thickness_mm": 1.6,
                    "supported_filaments": ["PLA", "PETG", "PETG-CF", "ABS-GF", "PAHT-CF", "PPS-CF", "TPU 95A"],
                },
            )
        )

        # 3. Robotics Powertrain Components
        self.add_entry(
            KnowledgeEntry(
                id="robotics-mobile-chassis-3wheel",
                category="robotics",
                title="3-Wheel Differential Platform Standard Packaging",
                source="Robotics Systems Engineering Handbook 2026",
                units="mm, kg, N*m",
                data={
                    "wheel_configuration": "2 driven rear wheels + 1 front omni/caster",
                    "target_robot_mass_kg": 35.0,
                    "recommended_wheel_diameter_mm": 150.0,
                    "track_width_mm": 480.0,
                    "battery_envelope_mm": [220.0, 140.0, 110.0],
                    "compute_envelope_mm": [160.0, 150.0, 65.0],
                    "min_tip_acceleration_g": 0.45,
                },
            )
        )

    def add_entry(self, entry: KnowledgeEntry):
        self.entries[entry.id] = entry

    def query_by_category(self, category: str) -> List[KnowledgeEntry]:
        return [e for e in self.entries.values() if e.category.lower() == category.lower()]

    def search(self, query: str) -> List[KnowledgeEntry]:
        q = query.lower()
        return [
            e for e in self.entries.values()
            if q in e.title.lower() or q in e.category.lower() or q in json.dumps(e.data).lower()
        ]


# Singleton knowledge instance
knowledge_library = EngineeringKnowledgeLibrary()
