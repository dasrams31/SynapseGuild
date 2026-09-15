import json
from llm import llm_chat

def generate_party_discussion(quest_goal: str, phase: str, context: str = "") -> list:
    prompt = f"""You are simulating a lively, intelligent, and in-character team discussion in SynapseGuild.
The party consists of 3 distinct characters:
1. "architect" (The Sage / Guild Leader): Strategic, visionary, ensures modularity and architecture standards.
2. "craftsman" (The Forge Master): Pragmatic engineer, talks about code implementation details, algorithms, and libraries.
3. "sentinel" (The Grand Inquisitor): Critical auditor, skeptical, challenges edge cases, security, and testing rigor.

Task Goal: {quest_goal}
Current Phase: {phase}
Context/Issues: {context}

Generate a realistic, collaborative 3-turn discussion where each character contributes their perspective, debates trade-offs, and aligns on next steps.

Output MUST be valid JSON strictly matching this schema:
{{
  "dialogues": [
    {{
      "actor": "architect",
      "speech": "Natural conversational dialogue in Indonesian (1-2 sentences)",
      "target_zone": "war_room"
    }},
    {{
      "actor": "craftsman",
      "speech": "Natural conversational dialogue in Indonesian (1-2 sentences)",
      "target_zone": "war_room"
    }},
    {{
      "actor": "sentinel",
      "speech": "Natural conversational dialogue in Indonesian (1-2 sentences)",
      "target_zone": "war_room"
    }}
  ]
}}
"""
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "Mulai diskusi tim untuk merencanakan solusi terbaik."}
    ]
    
    try:
        raw = llm_chat(messages, temperature=0.6)
        clean = raw.strip()
        if clean.startswith("```json"):
            clean = clean[7:]
        if clean.endswith("```"):
            clean = clean[:-3]
        clean = clean.strip()
        data = json.loads(clean)
        return data.get("dialogues", [])
    except Exception:
        return [
            {"actor": "architect", "speech": f"Mari kita bedah arsitektur untuk quest: {quest_goal}.", "target_zone": "war_room"},
            {"actor": "craftsman", "speech": "Saya akan siapkan struktur modul yang modular dan efisien di Forge.", "target_zone": "war_room"},
            {"actor": "sentinel", "speech": "Pastikan semua edge case dan unit test tercover dengan ketat!", "target_zone": "war_room"}
        ]
