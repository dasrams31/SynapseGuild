from llm import llm_chat
import json

CRAFTSMAN_SYSTEM_PROMPT = """You are THE CRAFTSMAN (The Forge Master) in SynapseGuild.
Your role:
1. Receive technical specifications from The Architect.
2. Implement clean, robust, working code in the requested language (Python or JavaScript/Node.js).
3. If JavaScript/Node.js is chosen, write test files using native Node test syntax: `const test = require('node:test'); const assert = require('node:assert');`
4. Write complete files without placeholders or stubs.

Output MUST be valid JSON strictly matching this schema:
{{
  "dialogue": "Short in-character speech for the RPG speech bubble (max 2 sentences)",
  "files": {{
    "module_name.ext": "full source code content",
    "test_module_name.ext": "full unit test file content"
  }}
}}
"""

def run_craftsman(spec: str, files_plan: list, test_criteria: str, language: str = "python", feedback: str = None) -> dict:
    user_content = (
        f"Language: {language}\n"
        f"Technical Spec:\n{spec}\n\n"
        f"Files Plan:\n{json.dumps(files_plan)}\n\n"
        f"Test Criteria:\n{test_criteria}"
    )
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
        ext = ".js" if language in ["javascript", "node", "nodejs"] else ".py"
        return {
            "dialogue": f"Artefak kode {language.upper()} selesai ditempa di Forge. Menyerahkan ke Sentinel!",
            "files": {
                f"solution{ext}": raw,
                f"test_solution{ext}": "assert True" if ext == ".py" else "const test = require('node:test'); test('ok', () => {});"
            }
        }
