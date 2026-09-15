from llm import llm_chat
import json

ARCHITECT_SYSTEM_PROMPT = """You are THE ARCHITECT (The Sage / Guild Leader) in SynapseGuild.
Your role:
1. Receive high-level quest prompts and the requested programming language (Python or JavaScript/TypeScript).
2. Decompose the goal into technical specifications, modular file structures, and strict test criteria matching the target language.
3. If JavaScript, specify files for native Node.js test runner (`node:test` and `node:assert`).

Output MUST be valid JSON strictly matching this schema:
{{
  "dialogue": "Short in-character speech for the RPG speech bubble (max 2 sentences)",
  "technical_spec": "Detailed implementation guide for The Craftsman",
  "files_plan": ["list", "of", "files", "to", "create"],
  "test_criteria": "Acceptance criteria that The Sentinel will test"
}}
"""

def run_architect(quest_goal: str, language: str = "python", iteration: int = 1, feedback: str = None) -> dict:
    user_content = f"Quest Goal: {quest_goal}\nTarget Programming Language: {language}\nIteration: {iteration}"
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
        ext = ".js" if language in ["javascript", "node", "nodejs"] else ".py"
        return {
            "dialogue": f"Saya telah menyusun blueprint arsitektur {language.upper()} untuk quest ini. Craftsman, silakan tempa!",
            "technical_spec": raw,
            "files_plan": [f"main{ext}", f"test_main{ext}"],
            "test_criteria": f"Unit tests in {language.upper()} must cover all core calculations with 100% pass rate."
        }
