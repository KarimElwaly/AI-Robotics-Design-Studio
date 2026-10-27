"""
SOLIDWORKS Version & Connection Manager.
Detects installed SOLIDWORKS versions via Windows Registry and process table,
manages active connections (2024, 2026, Auto-Detect, Mock),
and dispatches requests to the appropriate adapter.
"""
import os
import sys
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from cad.adapters.base import BaseSolidWorksAdapter, VersionInfo, CadOperationResult
from cad.adapters.mock import MockSolidWorksAdapter
from cad.adapters.sw2024 import SolidWorks2024Adapter
from cad.adapters.sw2026 import SolidWorks2026Adapter

logger = logging.getLogger("ConnectionManager")


class DetectedInstallation(BaseModel):
    year: int
    major_version: int
    install_path: Optional[str] = None
    executable_path: Optional[str] = None
    is_running: bool = False
    process_id: Optional[int] = None
    sp_info: Optional[str] = None


class ConnectionStatus(BaseModel):
    connected: bool
    mode: str  # "auto", "2024", "2026", "mock"
    active_version: Optional[VersionInfo] = None
    detected_installations: List[DetectedInstallation] = []
    active_document: Optional[str] = None
    message: str = "Ready"


class SolidWorksConnectionManager:
    """Manages SOLIDWORKS detection and versioned adapter lifecycle."""

    def __init__(self):
        self._current_adapter: Optional[BaseSolidWorksAdapter] = None
        self._current_mode: str = "mock"
        self._installations: List[DetectedInstallation] = []
        self.refresh_installations()
        # Default initialize to Mock adapter so system works immediately
        self.set_mode("mock")

    def refresh_installations(self) -> List[DetectedInstallation]:
        """Inspect Windows Registry and running processes for SOLIDWORKS."""
        detected = []

        if sys.platform == "win32":
            # 1. Registry Inspection
            try:
                import winreg
                registry_checks = [
                    (2024, 32, r"SOFTWARE\SolidWorks\SOLIDWORKS 2024\Setup"),
                    (2026, 34, r"SOFTWARE\SolidWorks\SOLIDWORKS 2026\Setup"),
                    (2025, 33, r"SOFTWARE\SolidWorks\SOLIDWORKS 2025\Setup"),
                ]
                for year, major, subkey in registry_checks:
                    for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
                        try:
                            with winreg.OpenKey(root, subkey) as key:
                                folder, _ = winreg.QueryValueEx(key, "SolidWorks Folder")
                                exe = os.path.join(folder, "SLDWORKS.exe")
                                detected.append(
                                    DetectedInstallation(
                                        year=year,
                                        major_version=major,
                                        install_path=folder,
                                        executable_path=exe if os.path.exists(exe) else None,
                                        is_running=False,
                                    )
                                )
                                break
                        except OSError:
                            continue
            except Exception as e:
                logger.debug(f"Registry inspection error: {e}")

            # 2. Process inspection via psutil or tasklist
            try:
                import psutil
                for proc in psutil.process_iter(["pid", "name", "exe"]):
                    name = proc.info.get("name") or ""
                    if "sldworks.exe" in name.lower():
                        pid = proc.info.get("pid")
                        exe_path = proc.info.get("exe") or ""
                        # Determine year from path
                        year = 2024 if "2024" in exe_path else (2026 if "2026" in exe_path else 2024)
                        major = 32 if year == 2024 else 34

                        # Update or add to detected list
                        matched = False
                        for inst in detected:
                            if inst.year == year:
                                inst.is_running = True
                                inst.process_id = pid
                                matched = True
                                break
                        if not matched:
                            detected.append(
                                DetectedInstallation(
                                    year=year,
                                    major_version=major,
                                    executable_path=exe_path,
                                    is_running=True,
                                    process_id=pid,
                                )
                            )
            except Exception as e:
                logger.debug(f"Process inspection error: {e}")

        self._installations = detected
        return self._installations

    def set_mode(self, mode: str) -> CadOperationResult:
        """Switch adapter mode: 'auto', '2024', '2026', 'mock'."""
        mode_lower = mode.lower()
        if self._current_adapter:
            try:
                self._current_adapter.disconnect()
            except Exception:
                pass

        self._current_mode = mode_lower

        if mode_lower == "mock":
            self._current_adapter = MockSolidWorksAdapter(target_year=2024)
            res = self._current_adapter.connect()
            return CadOperationResult(
                success=True,
                operation="set_mode",
                message="Activated Mock SOLIDWORKS Engine (Simulated Mode)",
                data={"mode": "mock"},
            )

        elif mode_lower == "2024":
            if sys.platform != "win32":
                return CadOperationResult(
                    success=False,
                    operation="set_mode",
                    message="Live SOLIDWORKS 2024 requires Windows host. Falling back to Mock.",
                )
            self._current_adapter = SolidWorks2024Adapter()
            res = self._current_adapter.connect()
            if not res.success:
                # Fallback to mock with warning
                logger.warning(f"Could not connect to live SW 2024: {res.message}. Using mock.")
                self._current_adapter = MockSolidWorksAdapter(target_year=2024)
                self._current_adapter.connect()
                return CadOperationResult(
                    success=True,
                    operation="set_mode",
                    message=f"Live SW 2024 unavailable ({res.message}). Active adapter: Mock SW 2024.",
                    data={"fallback": True, "mode": "mock_2024"},
                )
            return res

        elif mode_lower == "2026":
            if sys.platform != "win32":
                return CadOperationResult(
                    success=False,
                    operation="set_mode",
                    message="Live SOLIDWORKS 2026 requires Windows host. Falling back to Mock.",
                )
            self._current_adapter = SolidWorks2026Adapter()
            res = self._current_adapter.connect()
            if not res.success:
                logger.warning(f"Could not connect to live SW 2026: {res.message}. Using mock.")
                self._current_adapter = MockSolidWorksAdapter(target_year=2026)
                self._current_adapter.connect()
                return CadOperationResult(
                    success=True,
                    operation="set_mode",
                    message=f"Live SW 2026 unavailable ({res.message}). Active adapter: Mock SW 2026.",
                    data={"fallback": True, "mode": "mock_2026"},
                )
            return res

        elif mode_lower == "auto":
            self.refresh_installations()
            # Prioritize running instances
            running_2026 = any(i.is_running and i.year == 2026 for i in self._installations)
            running_2024 = any(i.is_running and i.year == 2024 for i in self._installations)

            if running_2026:
                return self.set_mode("2026")
            elif running_2024:
                return self.set_mode("2024")
            elif any(i.year == 2026 for i in self._installations):
                return self.set_mode("2026")
            elif any(i.year == 2024 for i in self._installations):
                return self.set_mode("2024")
            else:
                return self.set_mode("mock")

        return CadOperationResult(
            success=False,
            operation="set_mode",
            message=f"Unknown connection mode '{mode}'. Choose from: auto, 2024, 2026, mock.",
        )

    def get_adapter(self) -> BaseSolidWorksAdapter:
        """Get the currently active CAD adapter."""
        if not self._current_adapter:
            self.set_mode("mock")
        return self._current_adapter

    def get_status(self) -> ConnectionStatus:
        """Return the comprehensive connection status."""
        adapter = self.get_adapter()
        vinfo = adapter.get_version_info()
        doc_title = getattr(adapter, "active_doc", None)
        if hasattr(adapter, "model") and adapter.model:
            try:
                doc_title = adapter.model.GetTitle()
            except Exception:
                pass

        return ConnectionStatus(
            connected=adapter.is_connected(),
            mode=self._current_mode,
            active_version=vinfo,
            detected_installations=self._installations,
            active_document=doc_title,
            message=f"Active: {vinfo.version_name}",
        )


# Singleton instance
connection_manager = SolidWorksConnectionManager()
