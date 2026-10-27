# AI Robotics Design Studio — Agent Operating Guide (AGENTS.md)

> **Mandatory Reference for Future AI Agent Sessions**  
> Platform: Windows 10/11 x64  
> Core Technologies: SOLIDWORKS 2024 (Major 32) + 2026 (Major 34), Python 3.11, FastAPI, React 18, TypeScript, Tailwind CSS, pywin32 COM  

---

## 1. System Architecture Overview

```
d:\cad\
├── backend/                  # FastAPI Application Server (:8000)
│   └── app/
│       ├── main.py           # REST & WebSocket API endpoints
├── frontend/                 # React 18 + Vite + Tailwind CSS (:5173)
│   ├── src/
│   │   ├── components/       # Header, ConnectionModal, EngineeringChat, CadWorkspace, SkillsPanel, ValidationDashboard, ProjectLibrary
│   │   ├── types/            # Complete TypeScript interfaces
│   │   └── App.tsx           # Workstation layout & state orchestration
├── agents/                   # Multi-Agent Orchestration Layer
│   └── lead_manager.py       # Lead Engineering Design Manager
├── skills/                   # The 5 Specialized Engineering Skills
│   ├── mechanical_design/    # Stress, FoS, deflection, motor mount sizing
│   ├── industrial_design/    # CMF (RAL 9016 White, RAL 1036 Gold), G2 curvature, seams
│   ├── robotics_systems/     # 3-wheel platform, motor sizing, battery/compute envelopes
│   ├── additive_manufacturing/# Bambu Lab X1C/X1E (256mm³), heat-set inserts, part splitting
│   └── engineering_validation/# Scorecard, rebuild state, edge margins, printability
├── cad/                      # CAD Abstraction & Adapter Layer
│   ├── units.py              # Strict SI (meters, radians, kg) <-> Engineering (mm, deg, g)
│   ├── connection_manager.py # Registry inspection, process detection, version switching
│   ├── adapters/
│   │   ├── base.py           # BaseSolidWorksAdapter abstract interface
│   │   ├── sw_com_base.py    # win32com dispatcher with STA & dialog prevention
│   │   ├── sw2024.py         # SOLIDWORKS 2024 Adapter (Major 32)
│   │   ├── sw2026.py         # SOLIDWORKS 2026 Adapter (Major 34)
│   │   └── mock.py           # MockSolidWorksAdapter (CI/offline fallback)
├── engineering/              # Knowledge Library & Physical Engines
│   ├── calculations/         # Pure Python Shigley mechanics formulas
│   ├── materials/            # Materials database (aerospace alloys & Bambu filaments)
│   └── components/           # Catalog specs (inserts, clearance holes, NEMA faceplates)
├── projects/                 # Output CAD files (.SLDPRT, .SLDASM, .STEP, .STL)
├── tests/                    # Test Suites
│   └── test_parametric_bracket.py # Phase 2 Benchmark Test (10 steps)
├── scripts/                  # start.ps1, start.bat, run_tests.py
└── docs/                     # CAD_INTEGRATION_COMPARISON.md
```

---

## 2. SOLIDWORKS Version Management Rules

1. **Dual Version Targeting**:
   - **SOLIDWORKS 2024**: Major version `32`.
   - **SOLIDWORKS 2026**: Major version `34`.
2. **Process Isolation**:
   - When connecting, verify `app.RevisionNumber()`. Never blindly assume that `SldWorks.Application` connects to the desired version if both 2024 and 2026 are installed.
3. **Mock Mode Fallback**:
   - If no live SOLIDWORKS installation or license is detected, the platform automatically activates `MockSolidWorksAdapter`.
   - Mock adapter writes real STEP (`.STEP`), STL (`.STL`), and mockup binary (`.SLDPRT`) files to ensure downstream testing and downloads function seamlessly.
4. **Unit Conversion Law**:
   - SOLIDWORKS internal COM API strictly uses **SI Units**:
     - Length: Meters ($m$)
     - Angle: Radians ($rad$)
     - Mass: Kilograms ($kg$)
   - All user-facing methods, schemas, and chat instructions use **Engineering Units**:
     - Length: Millimeters ($mm$)
     - Angle: Degrees ($^\circ$)
     - Mass: Grams ($g$)
   - Always route dimension conversions through [cad/units.py](file:///d:/cad/cad/units.py).

---

## 3. The 5 Specialized Engineering Skills

1. **Mechanical Design Engineer** ([skills/mechanical_design/skill.py](file:///d:/cad/skills/mechanical_design/skill.py)):
   - Evaluates bending stress ($\sigma = \frac{M y}{I}$), torsion ($\tau = \frac{T r}{J}$), von Mises ($\sigma_v = \sqrt{\sigma^2 + 3\tau^2}$), and Factor of Safety ($FoS = \frac{S_y}{\sigma_v} \ge 2.0$).
   - Enforces fastener edge margin $\ge 1.5 \times d_{hole}$.
2. **Industrial Product Designer** ([skills/industrial_design/skill.py](file:///d:/cad/skills/industrial_design/skill.py)):
   - Standard palette: RAL 9016 Traffic White (#F6F6F6 gloss) body, RAL 1036 Satin Gold (#8F7242) trim, and #111111 dark display.
   - G2 curvature continuous blends and 1.5 mm panel reveal gaps.
3. **Robotics Systems Engineer** ([skills/robotics_systems/skill.py](file:///d:/cad/skills/robotics_systems/skill.py)):
   - 3-wheel platform (2 driven rear wheels, 1 front caster).
   - Motor sizing: $T_{wheel} = \frac{r}{2} (F_{rolling} + F_{incline} + F_{accel})$.
   - CG stability triangle: critical tip-over acceleration $a_{crit} \ge 0.45\text{g}$.
4. **Additive Manufacturing Engineer** ([skills/additive_manufacturing/skill.py](file:///d:/cad/skills/additive_manufacturing/skill.py)):
   - Target printer: Bambu Lab X1C / X1E ($256 \times 256 \times 256\text{ mm}$ build envelope).
   - If any dimension $>256\text{ mm}$, automatically flags for segmenting/splitting with alignment pin joints and M3 heat-set inserts.
   - Standard M3 insert hole: $\varnothing 4.0\text{ mm} \times 5.7\text{ mm}$ depth, boss wall $\ge 1.6\text{ mm}$.
5. **Engineering Validation Specialist** ([skills/engineering_validation/skill.py](file:///d:/cad/skills/engineering_validation/skill.py)):
   - Automated quality scorecard: rebuild errors == 0, manifold geometry, fastener edge margins, positive mass, printability, structural FoS.

---

## 4. Testing & Verification Commands

### Run Full Test Suite
```powershell
python scripts/run_tests.py
```

### Run Phase 2 Benchmark Test (10-Step Parametric Bracket)
```powershell
# In Mock mode:
python tests/test_parametric_bracket.py --mode mock --year 2024

# Against live SOLIDWORKS 2024:
python tests/test_parametric_bracket.py --mode 2024 --year 2024

# Against live SOLIDWORKS 2026:
python tests/test_parametric_bracket.py --mode 2026 --year 2026
```

### Launch Application
```powershell
# Using PowerShell helper:
powershell -ExecutionPolicy Bypass -File scripts/start.ps1

# Or batch script:
.\start.bat
```
- Frontend UI: `http://localhost:5173`
- Backend API Docs: `http://localhost:8000/docs`
