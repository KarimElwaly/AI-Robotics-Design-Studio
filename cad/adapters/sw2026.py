"""
SOLIDWORKS 2026 Adapter (Major Version 34).
Provides version-specific COM bindings and validation for SOLIDWORKS 2026.
"""
from cad.adapters.sw_com_base import SolidWorksCOMAdapter


class SolidWorks2026Adapter(SolidWorksCOMAdapter):
    """Specialized adapter for SOLIDWORKS 2026."""

    EXPECTED_MAJOR = 34

    def __init__(self):
        super().__init__(target_year=2026)
