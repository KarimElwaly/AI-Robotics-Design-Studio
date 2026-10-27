"""
SOLIDWORKS 2024 Adapter (Major Version 32).
Provides version-specific COM bindings and validation for SOLIDWORKS 2024.
"""
from cad.adapters.sw_com_base import SolidWorksCOMAdapter


class SolidWorks2024Adapter(SolidWorksCOMAdapter):
    """Specialized adapter for SOLIDWORKS 2024."""

    EXPECTED_MAJOR = 32

    def __init__(self):
        super().__init__(target_year=2024)
