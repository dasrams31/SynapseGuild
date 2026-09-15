from llm import llm_chat
import json

ARCHITECT_SYSTEM_PROMPT = """You are THE ARCHITECT (The Sage / Guild Leader) in SynapseGuild.
Your role:
1. Receive high-level quest prompts from the Guild Master (user).
2. Decompose the goal into technical system specifications, modular file structures, and strict BDD/Acceptance Criteria.
3. If an iteration failed tests, adjust the technical blueprint to guide The Craftsman towards resolving the bug.

Output MUST be valid JSON strictly matching this schema:
{
  "dialogue": "Short in-character speech for the RPG speech bubble (max 2 sentences)",
  "technical_spec": "Detailed implementation guide for The Craftsman",
  "files_plan": ["list", "of", "files", "to", "create"],
  "test_criteria": "Acceptance criteria that The Sentinel will test"
}
"""

def run_architect(quest_goal: str, iteration: int = 1, feedback: str = None) -> dict:
    user_content = f"Quest Goal: {quest_goal}\nIteration: {iteration}"
    if feedback:
        user_content += f"\nPrevious Sentinel Review Feedback:\n{feedback}\nPlease revise the technical specification to resolve these failures."

    messages = [
        {"role": "system", "content": ARCHITECT_SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]
    
    raw = llm_chat(messages, temperature=0.2)
    clean = raw.strip()
    if clean.startswith("```json"):
        clean = clean[7:]
    if clean.endswith("```"):
        clean = clean[:-3]
    clean = clean.strip()
    
    try:
        return json.loads(clean)
    except Exception:
        return {
            "dialogue": "Saya telah menyusun blueprint teknis untuk quest ini. Craftsman, silakan tempa kodenya!",
            "technical_spec": raw,
            "files_plan": ["main.py", "test_main.py"],
            "test_criteria": "Unit tests must cover all core calculations with 100% pass rate."
        }
