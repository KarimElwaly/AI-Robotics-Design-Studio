"""
FastAPI Backend Application for AI Robotics Design Studio.
Provides REST and WebSocket endpoints for AI natural-language chat,
SOLIDWORKS dual-version connection control, engineering calculations, and model inspection.
"""
import os
import sys
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from cad.connection_manager import connection_manager, ConnectionStatus
from cad.adapters.base import CadOperationResult, MassProperties
from agents.lead_manager import lead_agent, AgentResponse
from agents.llm_gateway import llm_gateway, LLMConfig
from engineering.materials.database import list_materials, get_material
from skills.engineering_validation.skill import EngineeringValidationSkill
from knowledge.knowledge_manager import knowledge_library
from projects.generate_mascot_robot import generate_mascot_robot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StudioBackend")

app = FastAPI(
    title="AI Robotics Design Studio API",
    version="1.0.0",
    description="Backend API for AI natural-language CAD generation, SOLIDWORKS 2024/2026 integration, and engineering analysis.",
)

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure projects folder exists and mount as static for downloads
PROJECTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "projects"))
os.makedirs(PROJECTS_DIR, exist_ok=True)
app.mount("/files", StaticFiles(directory=PROJECTS_DIR), name="projects_files")


# Request schemas
class ConnectRequest(BaseModel):
    mode: str  # "auto", "2024", "2026", "mock"


class ChatRequest(BaseModel):
    prompt: str


class SkillEvalRequest(BaseModel):
    skill_name: str
    request: str
    context: Optional[Dict[str, Any]] = None


class DimensionUpdateRequest(BaseModel):
    dimension_name: str
    value_mm: float


class LLMConfigRequest(BaseModel):
    provider: str
    model_name: Optional[str] = None


@app.get("/api/health")
def get_health():
    adapter = connection_manager.get_adapter()
    return {
        "status": "healthy",
        "app_name": "AI Robotics Design Studio",
        "cad_adapter": adapter.get_version_info().version_name,
        "is_mock": adapter.get_version_info().is_mock,
        "llm_provider": llm_gateway.config.provider,
        "llm_model": llm_gateway.config.model_name,
    }


@app.get("/api/cad/status", response_model=ConnectionStatus)
def get_cad_status():
    return connection_manager.get_status()


@app.post("/api/cad/connect")
def connect_cad(req: ConnectRequest):
    res = connection_manager.set_mode(req.mode)
    return {
        "result": res.model_dump(),
        "status": connection_manager.get_status().model_dump(),
    }


@app.post("/api/cad/disconnect")
def disconnect_cad():
    adapter = connection_manager.get_adapter()
    res = adapter.disconnect()
    return {"result": res.model_dump()}


@app.get("/api/cad/model-info")
def get_model_info():
    adapter = connection_manager.get_adapter()
    return {
        "active_document": getattr(adapter, "active_doc", "None"),
        "features": [f.model_dump() for f in adapter.get_feature_tree()],
        "dimensions": [d.model_dump() for d in adapter.get_dimensions()],
        "mass_properties": adapter.get_mass_properties().model_dump(),
        "version": adapter.get_version_info().model_dump(),
    }


@app.post("/api/cad/modify-dimension")
def modify_dimension(req: DimensionUpdateRequest):
    adapter = connection_manager.get_adapter()
    res = adapter.modify_dimension(req.dimension_name, req.value_mm)
    adapter.rebuild()
    return {
        "result": res.model_dump(),
        "mass_properties": adapter.get_mass_properties().model_dump(),
    }


@app.post("/api/cad/rebuild")
def rebuild_model():
    adapter = connection_manager.get_adapter()
    res = adapter.rebuild()
    return {"result": res.model_dump()}


@app.post("/api/cad/checkpoint")
def create_checkpoint():
    adapter = connection_manager.get_adapter()
    res = adapter.save_checkpoint()
    return {"result": res.model_dump()}


@app.post("/api/chat", response_model=AgentResponse)
def handle_chat(req: ChatRequest):
    response = lead_agent.process_request(req.prompt)
    return response


@app.get("/api/skills")
def list_skills():
    return [
        {"key": k, "name": s.name, "description": s.description}
        for k, s in lead_agent.skills.items()
    ]


@app.post("/api/skills/evaluate")
def evaluate_skill(req: SkillEvalRequest):
    skill = lead_agent.skills.get(req.skill_name.lower())
    if not skill:
        for s in lead_agent.skills.values():
            if s.name.lower() == req.skill_name.lower():
                skill = s
                break
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill '{req.skill_name}' not found.")

    ctx = req.context or lead_agent.current_state
    eval_res = skill.evaluate(req.request, ctx)
    return eval_res.model_dump()


@app.get("/api/materials")
def get_materials(category: Optional[str] = None):
    return [m.model_dump() for m in list_materials(category)]


@app.get("/api/knowledge")
def search_knowledge(q: Optional[str] = None, category: Optional[str] = None):
    if category:
        entries = knowledge_library.query_by_category(category)
    elif q:
        entries = knowledge_library.search(q)
    else:
        entries = list(knowledge_library.entries.values())
    return [e.model_dump() for e in entries]


@app.get("/api/llm/config")
def get_llm_config():
    return {
        "provider": llm_gateway.config.provider,
        "model_name": llm_gateway.config.model_name,
        "has_api_key": bool(llm_gateway.get_api_key()),
    }


@app.post("/api/llm/config")
def set_llm_config(req: LLMConfigRequest):
    llm_gateway.set_provider(req.provider, req.model_name)
    return {"status": "updated", "config": llm_gateway.config.model_dump()}


@app.get("/api/projects")
def list_project_files():
    files = []
    for root, _, filenames in os.walk(PROJECTS_DIR):
        for fn in filenames:
            full_path = os.path.join(root, fn)
            rel_path = os.path.relpath(full_path, PROJECTS_DIR)
            files.append({
                "filename": fn,
                "relative_path": rel_path.replace("\\", "/"),
                "size_bytes": os.path.getsize(full_path),
                "extension": os.path.splitext(fn)[1].lower(),
            })
    return {"files": files}


@app.post("/api/mascot-robot/generate")
def run_mascot_robot_generation():
    spec_path = generate_mascot_robot()
    return {"status": "generated", "spec_file": spec_path}


@app.post("/api/validation/run")
def run_validation():
    adapter = connection_manager.get_adapter()
    mp = adapter.get_mass_properties()
    ctx = dict(lead_agent.current_state)
    ctx["mass_g"] = mp.mass_g
    val_skill = lead_agent.skills["validation"]
    res = val_skill.evaluate("Run full engineering validation scorecard", ctx)
    return res.model_dump()


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            response = lead_agent.process_request(data)
            await websocket.send_json(response.model_dump())
    except WebSocketDisconnect:
        logger.info("Chat WebSocket client disconnected.")
