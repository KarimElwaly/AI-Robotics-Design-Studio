# SOLIDWORKS CAD Integration Comparison & Architecture Selection

> **Document ID:** DOC-CAD-001  
> **Status:** Approved Foundation Selection  
> **Target Environments:** SOLIDWORKS 2024 (Major 32) & SOLIDWORKS 2026 (Major 34) on Windows 10/11 x64  
> **Application:** AI Robotics Design Studio  

---

## 1. Executive Summary

To establish the CAD automation core of **AI Robotics Design Studio**, we evaluated five leading open-source SOLIDWORKS automation repositories against thirteen critical engineering criteria.

Our analysis concludes that **HarrierPigeon/Solidworks-MCP-Server** provides the most elegant, robust, and feature-complete foundation for natural-language CAD generation, geometric feedback, and assembly mating. We will synthesize HarrierPigeon's high-level tooling design and parameter semantics with the deep versioning and multi-year lifecycle mechanisms (`--year 2026`) pioneered by **andrewbartels1/SolidworksMCP-python**, alongside the unit conversion and registry discovery patterns from **alisamsam/solidworks-mcp**, referencing **kilwizac/solidworks-api-mcp** for complete API dispatch specifications.

---

## 2. Technical Evaluation Matrix

| Criteria | 1. HarrierPigeon | 2. Andrew Bartels | 3. Eyfel (SolidPilot) | 4. Ali SamSam | 5. Kilwizac |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Primary Language** | Python 3.10+ | Python 3.13+ | C# (.NET 4.8) + Python | Python 3.10+ | TypeScript (Bun) |
| **COM Integration** | `win32com.client` STA | `win32com` + VBA wrappers | C# Interop.SldWorks | `win32com.client` | None (Doc Lookup Only) |
| **SW 2024 Support** | Verified (2022-2025) | Supported | Supported | Verified (2023-2025) | Documentation only |
| **SW 2026 Support** | Compatible | **Explicit (`--year 2026`)** | **Target: 2026 SP3** | Compatible via COM | Documentation only |
| **Number of Tools** | ~35 high-level tools | **151 comprehensive** | 47 low-level + IR | 22 basic tools | Search & lookup only |
| **Sketching Capability** | Chained profiles, dims | Extensive | Entity by entity | Basic lines/circles | N/A |
| **Assembly & Mates** | Coincident, concentric, gears | Full mating | Index-based mates | Basic insertion | N/A |
| **Geometry Inspection** | Face/edge coords, mass, look_at | Mass, bounding box | Topology fingerprints | Feature list only | N/A |
| **Feedback / Vision** | Screenshots with labels | Screenshots | Model analysis | None | N/A |
| **Unit System** | Automatic mm / deg $\rightarrow$ SI | Configurable | Strict SI (meters) | Multi-unit conversion | N/A |
| **Offline / Mock Mode** | None (requires live SW) | **Yes (Mock Adapter)** | Simulated IR | Basic fallback | Standalone docs |
| **License** | MIT | MIT | MIT | MIT | MIT |
| **Architectural Role** | **Primary CAD Core** | **Version & Mock Core** | **Feature IR Reference** | **Registry & Unit Utility** | **API Reference Corpus** |

---

## 3. In-Depth Repository Breakdown

### 1. HarrierPigeon/Solidworks-MCP-Server (Primary Foundation)
- **Strengths:**
  - Designed specifically for LLMs: tools take intuitive engineering units ($mm$, $^\circ$) and convert internally to SOLIDWORKS SI units (meters, radians).
  - Closed feedback loop: `get_faces`, `get_mass_properties`, `look_at_model` (isometric/orthogonal screenshots) enable the AI agent to verify what it built.
  - High-level primitives: `sketch_profile` creates entire chained contours with fillet corners in a single call, preventing tool-call explosions.
  - Assemblies with functional mates (concentric, coincident, distance).
- **Adaptation Strategy:** Adopt as the primary CAD operation syntax and tool execution baseline.

### 2. andrewbartels1/SolidworksMCP-python (Dual Version & Mock Foundation)
- **Strengths:**
  - Explicit multi-year version targeting with support flags for `2024` through `2026`.
  - Production-ready `MockSolidWorksAdapter` allowing the full software platform, API endpoints, agent loops, and UI to run in automated CI and headless testing environments.
  - Extensive 151-tool surface covering advanced sheet metal, drawing generation, equations, and configurations.
- **Adaptation Strategy:** Integrate the version selection flags, version isolation logic, and mock adapter pipeline.

### 3. eyfel/mcp-server-solidworks (SolidPilot)
- **Strengths:**
  - Explicitly targets **SolidWorks 2026 SP3**.
  - Introduces a CAD-neutral Feature Graph Intermediate Representation (IR), decoupling intent from execution.
  - C# .NET 4.8 COM execution bridge provides rock-solid process separation.
- **Adaptation Strategy:** Utilize its topological reference resolution strategies when parameterizing 2026 features.

### 4. alisamsam/solidworks-mcp
- **Strengths:**
  - Clean Windows Registry interrogation for detecting installed SOLIDWORKS versions.
  - Robust cascading fallback chains for COM API failures.
- **Adaptation Strategy:** Integrate registry discovery rules into `cad/connection_manager.py`.

### 5. kilwizac/solidworks-api-mcp
- **Strengths:**
  - 14,000 documented SOLIDWORKS API interfaces, methods, properties, and enums.
- **Adaptation Strategy:** Serves as the authoritative offline reference for COM dispids, enum constants (e.g. `swUserPreferenceToggle_e`, `swDocumentTypes_e`), and API signatures.

---

## 4. Final Architectural Decision

We adopt a **Synthesized Modular Architecture**:
1. **Primary Interface:** HarrierPigeon's high-level parametric CAD schema and closed-loop inspection feedback.
2. **Version & Mock Engine:** Andrew Bartels' dual 2024/2026 version targeting and `MockSolidWorksAdapter`.
3. **Detection & Utilities:** Ali SamSam's registry discovery and multi-unit conversions.
4. **All licenses:** Full MIT attribution preserved in `cad/` source headers.
