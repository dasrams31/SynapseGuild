import asyncio
import json
import time
import os
import io
import zipfile
import shutil
import threading
from typing import List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from orchestrator import GuildOrchestrator
from sandbox_runner import SANDBOX_BASE_DIR

app = FastAPI(title="SynapseGuild Autonomous AI Engine")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-Memory Realtime Quest & Events Database
QUEST_HISTORY: Dict[str, Dict[str, Any]] = {}
CLEANUP_TTL_SECONDS = 900  # 15 Minutes auto-delete TTL

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

class QuestDispatchPayload(BaseModel):
    title: str
    prompt: str
    language: str = "python" # python | javascript
    difficulty: str = "normal"
    preset: str = "classic"
    author: str = "Guild Master Rama"

class GuildMasterInterventionPayload(BaseModel):
    quest_id: str
    instruction: str

def purge_quest_sandbox(quest_id: str, reason: str = "auto_ttl"):
    quest_dir = os.path.join(SANDBOX_BASE_DIR, quest_id)
    if os.path.exists(quest_dir):
        try:
            shutil.rmtree(quest_dir)
            print(f"🧹 [Auto-Purge] Sandbox directory for {quest_id} wiped from disk. ({reason})")
        except Exception as e:
            print(f"Error purging {quest_id}: {e}")
            
    if quest_id in QUEST_HISTORY:
        QUEST_HISTORY[quest_id]["purged"] = True
        QUEST_HISTORY[quest_id]["purged_at"] = time.time()
        QUEST_HISTORY[quest_id]["purge_reason"] = reason

def schedule_quest_auto_purge(quest_id: str, delay_seconds: int = 900):
    def timer_callback():
        purge_quest_sandbox(quest_id, reason="15_min_ttl_expired")
        asyncio.run(manager.broadcast({
            "event_type": "QUEST_PURGED",
            "quest_id": quest_id,
            "message": "⌛ Masa simpan 15 menit habis. Berkas kodingan otomatis dihapus demi efisiensi & keamanan server."
        }))
        
    t = threading.Timer(delay_seconds, timer_callback)
    t.daemon = True
    t.start()

@app.get("/")
def read_root():
    return FileResponse(os.path.join(os.path.dirname(__file__), "../frontend/index.html"))

@app.get("/api/health")
def health_check():
    return {"status": "online", "service": "SynapseGuild AI Engine", "timestamp": time.time(), "auto_cleanup_ttl": "15m", "languages": ["python", "javascript"]}

@app.get("/api/quests")
def list_quests():
    return {"quests": list(QUEST_HISTORY.values())}

@app.get("/api/quests/{quest_id}")
def get_quest(quest_id: str):
    if quest_id not in QUEST_HISTORY:
        raise HTTPException(status_code=404, detail="Quest not found")
    return QUEST_HISTORY[quest_id]

@app.get("/api/quests/{quest_id}/download")
def download_quest_artifacts(quest_id: str, auto_wipe: bool = True):
    quest_dir = os.path.join(SANDBOX_BASE_DIR, quest_id)
    if not os.path.exists(quest_dir) or QUEST_HISTORY.get(quest_id, {}).get("purged"):
        raise HTTPException(status_code=410, detail="Berkas artefak sudah dihapus (Masa simpan 15 menit telah habis atau sudah diunduh).")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(quest_dir):
            for file in files:
                if not file.endswith(".pyc") and ".pytest_cache" not in root:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, quest_dir)
                    zip_file.write(full_path, rel_path)

    zip_buffer.seek(0)
    
    if auto_wipe:
        threading.Timer(2.0, lambda: purge_quest_sandbox(quest_id, reason="downloaded_by_user")).start()

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={quest_id}_artifacts.zip"}
    )

@app.get("/api/quests/{quest_id}/file/{file_name}")
def download_single_file(quest_id: str, file_name: str):
    quest_dir = os.path.join(SANDBOX_BASE_DIR, quest_id)
    file_path = os.path.join(quest_dir, file_name)
    if not os.path.exists(file_path) or QUEST_HISTORY.get(quest_id, {}).get("purged"):
        raise HTTPException(status_code=410, detail="Berkas sudah dihapus (Masa simpan 15 menit habis).")
    return FileResponse(file_path, filename=file_name)

async def run_quest_task(quest_id: str, prompt: str, title: str, language: str = "python", preset: str = "classic"):
    async def ws_event_broadcaster(event_payload: dict):
        await manager.broadcast(event_payload)

    orchestrator = GuildOrchestrator(quest_id, prompt, language=language, preset=preset, event_callback=ws_event_broadcaster)
    result = await orchestrator.run()
    
    QUEST_HISTORY[quest_id]["status"] = result.get("status")
    QUEST_HISTORY[quest_id]["result"] = result
    QUEST_HISTORY[quest_id]["finished_at"] = time.time()
    QUEST_HISTORY[quest_id]["expires_at"] = time.time() + CLEANUP_TTL_SECONDS
    
    schedule_quest_auto_purge(quest_id, delay_seconds=CLEANUP_TTL_SECONDS)
    
    await manager.broadcast({
        "event_type": "QUEST_ARCHIVED",
        "quest_id": quest_id,
        "title": title,
        "language": language,
        "status": result.get("status"),
        "score": result.get("score"),
        "git_status": result.get("git"),
        "expires_in_seconds": CLEANUP_TTL_SECONDS
    })

@app.post("/api/quest/dispatch")
async def dispatch_quest(payload: QuestDispatchPayload, background_tasks: BackgroundTasks):
    quest_id = f"quest_{int(time.time())}"
    
    QUEST_HISTORY[quest_id] = {
        "id": quest_id,
        "title": payload.title,
        "prompt": payload.prompt,
        "language": payload.language,
        "difficulty": payload.difficulty,
        "preset": payload.preset,
        "author": payload.author,
        "status": "in_progress",
        "created_at": time.time(),
        "finished_at": None,
        "expires_at": None,
        "purged": False,
        "result": None
    }
    
    await manager.broadcast({
        "event_type": "QUEST_ENQUEUED",
        "quest_id": quest_id,
        "title": payload.title,
        "prompt": payload.prompt,
        "language": payload.language,
        "preset": payload.preset,
        "author": payload.author
    })
    
    background_tasks.add_task(run_quest_task, quest_id, payload.prompt, payload.title, payload.language, payload.preset)
    
    return {"status": "dispatched", "quest_id": quest_id, "title": payload.title}

@app.post("/api/quest/intervene")
async def intervene_quest(payload: GuildMasterInterventionPayload):
    await manager.broadcast({
        "event_type": "GUILD_MASTER_INTERVENTION",
        "quest_id": payload.quest_id,
        "instruction": payload.instruction,
        "message": f"👑 Guild Master mengintervensi strategi: '{payload.instruction}'"
    })
    return {"status": "intervention_broadcasted"}

@app.websocket("/ws/guild-events")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_json({
            "event_type": "GUILD_CONNECTED",
            "message": "Connected to SynapseGuild Live Event Stream",
            "timestamp": time.time()
        })
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
