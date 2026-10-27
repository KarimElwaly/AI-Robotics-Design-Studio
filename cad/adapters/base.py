"""
Abstract Base SOLIDWORKS Adapter.
Defines the standard interface for all SOLIDWORKS versions and mock implementations.
All dimensions in public methods use standard engineering units:
- Length: mm
- Angle: degrees
- Mass: grams
- Volume: mm^3
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field


class VersionInfo(BaseModel):
    version_name: str
    year: int
    major_version: int
    revision: str
    process_id: Optional[int] = None
    is_connected: bool = False
    is_mock: bool = False


class MassProperties(BaseModel):
    volume_mm3: float = 0.0
    mass_g: float = 0.0
    density_g_per_mm3: float = 0.0
    surface_area_mm2: float = 0.0
    center_of_gravity_mm: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    material_name: str = "Unassigned"


class FeatureInfo(BaseModel):
    name: str
    type_name: str
    suppressed: bool = False


class DimensionInfo(BaseModel):
    name: str
    value_mm: float
    full_name: str = ""


class CadOperationResult(BaseModel):
    success: bool
    operation: str
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)
    rebuild_errors: int = 0


class BaseSolidWorksAdapter(ABC):
    """Abstract interface for SOLIDWORKS Automation Adapters."""

    def __init__(self, target_year: int = 2024):
        self.target_year = target_year
        self._connected = False
        self._active_doc_title: Optional[str] = None

    @abstractmethod
    def connect(self) -> CadOperationResult:
        """Connect to the SOLIDWORKS instance."""
        pass

    @abstractmethod
    def disconnect(self) -> CadOperationResult:
        """Disconnect and release COM resources."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if currently connected."""
        pass

    @abstractmethod
    def get_version_info(self) -> VersionInfo:
        """Get connected application version information."""
        pass

    # Document management
    @abstractmethod
    def new_part(self, template: Optional[str] = None) -> CadOperationResult:
        """Create a new part document."""
        pass

    @abstractmethod
    def new_assembly(self, template: Optional[str] = None) -> CadOperationResult:
        """Create a new assembly document."""
        pass

    @abstractmethod
    def open_document(self, filepath: str) -> CadOperationResult:
        """Open an existing part or assembly."""
        pass

    @abstractmethod
    def save(self, filepath: Optional[str] = None) -> CadOperationResult:
        """Save the active document."""
        pass

    @abstractmethod
    def save_as(self, filepath: str) -> CadOperationResult:
        """Save As a new file."""
        pass

    @abstractmethod
    def export_step(self, filepath: str) -> CadOperationResult:
        """Export the active document to STEP format."""
        pass

    @abstractmethod
    def export_stl(self, filepath: str) -> CadOperationResult:
        """Export the active document to STL format."""
        pass

    @abstractmethod
    def save_checkpoint(self, checkpoint_name: Optional[str] = None) -> CadOperationResult:
        """Create a safe snapshot checkpoint before modifications."""
        pass

    # Parametric Sketching
    @abstractmethod
    def create_sketch(self, plane: str = "Front") -> CadOperationResult:
        """Create or open a sketch on a plane (Front/Top/Right)."""
        pass

    @abstractmethod
    def exit_sketch(self) -> CadOperationResult:
        """Exit the active sketch."""
        pass

    @abstractmethod
    def draw_rectangle(self, x1_mm: float, y1_mm: float, x2_mm: float, y2_mm: float) -> CadOperationResult:
        """Draw a rectangle from (x1, y1) to (x2, y2) in mm."""
        pass

    @abstractmethod
    def draw_circle(self, cx_mm: float, cy_mm: float, radius_mm: float) -> CadOperationResult:
        """Draw a circle centered at (cx, cy) with radius in mm."""
        pass

    @abstractmethod
    def draw_line(self, x1_mm: float, y1_mm: float, x2_mm: float, y2_mm: float) -> CadOperationResult:
        """Draw a straight line from (x1, y1) to (x2, y2) in mm."""
        pass

    @abstractmethod
    def draw_arc(self, cx_mm: float, cy_mm: float, start_x_mm: float, start_y_mm: float, end_x_mm: float, end_y_mm: float) -> CadOperationResult:
        """Draw an arc by center, start point, and end point in mm."""
        pass

    @abstractmethod
    def draw_spline(self, points_mm: List[Tuple[float, float]]) -> CadOperationResult:
        """Draw a smooth spline through a list of 2D coordinates in mm."""
        pass

    # Solid Modeling Features
    @abstractmethod
    def extrude_boss(self, depth_mm: float, direction_reverse: bool = False) -> CadOperationResult:
        """Extrude the active sketch into a solid boss (depth in mm)."""
        pass

    @abstractmethod
    def extrude_cut(self, depth_mm: float, direction_reverse: bool = False, through_all: bool = False) -> CadOperationResult:
        """Cut-extrude the active sketch (depth in mm)."""
        pass

    @abstractmethod
    def revolve_boss(self, angle_deg: float = 360.0, direction_reverse: bool = False) -> CadOperationResult:
        """Revolve the active sketch around an axis."""
        pass

    @abstractmethod
    def add_fillet(self, radius_mm: float, edge_names: Optional[List[str]] = None) -> CadOperationResult:
        """Add fillets to edges."""
        pass

    @abstractmethod
    def add_chamfer(self, distance_mm: float, angle_deg: float = 45.0, edge_names: Optional[List[str]] = None) -> CadOperationResult:
        """Add chamfers to edges."""
        pass

    @abstractmethod
    def shell(self, thickness_mm: float, open_faces: Optional[List[int]] = None) -> CadOperationResult:
        """Hollow out the solid body with specified wall thickness."""
        pass

    @abstractmethod
    def linear_pattern(self, count_x: int, spacing_x_mm: float, count_y: int = 1, spacing_y_mm: float = 0.0) -> CadOperationResult:
        """Pattern features linearly along X and optionally Y."""
        pass

    @abstractmethod
    def circular_pattern(self, count: int, total_angle_deg: float = 360.0) -> CadOperationResult:
        """Pattern features circularly around an axis."""
        pass

    @abstractmethod
    def mirror_feature(self, feature_name: str, mirror_plane: str = "Front") -> CadOperationResult:
        """Mirror a feature across a reference plane."""
        pass

    @abstractmethod
    def create_reference_plane(self, offset_mm: float, base_plane: str = "Front") -> CadOperationResult:
        """Create an offset reference plane."""
        pass

    # Parametric Modifications
    @abstractmethod
    def modify_dimension(self, dimension_name: str, value_mm: float) -> CadOperationResult:
        """Modify a driving parametric dimension."""
        pass

    @abstractmethod
    def rebuild(self) -> CadOperationResult:
        """Force rebuild of the active document and check for errors."""
        pass

    @abstractmethod
    def set_material(self, material_name: str, database: str = "SolidWorks Materials") -> CadOperationResult:
        """Assign engineering material to the part."""
        pass

    # Assembly Operations
    @abstractmethod
    def insert_component(self, part_filepath: str, x_mm: float = 0.0, y_mm: float = 0.0, z_mm: float = 0.0) -> CadOperationResult:
        """Insert a part component into the active assembly."""
        pass

    @abstractmethod
    def add_mate(self, mate_type: str, comp1_name: str, comp2_name: str, distance_mm: float = 0.0) -> CadOperationResult:
        """Add an assembly mate (coincident, concentric, distance, parallel, perpendicular)."""
        pass

    @abstractmethod
    def check_interference(self) -> CadOperationResult:
        """Check for mechanical interference among assembly components."""
        pass

    # Model Inspection
    @abstractmethod
    def get_mass_properties(self) -> MassProperties:
        """Retrieve volume, mass, CG, and surface area."""
        pass

    @abstractmethod
    def get_feature_tree(self) -> List[FeatureInfo]:
        """List all features in the active document."""
        pass

    @abstractmethod
    def get_dimensions(self) -> List[DimensionInfo]:
        """List active driving dimensions."""
        pass

    @abstractmethod
    def capture_screenshot(self, output_path: str) -> CadOperationResult:
        """Capture screenshot of the model viewport."""
        pass
