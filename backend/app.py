import asyncio
import json
import time
import os
import io
import zipfile
from typing import List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from orchestrator import GuildOrchestrator

app = FastAPI(title="SynapseGuild Autonomous AI Engine", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))
SANDBOX_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "sandbox"))

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

# In-Memory Quest Cache
QUEST_HISTORY: Dict[str, Any] = {}

class QuestDispatchPayload(BaseModel):
    title: str
    prompt: str
    difficulty: str = "normal"
    author: str = "Guild Master"

@app.get("/")
def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "SynapseGuild API is online"}

@app.get("/api/health")
def health_check():
    return {"status": "online", "service": "SynapseGuild AI Engine", "timestamp": time.time()}

@app.get("/api/quests")
def list_quests():
    return {"quests": list(QUEST_HISTORY.values())}

@app.get("/api/quests/{quest_id}")
def get_quest(quest_id: str):
    if quest_id not in QUEST_HISTORY:
        raise HTTPException(status_code=404, detail="Quest not found")
    return QUEST_HISTORY[quest_id]

@app.get("/api/quests/{quest_id}/download")
def download_quest_artifacts(quest_id: str):
    """Zips and returns all generated files in the quest sandbox directory."""
    quest_dir = os.path.join(SANDBOX_BASE_DIR, quest_id)
    if not os.path.exists(quest_dir):
        raise HTTPException(status_code=404, detail="Quest sandbox directory not found")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(quest_dir):
            for file in files:
                if not file.endswith(".pyc") and ".pytest_cache" not in root:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, quest_dir)
                    zip_file.write(full_path, rel_path)

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={quest_id}_artifacts.zip"}
    )

@app.get("/api/quests/{quest_id}/file/{file_name}")
def download_single_file(quest_id: str, file_name: str):
    """Returns single source file content directly."""
    quest_dir = os.path.join(SANDBOX_BASE_DIR, quest_id)
    file_path = os.path.join(quest_dir, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=file_name)

async def run_quest_task(quest_id: str, prompt: str, title: str):
    async def ws_event_broadcaster(event_payload: dict):
        await manager.broadcast(event_payload)

    orchestrator = GuildOrchestrator(quest_id, prompt, event_callback=ws_event_broadcaster)
    result = await orchestrator.run()
    
    # Update quest record
    QUEST_HISTORY[quest_id]["status"] = result.get("status")
    QUEST_HISTORY[quest_id]["result"] = result
    QUEST_HISTORY[quest_id]["finished_at"] = time.time()
    
    # Final event broadcast
    await manager.broadcast({
        "event_type": "QUEST_ARCHIVED",
        "quest_id": quest_id,
        "title": title,
        "status": result.get("status"),
        "score": result.get("score")
    })

@app.post("/api/quest/dispatch")
async def dispatch_quest(payload: QuestDispatchPayload, background_tasks: BackgroundTasks):
    quest_id = f"quest_{int(time.time())}"
    
    QUEST_HISTORY[quest_id] = {
        "id": quest_id,
        "title": payload.title,
        "prompt": payload.prompt,
        "difficulty": payload.difficulty,
        "author": payload.author,
        "status": "in_progress",
        "created_at": time.time(),
        "finished_at": None,
        "result": None
    }
    
    # Broadcast quest acceptance to visual clients
    await manager.broadcast({
        "event_type": "QUEST_ENQUEUED",
        "quest_id": quest_id,
        "title": payload.title,
        "prompt": payload.prompt,
        "author": payload.author
    })
    
    # Run async pipeline in background
    background_tasks.add_task(run_quest_task, quest_id, payload.prompt, payload.title)
    
    return {"status": "dispatched", "quest_id": quest_id, "title": payload.title}

@app.websocket("/ws/guild-events")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_json({
            "event_type": "GUILD_CONNECTED",
            "message": "Connected to SynapseGuild Realtime Neural Hub 🏛️",
            "active_party": ["The Sage (Architect)", "The Forge Master (Craftsman)", "The Grand Inquisitor (Sentinel)"]
        })
        while True:
            data = await websocket.receive_text()
            try:
                parsed = json.loads(data)
                if parsed.get("action") == "ping":
                    await websocket.send_json({"event_type": "PONG", "timestamp": time.time()})
            except Exception:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
