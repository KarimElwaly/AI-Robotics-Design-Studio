"""
Base Windows COM Adapter for Live SOLIDWORKS Instances.
Implements the core COM dispatch logic using win32com.client and pythoncom.
Enforces SI unit conversions (meters, radians, kg) via cad.units.
"""
import os
import sys
import logging
from typing import Dict, Any, List, Optional, Tuple

from cad.adapters.base import (
    BaseSolidWorksAdapter,
    CadOperationResult,
    VersionInfo,
    MassProperties,
    FeatureInfo,
    DimensionInfo,
)
from cad.units import (
    mm_to_m,
    m_to_mm,
    deg_to_rad,
    rad_to_deg,
    g_to_kg,
    kg_to_g,
    m3_to_mm3,
)

logger = logging.getLogger("SolidWorksCOM")


class SolidWorksCOMAdapter(BaseSolidWorksAdapter):
    """Shared COM implementation for SOLIDWORKS 2024 and 2026."""

    EXPECTED_MAJOR = 32  # 32 for 2024, 34 for 2026

    def __init__(self, target_year: int = 2024):
        super().__init__(target_year=target_year)
        self.year = target_year
        self.app = None
        self.model = None
        self._revision = ""
        self._pid = None
        self.checkpoints: List[str] = []

    def connect(self) -> CadOperationResult:
        if sys.platform != "win32":
            return CadOperationResult(
                success=False,
                operation="connect",
                message="SOLIDWORKS COM is only available on native Windows.",
            )

        try:
            import pythoncom
            import win32com.client
            pythoncom.CoInitialize()

            # Attempt to attach to running instance first
            try:
                self.app = win32com.client.GetActiveObject("SldWorks.Application")
                logger.info("Attached to running SldWorks.Application instance.")
            except Exception:
                # If not running, attempt Dispatch
                self.app = win32com.client.Dispatch("SldWorks.Application")
                self.app.Visible = True
                logger.info("Launched and dispatched new SldWorks.Application instance.")

            # Validate version
            self._revision = str(self.app.RevisionNumber())
            major_ver = int(self._revision.split(".")[0]) if "." in self._revision else int(self._revision)

            if major_ver != self.EXPECTED_MAJOR:
                logger.warning(
                    f"Connected SOLIDWORKS version is Major {major_ver} ('{self._revision}'), "
                    f"expected Major {self.EXPECTED_MAJOR} for {self.year}."
                )

            # Prevent blocking COM dialogs where possible (swUserPreferenceToggle_e.swStopDebuggingOnError = 11)
            try:
                self.app.SetUserPreferenceToggle(11, True)
            except Exception:
                pass

            self._connected = True
            self.model = self.app.IActiveDoc2

            return CadOperationResult(
                success=True,
                operation="connect",
                message=f"Connected to SOLIDWORKS {self.year} (Rev {self._revision})",
                data={"revision": self._revision, "major_version": major_ver},
            )

        except Exception as e:
            self._connected = False
            return CadOperationResult(
                success=False,
                operation="connect",
                message=f"Failed to connect to SOLIDWORKS {self.year} COM: {str(e)}",
            )

    def disconnect(self) -> CadOperationResult:
        self.model = None
        self.app = None
        self._connected = False
        try:
            import pythoncom
            pythoncom.CoUninitialize()
        except Exception:
            pass

        return CadOperationResult(
            success=True,
            operation="disconnect",
            message=f"Disconnected from SOLIDWORKS {self.year}",
        )

    def is_connected(self) -> bool:
        if not self._connected or not self.app:
            return False
        try:
            _ = self.app.RevisionNumber()
            return True
        except Exception:
            self._connected = False
            return False

    def get_version_info(self) -> VersionInfo:
        major = self.EXPECTED_MAJOR
        rev = self._revision or f"{major}.0.0"
        return VersionInfo(
            version_name=f"SOLIDWORKS {self.year} (Live COM)",
            year=self.year,
            major_version=major,
            revision=rev,
            process_id=self._pid,
            is_connected=self.is_connected(),
            is_mock=False,
        )

    def new_part(self, template: Optional[str] = None) -> CadOperationResult:
        if not self.is_connected():
            return CadOperationResult(success=False, operation="new_part", message="Not connected to SOLIDWORKS.")
        try:
            default_template = self.app.GetUserPreferenceStringValue(8) or ""
            part_template = template or default_template
            self.model = self.app.INewDocument2(part_template, 0, 0, 0)
            if not self.model:
                self.model = self.app.NewPart()

            doc_title = self.model.GetTitle() if self.model else "Untitled"
            return CadOperationResult(
                success=True,
                operation="new_part",
                message=f"Created new part document '{doc_title}' in SOLIDWORKS {self.year}",
                data={"title": doc_title},
            )
        except Exception as e:
            return CadOperationResult(success=False, operation="new_part", message=f"new_part error: {str(e)}")

    def new_assembly(self, template: Optional[str] = None) -> CadOperationResult:
        if not self.is_connected():
            return CadOperationResult(success=False, operation="new_assembly", message="Not connected to SOLIDWORKS.")
        try:
            default_template = self.app.GetUserPreferenceStringValue(9) or ""
            self.model = self.app.INewDocument2(template or default_template, 0, 0, 0)
            doc_title = self.model.GetTitle() if self.model else "Untitled"
            return CadOperationResult(
                success=True,
                operation="new_assembly",
                message=f"Created new assembly document '{doc_title}' in SOLIDWORKS {self.year}",
                data={"title": doc_title},
            )
        except Exception as e:
            return CadOperationResult(success=False, operation="new_assembly", message=f"new_assembly error: {str(e)}")

    def open_document(self, filepath: str) -> CadOperationResult:
        if not self.is_connected():
            return CadOperationResult(success=False, operation="open_document", message="Not connected to SOLIDWORKS.")
        try:
            errors = 0
            warnings = 0
            ext = os.path.splitext(filepath)[1].lower()
            doc_type = 1 if "sldprt" in ext else (2 if "sldasm" in ext else 3)
            self.model = self.app.OpenDoc6(filepath, doc_type, 1, "", errors, warnings)
            return CadOperationResult(
                success=bool(self.model),
                operation="open_document",
                message=f"Opened document '{filepath}'",
                data={"filepath": filepath},
            )
        except Exception as e:
            return CadOperationResult(success=False, operation="open_document", message=f"open_document error: {str(e)}")

    def save(self, filepath: Optional[str] = None) -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="save", message="No active document.")
        try:
            if filepath:
                return self.save_as(filepath)
            self.model.Save3(1, 0, 0)
            return CadOperationResult(success=True, operation="save", message="Document saved successfully.")
        except Exception as e:
            return CadOperationResult(success=False, operation="save", message=f"Save error: {str(e)}")

    def save_as(self, filepath: str) -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="save_as", message="No active document.")
        try:
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            self.model.Extension.SaveAs(filepath, 0, 1, None, 0, 0)
            return CadOperationResult(
                success=True,
                operation="save_as",
                message=f"Saved document As '{filepath}'",
                data={"filepath": filepath},
            )
        except Exception as e:
            return CadOperationResult(success=False, operation="save_as", message=f"SaveAs error: {str(e)}")

    def save_checkpoint(self, checkpoint_name: Optional[str] = None) -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="save_checkpoint", message="No active document.")
        title = self.model.GetTitle() or "part"
        cp_name = checkpoint_name or f"{title}_checkpoint_{len(self.checkpoints) + 1}"
        cp_path = os.path.abspath(f"d:\\cad\\projects\\checkpoints\\{cp_name}.SLDPRT")
        res = self.save_as(cp_path)
        if res.success:
            self.checkpoints.append(cp_path)
            res.message = f"Saved safety checkpoint to '{cp_path}'"
        return res

    def export_step(self, filepath: str) -> CadOperationResult:
        return self.save_as(filepath)

    def export_stl(self, filepath: str) -> CadOperationResult:
        return self.save_as(filepath)

    def create_sketch(self, plane: str = "Front") -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="create_sketch", message="No active document.")
        try:
            plane_name = f"{plane} Plane" if not plane.endswith("Plane") else plane
            self.model.ClearSelection2(True)
            self.model.Extension.SelectByID2(plane_name, "PLANE", 0, 0, 0, False, 0, None, 0)
            self.model.SketchManager.InsertSketch(True)
            return CadOperationResult(
                success=True,
                operation="create_sketch",
                message=f"Created sketch on plane '{plane_name}'",
                data={"plane": plane_name},
            )
        except Exception as e:
            return CadOperationResult(success=False, operation="create_sketch", message=f"create_sketch error: {str(e)}")

    def exit_sketch(self) -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="exit_sketch", message="No active document.")
        try:
            self.model.SketchManager.InsertSketch(True)
            return CadOperationResult(success=True, operation="exit_sketch", message="Exited active sketch.")
        except Exception as e:
            return CadOperationResult(success=False, operation="exit_sketch", message=f"exit_sketch error: {str(e)}")

    def draw_rectangle(self, x1_mm: float, y1_mm: float, x2_mm: float, y2_mm: float) -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="draw_rectangle", message="No active document.")
        try:
            x1, y1 = mm_to_m(x1_mm), mm_to_m(y1_mm)
            x2, y2 = mm_to_m(x2_mm), mm_to_m(y2_mm)
            self.model.SketchManager.CreateCornerRectangle(x1, y1, 0, x2, y2, 0)
            return CadOperationResult(
                success=True,
                operation="draw_rectangle",
                message=f"Created rectangle from ({x1_mm}, {y1_mm}) to ({x2_mm}, {y2_mm}) mm",
                data={"length_mm": abs(x2_mm - x1_mm), "width_mm": abs(y2_mm - y1_mm)},
            )
        except Exception as e:
            return CadOperationResult(success=False, operation="draw_rectangle", message=f"draw_rectangle error: {str(e)}")

    def draw_circle(self, cx_mm: float, cy_mm: float, radius_mm: float) -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="draw_circle", message="No active document.")
        try:
            cx, cy = mm_to_m(cx_mm), mm_to_m(cy_mm)
            r = mm_to_m(radius_mm)
            self.model.SketchManager.CreateCircleByRadius(cx, cy, 0, r)
            return CadOperationResult(
                success=True,
                operation="draw_circle",
                message=f"Created circle at ({cx_mm}, {cy_mm}) with radius {radius_mm} mm",
                data={"cx_mm": cx_mm, "cy_mm": cy_mm, "radius_mm": radius_mm},
            )
        except Exception as e:
            return CadOperationResult(success=False, operation="draw_circle", message=f"draw_circle error: {str(e)}")

    def draw_line(self, x1_mm: float, y1_mm: float, x2_mm: float, y2_mm: float) -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="draw_line", message="No active document.")
        try:
            x1, y1 = mm_to_m(x1_mm), mm_to_m(y1_mm)
            x2, y2 = mm_to_m(x2_mm), mm_to_m(y2_mm)
            self.model.SketchManager.CreateLine(x1, y1, 0, x2, y2, 0)
            return CadOperationResult(success=True, operation="draw_line", message="Created sketch line.")
        except Exception as e:
            return CadOperationResult(success=False, operation="draw_line", message=f"draw_line error: {str(e)}")

    def draw_arc(self, cx_mm: float, cy_mm: float, start_x_mm: float, start_y_mm: float, end_x_mm: float, end_y_mm: float) -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="draw_arc", message="No active document.")
        try:
            cx, cy = mm_to_m(cx_mm), mm_to_m(cy_mm)
            sx, sy = mm_to_m(start_x_mm), mm_to_m(start_y_mm)
            ex, ey = mm_to_m(end_x_mm), mm_to_m(end_y_mm)
            self.model.SketchManager.CreateArc(cx, cy, 0, sx, sy, 0, ex, ey, 0, 1)
            return CadOperationResult(success=True, operation="draw_arc", message="Created arc.")
        except Exception as e:
            return CadOperationResult(success=False, operation="draw_arc", message=f"draw_arc error: {str(e)}")

    def draw_spline(self, points_mm: List[Tuple[float, float]]) -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="draw_spline", message="No active document.")
        try:
            coords = []
            for p in points_mm:
                coords.extend([mm_to_m(p[0]), mm_to_m(p[1]), 0.0])
            self.model.SketchManager.CreateSpline(coords)
            return CadOperationResult(success=True, operation="draw_spline", message=f"Created spline through {len(points_mm)} points.")
        except Exception as e:
            return CadOperationResult(success=False, operation="draw_spline", message=f"draw_spline error: {str(e)}")

    def extrude_boss(self, depth_mm: float, direction_reverse: bool = False) -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="extrude_boss", message="No active document.")
        try:
            d_m = mm_to_m(depth_mm)
            feat = self.model.FeatureManager.FeatureExtrusion3(
                True, False, direction_reverse, 0, 0, d_m, 0,
                False, False, False, False, 0, 0, False, False, False, False,
                True, True, True, 0, 0, False
            )
            return CadOperationResult(
                success=bool(feat),
                operation="extrude_boss",
                message=f"Extruded boss with depth {depth_mm} mm",
                data={"depth_mm": depth_mm},
            )
        except Exception as e:
            return CadOperationResult(success=False, operation="extrude_boss", message=f"extrude_boss error: {str(e)}")

    def extrude_cut(self, depth_mm: float, direction_reverse: bool = False, through_all: bool = False) -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="extrude_cut", message="No active document.")
        try:
            d_m = mm_to_m(depth_mm)
            end_cond = 1 if through_all else 0
            feat = self.model.FeatureManager.FeatureCut4(
                True, False, direction_reverse, end_cond, 0, d_m, 0,
                False, False, False, False, 0, 0, False, False, False, False,
                False, True, True, True, True, False, 0, 0, False, False
            )
            return CadOperationResult(
                success=bool(feat),
                operation="extrude_cut",
                message=f"Created cut-extrusion with depth {depth_mm} mm",
                data={"depth_mm": depth_mm},
            )
        except Exception as e:
            return CadOperationResult(success=False, operation="extrude_cut", message=f"extrude_cut error: {str(e)}")

    def revolve_boss(self, angle_deg: float = 360.0, direction_reverse: bool = False) -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="revolve_boss", message="No active document.")
        try:
            angle_rad = deg_to_rad(angle_deg)
            feat = self.model.FeatureManager.FeatureRevolve2(
                True, True, False, False, False, False, 0, 0, angle_rad, 0, False, False, 0, 0, 0, 0, 0, True, True, True
            )
            return CadOperationResult(success=bool(feat), operation="revolve_boss", message=f"Created revolve boss ({angle_deg} deg).")
        except Exception as e:
            return CadOperationResult(success=False, operation="revolve_boss", message=f"revolve_boss error: {str(e)}")

    def add_fillet(self, radius_mm: float, edge_names: Optional[List[str]] = None) -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="add_fillet", message="No active document.")
        try:
            r_m = mm_to_m(radius_mm)
            feat = self.model.FeatureManager.FeatureFillet(1, r_m, 0, 0, 0, 0, 0)
            return CadOperationResult(
                success=bool(feat),
                operation="add_fillet",
                message=f"Added fillet with radius {radius_mm} mm",
                data={"radius_mm": radius_mm},
            )
        except Exception as e:
            return CadOperationResult(success=False, operation="add_fillet", message=f"add_fillet error: {str(e)}")

    def add_chamfer(self, distance_mm: float, angle_deg: float = 45.0, edge_names: Optional[List[str]] = None) -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="add_chamfer", message="No active document.")
        try:
            d_m = mm_to_m(distance_mm)
            a_rad = deg_to_rad(angle_deg)
            feat = self.model.FeatureManager.InsertFeatureChamfer(1, 1, d_m, a_rad, 0, 0, 0, 0)
            return CadOperationResult(
                success=bool(feat),
                operation="add_chamfer",
                message=f"Added chamfer ({distance_mm} mm x {angle_deg} deg)",
                data={"distance_mm": distance_mm},
            )
        except Exception as e:
            return CadOperationResult(success=False, operation="add_chamfer", message=f"add_chamfer error: {str(e)}")

    def shell(self, thickness_mm: float, open_faces: Optional[List[int]] = None) -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="shell", message="No active document.")
        try:
            t_m = mm_to_m(thickness_mm)
            feat = self.model.FeatureManager.InsertFeatureShell(t_m, False)
            return CadOperationResult(success=bool(feat), operation="shell", message=f"Shell created (thickness {thickness_mm} mm).")
        except Exception as e:
            return CadOperationResult(success=False, operation="shell", message=f"shell error: {str(e)}")

    def linear_pattern(self, count_x: int, spacing_x_mm: float, count_y: int = 1, spacing_y_mm: float = 0.0) -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="linear_pattern", message="No active document.")
        try:
            sp_x_m = mm_to_m(spacing_x_mm)
            sp_y_m = mm_to_m(spacing_y_mm)
            feat = self.model.FeatureManager.FeatureLinearPattern3(count_x, sp_x_m, count_y, sp_y_m, False, False, "", "", False, False, False, False, False, False, False, False, False)
            return CadOperationResult(success=bool(feat), operation="linear_pattern", message="Linear pattern created.")
        except Exception as e:
            return CadOperationResult(success=False, operation="linear_pattern", message=f"linear_pattern error: {str(e)}")

    def circular_pattern(self, count: int, total_angle_deg: float = 360.0) -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="circular_pattern", message="No active document.")
        try:
            a_rad = deg_to_rad(total_angle_deg)
            feat = self.model.FeatureManager.FeatureCircularPattern4(count, a_rad, False, "", False, True, False, False, False, False, False, False, False)
            return CadOperationResult(success=bool(feat), operation="circular_pattern", message="Circular pattern created.")
        except Exception as e:
            return CadOperationResult(success=False, operation="circular_pattern", message=f"circular_pattern error: {str(e)}")

    def mirror_feature(self, feature_name: str, mirror_plane: str = "Front") -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="mirror_feature", message="No active document.")
        try:
            plane_name = f"{mirror_plane} Plane" if not mirror_plane.endswith("Plane") else mirror_plane
            self.model.Extension.SelectByID2(plane_name, "PLANE", 0, 0, 0, False, 0, None, 0)
            feat = self.model.FeatureManager.InsertMirrorFeature2(True, False, False, False, 0)
            return CadOperationResult(success=bool(feat), operation="mirror_feature", message=f"Mirrored across '{plane_name}'.")
        except Exception as e:
            return CadOperationResult(success=False, operation="mirror_feature", message=f"mirror error: {str(e)}")

    def create_reference_plane(self, offset_mm: float, base_plane: str = "Front") -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="create_reference_plane", message="No active document.")
        try:
            plane_name = f"{base_plane} Plane" if not base_plane.endswith("Plane") else base_plane
            self.model.ClearSelection2(True)
            self.model.Extension.SelectByID2(plane_name, "PLANE", 0, 0, 0, False, 0, None, 0)
            off_m = mm_to_m(offset_mm)
            feat = self.model.FeatureManager.InsertRefPlane(8, off_m, 0, 0, 0, 0)
            return CadOperationResult(success=bool(feat), operation="create_reference_plane", message=f"Created reference plane offset {offset_mm} mm.")
        except Exception as e:
            return CadOperationResult(success=False, operation="create_reference_plane", message=f"create_ref_plane error: {str(e)}")

    def modify_dimension(self, dimension_name: str, value_mm: float) -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="modify_dimension", message="No active document.")
        try:
            val_m = mm_to_m(value_mm)
            param = self.model.Parameter(dimension_name)
            if not param:
                return CadOperationResult(
                    success=False,
                    operation="modify_dimension",
                    message=f"Dimension '{dimension_name}' not found.",
                )
            old_val_m = param.SystemValue
            param.SystemValue = val_m
            self.model.EditRebuild3()
            return CadOperationResult(
                success=True,
                operation="modify_dimension",
                message=f"Updated dimension '{dimension_name}' to {value_mm} mm",
                data={"dimension": dimension_name, "old_mm": m_to_mm(old_val_m), "new_mm": value_mm},
            )
        except Exception as e:
            return CadOperationResult(success=False, operation="modify_dimension", message=f"modify_dimension error: {str(e)}")

    def rebuild(self) -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="rebuild", message="No active document.")
        try:
            success = self.model.EditRebuild3()
            err_count = 0
            try:
                err_count = self.model.Extension.GetRebuildErrorCount()
            except Exception:
                pass

            return CadOperationResult(
                success=bool(success) and err_count == 0,
                operation="rebuild",
                message=f"Model rebuilt with {err_count} errors.",
                rebuild_errors=err_count,
            )
        except Exception as e:
            return CadOperationResult(success=False, operation="rebuild", message=f"rebuild error: {str(e)}")

    def set_material(self, material_name: str, database: str = "SolidWorks Materials") -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="set_material", message="No active document.")
        try:
            self.model.SetMaterialPropertyName2("Default", database, material_name)
            return CadOperationResult(
                success=True,
                operation="set_material",
                message=f"Applied material '{material_name}' from '{database}'",
                data={"material": material_name},
            )
        except Exception as e:
            return CadOperationResult(success=False, operation="set_material", message=f"set_material error: {str(e)}")

    def insert_component(self, part_filepath: str, x_mm: float = 0.0, y_mm: float = 0.0, z_mm: float = 0.0) -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="insert_component", message="No active assembly.")
        try:
            comp = self.model.AddComponent5(part_filepath, 0, "", False, "", mm_to_m(x_mm), mm_to_m(y_mm), mm_to_m(z_mm))
            return CadOperationResult(success=bool(comp), operation="insert_component", message=f"Inserted '{os.path.basename(part_filepath)}'.")
        except Exception as e:
            return CadOperationResult(success=False, operation="insert_component", message=f"insert_component error: {str(e)}")

    def add_mate(self, mate_type: str, comp1_name: str, comp2_name: str, distance_mm: float = 0.0) -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="add_mate", message="No active assembly.")
        try:
            # 0=coincident, 1=concentric, 5=distance
            mate_map = {"coincident": 0, "concentric": 1, "perpendicular": 2, "parallel": 3, "tangent": 4, "distance": 5}
            m_type_int = mate_map.get(mate_type.lower(), 0)
            mate = self.model.AddMate5(m_type_int, 0, False, mm_to_m(distance_mm), 0, 0, 0, 0, 0, 0, 0, False, False, 0, 0)
            return CadOperationResult(success=bool(mate), operation="add_mate", message=f"Added '{mate_type}' mate.")
        except Exception as e:
            return CadOperationResult(success=False, operation="add_mate", message=f"add_mate error: {str(e)}")

    def check_interference(self) -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="check_interference", message="No active assembly.")
        try:
            interf_mgr = self.model.Extension.CreateInterferenceDetectionMgr()
            interf_mgr.TreatCoincidenceAsInterference = False
            interferences = interf_mgr.GetInterferences()
            count = len(interferences) if interferences else 0
            return CadOperationResult(success=True, operation="check_interference", message=f"Interferences found: {count}", data={"count": count})
        except Exception as e:
            return CadOperationResult(success=False, operation="check_interference", message=f"interference check error: {str(e)}")

    def get_mass_properties(self) -> MassProperties:
        if not self.model:
            return MassProperties()
        try:
            mp = self.model.Extension.CreateMassProperty()
            if not mp:
                return MassProperties()

            vol_m3 = mp.Volume
            mass_kg = mp.Mass
            sa_m2 = mp.SurfaceArea
            cg_m = mp.CenterOfMass
            density_kg_m3 = mp.Density

            vol_mm3 = m3_to_mm3(vol_m3)
            mass_g = kg_to_g(mass_kg)
            cg_mm = (m_to_mm(cg_m[0]), m_to_mm(cg_m[1]), m_to_mm(cg_m[2]))

            mat_name = self.model.GetMaterialPropertyName2("Default")[0] or "Unassigned"

            return MassProperties(
                volume_mm3=round(vol_mm3, 2),
                mass_g=round(mass_g, 2),
                density_g_per_mm3=density_kg_m3 * 1e-6,
                surface_area_mm2=round(sa_m2 * 1e6, 2),
                center_of_gravity_mm=(round(cg_mm[0], 2), round(cg_mm[1], 2), round(cg_mm[2], 2)),
                material_name=mat_name,
            )
        except Exception:
            return MassProperties()

    def get_feature_tree(self) -> List[FeatureInfo]:
        if not self.model:
            return []
        features = []
        try:
            feat = self.model.FirstFeature()
            while feat:
                features.append(
                    FeatureInfo(
                        name=feat.Name,
                        type_name=feat.GetTypeName2(),
                        suppressed=feat.IsSuppressed(),
                    )
                )
                feat = feat.GetNextFeature()
        except Exception:
            pass
        return features

    def get_dimensions(self) -> List[DimensionInfo]:
        if not self.model:
            return []
        dims = []
        try:
            feat = self.model.FirstFeature()
            while feat:
                disp_dim = feat.GetFirstDisplayDimension()
                while disp_dim:
                    dim = disp_dim.GetDimension()
                    if dim:
                        dims.append(
                            DimensionInfo(
                                name=dim.Name,
                                value_mm=round(m_to_mm(dim.SystemValue), 4),
                                full_name=dim.FullName,
                            )
                        )
                    disp_dim = feat.GetNextDisplayDimension(disp_dim)
                feat = feat.GetNextFeature()
        except Exception:
            pass
        return dims

    def capture_screenshot(self, output_path: str) -> CadOperationResult:
        if not self.model:
            return CadOperationResult(success=False, operation="capture_screenshot", message="No active document.")
        try:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            self.model.ActiveView.SaveAsBitmap(output_path, 1280, 720)
            return CadOperationResult(
                success=os.path.exists(output_path),
                operation="capture_screenshot",
                message=f"Screenshot saved to '{output_path}'",
                data={"filepath": output_path},
            )
        except Exception as e:
            return CadOperationResult(success=False, operation="capture_screenshot", message=f"capture_screenshot error: {str(e)}")
