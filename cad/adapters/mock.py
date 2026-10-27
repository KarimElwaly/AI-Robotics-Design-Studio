"""
Mock SOLIDWORKS Adapter.
Provides a realistic, in-memory CAD simulation for headless CI/CD, offline development,
and automated testing when live SOLIDWORKS instances are not present.
Tracks parametric features, recalculates mass properties, and creates real export files.
"""
import os
import math
import shutil
from typing import Dict, Any, List, Optional, Tuple
from cad.adapters.base import (
    BaseSolidWorksAdapter,
    CadOperationResult,
    VersionInfo,
    MassProperties,
    FeatureInfo,
    DimensionInfo,
)


class MockSolidWorksAdapter(BaseSolidWorksAdapter):
    """In-memory simulated CAD engine conforming to BaseSolidWorksAdapter."""

    def __init__(self, target_year: int = 2024):
        super().__init__(target_year=target_year)
        self.year = target_year
        self._connected = True
        self.active_doc: Optional[str] = None
        self.doc_type: str = "Part"
        self.features: List[FeatureInfo] = []
        self.dimensions: Dict[str, float] = {}
        self.material: str = "6061-T6 Aluminum"
        self.density_g_per_mm3: float = 0.0027  # Al 6061 ~2.7 g/cm3
        self.active_sketch: Optional[str] = None
        self.sketch_entities: List[Dict[str, Any]] = []
        self.rebuild_errors_count: int = 0
        self.bounding_box: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # L, W, H mm
        self.assembly_components: List[Dict[str, Any]] = []
        self.assembly_mates: List[Dict[str, Any]] = []
        self.checkpoints: List[str] = []

    def connect(self) -> CadOperationResult:
        self._connected = True
        return CadOperationResult(
            success=True,
            operation="connect",
            message=f"Connected to Mock SOLIDWORKS {self.year} Engine",
            data={"year": self.year, "mock": True},
        )

    def disconnect(self) -> CadOperationResult:
        self._connected = False
        return CadOperationResult(
            success=True,
            operation="disconnect",
            message="Disconnected from Mock SOLIDWORKS Engine",
        )

    def is_connected(self) -> bool:
        return self._connected

    def get_version_info(self) -> VersionInfo:
        major = 32 if self.year == 2024 else 34
        return VersionInfo(
            version_name=f"SOLIDWORKS {self.year} SP0 (Simulated)",
            year=self.year,
            major_version=major,
            revision=f"{major}.0.0",
            process_id=9999,
            is_connected=self._connected,
            is_mock=True,
        )

    def new_part(self, template: Optional[str] = None) -> CadOperationResult:
        self.active_doc = f"Part_{self.year}_1"
        self.doc_type = "Part"
        self.features = [
            FeatureInfo(name="Front Plane", type_name="RefPlane"),
            FeatureInfo(name="Top Plane", type_name="RefPlane"),
            FeatureInfo(name="Right Plane", type_name="RefPlane"),
            FeatureInfo(name="Origin", type_name="OriginProfileFeature"),
        ]
        self.dimensions.clear()
        self.sketch_entities.clear()
        self.bounding_box = (0.0, 0.0, 0.0)
        return CadOperationResult(
            success=True,
            operation="new_part",
            message=f"Created new simulated part document '{self.active_doc}'",
            data={"document_name": self.active_doc},
        )

    def new_assembly(self, template: Optional[str] = None) -> CadOperationResult:
        self.active_doc = f"Assem_{self.year}_1"
        self.doc_type = "Assembly"
        self.features = [
            FeatureInfo(name="Front Plane", type_name="RefPlane"),
            FeatureInfo(name="Top Plane", type_name="RefPlane"),
            FeatureInfo(name="Right Plane", type_name="RefPlane"),
            FeatureInfo(name="Origin", type_name="OriginProfileFeature"),
        ]
        self.assembly_components.clear()
        self.assembly_mates.clear()
        return CadOperationResult(
            success=True,
            operation="new_assembly",
            message=f"Created new simulated assembly document '{self.active_doc}'",
            data={"document_name": self.active_doc},
        )

    def open_document(self, filepath: str) -> CadOperationResult:
        self.active_doc = os.path.basename(filepath)
        return CadOperationResult(
            success=True,
            operation="open_document",
            message=f"Opened simulated document '{self.active_doc}'",
            data={"filepath": filepath},
        )

    def save(self, filepath: Optional[str] = None) -> CadOperationResult:
        target = filepath or f"d:\\cad\\projects\\{self.active_doc}.SLDPRT"
        os.makedirs(os.path.dirname(os.path.abspath(target)), exist_ok=True)
        with open(target, "wb") as f:
            f.write(b"SOLIDWORKS MOCK BINARY MODEL DATA\n")
            f.write(f"Doc: {self.active_doc}\nVersion: {self.year}\n".encode())
        return CadOperationResult(
            success=True,
            operation="save",
            message=f"Saved model to '{target}'",
            data={"filepath": target, "size_bytes": os.path.getsize(target)},
        )

    def save_as(self, filepath: str) -> CadOperationResult:
        return self.save(filepath=filepath)

    def save_checkpoint(self, checkpoint_name: Optional[str] = None) -> CadOperationResult:
        cp_name = checkpoint_name or f"{self.active_doc}_cp{len(self.checkpoints) + 1}"
        cp_path = f"d:\\cad\\projects\\checkpoints\\{cp_name}.SLDPRT"
        os.makedirs(os.path.dirname(os.path.abspath(cp_path)), exist_ok=True)
        self.save(cp_path)
        self.checkpoints.append(cp_path)
        return CadOperationResult(
            success=True,
            operation="save_checkpoint",
            message=f"Created safety checkpoint at '{cp_path}'",
            data={"checkpoint_path": cp_path},
        )

    def export_step(self, filepath: str) -> CadOperationResult:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        step_content = f"""ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('SOLIDWORKS Mock AP214 STEP Export'),'2;1');
FILE_NAME('{os.path.basename(filepath)}','2026-10-27T00:00:00',('AI Robotics Design Studio'),('AI Lab'),'SOLIDWORKS Mock Adapter','SOLIDWORKS','');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));
ENDSEC;
DATA;
#1=APPLICATION_CONTEXT('core data for automotive mechanical design processes');
#2=APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,#1);
#3=PRODUCT('{self.active_doc}','{self.active_doc}','Part Model',(#1));
ENDSEC;
END-ISO-10303-21;
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(step_content)

        return CadOperationResult(
            success=True,
            operation="export_step",
            message=f"Exported STEP model to '{filepath}'",
            data={"filepath": filepath, "size_bytes": os.path.getsize(filepath)},
        )

    def export_stl(self, filepath: str) -> CadOperationResult:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        stl_content = f"""solid {self.active_doc}
  facet normal 0.0 0.0 1.0
    outer loop
      vertex 0.0 0.0 0.0
      vertex 100.0 0.0 0.0
      vertex 100.0 60.0 0.0
    endloop
  endfacet
  facet normal 0.0 0.0 1.0
    outer loop
      vertex 0.0 0.0 0.0
      vertex 100.0 60.0 0.0
      vertex 0.0 60.0 0.0
    endloop
  endfacet
endsolid {self.active_doc}
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(stl_content)

        return CadOperationResult(
            success=True,
            operation="export_stl",
            message=f"Exported STL model to '{filepath}'",
            data={"filepath": filepath, "size_bytes": os.path.getsize(filepath)},
        )

    def create_sketch(self, plane: str = "Front") -> CadOperationResult:
        sketch_name = f"Sketch{len(self.features) + 1}"
        self.active_sketch = sketch_name
        self.features.append(FeatureInfo(name=sketch_name, type_name="ProfileFeature"))
        return CadOperationResult(
            success=True,
            operation="create_sketch",
            message=f"Opened sketch '{sketch_name}' on '{plane}' plane",
            data={"sketch_name": sketch_name, "plane": plane},
        )

    def exit_sketch(self) -> CadOperationResult:
        sketch = self.active_sketch
        self.active_sketch = None
        return CadOperationResult(
            success=True,
            operation="exit_sketch",
            message=f"Closed sketch '{sketch}'",
        )

    def draw_rectangle(self, x1_mm: float, y1_mm: float, x2_mm: float, y2_mm: float) -> CadOperationResult:
        length = abs(x2_mm - x1_mm)
        width = abs(y2_mm - y1_mm)
        self.sketch_entities.append({"type": "rectangle", "x1": x1_mm, "y1": y1_mm, "x2": x2_mm, "y2": y2_mm})
        self.dimensions["D1@Sketch1"] = length
        self.dimensions["D2@Sketch1"] = width
        self.bounding_box = (length, width, self.bounding_box[2])
        return CadOperationResult(
            success=True,
            operation="draw_rectangle",
            message=f"Created rectangle ({length} mm x {width} mm)",
            data={"length_mm": length, "width_mm": width},
        )

    def draw_circle(self, cx_mm: float, cy_mm: float, radius_mm: float) -> CadOperationResult:
        diameter = radius_mm * 2.0
        hole_idx = len([e for e in self.sketch_entities if e.get("type") == "circle"]) + 1
        self.sketch_entities.append({"type": "circle", "cx": cx_mm, "cy": cy_mm, "radius": radius_mm})
        self.dimensions[f"D{hole_idx + 2}@Sketch1"] = diameter
        return CadOperationResult(
            success=True,
            operation="draw_circle",
            message=f"Created circle at ({cx_mm}, {cy_mm}) with dia {diameter} mm",
            data={"cx_mm": cx_mm, "cy_mm": cy_mm, "diameter_mm": diameter},
        )

    def draw_line(self, x1_mm: float, y1_mm: float, x2_mm: float, y2_mm: float) -> CadOperationResult:
        self.sketch_entities.append({"type": "line", "x1": x1_mm, "y1": y1_mm, "x2": x2_mm, "y2": y2_mm})
        return CadOperationResult(
            success=True,
            operation="draw_line",
            message=f"Created line from ({x1_mm}, {y1_mm}) to ({x2_mm}, {y2_mm})",
        )

    def draw_arc(self, cx_mm: float, cy_mm: float, start_x_mm: float, start_y_mm: float, end_x_mm: float, end_y_mm: float) -> CadOperationResult:
        r = math.sqrt((start_x_mm - cx_mm) ** 2 + (start_y_mm - cy_mm) ** 2)
        self.sketch_entities.append({"type": "arc", "cx": cx_mm, "cy": cy_mm, "radius": r, "start": (start_x_mm, start_y_mm), "end": (end_x_mm, end_y_mm)})
        return CadOperationResult(
            success=True,
            operation="draw_arc",
            message=f"Created arc centered at ({cx_mm}, {cy_mm}) radius {r:.2f} mm",
            data={"radius_mm": r},
        )

    def draw_spline(self, points_mm: List[Tuple[float, float]]) -> CadOperationResult:
        self.sketch_entities.append({"type": "spline", "points": points_mm})
        return CadOperationResult(
            success=True,
            operation="draw_spline",
            message=f"Created smooth spline with {len(points_mm)} interpolation points",
            data={"points_count": len(points_mm)},
        )

    def extrude_boss(self, depth_mm: float, direction_reverse: bool = False) -> CadOperationResult:
        feat_name = f"Boss-Extrude{len(self.features) + 1}"
        self.features.append(FeatureInfo(name=feat_name, type_name="Extrusion"))
        self.dimensions["D1@Boss-Extrude1"] = depth_mm
        self.bounding_box = (self.bounding_box[0], self.bounding_box[1], depth_mm)
        return CadOperationResult(
            success=True,
            operation="extrude_boss",
            message=f"Created extruded boss '{feat_name}' with depth {depth_mm} mm",
            data={"feature_name": feat_name, "depth_mm": depth_mm},
        )

    def extrude_cut(self, depth_mm: float, direction_reverse: bool = False, through_all: bool = False) -> CadOperationResult:
        feat_name = f"Cut-Extrude{len(self.features) + 1}"
        self.features.append(FeatureInfo(name=feat_name, type_name="CutExtrusion"))
        return CadOperationResult(
            success=True,
            operation="extrude_cut",
            message=f"Created cut-extrude '{feat_name}' (depth {depth_mm} mm, through_all={through_all})",
            data={"feature_name": feat_name, "depth_mm": depth_mm},
        )

    def revolve_boss(self, angle_deg: float = 360.0, direction_reverse: bool = False) -> CadOperationResult:
        feat_name = f"Revolve{len(self.features) + 1}"
        self.features.append(FeatureInfo(name=feat_name, type_name="Revolve"))
        return CadOperationResult(
            success=True,
            operation="revolve_boss",
            message=f"Created revolve boss '{feat_name}' ({angle_deg} deg)",
            data={"feature_name": feat_name, "angle_deg": angle_deg},
        )

    def add_fillet(self, radius_mm: float, edge_names: Optional[List[str]] = None) -> CadOperationResult:
        feat_name = f"Fillet{len(self.features) + 1}"
        self.features.append(FeatureInfo(name=feat_name, type_name="Fillet"))
        self.dimensions[f"D1@{feat_name}"] = radius_mm
        return CadOperationResult(
            success=True,
            operation="add_fillet",
            message=f"Created fillet '{feat_name}' with radius {radius_mm} mm",
            data={"feature_name": feat_name, "radius_mm": radius_mm},
        )

    def add_chamfer(self, distance_mm: float, angle_deg: float = 45.0, edge_names: Optional[List[str]] = None) -> CadOperationResult:
        feat_name = f"Chamfer{len(self.features) + 1}"
        self.features.append(FeatureInfo(name=feat_name, type_name="Chamfer"))
        return CadOperationResult(
            success=True,
            operation="add_chamfer",
            message=f"Created chamfer '{feat_name}' ({distance_mm} mm x {angle_deg} deg)",
            data={"feature_name": feat_name, "distance_mm": distance_mm},
        )

    def shell(self, thickness_mm: float, open_faces: Optional[List[int]] = None) -> CadOperationResult:
        feat_name = f"Shell{len(self.features) + 1}"
        self.features.append(FeatureInfo(name=feat_name, type_name="Shell"))
        return CadOperationResult(
            success=True,
            operation="shell",
            message=f"Hollowed shell with wall thickness {thickness_mm} mm",
            data={"thickness_mm": thickness_mm},
        )

    def linear_pattern(self, count_x: int, spacing_x_mm: float, count_y: int = 1, spacing_y_mm: float = 0.0) -> CadOperationResult:
        feat_name = f"LPattern{len(self.features) + 1}"
        self.features.append(FeatureInfo(name=feat_name, type_name="LinearPattern"))
        return CadOperationResult(
            success=True,
            operation="linear_pattern",
            message=f"Linear pattern created: {count_x} instances spaced {spacing_x_mm} mm",
            data={"count_x": count_x, "spacing_x_mm": spacing_x_mm},
        )

    def circular_pattern(self, count: int, total_angle_deg: float = 360.0) -> CadOperationResult:
        feat_name = f"CirPattern{len(self.features) + 1}"
        self.features.append(FeatureInfo(name=feat_name, type_name="CircularPattern"))
        return CadOperationResult(
            success=True,
            operation="circular_pattern",
            message=f"Circular pattern created: {count} instances over {total_angle_deg} deg",
            data={"count": count, "angle_deg": total_angle_deg},
        )

    def mirror_feature(self, feature_name: str, mirror_plane: str = "Front") -> CadOperationResult:
        feat_name = f"Mirror{len(self.features) + 1}"
        self.features.append(FeatureInfo(name=feat_name, type_name="Mirror"))
        return CadOperationResult(
            success=True,
            operation="mirror_feature",
            message=f"Mirrored '{feature_name}' across '{mirror_plane}' plane",
            data={"mirrored_feature": feature_name, "plane": mirror_plane},
        )

    def create_reference_plane(self, offset_mm: float, base_plane: str = "Front") -> CadOperationResult:
        plane_name = f"Plane{len(self.features) + 1}"
        self.features.append(FeatureInfo(name=plane_name, type_name="RefPlane"))
        return CadOperationResult(
            success=True,
            operation="create_reference_plane",
            message=f"Created reference plane '{plane_name}' offset {offset_mm} mm from '{base_plane}'",
            data={"plane_name": plane_name, "offset_mm": offset_mm},
        )

    def modify_dimension(self, dimension_name: str, value_mm: float) -> CadOperationResult:
        matched_key = None
        for k in self.dimensions:
            if k.lower() == dimension_name.lower() or dimension_name.lower() in k.lower():
                matched_key = k
                break

        if not matched_key:
            matched_key = dimension_name

        old_val = self.dimensions.get(matched_key, 0.0)
        self.dimensions[matched_key] = value_mm

        if "D1@Sketch" in matched_key or "length" in matched_key.lower():
            self.bounding_box = (value_mm, self.bounding_box[1], self.bounding_box[2])
        elif "D2@Sketch" in matched_key or "width" in matched_key.lower():
            self.bounding_box = (self.bounding_box[0], value_mm, self.bounding_box[2])
        elif "Boss-Extrude" in matched_key or "thickness" in matched_key.lower():
            self.bounding_box = (self.bounding_box[0], self.bounding_box[1], value_mm)

        return CadOperationResult(
            success=True,
            operation="modify_dimension",
            message=f"Modified dimension '{matched_key}' from {old_val} mm to {value_mm} mm",
            data={"dimension": matched_key, "previous_value_mm": old_val, "new_value_mm": value_mm},
        )

    def rebuild(self) -> CadOperationResult:
        self.rebuild_errors_count = 0
        return CadOperationResult(
            success=True,
            operation="rebuild",
            message="Rebuilt model successfully with 0 errors",
            rebuild_errors=0,
            data={"features_count": len(self.features)},
        )

    def set_material(self, material_name: str, database: str = "SolidWorks Materials") -> CadOperationResult:
        self.material = material_name
        density_map = {
            "6061-t6 aluminum": 0.0027,
            "aluminum": 0.0027,
            "1018 steel": 0.00787,
            "steel": 0.00785,
            "brass": 0.0085,
            "pla": 0.00124,
            "petg": 0.00127,
            "abs": 0.00104,
            "paht-cf": 0.00121,
            "tpu": 0.00120,
        }
        for k, v in density_map.items():
            if k in material_name.lower():
                self.density_g_per_mm3 = v
                break
        return CadOperationResult(
            success=True,
            operation="set_material",
            message=f"Applied material '{material_name}' (density: {self.density_g_per_mm3} g/mm3)",
            data={"material": material_name, "density_g_per_mm3": self.density_g_per_mm3},
        )

    def insert_component(self, part_filepath: str, x_mm: float = 0.0, y_mm: float = 0.0, z_mm: float = 0.0) -> CadOperationResult:
        comp_name = os.path.basename(part_filepath)
        self.assembly_components.append({"file": part_filepath, "name": comp_name, "pos": (x_mm, y_mm, z_mm)})
        return CadOperationResult(
            success=True,
            operation="insert_component",
            message=f"Inserted component '{comp_name}' at ({x_mm}, {y_mm}, {z_mm}) mm",
            data={"component": comp_name, "position_mm": (x_mm, y_mm, z_mm)},
        )

    def add_mate(self, mate_type: str, comp1_name: str, comp2_name: str, distance_mm: float = 0.0) -> CadOperationResult:
        mate_id = f"Mate_{len(self.assembly_mates) + 1}_{mate_type}"
        self.assembly_mates.append({"id": mate_id, "type": mate_type, "comp1": comp1_name, "comp2": comp2_name, "distance_mm": distance_mm})
        return CadOperationResult(
            success=True,
            operation="add_mate",
            message=f"Added '{mate_type}' mate between '{comp1_name}' and '{comp2_name}'",
            data={"mate_id": mate_id, "type": mate_type},
        )

    def check_interference(self) -> CadOperationResult:
        return CadOperationResult(
            success=True,
            operation="check_interference",
            message="Interference detection complete: 0 collisions detected.",
            data={"interferences_count": 0, "status": "CLEAR"},
        )

    def get_mass_properties(self) -> MassProperties:
        l, w, h = self.bounding_box
        gross_vol = l * w * h if (l > 0 and w > 0 and h > 0) else 60000.0
        circle_holes = [e for e in self.sketch_entities if e.get("type") == "circle"]
        hole_vol = sum(math.pi * (e["radius"] ** 2) * h for e in circle_holes)
        net_vol = max(gross_vol - hole_vol, 100.0)
        mass_g = net_vol * self.density_g_per_mm3
        surface_area = 2 * (l * w + l * h + w * h)

        return MassProperties(
            volume_mm3=round(net_vol, 2),
            mass_g=round(mass_g, 2),
            density_g_per_mm3=self.density_g_per_mm3,
            surface_area_mm2=round(surface_area, 2),
            center_of_gravity_mm=(round(l / 2.0, 2), round(w / 2.0, 2), round(h / 2.0, 2)),
            material_name=self.material,
        )

    def get_feature_tree(self) -> List[FeatureInfo]:
        return list(self.features)

    def get_dimensions(self) -> List[DimensionInfo]:
        return [
            DimensionInfo(name=k, value_mm=v, full_name=k)
            for k, v in self.dimensions.items()
        ]

    def capture_screenshot(self, output_path: str) -> CadOperationResult:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        try:
            from PIL import Image, ImageDraw
            img = Image.new("RGB", (800, 600), color=(15, 23, 42))  # Slate 900
            draw = ImageDraw.Draw(img)
            l, w, h = self.bounding_box
            draw.rectangle([150, 150, 650, 450], outline=(0, 229, 255), width=3)
            draw.ellipse([180, 180, 220, 220], outline=(0, 229, 255), width=2)
            draw.ellipse([580, 180, 620, 220], outline=(0, 229, 255), width=2)
            draw.ellipse([180, 380, 220, 420], outline=(0, 229, 255), width=2)
            draw.ellipse([580, 380, 620, 420], outline=(0, 229, 255), width=2)
            draw.text((30, 30), f"AI ROBOTICS DESIGN STUDIO - CAD VIEWPORT ({self.year})", fill=(0, 229, 255))
            draw.text((30, 55), f"Model: {self.active_doc} | Material: {self.material}", fill=(203, 213, 225))
            draw.text((30, 75), f"Dimensions: {l:.1f} mm x {w:.1f} mm x {h:.1f} mm", fill=(203, 213, 225))
            draw.text((30, 550), "STATUS: REBUILD SUCCESSFUL [0 ERRORS]", fill=(74, 222, 128))
            img.save(output_path)
        except Exception:
            with open(output_path, "wb") as f:
                f.write(b"MOCK CAD SCREENSHOT IMAGE DATA")

        return CadOperationResult(
            success=True,
            operation="capture_screenshot",
            message=f"Captured screenshot to '{output_path}'",
            data={"filepath": output_path},
        )
