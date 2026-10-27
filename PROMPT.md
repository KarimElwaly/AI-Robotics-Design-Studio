MASTER BUILD PROMPT — AI ROBOTICS DESIGN STUDIO
 | SOLIDWORKS 2024 + 2026 | Full Development Authorization
You are acting as an elite multidisciplinary engineering software development team consisting of:
1.	Principal AI Systems Architect
2.	Senior Python and Full-Stack Software Engineer
3.	SOLIDWORKS API and COM Automation Specialist
4.	Senior Mechanical Design Engineer
5.	Senior Industrial Product Designer
6.	Robotics Systems Engineer
7.	Additive Manufacturing Engineer
8.	Engineering Validation and Simulation Specialist
9.	Software Testing and DevOps Engineer
Your mission is to design, develop, install, configure, execute, test, debug, and improve a real AI-powered robotics and mechanical product development platform named:
AI Robotics Design Studio
You are operating inside  Agent Mode on a Windows computer.
I authorize you to work autonomously on this project, use the terminal, execute code, install development dependencies, inspect GitHub repositories, create and modify project files, configure local services, and interact with SOLIDWORKS through its supported APIs.
I want a working application, not documentation, pseudocode, or a static demonstration.
The application must support both:
•	SOLIDWORKS 2024
•	SOLIDWORKS 2026
It must detect available versions, allow users to select the appropriate installation, and communicate with the correct SOLIDWORKS process.
Do not assume that the two installed versions expose identical functionality.
________________________________________
PART 1 — DEVELOPMENT AUTHORIZATION
1.1 Authorized Activities
Within the dedicated project directory, you have permission to:
•	Create and modify source code.
•	Create and organize folders.
•	Clone and inspect public GitHub repositories.
•	Download compatible open-source dependencies.
•	Install Python packages into virtual environments.
•	Install Node.js packages locally.
•	Create and run PowerShell scripts.
•	Execute Python and JavaScript applications.
•	Configure local MCP servers.
•	Configure SOLIDWORKS API connections.
•	Generate and execute SOLIDWORKS automation scripts.
•	Create test CAD parts and assemblies.
•	Create local databases.
•	Run automated tests.
•	Debug errors.
•	Refactor code.
•	Create local Git branches and commits.
•	Generate documentation and reports.
•	Run the backend and frontend.
•	Perform real CAD operations in a dedicated test workspace.
You may choose appropriate engineering libraries, AI orchestration frameworks, and compatible open-source implementations.
Avoid unnecessary interruptions for normal development decisions.
1.2 Authorization Boundaries
Do not:
•	Delete or overwrite existing personal or business CAD models.
•	Modify existing production assemblies without explicit approval.
•	Access unrelated personal or company files.
•	Upload confidential CAD data to external services without approval.
•	Expose API keys or credentials.
•	Disable security protection.
•	Make firewall changes or install privileged system-wide software without approval.
•	Execute unreviewed remote installation scripts.
•	Publish repositories or source code publicly without approval.
•	Deploy software to company networks without approval.
•	Purchase software, API services, or paid subscriptions without approval.
Use a dedicated test workspace for all generated models.
Before performing a potentially destructive operation, create a backup and obtain approval.
1.3 Autonomous Execution
Within these boundaries, proceed independently.
If an implementation fails:
1.	Diagnose the error.
2.	Inspect logs.
3.	Identify the root cause.
4.	Implement a correction.
5.	Run the test again.
6.	Record the outcome.
Do not repeatedly ask me for implementation choices that you can resolve through technical investigation.
Only request input when necessary for permissions, credentials, engineering safety, or essential unavailable information.
________________________________________
PART 2 — RESEARCH EXISTING GITHUB PROJECTS
Before building the application, clone and evaluate:
1.	https://github.com/HarrierPigeon/Solidworks-MCP-Server
2.	https://github.com/andrewbartels1/SolidworksMCP-python
3.	https://github.com/eyfel/mcp-server-solidworks
4.	https://github.com/alisamsam/solidworks-mcp
5.	https://github.com/kilwizac/solidworks-api-mcp
Search for other useful open-source projects involving:
•	SOLIDWORKS AI automation.
•	SOLIDWORKS API.
•	Parametric CAD generation.
•	AI engineering agents.
•	Mechanical engineering calculations.
•	Industrial design workflows.
•	CAD geometry inspection.
•	Engineering simulation.
•	CAD assembly automation.
•	Design for additive manufacturing.
Evaluate the actual source code, not only the README files.
Compare:
•	Supported CAD functionality.
•	Architecture.
•	Windows compatibility.
•	SOLIDWORKS 2024 compatibility.
•	SOLIDWORKS 2026 compatibility.
•	COM integration.
•	API reliability.
•	Error recovery.
•	Assembly support.
•	Geometry inspection.
•	Licensing.
•	Security.
•	Test coverage.
•	Ease of extension.
Create a comparison document:
docs/CAD_INTEGRATION_COMPARISON.md
Choose the strongest foundation based on technical evidence.
My initial preference is HarrierPigeon, but you may select Andrew Bartels or another better alternative if testing supports that decision.
Use kilwizac as an additional SOLIDWORKS API documentation reference when useful.
Do not combine complete MCP implementations blindly. Prefer one primary adapter and selectively reuse compatible components.
Preserve license notices, attribution, and applicable distribution obligations.
________________________________________
PART 3 — SOLIDWORKS 2024 AND 2026 INTEGRATION
This is the most important technical requirement.
3.1 Version Detection
Develop an automatic SOLIDWORKS installation discovery system.
Inspect relevant Windows registry entries, installed executable paths, and COM registrations.
Determine:
•	Installed SOLIDWORKS versions.
•	Available executable paths.
•	Registered COM identifiers.
•	Available API libraries.
•	Active SOLIDWORKS processes.
•	Active documents.
•	Application versions.
•	Relevant service-pack information, when accessible.
Do not rely solely on a generic COM ProgID to determine which version is selected.
Implement a version-selection mechanism.
The user should be able to select:
•	Auto Detect
•	SOLIDWORKS 2024
•	SOLIDWORKS 2026
Show the actual connected version in the interface.
3.2 Version-Specific Connections
Implement a SOLIDWORKS connection manager.
It must:
1.	Discover installed versions.
2.	Identify running application instances.
3.	Connect to the requested version.
4.	Verify the actual application identity.
5.	Prevent accidental attachment to the wrong version.
6.	Open or create a controlled session where supported.
7.	Handle disconnected applications.
8.	Recover from COM failures.
9.	Report unsupported operations.
When both versions are installed, ensure the application does not accidentally control the wrong process.
If reliable process-specific COM attachment cannot be established, implement a supported alternative and explicitly report the limitation.
Use COM automation on Windows, with pywin32 or another appropriate supported implementation.
Handle COM threading and initialization correctly.
Avoid running real SOLIDWORKS COM operations from an incompatible WSL/Linux runtime.
3.3 Compatibility Layer
Create a common CAD interface with version-specific adapters:
•	SolidWorks2024Adapter
•	SolidWorks2026Adapter
Use shared functionality whenever possible.
Introduce version-specific overrides only where necessary.
Each adapter must support capability discovery and report whether a requested operation is available.
Examples:
•	Sketch creation
•	Extrusion
•	Loft
•	Sweep
•	Fillet
•	Assembly insertion
•	Component mating
•	Mass properties
•	Export
•	Screenshot capture
•	Drawing generation
Do not falsely report unsupported functions as implemented.
3.4 Connection Reliability
Implement:
•	Connection health checks.
•	Version verification.
•	Timeouts.
•	COM exception handling.
•	Structured logs.
•	Document-state tracking.
•	Recovery procedures.
•	Safe disconnect.
•	Operation serialization when required.
•	Detection of blocking SOLIDWORKS dialogs.
The user must always know:
•	Which SOLIDWORKS version is connected.
•	Which document is active.
•	Whether an operation succeeded.
•	Whether the model rebuilt successfully.
•	Whether the output was saved.
3.5 CAD Operation Engine
Support these operations progressively.
Document management
•	Create parts.
•	Open parts.
•	Create assemblies.
•	Open assemblies.
•	Save documents.
•	Save As.
•	Export STEP.
•	Export STL.
•	Manage active documents.
Parametric sketching
•	Lines.
•	Rectangles.
•	Circles.
•	Arcs.
•	Splines.
•	Geometric relations.
•	Dimensions.
•	Fully constrained sketches where appropriate.
Solid modelling
•	Extruded bosses.
•	Extruded cuts.
•	Revolves.
•	Sweeps.
•	Lofts.
•	Fillets.
•	Chamfers.
•	Shells.
•	Patterns.
•	Mirrors.
•	Reference planes.
•	Parametric modifications.
Assemblies
•	Insert components.
•	Position components.
•	Create mates.
•	Read component transformations.
•	Inspect assembly structure.
•	Identify interference.
•	Extract mass properties.
Model inspection
•	Feature tree.
•	Dimensions.
•	Bounding boxes.
•	Faces and edges.
•	Model rebuild errors.
•	Volume.
•	Mass.
•	Center of gravity.
•	Model screenshots.
Engineering files
•	Native SLDPRT files.
•	Native SLDASM files.
•	STEP exports.
•	STL exports.
•	Engineering drawings where supported.
All dimensions must have explicit units.
Handle SOLIDWORKS API unit conversions correctly.
________________________________________
PART 4 — AI ENGINEERING AGENT SYSTEM
Create an AI system that coordinates specialized engineering skills.
Initially use one lead agent with separate skills and tools.
Do not create unnecessarily complex autonomous-agent infrastructure before the core functionality works.
4.1 Lead Engineering Agent
The lead agent acts as an Engineering Design Manager.
Responsibilities:
1.	Understand user requirements.
2.	Produce a design specification.
3.	Identify missing information.
4.	Select the appropriate engineering skills.
5.	Plan design operations.
6.	Coordinate industrial and mechanical design.
7.	Control CAD tool execution.
8.	Review results.
9.	Resolve design conflicts.
10.	Recommend improvements.
11.	Prepare engineering outputs.
The agent must maintain a clear distinction between assumptions, requirements, calculated values, and verified results.
4.2 Mechanical Design Engineer Skill
Create a reusable skill containing engineering guidance and executable tools for:
•	Mechanical component design.
•	Shafts.
•	Bearings.
•	Brackets.
•	Fasteners.
•	Structural supports.
•	Gear mechanisms.
•	Linear mechanisms.
•	Rotating joints.
•	Motor mounts.
•	Suspension components.
•	Parametric CAD.
•	Tolerance analysis.
•	Material selection.
•	Mechanical design review.
Support calculations for:
•	Forces.
•	Moments.
•	Torque.
•	Bending stress.
•	Axial stress.
•	Deflection.
•	Factor of safety.
•	Basic bearing and shaft sizing.
•	Fastener loads.
•	Mass and center of gravity.
Use established analytical formulas and verified input data.
Do not invent missing loads or material strengths.
4.3 Industrial Product Designer Skill
Create a specialized industrial designer capable of:
•	Product form development.
•	Shape exploration.
•	Aesthetic direction.
•	Organic surfaces.
•	Ergonomics.
•	Product proportions.
•	Design language.
•	Brand-inspired styling.
•	Color, material, and finish.
•	Exterior panels.
•	Surface continuity.
•	Assembly seam planning.
The skill should emphasize premium commercial product appearance.
It should not default to generic boxes, cylinders, or primitive-looking robot bodies when the brief calls for sophisticated industrial design.
Where available, connect an appropriate image-generation provider to generate concept references.
Use approved reference concepts to guide CAD modelling.
Do not claim that automatically created CAD surfaces match an approved concept without visual verification.
4.4 Robotics Systems Engineer Skill
Implement engineering workflows for:
•	Robot architecture.
•	Mobile robot chassis.
•	Motor sizing.
•	Wheel configuration.
•	Suspension.
•	Actuators.
•	Sensors.
•	Battery packaging.
•	Computing hardware.
•	Electronics integration.
•	Wiring space.
•	Payload requirements.
•	Stability and center-of-gravity evaluation.
•	System-level packaging.
Support configurable component specifications and supplier datasheets.
4.5 Additive Manufacturing Engineer Skill
Focus initially on Bambu Lab X1C and X1E printers.
Support:
•	Build-volume validation.
•	Printer capability profiles.
•	Material selection.
•	Part orientation.
•	Minimum feature recommendations.
•	Wall thickness.
•	Infill considerations.
•	Dimensional allowances.
•	Heat-set inserts.
•	Screw mounting.
•	Assembly clearance.
•	Joining methods.
•	Part splitting.
•	Support requirements.
•	Surface finishing.
•	Post-processing.
Include configurable material profiles for:
•	PLA
•	PETG
•	PETG-CF
•	ABS-GF
•	PAHT-CF
•	PPS-CF
•	TPU
Verify printer-material compatibility and drying requirements before recommending production settings.
Do not assume identical tolerances for every printer or material.
4.6 Engineering Validation Skill
Create automated validation routines for:
•	Dimensional consistency.
•	Geometric validity.
•	Feature rebuild state.
•	Mechanical interference.
•	Assembly clearances.
•	Mass properties.
•	Center of gravity.
•	Material assumptions.
•	Manufacturing constraints.
•	Structural calculation checks.
Prepare reports distinguishing:
•	Passed checks.
•	Failed checks.
•	Warnings.
•	Missing data.
•	Checks not performed.
Support SOLIDWORKS Simulation integration where the required license and interfaces are available.
Never fabricate FEA results.
________________________________________
PART 5 — AI MODEL CONFIGURATION
Support multiple AI providers.
Initially implement:
•	Anthropic Claude
•	OpenAI
The user should be able to choose the provider and supported model through the application interface.
Store credentials securely.
Do not hard-code API keys.
Support:
•	Model configuration.
•	Context management.
•	Tool calling.
•	MCP execution.
•	Conversation history.
•	Engineering skill selection.
•	Structured outputs.
•	Controlled execution loops.
Use a suitable agent orchestration framework only when it genuinely improves the application.
Do not introduce unnecessary frameworks.
________________________________________
PART 6 — APPLICATION INTERFACE
Build a modern local application.
Preferred technologies:
Frontend
•	React
•	TypeScript
•	Tailwind CSS
Backend
•	Python
•	FastAPI
•	Pydantic
Storage
•	SQLite for the initial version
The interface should contain:
A. Engineering Chat
Natural-language design instructions.
Examples:
"Create a motor mounting bracket."
"Increase the wall thickness to 5 mm."
"Change the hole spacing to 60 mm."
"Check if the bracket is suitable for 3D printing."
"Improve the exterior styling of this robot."
Display:
•	AI responses.
•	Engineering calculations.
•	Execution plans.
•	CAD tool calls.
•	Warnings.
•	Design decisions.
•	Operation results.
B. SOLIDWORKS Connection Panel
Show:
•	Installed versions.
•	Selected version.
•	Connection state.
•	Active document.
•	CAD operations.
•	Rebuild state.
•	Recent errors.
Provide buttons for:
•	Connect.
•	Disconnect.
•	Refresh.
•	Open test document.
•	Run connection test.
C. Engineering Skills Panel
Allow users to view and enable:
•	Mechanical Design Engineer.
•	Industrial Product Designer.
•	Robotics Systems Engineer.
•	Additive Manufacturing Engineer.
•	Engineering Validation Engineer.
Display the skill selected for the current task.
D. CAD Workspace
Display:
•	Model screenshots.
•	Project file structure.
•	Current part or assembly.
•	Key dimensions.
•	Feature information.
•	CAD operation history.
Add an interactive model viewer only when a suitable export and viewing pipeline is implemented.
Do not substitute a decorative 3D mockup for the real CAD model.
E. Project Library
Users should be able to:
•	Create projects.
•	Open existing projects.
•	Import CAD references.
•	Upload datasheets.
•	Store engineering requirements.
•	Save design revisions.
•	View previous sessions.
•	Export project documentation.
F. Validation Dashboard
Display engineering validation results and outstanding issues.
The system must distinguish calculated results from AI-generated suggestions.
________________________________________
PART 7 — ENGINEERING KNOWLEDGE LIBRARY
Build a structured engineering knowledge system.
Store:
•	Mechanical design guidelines.
•	Engineering reference calculations.
•	Manufacturer specifications.
•	Material properties.
•	Approved component models.
•	Robotics component specifications.
•	Manufacturing rules.
•	Engineering templates.
•	Previously designed robot components.
Support importing:
•	PDF datasheets.
•	STEP files.
•	Existing SOLIDWORKS models.
•	Technical documentation.
•	Engineering reference tables.
Track units, sources, revision dates, and confidence in extracted values.
Do not treat AI-generated values as verified manufacturer specifications.
________________________________________
PART 8 — PROJECT STRUCTURE
Use a maintainable directory structure similar to:
AI-Robotics-Design-Studio/
•	frontend/
•	backend/
•	agents/
•	skills/
o	mechanical-design-engineer/
o	industrial-product-designer/
o	robotics-systems-engineer/
o	additive-manufacturing-engineer/
o	engineering-validation/
•	cad/
o	adapters/
o	solidworks2024/
o	solidworks2026/
o	mcp/
o	operations/
o	validation/
•	engineering/
o	calculations/
o	materials/
o	components/
•	knowledge/
•	projects/
•	tests/
o	unit/
o	integration/
o	solidworks2024/
o	solidworks2026/
•	scripts/
•	logs/
•	docs/
•	AGENTS.md
•	README.md
You may improve the structure as needed.
Create a detailed AGENTS.md file documenting the architecture, operating rules, testing commands, engineering constraints, and development conventions.
This file should help future Cursor Agent sessions continue development consistently.
________________________________________
PART 9 — DEVELOPMENT AND TESTING STRATEGY
Phase 1 — Environment and SOLIDWORKS Connectivity
This phase is mandatory before advanced AI development.
1.	Inspect Windows environment.
2.	Detect installed SOLIDWORKS versions.
3.	Verify licensing and API availability.
4.	Inspect open-source MCP implementations.
5.	Create the compatibility layer.
6.	Establish a connection to SOLIDWORKS 2024.
7.	Establish a connection to SOLIDWORKS 2026.
8.	Read application version information.
9.	Verify active document access.
10.	Produce connection-test logs.
When both installations are available, test them separately.
Do not claim compatibility solely because a library supports a generic COM interface.
Phase 2 — Basic CAD Automation
Using a dedicated test directory, create a parametric mounting plate:
•	Length: 100 mm.
•	Width: 60 mm.
•	Thickness: 10 mm.
•	Four mounting holes.
•	Hole diameter: 6 mm.
•	Hole centers: 10 mm from their nearest two plate edges.
Save as:
Test_Bracket_2024.SLDPRT
Repeat using SOLIDWORKS 2026:
Test_Bracket_2026.SLDPRT
Then:
1.	Read back the dimensions.
2.	Change the length to 150 mm.
3.	Rebuild.
4.	Verify dimensions.
5.	Verify hole positions.
6.	Retrieve volume.
7.	Assign a known material when available.
8.	Retrieve mass properties.
9.	Export STEP.
10.	Export STL.
Verify files exist, are nonempty, and can be reopened where possible.
Record actual test results for each SOLIDWORKS version.
Phase 3 — AI Natural-Language Control
Implement the AI-to-CAD workflow.
Test prompts:
"Create a rectangular plate with four mounting holes."
"Increase its length by 20 mm."
"Add 3 mm fillets to its external vertical corners."
"Save the model as a new revision."
"Show me the updated model dimensions."
The AI must execute real CAD operations, inspect their results, and report any failures.
Phase 4 — Engineering Skills
Implement and test the Mechanical Design Engineer and Industrial Product Designer first.
Then introduce Robotics Systems Engineer, Additive Manufacturing Engineer, and Engineering Validation Engineer.
Each skill must include:
•	Instructions.
•	Expected inputs.
•	Structured outputs.
•	Tools.
•	Relevant reference information.
•	Validation rules.
•	Automated tests.
Phase 5 — Application Interface
Develop the complete frontend and connect it to the backend.
Implement:
•	Chat.
•	Version selection.
•	CAD status.
•	Project management.
•	Skill management.
•	Operation logs.
•	Model preview.
•	Validation results.
Run the application locally.
Phase 6 — Robotics Product Demonstration
After reliable CAD integration, build a demonstration of a futuristic mascot robot.
Specifications:
•	Overall height approximately 1,400 mm.
•	Premium aviation-inspired industrial design.
•	Smooth white exterior.
•	RAL 9016 glossy white.
•	RAL 1036 metallic gold accents.
•	Black expressive face display.
•	Two articulated side wings.
•	Three-wheel platform.
•	Two driven rear wheels.
•	One front caster.
•	Internal space for battery, motors, controllers, computing hardware, and sensors.
•	Removable exterior panels.
•	Suitable for additive manufacturing prototypes.
First create the overall design specification.
Then develop:
1.	Main proportions.
2.	Exterior styling.
3.	Internal component envelopes.
4.	Chassis.
5.	Shell panels.
6.	Mechanical interfaces.
7.	Basic assembly.
8.	Geometric validation.
9.	Manufacturing preparation.
Preserve editable parametric geometry wherever possible.
If automated organic surfacing is insufficient, identify the limitation rather than presenting a rough model as a premium finished design.
________________________________________
PART 10 — AUTOMATED QUALITY ASSURANCE
Implement:
•	Unit tests.
•	Backend integration tests.
•	Frontend build tests.
•	CAD tool schema validation.
•	Mock CAD tests.
•	Real CAD integration tests.
•	Regression tests.
•	Version-specific compatibility tests.
•	Exception logging.
•	Test reports.
Separate mock and real CAD results.
Mock test success must never be reported as real SOLIDWORKS operation success.
For both versions, report:
•	Connected successfully?
•	Correct version verified?
•	Part creation successful?
•	Parametric modification successful?
•	Rebuild successful?
•	Save successful?
•	STEP export successful?
•	STL export successful?
•	Model reopening successful?
•	Errors or limitations?
________________________________________
PART 11 — RELIABILITY AND SECURITY
Implement an execution approval system.
The agent may automatically perform ordinary operations on newly created test models.
Require user approval before:
•	Overwriting existing CAD files.
•	Deleting components or project data.
•	Making destructive changes to imported assemblies.
•	Changing protected system settings.
•	Installing software requiring elevated privileges.
•	Sending confidential engineering documents to cloud services.
Create CAD checkpoints before substantial modifications.
Do not allow unrestricted filesystem access through MCP tools.
Keep all local MCP endpoints restricted to the local machine unless separately authorized.
Validate tool arguments, file paths, dimensions, and operating states.
Prevent arbitrary AI-generated scripts from executing without appropriate controls.
Never report success based only on an AI response.
________________________________________
PART 12 — PERFORMANCE AND EXTENSIBILITY
Design the application so it can later support:
•	Additional CAD software.
•	More advanced mechanical engineering agents.
•	Advanced assembly generation.
•	Engineering drawing generation.
•	FEA and structural optimization.
•	Robotics component selection.
•	Automated manufacturing reports.
•	CAD revision comparison.
•	Simulation-driven design.
•	Additional additive manufacturing equipment.
•	3D printer monitoring.
•	Reusable robotics design templates.
Keep the CAD adapter independent of the AI provider.
Keep engineering calculations independent of the language model wherever possible.
Avoid unnecessary complexity in the MVP.
________________________________________
PART 13 — DEVELOPMENT PRIORITIES
Follow this strict priority order:
Priority 1: Reliable SOLIDWORKS 2024 and 2026 connectivity.
Priority 2: Real parametric CAD creation and editing.
Priority 3: AI natural-language CAD control.
Priority 4: Mechanical Design Engineer skill.
Priority 5: Industrial Product Designer skill.
Priority 6: Robotics engineering and manufacturing skills.
Priority 7: Advanced autonomous design, validation, and optimization.
Do not spend excessive time designing a sophisticated interface before real CAD operations work.
________________________________________
PART 14 — REQUIRED DELIVERABLES
Deliver a complete working project containing:
1.	Application source code.
2.	Windows development environment configuration.
3.	Selected open-source CAD integration.
4.	SOLIDWORKS 2024 adapter.
5.	SOLIDWORKS 2026 adapter.
6.	AI provider integration.
7.	Engineering agent system.
8.	Mechanical Design Engineer skill.
9.	Industrial Product Designer skill.
10.	Additional engineering skill modules.
11.	Frontend application.
12.	Backend application.
13.	CAD tests.
14.	Engineering calculation tests.
15.	Test reports.
16.	Installation and startup instructions.
17.	Known limitations.
18.	Development roadmap.
Create scripts for starting the complete application.
Document how to select and connect each SOLIDWORKS version.
Maintain a clear distinction between implemented, tested, partially working, and planned functionality.
________________________________________
PART 15 — EXECUTION INSTRUCTIONS
You are Cursor Agent, working inside the actual development workspace.
Start executing this project now.
Do the following in order:
1.	Inspect the development environment.
2.	Identify installed SOLIDWORKS versions.
3.	Verify Windows COM availability.
4.	Clone and evaluate the five GitHub repositories.
5.	Select the primary CAD integration.
6.	Create the project architecture.
7.	Implement the SOLIDWORKS version manager.
8.	Establish real SOLIDWORKS 2024 connectivity.
9.	Establish real SOLIDWORKS 2026 connectivity.
10.	Run basic CAD tests for each available version.
11.	Implement the AI orchestration layer.
12.	Implement the first two engineering skills.
13.	Build the backend.
14.	Build the frontend.
15.	Integrate everything.
16.	Run automated tests.
17.	Debug failures.
18.	Execute an end-to-end CAD demonstration.
19.	Document the actual results.
Continue iteratively without stopping after the architecture phase.
If a dependency is missing, install a compatible project-local version when permitted.
If a GitHub project is unsuitable, investigate alternatives.
If an API call fails, inspect the real error and fix the integration.
If a SOLIDWORKS version is not available or accessible, complete the testable software work and clearly identify what remains unverified.
Do not claim that both versions work unless both have passed real integration tests.
Final Success Criteria
The project is successful when I can open Cursor or the local AI Robotics Design Studio application, select SOLIDWORKS 2024 or 2026, and type:
"Design a motor mounting bracket with four mounting holes, rounded corners, and a 10 mm plate thickness."
The AI should:
1.	Understand the request.
2.	Select the Mechanical Design Engineer skill.
3.	Prepare the CAD operations.
4.	Create the actual part in the selected SOLIDWORKS version.
5.	Verify the geometry.
6.	Save the model.
7.	Display the result.
8.	Allow me to request modifications through natural language.
The final system should provide a reliable foundation for more advanced robotics and industrial product design.
Begin implementing immediately. Your primary objective is verified, working software—not a presentation, prototype mockup, or theoretical architecture.

