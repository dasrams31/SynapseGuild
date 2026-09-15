import asyncio
import time
from typing import Dict, Any, Callable, Optional

from agents.architect import run_architect
from agents.craftsman import run_craftsman
from agents.sentinel import run_sentinel
from agents.dialogue_engine import generate_party_discussion
from sandbox_runner import CodeSandbox

class GuildOrchestrator:
    def __init__(self, quest_id: str, quest_prompt: str, event_callback: Optional[Callable[[Dict[str, Any]], Any]] = None):
        self.quest_id = quest_id
        self.quest_prompt = quest_prompt
        self.event_callback = event_callback
        self.sandbox = CodeSandbox(quest_id)
        
        # Party RPG State
        self.party_stats = {
            "architect": {"hp": 100, "mp": 500, "zone": "war_room", "pos": [150, 210]},
            "craftsman": {"hp": 100, "mp": 500, "zone": "forge", "pos": [400, 210]},
            "sentinel":  {"hp": 100, "mp": 500, "zone": "judgment_chamber", "pos": [650, 210]}
        }
        self.iteration = 1
        self.max_iterations = 3
        self.quest_result = None

    async def emit(self, event_type: str, actor: str, dialogue: str, emote: str, extra: dict = None):
        payload = {
            "quest_id": self.quest_id,
            "timestamp": time.time(),
            "event_type": event_type,
            "actor": {
                "id": actor,
                "name": {"architect": "The Sage", "craftsman": "The Forge Master", "sentinel": "The Grand Inquisitor"}.get(actor, "Guild Master"),
                "zone": self.party_stats.get(actor, {}).get("zone", "guild_hall"),
                "position": self.party_stats.get(actor, {}).get("pos", [400, 210])
            },
            "action": {
                "dialogue": dialogue,
                "emote": emote
            },
            "party_stats": self.party_stats,
            "extra": extra or {}
        }
        if self.event_callback:
            if asyncio.iscoroutinefunction(self.event_callback):
                await self.event_callback(payload)
            else:
                self.event_callback(payload)

    async def run(self) -> dict:
        await self.emit("QUEST_INITIALIZED", "architect", f"Misi baru diterima: '{self.quest_prompt}'. Party berkumpul di War Room!", "ready")
        
        # ── 1. REALTIME TEAM BRAINSTORMING & DEBATE (WAR ROOM) ────────────────
        await self.emit("AGENT_PHASE_START", "architect", "Memulai sesi diskusi dan debat strategi di War Room...", "meeting")
        
        # Gather all characters to War Room for discussion
        discussion = generate_party_discussion(self.quest_prompt, phase="PLANNING_AND_DESIGN")
        for turn in discussion:
            actor = turn.get("actor", "architect")
            speech = turn.get("speech", "")
            await self.emit("AGENT_SPEECH", actor, speech, "chat", {"mode": "discussion", "zone": "war_room"})
            await asyncio.sleep(2.5) # Natural conversational pacing for web visual
        
        feedback = None
        while self.iteration <= self.max_iterations:
            # ── 2. ARCHITECT BLUEPRINT ─────────────────────────────────────────
            await self.emit("AGENT_PHASE_START", "architect", f"Menyusun blueprint teknis (Iterasi {self.iteration})...", "thinking")
            self.party_stats["architect"]["mp"] -= 40
            
            architect_res = run_architect(self.quest_prompt, iteration=self.iteration, feedback=feedback)
            spec = architect_res.get("technical_spec", "")
            files_plan = architect_res.get("files_plan", [])
            test_criteria = architect_res.get("test_criteria", "")
            
            await self.emit("AGENT_SPEECH", "architect", architect_res.get("dialogue", "Rancangan selesai, silakan tempa kodenya!"), "idea", {
                "spec_preview": spec[:200] + "...",
                "files_plan": files_plan
            })
            await asyncio.sleep(2.0)

            # ── 3. CRAFTSMAN AT THE FORGE ──────────────────────────────────────
            await self.emit("AGENT_PHASE_START", "craftsman", "Craftsman bergerak ke Forge untuk merakit kode & unit test...", "crafting")
            self.party_stats["craftsman"]["mp"] -= 60
            
            craftsman_res = run_craftsman(spec, files_plan, test_criteria, feedback=feedback)
            generated_files = craftsman_res.get("files", {})
            
            # Write files to Sandbox
            for fname, content in generated_files.items():
                self.sandbox.write_file(fname, content)
                
            await self.emit("AGENT_SPEECH", "craftsman", craftsman_res.get("dialogue", "Kode berhasil ditempa. Menyerahkan ke Sentinel!"), "hammer", {
                "files_generated": list(generated_files.keys())
            })
            await asyncio.sleep(2.0)

            # ── 4. SENTINEL AUDIT & SANDBOX EXECUTION ──────────────────────────
            await self.emit("AGENT_PHASE_START", "sentinel", "Sentinel memeriksa dan mengeksekusi pengujian di Chamber of Judgment...", "inspecting")
            self.party_stats["sentinel"]["mp"] -= 50
            
            sandbox_result = self.sandbox.run_tests()
            sentinel_res = run_sentinel(spec, test_criteria, generated_files, sandbox_result)
            
            approved = sentinel_res.get("approved", False)
            score = sentinel_res.get("score", 0)
            
            if approved:
                self.party_stats["craftsman"]["hp"] = min(100, self.party_stats["craftsman"]["hp"] + 10)
                await self.emit("QUEST_SUCCESS", "sentinel", sentinel_res.get("dialogue", "Semua pengujian 100% lolos!"), "victory", {
                    "score": score,
                    "sandbox": sandbox_result,
                    "artifacts": list(generated_files.keys())
                })
                
                # Victory team celebration dialogue
                await asyncio.sleep(2.0)
                await self.emit("AGENT_SPEECH", "craftsman", "Kerja sama tim yang luar biasa! Artefak siap dikirim ke Guild Master.", "celebrate")
                await asyncio.sleep(1.5)
                await self.emit("AGENT_SPEECH", "architect", "Misi sukses terselesaikan dengan standar kualitas tertinggi. Quest Complete!", "victory")
                
                self.quest_result = {
                    "status": "completed",
                    "iterations": self.iteration,
                    "score": score,
                    "files": generated_files,
                    "sandbox_result": sandbox_result,
                    "review": sentinel_res.get("review_summary")
                }
                return self.quest_result
            else:
                # Deduct HP on failure
                self.party_stats["craftsman"]["hp"] = max(10, self.party_stats["craftsman"]["hp"] - 25)
                feedback = f"Pytest Output:\n{sandbox_result.get('stdout')}\n{sandbox_result.get('stderr')}\nReview: {sentinel_res.get('review_summary')}"
                
                await self.emit("QUEST_REVISION_REQUIRED", "sentinel", sentinel_res.get("dialogue", "Ditemukan kegagalan pengujian! Segera perbaiki di Forge!"), "warning", {
                    "score": score,
                    "feedback": feedback,
                    "sandbox": sandbox_result
                })
                
                # Short debate on failure before re-forging
                await asyncio.sleep(2.0)
                await self.emit("AGENT_SPEECH", "craftsman", "Saya melihat titik error pada assertions, saya perbaiki sekarang di Forge!", "hammer")
                
                self.iteration += 1

        # Fallback if max iterations exceeded
        await self.emit("QUEST_FAILED", "architect", "Batas iterasi habis. Quest memerlukan intervensi Guild Master.", "skull")
        self.quest_result = {
            "status": "failed",
            "iterations": self.iteration - 1,
            "feedback": feedback
        }
        return self.quest_result
