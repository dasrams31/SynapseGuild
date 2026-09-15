import asyncio
import json
import time
from typing import Dict, Any, Callable, Optional

from agents.architect import run_architect
from agents.craftsman import run_craftsman
from agents.sentinel import run_sentinel
from agents.dialogue_engine import generate_party_discussion
from sandbox_runner import CodeSandbox
from git_courier import push_artifacts_to_git

class GuildOrchestrator:
    def __init__(self, quest_id: str, quest_prompt: str, language: str = "python", preset: str = "classic", event_callback: Optional[Callable] = None):
        self.quest_id = quest_id
        self.quest_prompt = quest_prompt
        self.language = language.lower() # python | javascript
        self.preset = preset # classic | speedrun | security
        self.event_callback = event_callback
        self.sandbox = CodeSandbox(quest_id, language=self.language)
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
            "language": self.language,
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
        await self.emit("QUEST_INITIALIZED", "architect", f"Misi [{self.language.upper()}] diterima: '{self.quest_prompt}'. Party berkumpul!", "ready")
        
        # ── 1. REALTIME TEAM BRAINSTORMING & DEBATE (WAR ROOM) ────────────────
        if self.preset != "speedrun":
            await self.emit("AGENT_PHASE_START", "architect", f"Memulai sesi diskusi strategi {self.language.upper()} di War Room...", "meeting")
            discussion = generate_party_discussion(f"[{self.language.upper()}] {self.quest_prompt}", phase="PLANNING_AND_DESIGN")
            for turn in discussion:
                actor = turn.get("actor", "architect")
                speech = turn.get("speech", "")
                await self.emit("AGENT_SPEECH", actor, speech, "chat", {"mode": "discussion", "zone": "war_room"})
                await asyncio.sleep(2.0)
        
        feedback = None
        while self.iteration <= self.max_iterations:
            # ── 2. ARCHITECT BLUEPRINT ─────────────────────────────────────────
            await self.emit("AGENT_PHASE_START", "architect", f"Menyusun blueprint teknis {self.language.upper()} (Iterasi {self.iteration})...", "thinking")
            self.party_stats["architect"]["mp"] -= 30
            
            architect_res = run_architect(self.quest_prompt, language=self.language, iteration=self.iteration, feedback=feedback)
            spec = architect_res.get("technical_spec", "")
            files_plan = architect_res.get("files_plan", [])
            test_criteria = architect_res.get("test_criteria", "")
            
            await self.emit("AGENT_SPEECH", "architect", architect_res.get("dialogue", "Rancangan blueprint siap ditempa di Forge!"), "idea", {
                "spec_preview": spec,
                "files_plan": files_plan
            })
            await asyncio.sleep(1.8)

            # ── 3. CRAFTSMAN AT THE FORGE (WITH LIVE CODE STREAMING) ───────────
            await self.emit("AGENT_PHASE_START", "craftsman", f"Forge Master bergerak ke workshop untuk menempa kode {self.language.upper()} & unit test...", "crafting")
            self.party_stats["craftsman"]["mp"] -= 40
            
            craftsman_res = run_craftsman(spec, files_plan, test_criteria, language=self.language, feedback=feedback)
            generated_files = craftsman_res.get("files", {})
            
            # Write files to Sandbox & Stream live code to frontend inspector
            for fname, content in generated_files.items():
                self.sandbox.write_file(fname, content)
                await self.emit("CODE_FILE_FORGED", "craftsman", f"File '{fname}' selesai ditempa.", "hammer", {
                    "file_name": fname,
                    "code_content": content,
                    "language": self.language
                })
                
            await self.emit("AGENT_SPEECH", "craftsman", craftsman_res.get("dialogue", f"Kode {self.language.upper()} berhasil ditempa. Menyerahkan ke Sentinel!"), "hammer", {
                "files_generated": list(generated_files.keys()),
                "files_dict": generated_files
            })
            await asyncio.sleep(1.8)

            # ── 4. SENTINEL AUDIT & SANDBOX BOSS BATTLE ────────────────────────
            await self.emit("AGENT_PHASE_START", "sentinel", f"The Grand Inquisitor menguji kode {self.language.upper()} di Altar...", "inspecting")
            self.party_stats["sentinel"]["mp"] -= 35
            
            sandbox_result = self.sandbox.run_tests()
            sentinel_res = run_sentinel(spec, test_criteria, generated_files, sandbox_result)
            
            approved = sentinel_res.get("approved", False)
            score = sentinel_res.get("score", 0)
            
            if approved:
                # ── 5. THE ROYAL COURIER: AUTO GIT COMMIT & HALL OF FAME LOGGING ───
                git_res = push_artifacts_to_git(self.quest_id, self.quest_prompt, generated_files)
                
                await self.emit("QUEST_SUCCESS", "sentinel", sentinel_res.get("dialogue", "Semua pengujian lolos sempurna!"), "victory", {
                    "score": score,
                    "language": self.language,
                    "artifacts": self.sandbox.list_files(),
                    "review": sentinel_res.get("review_summary", ""),
                    "git_status": git_res
                })
                return {
                    "status": "completed",
                    "score": score,
                    "language": self.language,
                    "files": generated_files,
                    "iterations": self.iteration,
                    "review": sentinel_res.get("review_summary", ""),
                    "git": git_res
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
            "language": self.language,
            "files": generated_files if 'generated_files' in locals() else {},
            "iterations": self.iteration
        }
