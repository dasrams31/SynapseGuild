import asyncio
import json
import time
from typing import Dict, Any, Callable, Optional

from agents.architect import run_architect
from agents.craftsman import run_craftsman
from agents.sentinel import run_sentinel
from agents.dialogue_engine import generate_party_discussion
from sandbox_runner import CodeSandbox

class GuildOrchestrator:
    def __init__(self, quest_id: str, quest_prompt: str, preset: str = "classic", event_callback: Optional[Callable] = None):
        self.quest_id = quest_id
        self.quest_prompt = quest_prompt
        self.preset = preset # classic | speedrun | security
        self.event_callback = event_callback
        self.sandbox = CodeSandbox(quest_id)
        self.iteration = 1
        self.max_iterations = 3
        self.party_stats = {
            "architect": {"hp": 100, "mp": 100},
            "craftsman": {"hp": 100, "mp": 100},
            "sentinel": {"hp": 100, "mp": 100}
        }

    async def emit(self, event_type: str, actor_id: str, dialogue: str, emote: str = "chat", extra: dict = None):
        actor_names = {
            "architect": "The Sage",
            "craftsman": "The Forge Master",
            "sentinel": "The Grand Inquisitor"
        }
        payload = {
            "event_type": event_type,
            "quest_id": self.quest_id,
            "timestamp": time.time(),
            "iteration": self.iteration,
            "actor": {
                "id": actor_id,
                "name": actor_names.get(actor_id, actor_id.capitalize()),
                "hp": self.party_stats.get(actor_id, {}).get("hp", 100),
                "mp": self.party_stats.get(actor_id, {}).get("mp", 100)
            },
            "action": {
                "dialogue": dialogue,
                "emote": emote
            },
            "extra": extra or {}
        }
        if self.event_callback:
            if asyncio.iscoroutinefunction(self.event_callback):
                await self.event_callback(payload)
            else:
                self.event_callback(payload)

    async def run(self) -> dict:
        await self.emit("QUEST_INITIALIZED", "architect", f"Misi diterima: '{self.quest_prompt}'. Party berkumpul!", "ready")
        
        # ── 1. REALTIME TEAM BRAINSTORMING & DEBATE (WAR ROOM) ────────────────
        if self.preset != "speedrun":
            await self.emit("AGENT_PHASE_START", "architect", "Memulai sesi diskusi dan debat strategi di War Room...", "meeting")
            discussion = generate_party_discussion(self.quest_prompt, phase="PLANNING_AND_DESIGN")
            for turn in discussion:
                actor = turn.get("actor", "architect")
                speech = turn.get("speech", "")
                await self.emit("AGENT_SPEECH", actor, speech, "chat", {"mode": "discussion", "zone": "war_room"})
                await asyncio.sleep(2.0)
        
        feedback = None
        while self.iteration <= self.max_iterations:
            # ── 2. ARCHITECT BLUEPRINT ─────────────────────────────────────────
            await self.emit("AGENT_PHASE_START", "architect", f"Menyusun blueprint teknis (Iterasi {self.iteration})...", "thinking")
            self.party_stats["architect"]["mp"] -= 30
            
            architect_res = run_architect(self.quest_prompt, iteration=self.iteration, feedback=feedback)
            spec = architect_res.get("technical_spec", "")
            files_plan = architect_res.get("files_plan", [])
            test_criteria = architect_res.get("test_criteria", "")
            
            await self.emit("AGENT_SPEECH", "architect", architect_res.get("dialogue", "Rancangan blueprint siap ditempa di Forge!"), "idea", {
                "spec_preview": spec,
                "files_plan": files_plan
            })
            await asyncio.sleep(1.8)

            # ── 3. CRAFTSMAN AT THE FORGE (WITH LIVE CODE STREAMING) ───────────
            await self.emit("AGENT_PHASE_START", "craftsman", "Forge Master bergerak ke workshop untuk menempa kode & unit test...", "crafting")
            self.party_stats["craftsman"]["mp"] -= 40
            
            craftsman_res = run_craftsman(spec, files_plan, test_criteria, feedback=feedback)
            generated_files = craftsman_res.get("files", {})
            
            # Write files to Sandbox & Stream live code to frontend inspector
            for fname, content in generated_files.items():
                self.sandbox.write_file(fname, content)
                await self.emit("CODE_FILE_FORGED", "craftsman", f"File '{fname}' selesai ditempa.", "hammer", {
                    "file_name": fname,
                    "code_content": content
                })
                
            await self.emit("AGENT_SPEECH", "craftsman", craftsman_res.get("dialogue", "Kode berhasil ditempa. Menyerahkan ke Sentinel!"), "hammer", {
                "files_generated": list(generated_files.keys()),
                "files_dict": generated_files
            })
            await asyncio.sleep(1.8)

            # ── 4. SENTINEL AUDIT & SANDBOX BOSS BATTLE ────────────────────────
            await self.emit("AGENT_PHASE_START", "sentinel", "The Grand Inquisitor menguji kode di Chamber of Judgment Altar...", "inspecting")
            self.party_stats["sentinel"]["mp"] -= 35
            
            sandbox_result = self.sandbox.run_tests()
            sentinel_res = run_sentinel(spec, test_criteria, generated_files, sandbox_result)
            
            approved = sentinel_res.get("approved", False)
            score = sentinel_res.get("score", 0)
            
            if approved:
                await self.emit("QUEST_SUCCESS", "sentinel", sentinel_res.get("dialogue", "Semua pengujian lolos sempurna!"), "victory", {
                    "score": score,
                    "artifacts": self.sandbox.list_files(),
                    "review": sentinel_res.get("review_summary", "")
                })
                return {
                    "status": "completed",
                    "score": score,
                    "files": generated_files,
                    "iterations": self.iteration,
                    "review": sentinel_res.get("review_summary", "")
                }
            else:
                feedback = sentinel_res.get("review_summary", "Unit test gagal. Perbaiki logika kode.")
                await self.emit("QUEST_REVISION_REQUIRED", "sentinel", sentinel_res.get("dialogue", "Pengujian gagal! Rombak kembali kodenya di Forge!"), "warning", {
                    "feedback": feedback,
                    "sandbox_output": sandbox_result
                })
                self.iteration += 1
                await asyncio.sleep(2.0)
                
        # If max iterations reached
        await self.emit("QUEST_FAILED", "sentinel", "Batas iterasi habis. Quest membutuhkan intervensi Guild Master.", "skull")
        return {
            "status": "failed",
            "score": 40,
            "files": generated_files if 'generated_files' in locals() else {},
            "iterations": self.iteration
        }
