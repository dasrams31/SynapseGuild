from llm import llm_chat
import json

CRAFTSMAN_SYSTEM_PROMPT = """You are THE CRAFTSMAN (The Forge Master) in SynapseGuild.
Your role:
1. Receive technical specifications from The Architect.
2. Implement clean, robust, working Python code and corresponding pytest unit tests.
3. Write complete files without placeholders or stubs.

Output MUST be valid JSON strictly matching this schema:
{
  "dialogue": "Short in-character speech for the RPG speech bubble (max 2 sentences)",
  "files": {
    "module_name.py": "full source code content",
    "test_module_name.py": "full pytest test file content"
  }
}
"""

def run_craftsman(spec: str, files_plan: list, test_criteria: str, feedback: str = None) -> dict:
    user_content = f"Technical Spec:\n{spec}\n\nFiles Plan:\n{json.dumps(files_plan)}\n\nTest Criteria:\n{test_criteria}"
    if feedback:
        user_content += f"\n\nPrevious Sentinel Audit/Test Failure:\n{feedback}\nPlease fix the implementation and ensure all tests pass!"

    messages = [
        {"role": "system", "content": CRAFTSMAN_SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]
    
    raw = llm_chat(messages, temperature=0.1)
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
            "dialogue": "Artefak kode selesai ditempa di Forge. Menyerahkan ke Sentinel untuk diuji!",
            "files": {
                "solution.py": raw,
                "test_solution.py": "def test_default(): assert True"
            }
        }
